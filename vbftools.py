from sys import stdin, stdout, stderr

def decode_header(header: list[str]) -> tuple[str, ...]:
    return tuple(
        ''.join(
            chr(int(hexcode, base=16))
            for hexcode in sequence.split('U+')[1:])
        for sequence in ''.join(header).replace(' ', '').split(','))

def decode_glyph(glyph: list[str]) -> tuple[tuple[bool, ...], ...]:
    return tuple(tuple(   
            {'  ': False, 'XX': True}[window]
            for window in [
                row[i:i+2]
                for i in range(0, len(row), 2)])
        for row in glyph)

def decode_box(vbf, row_1st, col_1st) -> tuple[list[str], list[str]]:
    box_width = vbf[row_1st][col_1st+1:].index('*')

    box_height = 0
    for row in vbf[row_1st+1:]:
        if len(row) < 1:
            break
        if row[0] == '*':
            break
        box_height += 1

    header_height = 0
    for row in vbf[row_1st+1:]:
        if len(row) < 2:
            break
        if row[1] == '-':
            break
        header_height += 1
    
    header_col_start = col_1st + 1
    header_col_stop  = header_col_start + box_width
    header_row_start = row_1st + 1
    header_row_stop  = header_row_start + header_height
    glyph_col_start  = col_1st + 1
    glyph_col_stop   = glyph_col_start + box_width
    glyph_row_start  = header_row_stop + 1
    glyph_row_stop   = glyph_row_start + (box_height - header_height - 1)

    header = [
        row[header_col_start:header_col_stop]
        for row in vbf[header_row_start:header_row_stop]]
    
    glyph = [
        row[glyph_col_start:glyph_col_stop]
        for row in vbf[glyph_row_start:glyph_row_stop]]

    return header, glyph

def encode_header(sequences: list[str], header_width: int) -> list[str]:
    header = ','.join(
            ''.join(f'U+{ord(char):04x}' 
            for char in sequence)
        for sequence in sequences)
    
    return (
        [   header[i:i+header_width]
            for i in range(0, len(header) - header_width, header_width)]
        + [header[(len(header)//header_width)*header_width:].ljust(header_width)])

def encode_glyph(rows: list[list[bool]]) -> list[str]:
    return [
        ''.join(
            {False: '  ', True: 'XX'}[pixel]
            for pixel in row)
        for row in rows]

def encode_box(header: list[str], glyph: list[str]) -> list[str]:
    inner_width = len(header[0])
    return (
          ['*' + '-' * inner_width + '*']
        + ['|' + line + '|' for line in header]
        + ['|' + '-' * inner_width + '|']
        + ['|' + line + '|' for line in glyph]
        + ['*' + '-' * inner_width + '*'])

# impure function. mutates lines for memory efficiency
def draw_box(lines: list[str], box: list[str], row_1st: int, col_1st: int) -> None:
    lines.extend([''] * (row_1st + len(box) - len(lines)))
    
    for i, box_row in enumerate(box, start = row_1st):
        left = lines[i][:col_1st].ljust(col_1st)
        right = lines[i][col_1st + len(box_row):]
        lines[i] = left + box_row + right

# given n boxes of pxq dimensions, fit them in a matrix so that they fit on a canvas whose ratio is r

# canvas_width = cell_width * cells_per_row
# canvas_height = cell_height * cells_per_col

def arrange_boxes(boxes: list[list[str]], ratio: float = 2) -> list[tuple[int, int]]:
    cell_height = max(len(box) for box in boxes)
    cell_width = max(len(box[0]) for box in boxes)
    
    cells_per_row = int((len(boxes) * ratio) ** 0.5) 
    cells_per_col = int((len(boxes) / ratio) ** 0.5)
    
    return [
        (row * (cell_height + 1), col * (cell_width + 1))
        for row in range(cells_per_col)
        for col in range(cells_per_row)] + [
        (cells_per_col * (cell_height + 1), col * (cell_width + 1))
        for col in range(len(boxes) - cells_per_row * cells_per_col)]

def at(matrix, row, col):
    return (matrix[row][col] 
        if 0 <= row < len(matrix) 
        and 0 <= col < len(matrix[row])
        else None)

def vbf_to_IR(vbf: list[str]) -> dict[tuple[str], list[list[bool]]]:
    boxes = [decode_box(vbf, row, col)
        for row, line in enumerate(vbf)
        for col, char in enumerate(line)
        if (
            char == '*' 
            and at(vbf, row    , col + 1) == '-' 
            and at(vbf, row + 1, col    ) == '|')]
    
    return {
        decode_header(header): decode_glyph(glyph)
        for header, glyph in boxes}

def IR_to_vbf(IR: dict[tuple[str], list[list[bool]]]) -> list[str]:
    headers = []
    glyphs = []
    for header, glyph in IR.items():
        headers.append(header)
        glyphs.append(encode_glyph(glyph))
    
    # make all headers uniform
    header_width = max(len(glyph) for glyph in glyphs)
    headers = [encode_header(header, header_width) for header in headers]
    header_height = max(len(header) for header in headers)
    headers = [
        header + [' ' * header_width] * (header_height - len(header)) 
        for header in headers]
    
    boxes = [
        encode_box(header, glyph) 
        for header, glyph in zip(headers, glyphs)]

    positions = arrange_boxes(boxes)
    
    lines = []
    
    # we do it without comprehension because draw_box is mutating, not pure
    for box, position in zip(boxes, positions):
        row, col = position
        draw_box(lines, box, row, col)
    
    return [line + '\n' for line in lines]

# to/from psf ------------------------------------------------------------------

PSF1_MAGIC = b'\x36\x04'
PSF2_MAGIC = b'\x72\xB5\x4A\x86'
PSF2_SEPARATOR = b'\xFF'
PSF2_STARTSEQ = b'\xFE'

def IR_to_psf2(IR: dict[tuple[str], list[list[bool]]]) -> bytes:
    char_heights = set(len(glyph) for glyph in IR.values())
    char_widths = set(len(glyph[0]) for glyph in IR.values())

    if len(char_heights) != 1 or len(char_widths) != 1:
        raise ValueError(f'psf requires that all characters are the same dimension. the ones we found were {char_heights=} and {char_widths=}')

    char_height = next(iter(char_heights))
    char_width = next(iter(char_widths))
    char_size = char_height * ((char_width + 7) // 8)
    
    header = b''.join([
        PSF2_MAGIC,
        (0).to_bytes(4, 'little'),   # version (0 is the max version recognized so far)
        (4*8).to_bytes(4, 'little'), # headersize
        (0x01).to_bytes(4, 'little'), # flags (always has unicode mappings)
        (len(IR)).to_bytes(4, 'little'), # length
        (char_size).to_bytes(4, 'little'), # charsize
        (char_height).to_bytes(4, 'little'), # height
        (char_width).to_bytes(4, 'little')]) # width
    
    bitmaps: bytes = b''
    unicodes: bytes = b''

    for sequences, glyph in IR.items():
        bitmaps += bytes(
            sum(
                bit << (7 - i) 
                for i, bit in enumerate(row))
            for row in glyph)

        for sequence in sequences:
            if len(sequence) == 1:
                unicodes += sequence.encode(encoding='utf-8')
            else: 
                unicodes += PSF2_STARTSEQ + b''.join(
                    char.encode(encoding='utf-8') 
                    for char in sequence)
        unicodes += PSF2_SEPARATOR
    
    return header + bitmaps + unicodes

def bytes_to_list_of_bool(thebyteof87: bytes) -> list[bool]:
    return [bool(byte & (1 << i))
        for byte in thebyteof87 
        for i in range(7, -1, -1)]

def psf2_to_IR(psf: bytes) -> dict[tuple[str], list[list[bool]]]:
    if (magic := psf[0:4]) != PSF2_MAGIC:
        raise Exception(f'{magic=} != {PSF2_MAGIC=}')
    if (version := int.from_bytes(psf[ 4: 8], 'little')) != 0:
        raise Exception(f'{version=} != 0')
    headersize = int.from_bytes(psf[ 8:12], 'little')
    if (flags := int.from_bytes(psf[12:16], 'little')) != 1:
        raise Exception(f'{flags=} != 1')
    length     = int.from_bytes(psf[16:20], 'little')
    charsize   = int.from_bytes(psf[20:24], 'little')
    height     = int.from_bytes(psf[24:28], 'little')
    width      = int.from_bytes(psf[28:32], 'little')
    
    codepoints_start = headersize + charsize * length
    width_bytes = charsize // height
    
    bitmaps = [
        [   bytes_to_list_of_bool(row)[:width]
            for row in [
                glyph[i:i+width_bytes]
                for i in range(0, charsize, width_bytes)]]
        for glyph in [
            psf[i:i+charsize]
            for i in range(headersize, codepoints_start, charsize)]]
    
    unicodes = [
        tuple(strings[0]) + tuple(strings[1:])
        for strings in [
            [   sequence.decode(encoding='utf-8')
                for sequence in sequences.split(PSF2_STARTSEQ)]
            for sequences in psf[codepoints_start:].split(PSF2_SEPARATOR)[:-1]]]
    
    return dict(zip(unicodes, bitmaps, strict=True))

# def psf1_to_(psf: bytes) -> dict[tuple[str], list[list[bool]]]:
#     if (magic := psf[0:2]) != PSF1_MAGIC:
#         raise Exception(f'{magic=} != {PSF1_MAGIC=}')
#     mode = 
#     charsize = 

def vbf_to_psf():
    stdout.buffer.write(IR_to_psf2(vbf_to_IR(stdin.readlines())))

def psf_to_vbf():
    file = stdin.buffer.read()
    if file[0:2] == PSF1_MAGIC:
        stdout.writelines(IR_to_vbf(psf1_to_IR(file)))
    elif file[0:4] == PSF2_MAGIC:
        stdout.writelines(IR_to_vbf(psf2_to_IR(file)))
    else:
        raise Exception('magic number is not a valid psf magic number')

