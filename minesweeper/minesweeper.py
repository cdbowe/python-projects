#!/usr/bin/env python3
"""
Minesweeper Learning Exercise
Fill in the TODOs to complete this game and learn Python idioms.

Run: python3 minesweeper.py
"""

import random
import re
from enum import Enum
from typing import List, Tuple, Set, Optional


class CellState(Enum):
    """TODO-1: Python Enums (similar to C# enums, but more powerful with methods)"""
    UNREVEALED = "."
    REVEALED = " "
    FLAGGED = "F"
    MINE = "*"

class FooBar(Enum):
    A = "a"
    B = "2"
    C = 123
    D = "Hello"

class Logger:
    # _enabled: bool = True
    _enabled: bool = False

    # @classmethod
    # def get_enabled(cls) -> bool:
    #     return cls._enabled
    
    # @classmethod
    # def set_enabled(cls, value: bool) -> None:
    #     cls._enabled = value

    @classmethod
    def debug(cls, message: str):
        if cls._enabled == True:
            print(f"DEBUG: {message}")

class Cell:
    """
    TODO-2: Class with __init__ and properties

    CONCEPT: Python constructor is __init__, called automatically when instantiating.
    Unlike C#/Java constructors that match the class name, Python uses __init__.

    TEACHING EXAMPLE:
        class Point:
            def __init__(self, x, y):  # Not Point(x, y)
                self.x = x
                self.y = y

    IMPLEMENTATION: Create a Cell class that stores:
    - is_mine (bool): whether this cell contains a mine
    - revealed (bool): whether this cell has been revealed
    - flagged (bool): whether player flagged this cell
    - adjacent_mines (int): number of mines adjacent to this cell (computed later)
    """
    # TODO-2: Implement Cell.__init__ with the fields above
    # pass

    def __init__(self, r: int, c: int, is_mine: bool = False, revealed: bool = False, flagged: bool = False, adjacent_mines: int = 0) -> str:
        self.r = r
        self.c = c
        Logger.debug(f"Cell: {r},{c}")
        self.is_mine = is_mine
        self.revealed = revealed
        self.flagged = flagged
        self.adjacent_mines = adjacent_mines

    def __repr__(self) -> str:
        if self.flagged == True:
            return CellState.FLAGGED.value
        
        if not self.revealed:
            return CellState.UNREVEALED.value
        
        if self.is_mine == True:
            return CellState.MINE.value
        
        return str(self.adjacent_mines) if self.adjacent_mines > 0 else CellState.REVEALED.value
        
        

class Minesweeper:
    """Main game class."""

    def __init__(self, width: int = 10, height: int = 10, num_mines: int = 10):
        """
        Initialize the game board.

        CONCEPT: Type hints in Python (PEP 484) are optional but recommended.
        Unlike Java/C# where types are required, Python lets you skip them.
        They don't affect runtime but help with IDE autocomplete and type checkers.
        """
        self.width = width
        self.height = height
        self.num_mines = num_mines
        self.board: List[List[Cell]] = []
        self.game_over = False
        self.won = False

        self._initialize_board()
        self._place_mines()
        self._compute_adjacent_mines()

    def _initialize_board(self) -> None:
        """
        TODO-3: Create the game board as a 2D list using list comprehension

        CONCEPT: List comprehensions are Python's answer to C# LINQ.
        They're more concise and usually faster than loops.

        TEACHING EXAMPLE (LINQ vs comprehension):
            \# C#: var grid = Enumerable.Range(0, height)
            \#                    .Select(_ => Enumerable.Range(0, width)
            \#                               .Select(_ => new Cell()).ToList())
            \#                    .ToList();

            \# Python:
            board = [[Cell() for _ in range(width)] for _ in range(height)]

        IMPLEMENTATION: Initialize self.board as a 2D list of Cell objects.
        Use nested list comprehensions: one for height (rows), one for width (cols).
        Each cell should be a new Cell instance.
        """
        # Create 2D board with nested list comprehension
        self.board = [[Cell(r, c) for c in range(self.width)] for r in range(self.height)]

    """
    Define a random position on the board. Returns a Tuple[int,int]. 
    Board grid uses 0-based indices.
    First number represents the row position.
    Second number represents the col position.
    """
    def _random_board_position(self) -> Tuple[int, int]:
        return (random.randint(0, self.height - 1), random.randint(0, self.width - 1))

    def _place_mines(self) -> None:
        """
        TODO-4: Randomly place mines using set operations and tuple unpacking

        CONCEPT: Sets in Python (like C# HashSet<T>) are unordered, unique collections.
        Use them when you need fast membership testing (O(1) average).

        TEACHING EXAMPLE (avoiding duplicates):
            # C#: var placed = new HashSet<string>();
            #     while (placed.Count < needed) placed.Add(RandomPosition());

            # Python:
            placed = set()
            while len(placed) < needed:
                placed.add(random_position())

        IMPLEMENTATION:
        - Generate random (row, col) tuples until you have num_mines unique positions.
        - Use a while loop with a set to track placed positions (avoid duplicates).
        - For each position tuple, unpack it as (row, col) and mark the cell as a mine.
        - The random module has random.randint(a, b) for integers.
        """
        # TODO-4: Place mines using set and tuple unpacking

        # Generate random unique mine positions
        # Optional: set the mine flags in a separate loop because the set() loop needs to account for duplicate board positions
        placed_mines: Set[Tuple[int, int]] = set()
        while len(placed_mines) < self.num_mines:
            (row, col) = self._random_board_position()
            placed_mines.add((row, col))
            # Set the mine flags in the same loop.
            # If a position was already generated it'll just set the is_mine flag a second time, a no-op operation.
            # self.board[row][col].is_mine = True

        # Flag the board positions with mine flags
        for row, col in placed_mines:
            Logger.debug(f"Placing mine at {row},{col}")
            self.board[row][col].is_mine = True

    def _compute_adjacent_mines(self) -> None:
        """
        TODO-5: Count adjacent mines for each cell using enumerate() and slicing

        CONCEPT: enumerate() returns (index, value) tuples. Use it instead of
        range(len(list)) - this is more Pythonic and readable.

        TEACHING EXAMPLE (Python vs C#):
            # C#: for (int i = 0; i < items.Count; i++) { var item = items[i]; }
            # Python: for i, item in enumerate(items):

        CONCEPT: Slicing (e.g., list[1:3], list[:-1]) is central to Python.
        Use it to get adjacent cells without explicit bounds checking.
        Python handles negative indices: list[-1] is last element.

        TEACHING EXAMPLE:
            neighbors = matrix[max(0, r-1):r+2, max(0, c-1):c+2]  # Gets 3x3 around (r,c)
            # Slicing is safe: list[100:200] on a 10-element list just returns what exists

        IMPLEMENTATION:
        - Loop through all cells using enumerate() on both rows and columns.
        - For each cell, count mines in adjacent cells (8-neighbor grid).
        - Use slicing to get the adjacent region: board[row-1:row+2][col-1:col+2]
        - Subtract 1 if counting the center cell (which might be a mine itself).
        - Store the count in cell.adjacent_mines.
        """
        # TODO-5: Count adjacent mines with enumerate() and slicing

        # Loop through all cells on the board
        for r, row_cells in enumerate(self.board):
            for c, cell in enumerate(row_cells):
                # Get the neighbor section
                # Use `max(0, thing)` to prevent slicing with a starting index of -1, that brings weird outcomes
                cell_neighbors = [row[max(0, c-1):c+2] for row in self.board[max(0, r-1):r+2]]
                Logger.debug(f"[{r},{c}] -> Neighbors: {len(cell_neighbors)}x{len(cell_neighbors[0])}")

                # Skip if the cell is a mine
                if cell.is_mine == True:
                    Logger.debug(f"[{r},{c}] -> MINE")
                    continue

                # Count the neighboring mines
                mine_neighbor_count = 0
                for _, neighbor_row_cells in enumerate(cell_neighbors):
                    for _, neighbor_cell in enumerate(neighbor_row_cells):
                        # Exclude the current cell
                        if r == neighbor_cell.r and c == neighbor_cell.c:
                            continue

                        if neighbor_cell.is_mine == True:
                            mine_neighbor_count += 1

                # Set the cell value
                cell.adjacent_mines = mine_neighbor_count
                Logger.debug(f"{cell.r},{cell.c} -> {cell.adjacent_mines} adjacent mines")
        # pass

    def get_neighbors(self, row: int, col: int) -> List[Tuple[int, int]]:
        """
        TODO-6: Return list of valid adjacent cell coordinates using list comprehension + filter

        CONCEPT: List comprehensions can include conditions (filter) and nested loops.

        TEACHING EXAMPLE (filter pattern):
            # C#: var valid = cells.Where(c => c.IsValid).ToList();
            # Python: valid = [c for c in cells if c.is_valid]

        IMPLEMENTATION:
        - Generate all 8 neighbors as (row + dr, col + dc) for dr, dc in [(-1,-1), (-1,0), ...]
        - Filter to only those within board bounds: 0 <= row < height, 0 <= col < width
        - Return as a list of (row, col) tuples.
        """
        # TODO-6: Return neighbors using list comprehension with conditions

        cell_neighbors = [
            (row + dr, col + dc) 
                for dc in range(-1, 2) 
                for dr in range(-1, 2)
                if not(dc == 0 and dr == 0) and 0 <= (col + dc) < self.width and 0 <= (row + dr) < self.height
        ]

        return cell_neighbors
        # pass

    def flag_cell(self, row: int, col: int) -> None:
        """
        TODO-7: Toggle flag on a cell (unpacking pattern)

        CONCEPT: Python uses tuple unpacking for swapping and toggling.

        TEACHING EXAMPLE (Pythonic toggling):
            # C#: flagged = !flagged;  // Or: flagged ^= true;
            # Python: flagged = not flagged

            # Or with walrus operator (Python 3.8+):
            # if (cell.flagged := not cell.flagged): ...

        IMPLEMENTATION:
        - Access board[row][col] and toggle its flagged attribute.
        - Don't reveal if flagging an unrevealed cell.
        - Guard with: if not self.board[row][col].revealed
        """
        # TODO-7: Toggle flag on cell
        if self.board[row][col].revealed:
            Logger.debug(f"CELL[{row},{col}] REVEALED")
            return
        
        # self.board[row][col].flagged = not self.board[row][col].flagged
        cell = self.board[row][col]
        cell.flagged = not cell.flagged

        # pass

    def _is_out_of_bounds(self, row: int, col: int) -> bool:
        return not (0 <= row < self.height and 0 <= col < self.width)

    def reveal_cell(self, row: int, col: int) -> None:
        """
        TODO-8: Reveal a cell and recursively flood-fill empty neighbors

        CONCEPT: Recursion in Python is similar to C#/Java, but watch the call stack depth.
        Python's default recursion limit is ~1000. For Minesweeper, this is fine.

        TEACHING EXAMPLE (recursion vs loop):
            # C#: Typically use a stack or queue for flood-fill to avoid stack overflow.
            # Python: Recursion is cleaner, but can hit limit. Add sys.setrecursionlimit() if needed.

        IMPLEMENTATION:
        - Bounds check: if (row, col) is outside board, return.
        - Already revealed? Return to avoid reprocessing.
        - Is it a mine? Game over.
        - Mark as revealed.
        - If adjacent_mines == 0 (empty cell), recursively reveal all neighbors.
        - Otherwise, stop (user sees the number).
        """
        # TODO-8: Reveal cell with recursive flood-fill

        # Base case: If out of bounds, return
        if self._is_out_of_bounds(row, col):
            return
        
        cell = self.board[row][col]

        # If already revealed, noop and return
        if cell.revealed == True:
            return

        # Set the cell as revealed
        cell.revealed = True
        Logger.debug(f"REVEALED [{row},{col}]")

        # if is a mine, game over. Return
        if cell.is_mine == True:
            self.game_over = True
            return

        # If no adjacent mines, recursively reveal neighbors
        if cell.adjacent_mines == 0:
            for neighbor_row, neighbor_col in self.get_neighbors(row, col):
                neighbor_cell = self.board[neighbor_row][neighbor_col]
                if not neighbor_cell.flagged:
                    self.reveal_cell(neighbor_row, neighbor_col)

        # pass

    @property
    def is_complete(self) -> bool:
        """
        TODO-9: Check if game is won using @property decorator

        CONCEPT: @property decorator in Python replaces C#/Java get/set properties.

        TEACHING EXAMPLE (Property vs method):
            # C#:
            public bool IsComplete {
                get { return condition; }
            }
            // Usage: if (game.IsComplete)

            # Python:
            @property
            def is_complete(self):
                return condition
            # Usage: if game.is_complete  (NOT game.is_complete())

        CONCEPT: Python convention is snake_case (is_complete) vs C#/Java camelCase (IsComplete).

        IMPLEMENTATION:
        - Win condition: all non-mine cells are revealed.
        - Count unrevealed cells that aren't mines. If 0, return True.
        - Also can be: all mines are flagged and no unrevealed non-mines exist.
        """
        # TODO-9: Implement win condition check as a property

        if self.game_over:
            return False

        for row in self.board:
            for cell in row:
                # Any unrevealed cell that is NOT a mine, return False
                if not cell.revealed and not cell.is_mine:
                    return False

        return True

        # pass

    def display(self) -> None:
        """
        TODO-10: Display the board using f-strings and enumerate()

        CONCEPT: f-strings (Python 3.6+) are like C# string interpolation.

        TEACHING EXAMPLE:
            # C#: Console.WriteLine($"Row {i}: {row}");
            # Python: Logger.debug(f"Row {i}: {row}")

        CONCEPT: f-strings support format specifiers:
            f"{value:5}"      # Width 5, right-aligned
            f"{value:<5}"     # Width 5, left-aligned
            f"{value:02d}"    # Zero-padded to 2 digits

        IMPLEMENTATION:
        - Print column numbers as header: 0 1 2 3 ...
        - For each row, print row number and cells.
        - For each cell, print its symbol based on state:
          - If flagged and unrevealed: "F"
          - If unrevealed: "."
          - If mine and revealed: "*"
          - If revealed with adjacent_mines > 0: str(adjacent_mines)
          - If revealed with adjacent_mines == 0: " " (space)
        - Use enumerate() to get row/col numbers.
        """
        # TODO-10: Display board with f-strings and formatting

        # Print grid header
        print(f"  {''.join(f'{str(n):<2}' for n in range(self.width))}")

        # Print each row
        for r, row in enumerate(self.board):
            print(f"{r:<2}{' '.join(str(cell) for cell in row)}")

        # pass

    def play(self) -> None:
        """
        TODO-11: Main game loop using input() and unpacking

        CONCEPT: Python's input() reads a line of text. Strip whitespace with .strip().

        TEACHING EXAMPLE:
            # C#: var line = Console.ReadLine();
            # Python: line = input().strip()

        CONCEPT: Tuple unpacking can handle variable destructuring in one line.

        TEACHING EXAMPLE:
            # C#: var parts = input.Split(',');
            #     int row = int.Parse(parts[0]);
            #     int col = int.Parse(parts[1]);

            # Python (unpacking):
            row, col = map(int, input().split(','))
            # Or with multiple vars:
            action, row, col = input().split()

        IMPLEMENTATION:
        - Loop until game_over or won.
        - Display board.
        - Prompt: "Enter r,c,a (r=row, c=col, a=action: r for reveal, f for flag) or q to quit"
        - Parse input: row, col, action = input().split()
        - Call reveal_cell() or flag_cell() based on action.
        - After each move, check if self.is_complete to detect win.
        - Handle exceptions: invalid input, out of bounds, etc.
        """
        # TODO-11: Implement game loop with input parsing

        while not self.game_over and not self.is_complete:
            self.display()

            line = input("Enter `a[ction] r[ow] c[col]` (actions: r for reveal, f for flag) or q to quit > ").strip()

            # 'q' -> Exit the game
            if line == "q":
                print("Exiting game")
                break

            if not re.match("[rf] \d \d", line):
                print("INVALID INPUT")
                continue

            action, row, col = line.split(' ')
            row = int(row)
            col = int(col)

            if action == "f":
                self.flag_cell(row, col)
            elif action == "r":
                self.reveal_cell(row, col)
            else:
                print("Invalid input")

        if self.game_over:
            print("GAME OVER")
            self.display()
        elif self.is_complete:
            print("YOU WIN!!")
            self.display()
        # pass


def main() -> None:
    """Entry point."""
    print("=== Minesweeper ===")
    game = Minesweeper(width=10, height=10, num_mines=10)
    game.play()


if __name__ == "__main__":
    main()
