from sys import stdin as _stdin, stdout as _stdout
from math import ceil as _ceil
from itertools import batched

def decode_header(header: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(
        ''.join(
            chr(int(codepoint[2:], 16)) 
            for codepoint in sequence.strip().split(' '))
        for sequence in ''.join(header).split(','))

def decode_glyph(glyph: tuple[str, ...]) -> tuple[int, ...]:
    glyph_width = len(glyph[0])
    binary = [''.join(
            {' ':'0','X':'1'}[char] 
            for char in line[::2]
        ).ljust(_ceil(glyph_width/8)*8, '0')
        for line in glyph]
    return tuple(int(row, 2) for row in binary)

def encode_header(header: tuple[str, ...]) -> tuple[str, ...]:
    ...

def encode_glyph(glyph: tuple[int, ...]) -> tuple[str, ...]:
    ...

def ipsf_to_glyphs(lines: list[str]) -> dict[tuple[str, ...], tuple[int, ...]]:
    first_row = lines[0]
    first_col = ''.join(line[0] for line in lines)
    corner_xs = [i for i, c in enumerate(first_row) if c == '+']
    corner_ys = [i for i, c in enumerate(first_col) if c == '+']
    header_width = lines[0][1:].index('+')
    header_height = first_col[1:].index('+')
    glyph_width = header_width
    glyph_height = first_col[header_height+2:].index('+')

    cells: dict[tuple[str, ...], tuple[str, ...]] = {
        tuple(
            line[x+1:x+1+header_width] 
            for line in lines[y+1              :y+1+header_height             ]):
        tuple(
            line[x+1:x+1+ glyph_width] 
            for line in lines[y+2+header_height:y+2+header_height+glyph_height])
        for y in corner_ys[::3]
        for x in corner_xs[:-1]}
    
    return {decode_header(header): decode_glyph(glyph) for header, glyph in cells.items()}

def glyphs_to_psf(glyphs: dict[tuple[str, ...], tuple[bytes, ...]]) -> list[str]:
    ...
    
    int(row, 2).to_bytes(len(row) // 8, 'big') 
    print(' '.join(f'{b:02X}' for b in row))
    
def ipsf_to_glyphs(lines: list[str]) -> dict[tuple[str, ...], tuple[bytes, ...]]:

def psf_to_glyphs():
    ...

def glyphs_to_ipsf(glyphs: dict[tuple[str, ...], tuple[bytes, ...]], col_count=4) -> list[str]:
    row_count = len(glyphs) // col_count

    if row_count * col_count != len(glyphs):
        raise ValueError(f'cant divide {len(glyphs)} glyphs cleanly into {col_count} columns')

    output: list[str] = []
    for batch in batched(glyphs.items(), col_count):
        batch = [(encode_header(header), encode_glyph(glyph)) for header, glyph in batched(glyphs.items(), col_count)]

        output += '-'*glyph_width.join('+'*(col_count+1))
        for 
        output += '|' + '|'.join(header[i] for i,  in batch) + '|'
        output += '-'*glyph_width.join('+'*(col_count+1))
        output += '|' + '|'.join(glyph[i] for header, glyph in batch) + '|'
        output += '-'*glyph_width.join('+'*(col_count+1))
        print()

def ipsf_to_psf_cli():
    _stdout.writelines(glyphs_to_psf(ipsf_to_glyphs(_stdin.readlines())))

def psf_to_ipsf_cli():
    _stdout.writelines(glyphs_to_ipsf(psf_to_glyphs(_stdin.readlines())))
