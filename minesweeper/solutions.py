#!/usr/bin/env python3
"""
Minesweeper Solutions - Complete Implementation
Reference to check your work after implementing each TODO.
"""

import random
from enum import Enum
from typing import List, Tuple, Set, Optional


class CellState(Enum):
    """
    SOLUTION-1: Python Enum (superior to C# enum)

    Why this matters:
    - C# Enum: just values; methods need helper classes
    - Python Enum: can have methods, properties, and custom logic
    - Members have .name and .value attributes automatically
    """
    UNREVEALED = "."
    REVEALED = " "
    FLAGGED = "F"
    MINE = "*"


class Cell:
    """
    SOLUTION-2: Python class with __init__

    Why this matters:
    - __init__ is the initializer, NOT a constructor that returns an instance.
    - The instance is created implicitly by Python, __init__ just initializes fields.
    - No 'new' keyword needed when calling; Python creates the instance automatically.
    - self is explicit (not implicit 'this'), making it clear what's an instance variable.
    """

    def __init__(self, is_mine: bool = False) -> None:
        self.is_mine = is_mine
        self.revealed = False
        self.flagged = False
        self.adjacent_mines = 0

    def __repr__(self) -> str:
        """
        __repr__ is the 'official' string representation (for debugging).
        Used by print() if __str__ isn't defined.

        Why this matters:
        - C#: ToString()
        - Python: __repr__() is called by repr(), __str__() by str(). Define both if you want different behaviors.
        """
        status = "M" if self.is_mine else str(self.adjacent_mines)
        revealed_status = "R" if self.revealed else "U"
        flagged_status = "F" if self.flagged else "-"
        return f"Cell({status},{revealed_status},{flagged_status})"


class Minesweeper:
    """Main game class."""

    def __init__(self, width: int = 10, height: int = 10, num_mines: int = 10):
        """
        Initialize the game board.

        Type hints are optional but encouraged (PEP 484).
        Run: python -m mypy minesweeper.py  to check types statically.
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
        SOLUTION-3: 2D board using nested list comprehension

        Why this matters:
        - List comprehension is faster and more readable than a loop.
        - Nested comprehensions flatten left-to-right: [row for each row] where each row = [cell for each col].
        - The _ variable is a Python convention for "I don't use this value."

        This is equivalent to:
            board = []
            for _ in range(self.height):
                row = []
                for _ in range(self.width):
                    row.append(Cell())
                board.append(row)

        But the comprehension is one line and avoids intermediate lists.
        """
        self.board = [[Cell() for _ in range(self.width)] for _ in range(self.height)]

    def _place_mines(self) -> None:
        """
        SOLUTION-4: Place mines using set operations and tuple unpacking

        Why this matters:
        - Sets prevent duplicates automatically (O(1) average insert).
        - While loop with set.add() is the Pythonic way to accumulate random unique values.
        - Tuple unpacking (row, col = position) is cleaner than position[0], position[1].

        This is equivalent to:
            placed = set()
            while len(placed) < self.num_mines:
                row = random.randint(0, self.height - 1)
                col = random.randint(0, self.width - 1)
                placed.add((row, col))
            for row, col in placed:
                self.board[row][col].is_mine = True

        But with tuple unpacking in one line.
        """
        placed: Set[Tuple[int, int]] = set()
        while len(placed) < self.num_mines:
            position = (random.randint(0, self.height - 1), random.randint(0, self.width - 1))
            placed.add(position)

        for row, col in placed:  # Unpacking each (row, col) tuple
            self.board[row][col].is_mine = True

    def _compute_adjacent_mines(self) -> None:
        """
        SOLUTION-5: Count adjacent mines with enumerate() and slicing

        Why this matters:
        - enumerate() gives (index, value). Use instead of range(len(...)).
        - Slicing is safe: board[0:100] on a 10-element board returns elements 0-9 (no error).
        - Negative indices work: list[-1] is the last element.

        For a 3x3 grid around (row, col), we get indices [row-1:row+2][col-1:col+2].
        If row=0, slicing [−1:2] safely gives [0:2].

        This is equivalent to:
            for row in range(self.height):
                for col in range(self.width):
                    count = 0
                    for dr in [-1, 0, 1]:
                        for dc in [-1, 0, 1]:
                            if dr == 0 and dc == 0:
                                continue
                            nr, nc = row + dr, col + dc
                            if 0 <= nr < self.height and 0 <= nc < self.width:
                                if self.board[nr][nc].is_mine:
                                    count += 1
                    self.board[row][col].adjacent_mines = count

        But slicing handles bounds safely.
        """
        for row, cells in enumerate(self.board):
            for col, cell in enumerate(cells):
                count = 0
                # Get 3x3 region around (row, col). Slicing is safe with out-of-bounds indices.
                for neighbor_row in self.board[row - 1 : row + 2]:
                    for neighbor_cell in neighbor_row[col - 1 : col + 2]:
                        if neighbor_cell.is_mine:
                            count += 1
                # Subtract 1 if the center cell is a mine (we counted it).
                if cell.is_mine:
                    count -= 1
                cell.adjacent_mines = count

    def get_neighbors(self, row: int, col: int) -> List[Tuple[int, int]]:
        """
        SOLUTION-6: Get adjacent cells using list comprehension with filter

        Why this matters:
        - List comprehension with if clause is cleaner than filter().
        - Reads left-to-right: [expression for item in iterable if condition]
        - More Pythonic than: [x for x in filter(lambda t: is_valid(t), neighbors)]

        This is equivalent to:
            neighbors = []
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = row + dr, col + dc
                    if 0 <= nr < self.height and 0 <= nc < self.width:
                        neighbors.append((nr, nc))
            return neighbors
        """
        return [
            (row + dr, col + dc)
            for dr in [-1, 0, 1]
            for dc in [-1, 0, 1]
            if not (dr == 0 and dc == 0)  # Skip center
            and 0 <= row + dr < self.height
            and 0 <= col + dc < self.width
        ]

    def flag_cell(self, row: int, col: int) -> None:
        """
        SOLUTION-7: Toggle flag on unrevealed cell

        Why this matters:
        - 'not' is Python's boolean negation (not ! like C#/Java).
        - Toggling with 'not' is cleaner than manual if/else.
        """
        cell = self.board[row][col]
        if not cell.revealed:
            cell.flagged = not cell.flagged

    def reveal_cell(self, row: int, col: int) -> None:
        """
        SOLUTION-8: Reveal cell with recursive flood-fill

        Why this matters:
        - Recursion in Python is simpler for small depths (Minesweeper board << 1000).
        - Python's default recursion limit is ~1000; games are safe.
        - If you hit the limit, call sys.setrecursionlimit(10000) at module start.

        The flood-fill logic:
        1. Bounds check: if out of bounds, return.
        2. Already revealed? Return (base case for recursion).
        3. Is mine? Game over.
        4. Mark revealed.
        5. If no adjacent mines, recursively reveal neighbors.
        """
        # Bounds check
        if not (0 <= row < self.height and 0 <= col < self.width):
            return

        cell = self.board[row][col]

        # Already revealed or flagged? Stop.
        if cell.revealed or cell.flagged:
            return

        # Mark as revealed.
        cell.revealed = True

        # Hit a mine? Game over.
        if cell.is_mine:
            self.game_over = True
            return

        # If empty (no adjacent mines), flood-fill neighbors.
        if cell.adjacent_mines == 0:
            for neighbor_row, neighbor_col in self.get_neighbors(row, col):
                self.reveal_cell(neighbor_row, neighbor_col)

    @property
    def is_complete(self) -> bool:
        """
        SOLUTION-9: Check win condition with @property decorator

        Why this matters:
        - @property decorator replaces C#/Java get-only properties.
        - Allows you to call is_complete (no parens) instead of is_complete().
        - Underneath, it's a method; the decorator makes it look like an attribute.
        - Pythonic convention: is_complete (snake_case), not IsComplete (PascalCase).

        Win condition: all non-mine cells are revealed.
        Count unrevealed cells that aren't mines. If 0, player won.
        """
        for row in self.board:
            for cell in row:
                # If unrevealed and not a mine, game is not complete.
                if not cell.revealed and not cell.is_mine:
                    return False
        return True

    def display(self) -> None:
        """
        SOLUTION-10: Display board with f-strings and enumerate()

        Why this matters:
        - f-strings (Python 3.6+) are like C# string interpolation, but more powerful.
        - f-strings support format specs: f"{value:5}" (width 5), f"{value:02d}" (zero-padded).
        - enumerate() gives both index and value, avoiding manual range(len(...)).
        - print() with end="" prevents newline (like Console.Write in C#).

        Display format:
            0 1 2 3 4 5 6 7 8 9
          0 . . . . . . . . . .
          1 . 1 . . . . . . . .
          ...
        """
        # Print column headers.
        print("  ", end="")
        for col in range(self.width):
            print(f"{col} ", end="")
        print()

        # Print each row.
        for row, cells in enumerate(self.board):
            print(f"{row} ", end="")
            for cell in cells:
                if cell.flagged and not cell.revealed:
                    print("F ", end="")
                elif not cell.revealed:
                    print(". ", end="")
                elif cell.is_mine:
                    print("* ", end="")
                elif cell.adjacent_mines > 0:
                    print(f"{cell.adjacent_mines} ", end="")
                else:
                    print("  ", end="")  # Empty cell (two spaces)
            print()

    def play(self) -> None:
        """
        SOLUTION-11: Main game loop with input parsing and unpacking

        Why this matters:
        - input() reads a line as a string; .strip() removes leading/trailing whitespace.
        - .split() with no args splits on any whitespace and removes empty strings.
        - Tuple unpacking (a, b, c = input().split()) assigns values in one line.
        - map(int, ...) applies int() to each element; great for parsing.

        Input format: "row col action" or "r,c,action"
        Example: "3 5 r" to reveal (3, 5)
                 "7 8 f" to flag (7, 8)
                 "q" to quit
        """
        while not self.game_over and not self.is_complete:
            self.display()
            print()

            # Prompt and parse input.
            user_input = input("Enter 'row col action' (r=reveal, f=flag) or 'q' to quit: ").strip()

            if user_input.lower() == "q":
                print("Quit.")
                return

            try:
                parts = user_input.split()
                if len(parts) != 3:
                    print("Invalid input. Use 'row col action'.")
                    continue

                row, col, action = int(parts[0]), int(parts[1]), parts[2].lower()

                if not (0 <= row < self.height and 0 <= col < self.width):
                    print(f"Out of bounds. Use 0-{self.height - 1} for row, 0-{self.width - 1} for col.")
                    continue

                if action == "r":
                    self.reveal_cell(row, col)
                elif action == "f":
                    self.flag_cell(row, col)
                else:
                    print("Invalid action. Use 'r' (reveal) or 'f' (flag).")

            except ValueError:
                print("Invalid input. Use 'row col action'.")
                continue

            print()

        # Game end.
        self.display()
        if self.game_over:
            print("Game Over! You hit a mine.")
        elif self.is_complete:
            print("You won!")


def main() -> None:
    """Entry point."""
    print("=== Minesweeper ===")
    game = Minesweeper(width=10, height=10, num_mines=10)
    game.play()


if __name__ == "__main__":
    main()
