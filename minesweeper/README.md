# Minesweeper Learning Exercise

A fill-in-the-blanks Minesweeper game designed to teach Python idioms and concepts to engineers who already know C# and Java. Each `TODO` exercises a specific Python feature and shows how it differs from C#/Java equivalents.

## Quick Start

```bash
python3 minesweeper.py
```

Play by entering commands like:
```
3 5 r    # Reveal cell at row 3, column 5
7 2 f    # Flag cell at row 7, column 2
q        # Quit
```

## The TODOs: Concepts and Order

Complete the TODOs in this order. Each builds on the previous and introduces new Python idioms.

### TODO-1: Enums (classes)
**Concept:** Python `Enum` with custom values; similar to C#'s `Enum` but more powerful.

**Why it matters:** 
- C# enums are just integer constants; Python Enum members are objects with `.name`, `.value`, and methods.
- You can define methods on Enum members, iterate over them, and use them as dict keys.

**Your task:** This one is already complete as an example. Review how `CellState` uses `.value` to store display symbols (".", "F", etc.).

**Testing:**
```python
# In Python shell:
>>> from minesweeper import CellState
>>> print(CellState.UNREVEALED.value)
.
>>> list(CellState)  # Iterate all members
```

---

### TODO-2: `__init__` and Dunder Methods
**Concept:** Python constructor is `__init__`, not a method named after the class.

**Why it matters:**
- C#/Java: Constructor is `class Point { public Point(int x, int y) { } }`
- Python: Constructor is `def __init__(self, x, y): ...` (no return, no type matching class name)
- The instance is created *implicitly* by Python; `__init__` just initializes fields.
- `self` is explicit (not implicit `this`), making it clear what's instance state.

**Your task:** Implement `Cell.__init__` with these fields:
- `is_mine` (bool, default False)
- `revealed` (bool, default False)
- `flagged` (bool, default False)
- `adjacent_mines` (int, default 0)

Also implement `__repr__` for a string representation (used by print() for debugging).

**Example of the pattern:**
```python
class Point:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    def __repr__(self) -> str:
        return f"Point({self.x}, {self.y})"

p = Point(3, 4)  # No 'new' keyword; Python creates the instance automatically
print(p)         # Calls __repr__
```

**Testing:**
```bash
python3 -c "
from minesweeper import Cell
c = Cell(is_mine=True)
print(c.is_mine, c.revealed, c.adjacent_mines)
print(repr(c))
"
```

---

### TODO-3: List Comprehensions
**Concept:** Python's answer to C# LINQ; create lists concisely without explicit loops.

**Why it matters:**
- C# uses `.Select()` and `.ToList()` from LINQ; Python uses comprehensions.
- Comprehensions are faster, more readable, and more Pythonic.
- Nested comprehensions build multi-dimensional lists in one expression.

**Your task:** Initialize `self.board` as a 2D list of `Cell` objects.
- Use nested list comprehensions: `[[... for _ in range(width)] for _ in range(height)]`
- Each cell should be a new `Cell()` instance.

**Example of the pattern:**
```python
# C# (LINQ):
var matrix = Enumerable.Range(0, height)
    .Select(_ => Enumerable.Range(0, width)
               .Select(_ => new Cell()).ToList())
    .ToList();

# Python (comprehension):
matrix = [[Cell() for _ in range(width)] for _ in range(height)]
```

**Testing:**
```bash
python3 -c "
from minesweeper import Minesweeper
game = Minesweeper(5, 5, 3)
print(f'Board size: {len(game.board)} rows, {len(game.board[0])} cols')
print(f'First cell: {game.board[0][0]}')
"
```

---

### TODO-4: Sets and Tuple Unpacking
**Concept:** Use sets to track unique values; unpack tuples into variables.

**Why it matters:**
- Sets (like C# `HashSet<T>`) ensure uniqueness automatically.
- Tuple unpacking (`a, b = (1, 2)`) is cleaner than indexing (`a = tuple[0]`).
- Using `(row, col)` tuples is more Pythonic than creating a Position class.

**Your task:** Implement `_place_mines()`:
- Generate random `(row, col)` tuples until you have `num_mines` unique positions.
- Use a `while len(placed) < self.num_mines` loop with a set to avoid duplicates.
- For each position, unpack it as `row, col` and mark the cell as a mine.

**Example of the pattern:**
```python
# C# (HashSet):
var placed = new HashSet<(int, int)>();
while (placed.Count < numMines) {
    int r = random.Next(height);
    int c = random.Next(width);
    placed.Add((r, c));
}
foreach (var (row, col) in placed) {
    board[row, col].IsMine = true;
}

# Python (set + unpacking):
placed = set()
while len(placed) < num_mines:
    placed.add((random.randint(0, height-1), random.randint(0, width-1)))
for row, col in placed:  # Unpack
    board[row][col].is_mine = True
```

**Testing:**
```bash
python3 -c "
from minesweeper import Minesweeper
game = Minesweeper(5, 5, 3)
mine_count = sum(1 for row in game.board for cell in row if cell.is_mine)
print(f'Mines placed: {mine_count}')
"
```

---

### TODO-5: `enumerate()` and Slicing
**Concept:** Use `enumerate()` to get index and value; use slicing for safe access.

**Why it matters:**
- `enumerate()` replaces C#/Java's `for (int i = 0; i < items.Count; i++)`.
- Slicing is safe: `list[10:20]` on a 5-element list just returns what exists.
- Negative indices work: `list[-1]` is the last element.

**Your task:** Implement `_compute_adjacent_mines()`:
- Loop through all cells using `enumerate()` on rows and columns.
- For each cell, count mines in the 3×3 region around it (8 neighbors).
- Use slicing to get the region: `board[row-1:row+2]` and `row[col-1:col+2]`.
- Subtract 1 if the center cell is a mine (we counted it).
- Store the count in `cell.adjacent_mines`.

**Example of the pattern:**
```python
# C# (explicit bounds checking):
for (int r = 0; r < height; r++) {
    for (int c = 0; c < width; c++) {
        int count = 0;
        for (int dr = -1; dr <= 1; dr++) {
            for (int dc = -1; dc <= 1; dc++) {
                int nr = r + dr, nc = c + dc;
                if (nr >= 0 && nr < height && nc >= 0 && nc < width) {
                    if (board[nr, nc].IsMine) count++;
                }
            }
        }
    }
}

# Python (slicing handles bounds):
for r, row_cells in enumerate(board):
    for c, cell in enumerate(row_cells):
        count = sum(1 for neighbor in board[r-1:r+2] 
                        for n_cell in neighbor[c-1:c+2]
                        if n_cell.is_mine)
        if cell.is_mine: count -= 1
        cell.adjacent_mines = count
```

**Testing:**
```bash
python3 -c "
from minesweeper import Minesweeper
game = Minesweeper(5, 5, 3)
print(f'Cell [0][0]: {game.board[0][0].adjacent_mines} adjacent mines')
print(f'Cell [2][2]: {game.board[2][2].adjacent_mines} adjacent mines')
"
```

---

### TODO-6: List Comprehensions with Conditions
**Concept:** Filter lists using conditions in comprehensions.

**Why it matters:**
- Comprehensions can include `if` clauses to filter.
- This is cleaner than separate filter calls or nested if statements.
- Reads naturally: `[expr for item in items if condition]`

**Your task:** Implement `get_neighbors(row, col)`:
- Generate all 8 neighbor positions as `(row+dr, col+dc)` tuples.
- Filter to only valid positions: `0 <= row < height` and `0 <= col < width`.
- Return a list of `(row, col)` tuples.

**Example of the pattern:**
```python
# C# (LINQ with Where):
var neighbors = Enumerable.Range(-1, 3)
    .SelectMany(dr => Enumerable.Range(-1, 3)
        .Select(dc => (r: row + dr, c: col + dc)))
    .Where(pos => pos.r >= 0 && pos.r < height && pos.c >= 0 && pos.c < width)
    .ToList();

# Python (comprehension with if):
neighbors = [
    (row + dr, col + dc)
    for dr in [-1, 0, 1]
    for dc in [-1, 0, 1]
    if not (dr == 0 and dc == 0)  # Skip center
    and 0 <= row + dr < height
    and 0 <= col + dc < width
]
```

**Testing:**
```bash
python3 -c "
from minesweeper import Minesweeper
game = Minesweeper(5, 5, 3)
neighbors = game.get_neighbors(0, 0)
print(f'Neighbors of (0,0): {neighbors}')
print(f'Count: {len(neighbors)}')  # Should be 8 for center cell
"
```

---

### TODO-7: Boolean Negation and Toggling
**Concept:** Use `not` to negate booleans; toggle with `value = not value`.

**Why it matters:**
- C#/Java use `!` for negation; Python uses `not`.
- Toggling with `not` is cleaner than manual if/else.
- Guard clauses use `if not condition:` to exit early.

**Your task:** Implement `flag_cell(row, col)`:
- Guard: only flag unrevealed cells.
- Toggle the `flagged` attribute: `cell.flagged = not cell.flagged`.

**Example of the pattern:**
```python
# C#:
if (!cell.Revealed) {
    cell.Flagged = !cell.Flagged;
}

# Python:
if not cell.revealed:
    cell.flagged = not cell.flagged
```

**Testing:**
```bash
python3 -c "
from minesweeper import Minesweeper
game = Minesweeper(5, 5, 3)
cell = game.board[0][0]
print(f'Before: flagged = {cell.flagged}')
game.flag_cell(0, 0)
print(f'After: flagged = {cell.flagged}')
game.flag_cell(0, 0)
print(f'After second toggle: flagged = {cell.flagged}')
"
```

---

### TODO-8: Recursion and Bounds Checking
**Concept:** Use recursion for tree/graph traversal (like flood-fill); Python handles it well for small depths.

**Why it matters:**
- C#/Java often use explicit stacks to avoid stack overflow; Python's recursion is fine for Minesweeper.
- Python's default recursion limit is ~1000, sufficient for typical games.
- Recursion is cleaner than a manual queue for flood-fill logic.

**Your task:** Implement `reveal_cell(row, col)`:
- Bounds check: return if `(row, col)` is outside the board.
- Already revealed? Return (base case).
- Mark as revealed.
- Is it a mine? Set `self.game_over = True` and return.
- If `cell.adjacent_mines == 0` (empty), recursively call `reveal_cell()` on all neighbors.

**Example of the pattern:**
```python
# C# (explicit stack):
var stack = new Stack<(int, int)>();
stack.Push((row, col));
while (stack.Count > 0) {
    var (r, c) = stack.Pop();
    if (r < 0 || r >= height || c < 0 || c >= width) continue;
    if (board[r, c].Revealed) continue;
    board[r, c].Revealed = true;
    if (board[r, c].IsMine) { /* game over */ return; }
    if (board[r, c].AdjacentMines == 0) {
        foreach (var (nr, nc) in GetNeighbors(r, c)) stack.Push((nr, nc));
    }
}

# Python (recursion):
def reveal_cell(row, col):
    if not (0 <= row < height and 0 <= col < width):
        return
    cell = board[row][col]
    if cell.revealed:
        return
    cell.revealed = True
    if cell.is_mine:
        game_over = True
        return
    if cell.adjacent_mines == 0:
        for nr, nc in get_neighbors(row, col):
            reveal_cell(nr, nc)
```

**Testing:**
```bash
python3 << 'EOF'
from minesweeper import Minesweeper
game = Minesweeper(5, 5, 1)
game.reveal_cell(0, 0)
revealed_count = sum(1 for row in game.board for cell in row if cell.revealed)
print(f'Revealed cells: {revealed_count}')
print(f'Game over: {game.game_over}')
EOF
```

---

### TODO-9: The `@property` Decorator
**Concept:** Use `@property` to create getter-like methods that look like attributes.

**Why it matters:**
- C#/Java use properties with get/set: `public bool IsComplete { get { ... } }`
- Python uses `@property`: `def is_complete(self): ...` then call as `obj.is_complete` (no parens).
- Pythonic naming: `is_complete` (snake_case) instead of `IsComplete` (PascalCase).
- You can add computation without breaking callers (they still call it the same way).

**Your task:** Implement the `is_complete` property:
- Return `True` if the player has won (all non-mine cells are revealed).
- Check all cells: if any unrevealed cell is not a mine, return `False`.
- Otherwise, return `True`.

**Example of the pattern:**
```python
# C#:
public class Player {
    public bool IsAlive { get { return health > 0; } }
}
if (player.IsAlive) { ... }

# Python:
class Player:
    @property
    def is_alive(self):
        return self.health > 0

if player.is_alive:  # No parens!
    ...
```

**Testing:**
```bash
python3 << 'EOF'
from minesweeper import Minesweeper
game = Minesweeper(3, 3, 1)
print(f'Complete: {game.is_complete}')
# Manually reveal all non-mine cells
for row in game.board:
    for cell in row:
        if not cell.is_mine:
            cell.revealed = True
print(f'Complete after reveal: {game.is_complete}')
EOF
```

---

### TODO-10: F-Strings and String Formatting
**Concept:** Use f-strings for string interpolation with format specifiers.

**Why it matters:**
- C#: `$"Value: {x}"` (string interpolation)
- Python 3.6+: `f"Value: {x}"` (f-strings, equivalent to C#)
- f-strings support format specs: `f"{x:5}"` (width 5), `f"{x:02d}"` (zero-padded)
- f-strings are faster and more readable than `.format()` or `%` operators.

**Your task:** Implement `display()` to draw the board:
```
  0 1 2 3 4 5 6 7 8 9
0 . . . . . . . . . .
1 . 1 . . . . . . . .
...
```

- Print column header with numbers.
- For each row, print the row number, then each cell's symbol:
  - Flagged unrevealed: "F"
  - Unrevealed: "."
  - Mine (revealed): "*"
  - Revealed with count: "1", "2", etc.
  - Revealed empty: " " (space)

Use `enumerate()` to get row/col numbers and f-strings for formatting.

**Example of the pattern:**
```python
# C#:
for (int i = 0; i < items.Count; i++) {
    Console.WriteLine($"{i,3}: {items[i],10}");
}

# Python:
for i, item in enumerate(items):
    print(f"{i:3}: {item:10}")
```

**Testing:**
```bash
python3 << 'EOF'
from minesweeper import Minesweeper
game = Minesweeper(5, 5, 0)
game.board[0][0].revealed = True
game.board[0][0].adjacent_mines = 2
game.display()
EOF
```

---

### TODO-11: Input Parsing and the Game Loop
**Concept:** Parse user input using `.split()` and tuple unpacking; loop until game ends.

**Why it matters:**
- `input()` reads a line; `.strip()` removes whitespace.
- `.split()` tokenizes; tuple unpacking assigns to multiple variables in one line.
- `map(int, ...)` applies a function to each element (like C# `.Select()`).
- Game loops use `while` conditions to check game state.

**Your task:** Implement `play()`:
- Loop while `not self.game_over and not self.is_complete`.
- Display the board each turn.
- Prompt: `"Enter 'row col action' (r=reveal, f=flag) or 'q' to quit: "`
- Parse input:
  - If "q", exit.
  - Otherwise, split into row, col, action.
  - Convert row and col to integers using `map()` or explicit `int()` calls.
  - Bounds check: ensure row and col are in [0, height) and [0, width).
  - If action is "r", call `reveal_cell(row, col)`.
  - If action is "f", call `flag_cell(row, col)`.
- Handle `ValueError` if parsing fails (e.g., non-integer row/col).
- After the loop, display the board and print the outcome.

**Example of the pattern:**
```python
# C#:
while (!gameOver && !won) {
    string line = Console.ReadLine();
    if (line == "q") break;
    var parts = line.Split(' ');
    int row = int.Parse(parts[0]);
    int col = int.Parse(parts[1]);
    string action = parts[2];
    // ... process move
}

# Python:
while not game_over and not won:
    line = input("> ").strip()
    if line == "q":
        break
    try:
        row, col, action = line.split()
        row, col = int(row), int(col)  # Or: row, col = map(int, [row, col])
        # ... process move
    except ValueError:
        print("Invalid input")
```

**Testing:**
```bash
# Create a script to send input:
(echo "0 0 r"; sleep 0.1; echo "q") | python3 minesweeper.py
```

---

## How to Complete This Exercise

1. **Read a TODO** and the teaching block above it.
2. **Look at the example** showing C#/Java vs Python patterns.
3. **Implement the TODO** in `minesweeper.py`.
4. **Test** your implementation using the provided test commands.
5. **Compare** your code to `solutions.py` to see alternative approaches.
6. **Move to the next TODO**.

## Checking Your Work

### Run the Game
```bash
python3 minesweeper.py
```

Try playing a full game:
```
Enter 'row col action' (r=reveal, f=flag) or 'q' to quit: 5 5 r
Enter 'row col action' (r=reveal, f=flag) or 'q' to quit: 3 3 f
Enter 'row col action' (r=reveal, f=flag) or 'q' to quit: q
```

### Compare to Solutions
```bash
# Check a specific TODO's solution:
python3 -c "from solutions import Minesweeper; help(Minesweeper._initialize_board)"
```

### Run Type Checking (Optional)
```bash
pip install mypy
mypy minesweeper.py
```

## Key Python Idioms Covered

| Concept | C#/Java | Python |
|---------|---------|--------|
| Enum | Bare values + helper class | `Enum` class with methods |
| Constructor | `ClassName() { ... }` | `__init__(self, ...)` |
| List creation | `new List<int>() { ... }` or LINQ | List comprehension `[x for x in ...]` |
| Deduplication | `HashSet<T>` | `set()` |
| Unpacking | Manual index access `tuple[0]`, `tuple[1]` | `a, b = tuple` |
| Iteration + index | `for (int i = 0; i < n; i++)` | `for i, x in enumerate(...)` |
| Safe slicing | Manual bounds check | `list[start:end]` (safe) |
| Filter | `.Where().ToList()` | `[x for x in list if cond]` |
| Boolean negation | `!` | `not` |
| Property/getter | `{ get { ... } }` | `@property def ...` |
| String interpolation | `$"text {var}"` | `f"text {var}"` |
| Input parsing | `Console.ReadLine().Split()` | `input().split()` |

## Trouble?

- **"ModuleNotFoundError: No module named minesweeper"** — Make sure you're in the right directory and run `python3 minesweeper.py`.
- **"TODO-N: pass"** — You haven't implemented this TODO yet.
- **Recursion limit error** — Unlikely for Minesweeper, but if it happens, add `import sys; sys.setrecursionlimit(10000)` at the top of `minesweeper.py`.
- **Game behavior seems wrong** — Compare your implementation to `solutions.py` line by line.

## Next Steps

Once you've completed all TODOs:
1. Refactor for readability (add comments, rename variables if needed).
2. Add difficulty levels (adjust board size and mine count).
3. Add a timer to track how fast you clear a board.
4. Implement Minesweeper's "chord" action (reveal all neighbors of a numbered cell if it's marked correctly).
5. Add a save/load feature using pickle or JSON (teaches file I/O and serialization).
6. Port to a GUI using tkinter or pygame (teaches library integration beyond stdlib).

Happy learning! 🎮
