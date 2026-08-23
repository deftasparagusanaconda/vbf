# vbf (IN DEVELOPMENT)

a **v**isual **b**itmap **f**ont format. you can edit a .vbf font with a text editor like its ASCII art (recommend you use a monospaced font with a 2:1 ratio)

```
uppercase alpha is very
similar to uppercase A
so lets use the same 
for both             +------------------+
+------------------+ |               U+0|  
| U+0041, U+0391   | |042,U+0392        |  
|------------------| |------------------|   +------------+
|                  | |                  |   |   U+0044   |
|      XXXXXX      | |  XXXXXXXXXX      |   |------------|
|    XX      XX    | |  XX        XX    |   |  XXXX      |
|  XX          XX  | |  XX          XX  |   |  XX  XX    |
|  XX          XX  | |  XX          XX  |   |  XX    XX  |
|  XX          XX  | |  XX          XX  |   |  XX    XX  |
|  XX          XX  | |  XX        XX    |   |  XX    XX  |
|  XXXXXXXXXXXXXX  | |  XXXXXXXXXX      |   |  XX    XX  |
|  XX          XX  | |  XX        XX    |   |  XX  XX    |
|  XX          XX  | |  XX          XX  |   |  XXXX      |
|  XX          XX  | |  XX          XX  |   +------------+
|  XX          XX  | |  XX          XX  |   "daa.. why is D smaller?"
|  XX          XX  | |  XX        XX    |  for the sake of example.
|  XX          XX  | |  XXXXXXXXXX      |  thats why.
|                  | |                  |
+------------------+ +------------------+
```
[examples](https://github.com/deftasparagusanaconda/vbf/tree/main/examples)

glyphs are defined in floating boxes drawn with `+` `-` `|`. everything not in a box is ignored. pixels are drawn two characters wide: `  ` or `XX`

each glyph is mapped to one or more unicode sequences (a series of U+XXXX codepoints) separated by commas. whitespace in the header box is ignored.

# converting to/from [psf](https://en.wikipedia.org/wiki/PC_Screen_Font)

install the two conversion tools:
```
pip install vbftools
```
convert to/from .psf:
```
psf_to_vbf < font.psf > font.vbf
vbf_to_psf < font.vbf > font.psf
```
_(note: psf requires that all glyphs are the same size)_  

load a psf font: `setfont font.psf`  
show the current font: `showconsolefont`  
compress a font: `gzip font.psf`  
decompress a font: `gunzip font.psf.gz`  
find fonts: `man setfont`  
