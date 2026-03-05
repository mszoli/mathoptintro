# Puzzles

Puzzles provide a fun way to get hands-on experience with CP/MIP formulations and solvers.

## <a href="https://www.puzzle-thermometers.com/" target="_blank">Thermometers</a>

There is a *grid* of size $n\times n$, where the cells are covered by thermometers.
The goal is to fill some thermometers with mercury starting from the bulb and going toward the end without gaps.
The *clue values* on the top and on the left side indicate the number of filled cells horizontally and vertically, respectively.

```
Task:       Solution:
   3211        3211
 2 ╶╴╶┐      2   ╶┐
 1 ╷┌╴╵      1 ╷
 2 │╵╶╴      2 │╵
 2 └──╴      2 └─
```

Thermometers instances are encoded as strings as follows.
For example, the instance shown above is given as:
```python
thermometers_instance = '3_2_1_1_2_1_2_2;1,2;5,2,3,7;5,4,8,12,13,14,15;5,9,5,6;1,2'
```
The first part of the string (i.e., the substring until the first semicolon) refers to the $2n$ clue values for columns (left to right) and for rows (top to bottom) separated by underscores.
The second part of the string refers to the thermometers, separated by semicolons.
Each thermometer is given as a sequence of numbers, separated by commas, where the first number indicates the type of the thermometer.

- *Curved thermometers* are indicated with type `'5'`, which is followed by the explicit description of the corresponding cell sequence.
Note that the cells are number from 1 to $n^2$ in row-major order (i.e., left to right and top to bottom).
- *Straight thermometers* are indicited with types `'1'`-`'4'`, which describe their direction (1: horizontal, left to right; 2: horizontal, right to left; 3: vertical, top to bottom; 4: vertical, bottom to top).
Each straight thermometers starts (types `'1'`, `'3'`) or ends (types `'2'`, `'4'`) in the first cell, which is not occupied by a former thermometer.

File <a href="https://github.com/hmarko89/mathoptintro/blob/master/src/puzzles/thermometers.py" target="_blank">`src/puzzles/thermometers.py`</a> contains a decoding method for Thermometers instances.

## <a href="https://www.puzzle-kakurasu.com/" target="_blank">Kakurasu</a>

Given an $n\times n$ grid with target values assigned to each row and column.
The goal is to mark (for example, shade) some cells so that the sum of the indices of the marked cells in every row and column matches the given target values.

```text
Instance:         Solution:      
    1 2 3 4           1 2 3 4    
  ┌─────────┐       ┌─────────┐  
1 │         │ 5   1 │ ×     × │ 5   indices: top and left
2 │         │ 4   2 │       × │ 4   target values: bottom and right
3 │         │ 2   3 │   ×     │ 2
4 │         │ 8   4 │ ×   × × │ 8
  └─────────┘       └─────────┘  
    5 3 4 7           5 3 4 7    
```

Kakurasu instances are encoded as strings that consist of the target values for columns (from left to right) and for rows (from top to bottom) separated by slashes `'/'`.
For example, the instance shown above is encoded as:
```python
kakurasu_instance = '5/3/4/7/5/4/2/8'
```

File <a href="https://github.com/hmarko89/mathoptintro/blob/master/src/puzzles/kakurasu.py" target="_blank">`src/puzzles/kakurasu.py`</a> contains a decoding method for Kakurasu instances.

## <a href="https://www.puzzle-skyscrapers.com/" target="_blank">Skyscrapers (Skylines, Towers)</a>

Given an $n\times n$ grid with clues along the edges (top, bottom, left, right) and some pre-filled cells.
The goal is to fill the remaining cells with numbers $1,\ldots,n$ – representing skyscrapers of that heights – such that:

- each number appears exactly once in every row and every column;
- each edge clue indicates how many skyscrapers are visible from that direction in the corresponding row or column.
Note that a taller skyscraper blocks the view of any shorter skyscraper behind it.

```text
Instance:           Solution:       
          2                   2      
  ┌───────────┐       ┌───────────┐  
4 │ · · · · · │     4 │ 2 1 3 4 5 │  
  │ · · · · · │ 4     │ 5 4 1 3 2 │ 4
  │ · · · · · │       │ 4 2 5 1 3 │  
  │ · · · · 1 │       │ 1 3 2 5 4 │  
  │ · · 2 · · │       │ 3 5 4 2 1 │  
  └───────────┘       └───────────┘  
    3     2             3     2      
```

Skyscrapers instances are encoded as strings, as follows.
The string consists of one or two parts, separated by a comma `','` in the latter case.
The first part encodes the clues for columns (top and bottom, from left to right) and for rows (left and right, from top to bottom), separated by slashes `'/'`, using `''` for missing clues.
The optional second part encodes the grid itself.
Cells are listed in row-major order (i.e., left to right and top to bottom).
If a cell contains a number, the number is written directly; if it is empty, the number of consecutive empty cells until the next pre-given number (or until the end) is represented by a single character: `'a'` for 1 empty cell, `'b'` for 2 empty cells, `'c'` for 3 empty cells, etc.
Underscores `'_'` can optionally be used to separate adjacent numbers for readability.
For example, the instance shown above is encoded as:
```python
skyscrapers_instance = '///2//3///2//4//////4///,s1b2b'
```

File <a href="https://github.com/hmarko89/mathoptintro/blob/master/src/puzzles/skyscrapers.py" target="_blank">`src/puzzles/skyscrapers.py`</a> contains a decoding method for Skyscrapers instances.

## <a href="https://www.puzzle-binairo.com/" target="_blank">Binario (Takuzu)</a>

Given a $2n \times 2n$ grid, some cells may already be filled with black or white circles.
The goal is to fill the remaining cells with black and white circles so that:

- each row and each column contains exactly $n$ black circles and $n$ white circles;
- no row or column contains three consecutive circles of the same color;
- all rows are pairwise distinct, and all columns are pairwise distinct.

```text
Instance:       Solution:
┌─────────────┐ ┌─────────────┐ 
│ 0 0 · · · · │ │ 0 0 1 0 1 1 │  0: white circle
│ · · 1 · · · │ │ 1 0 1 0 1 0 │  1: black circle
│ 1 · · · · · │ │ 1 1 0 1 0 0 │
│ · · · 1 · · │ │ 0 0 1 1 0 1 │
│ · · · · · · │ │ 1 1 0 0 1 0 │
│ · 1 · · 0 1 │ │ 0 1 0 1 0 1 │
└─────────────┘ └─────────────┘
```

Binario instances are encoded as strings, as follows.
Cells are listed in row-major order (i.e., left to right and top to bottom).
If a cell contains a white or black circle, the character `'0'` or `'1'` is written, respectively.
If a cell is empty, the number of consecutive empty cells until the next number (or until the end) is represented by a single character: `'a'` for 1 empty cell, `'b'` for 2 empty cells, `'c'` for 3 empty cells, etc.
For example, the instance shown above is encoded as:
```python
binario_instance = '00f1c1h1i1b01'
```

File <a href="https://github.com/hmarko89/mathoptintro/blob/master/src/puzzles/binario.py" target="_blank">`src/puzzles/binario.py`</a> contains a decoding method for Binario instances.

## <a href="https://www.puzzle-loop.com/" target="_blank">Slitherlink (Loops, Fences)</a>

Given an $n \times n$ grid, where some cells contain a number from 0 to 3.
The goal is to draw a **single non-crossing loop** along the edges of the cells such that the number in each cell indicates how many of its sides are crossed by the loop.

```text
Instance:                 Solution:
·   ·   ·   ·   ·   ·     ·   ┌───┐   ·   ┌───┐ 
  2       1   2             2 │   │ 1   2 │   │ 
·   ·   ·   ·   ·   ·     ┌───┘   │   ┌───┘   │ 
  3   1                   │ 3   1 │   │       │ 
·   ·   ·   ·   ·   ·     └───┐   └───┘   ┌───┘ 
  3           1             3 │         1 │     
·   ·   ·   ·   ·   ·     ┌───┘   ┌───┐   └───┐ 
  2               2       │ 2     │   │     2 │ 
·   ·   ·   ·   ·   ·     │   ┌───┘   └───┐   │ 
      2   0   2           │   │ 2   0   2 │   │ 
·   ·   ·   ·   ·   ·     └───┘   ·   ·   └───┘ 
```

Slitherlink instances are encoded as strings, as follows.
Cells are listed in row-major order (i.e., left to right and top to bottom).
If a cell contains a number, the number is written directly; if it is empty, the number of consecutive empty cells until the next number (or until the end) is represented by a single character: `'a'` for 1 empty cell, `'b'` for 2 empty cells, `'c'` for 3 empty cells, etc.
For example, the instance shown above is encoded as:
```python
slitherlink_instance = '2a12a31c3b1a2c2a202a'
```

## <a href="https://www.puzzle-bridges.com/" target="_blank">Hashi (Bridges)</a>

Given an $n\times n$ grid, where some cells contain a number between 1 and 8 representing islands.
The goal is to connect all islands into a **single connected group** using bridges, such that:

- each bridge connects exactly two islands in a straight line;
- bridges run only horizontally or vertically;
- bridges cannot cross other bridges or islands;
- at most two bridges can connect any pair of islands;
- the number of bridges connected to each island must equal the number written on that island.

```text
Instance:                      Solution:
·   4   ·   ·   ·   ·   3      ·   4 ═════════════════ 3
                                   ║                   │
2   ·   4   ·   ·   4   ·      2   ║   4 ═════════ 4   │
                               ║   ║   ║           ║   │
·   2   ·   ·   ·   ·   ·      ║   2   ║   ·   ·   ║   │
                               ║       ║           ║   │
·   ·   ·   ·   ·   2   ·      ║   ·   ║   ·   ·   2   │
                               ║       ║               │
3   ·   4   ·   ·   ·   4      3 ───── 4 ───────────── 4
                                                       ║
·   ·   ·   ·   ·   ·   ·      ·   ·   ·   ·   ·   ·   ║
                                                       ║
·   1   ·   2   ·   ·   3      ·   1 ───── 2 ───────── 3
```

Hashi instances are encoded as strings, as follows.
Cells are listed in row-major order (i.e., left to right and top to bottom).
If a cell contains a number, the number is written directly; if it is empty, the number of consecutive empty cells until the next number (or until the end) is represented by a single character: `'a'` for 1 empty cell, `'b'` for 2 empty cells, `'c'` for 3 empty cells, etc.
For example, the instance shown above is encoded as:
```python
hashi_instance = 'a4d32a4b4b2j2a3a4c4h1a2b3'
```

## <a href="https://www.puzzle-masyu.com/" target="_blank">Masyu</a>

Given an $n\times n$ grid, where some cells contain a black or a white circle.
The goal is to draw a **single non-crossing loop** that passes through all the circles, such that

- the loop moves only along the centers of cells, horizontally or vertically;
- the loop must turn on black circles, and must go straight in the cells immediately before **and** after each black circle;
- the loop must go straight through white circles, and must turn in at least one of the cells immediately before **or** after each white circle.

```text
Instance:                  Solution:            
·   ·   ·   ·   W   B      ┌───┐   ·   ┌── W ─ B      W: white circle 
                           │   │       │       │      B: black circle
W   ·   W   ·   ·   W      W   └── W ──┘   ·   W
                           │                   │
·   ·   ·   B   ·   ·      │   ┌────── B   ┌───┘
                           │   │       │   │    
·   W   ·   W   W   ·      │   W   ·   W   W   ·
                           │   │       │   │    
W   W   ·   ·   ·   ·      W   W   ·   │   └───┐
                           │   │       │       │
·   ·   ·   B   ·   ·      └───┘   ·   B ──────┘
```

Masyu instances are encoded as strings, as follows.
Cells are listed in row-major order (i.e., left to right and top to bottom).
If a cell contains a white or a black circle, the upper case letter `'W'` or `'B'` is written, respectively; if it is empty, the number of consecutive empty cells until the next number (or until the end) is represented by a single lower case letter: `'a'` for 1 empty cell, `'b'` for 2 empty cells, `'c'` for 3 empty cells, etc.
For example, the instance shown above is encoded as:
```python
masyu_instance = 'dWBWaWbWcBcWaWWaWWgBb'
```

## <a href="https://www.puzzle-hitori.com/" target="_blank">Hitori</a>

Given an $n\times n$ grid where each cell contains a number from $1$ to $n$.
The goal is to mark (for example, shade) some cells such that:

- in every row and column, the unmarked numbers are all distinct;
- marked cells cannot be adjacent horizontally or vertically;
- all unmarked cells form a **single connected group**.

```text
Instance:     Solution:
┌───────────┐ ┌───────────┐
│ 1 5 4 4 3 │ │ 1 5 ▒ 4 ▒ │
│ 3 3 1 2 5 │ │ ▒ 3 1 2 5 │
│ 3 1 1 5 3 │ │ 3 1 ▒ 5 ▒ │
│ 1 2 4 3 1 │ │ ▒ 2 4 3 1 │
│ 2 4 5 5 3 │ │ 2 4 5 ▒ 3 │
└───────────┘ └───────────┘
```

Hitori instances are encoded as strings, where cells are listed in row-major order (i.e., left to right and top to bottom).
For example, the instance shown above is encoded as:
```python
hitori_instance = '1544333125311531243124553'
```

## <a href="https://www.puzzle-pipes.com/" target="_blank">Pipes</a>

Given an $n\times n$ grid where each cell contains a pipe tile.
The goal is to rotate the tiles so that they form a **single connected network** without cycles.

```text
Instance:    Solution:
╵╴╵┘         ╷╷╶┐ 
┬├─┴         ├┴─┤ 
╴┘┬┬         ╵┌┬┤ 
╷└╷╴         ╶┘╵╵ 
```

Pipes instances are encoded as strings, where cells (with the following tile-encoding) are listed in row-major order (i.e., left to right and top to bottom).

char  | tile | description    | char  | tile | description
:----:|:----:|:---------------|:-----:|:----:|:--------------
**1** | ╶    | sink     (r)   | **8** | ╷    | sink     (d)
**2** | ╵    | sink     (u)   | 9     | ┌    | curve    (rd)
3     | └    | curve    (ru)  | a     | │    | straight (ud)
**4** | ╴    | sink     (l)   | b     | ├    | branch   (rud)
5     | ─    | straight (rl)  | c     | ┐    | curve    (ld)
6     | ┘    | curve    (ul)  | d     | ┬    | branch   (rld)
7     | ┴    | branch   (rul) | e     | ┤    | branch   (uld)

!!! tip "Tile-encoding"
    The tile-encoding is systematic, not ad-hoc.

For example, the instance shown above is encoded as:

```python
pipes_instance = '2426db5746dd8384'
```

Note that the solution can be encoded in the same way.

```python
pipes_solution = '881cb75e29de1622'
```
