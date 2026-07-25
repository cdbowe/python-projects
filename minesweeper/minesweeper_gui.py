#!/usr/bin/env python3
"""
Minesweeper GUI (tkinter) — Learning Exercise
Fill in the TODOs to wrap your existing, already-tested Minesweeper class in a
clickable window. This file should NOT reimplement game rules — every TODO
just calls into minesweeper.py's Minesweeper/Cell classes and repaints.

Run: python3 minesweeper_gui.py
"""

import tkinter as tk
from tkinter import messagebox

from minesweeper import Minesweeper, CellState


class MinesweeperGUI:
    """
    TODO-1: Build the window and the button grid

    CONCEPT: tkinter's Button `command=` is like a WinForms Button.Click handler,
    but wired inline instead of as a separate event subscription.

    TEACHING EXAMPLE:
        # C# / WinForms:
        var button = new Button();
        button.Click += (s, e) => OnCellClicked(row, col);

        # Python / tkinter:
        button = tk.Button(self.root, width=2, command=lambda: self.on_left_click(row, col))
        button.grid(row=row, column=col)

    GOTCHA — closures in a loop:
        Python closures capture VARIABLES, not values. A loop variable like `r`
        keeps changing, so every lambda created inside the loop would see
        whatever `r`/`c` ended up as on the LAST iteration unless you freeze
        the current value as a default argument:

            for r in range(3):
                bad = lambda: print(r)        # all three print 2 (the last r)
                good = lambda r=r: print(r)    # prints 0, 1, 2 as intended

    IMPLEMENTATION:
    - Store the game instance: self.game = Minesweeper(width, height, num_mines)
    - Create self.root = tk.Tk()
    - Build self.buttons: list[list[tk.Button]], one per cell, via nested loops
      (same shape as the nested list comprehension you used for self.board).
    - Each button needs BOTH:
        - command=... for left-click (reveal)
        - .bind("<Button-3>", ...) for right-click (flag) — see TODO-3 for why
          right-click can't use `command=`.
    - Call self.refresh() once at the end of __init__ so the initial board
      (all-hidden) is drawn correctly before the first click.
    """

    def __init__(self, width: int = 10, height: int = 10, num_mines: int = 10) -> None:
        self.game = Minesweeper(width=width, height=height, num_mines=num_mines)
        self.root = tk.Tk()
        self.root.title("Minesweeper")
        self.buttons: list[list[tk.Button]] = [
            [self._init_button(r, c) for c in range(self.game.width)] for r in range(self.game.height)
        ]

        self.refresh()

        # raise NotImplementedError("TODO-1: build self.buttons as a grid of tk.Button widgets")

        # self.refresh()  # uncomment once TODO-4 is implemented

    def _init_button(self, row: int, col: int) -> tk.Button:
        button = tk.Button(self.root, width=2, command=lambda r=row, c=col: self.on_left_click(r, c))
        button.bind("<Button-3>", lambda event, r=row, c=col: self.on_right_click(r, c))
        button.grid(row=row, column=col)
        return button

    def on_left_click(self, row: int, col: int) -> None:
        """
        TODO-2: Reveal a cell, then repaint.

        CONCEPT: this is just Minesweeper.reveal_cell — logic you already wrote
        and unit tested. The GUI's only job is: call it, then call self.refresh().
        Don't duplicate flood-fill/game-over rules here.
        """

        self.game.reveal_cell(row, col)
        self.refresh()
        # raise NotImplementedError("TODO-2: self.game.reveal_cell(row, col), then self.refresh()")

    def on_right_click(self, row: int, col: int) -> None:
        """
        TODO-3: Toggle a flag, then repaint.

        CONCEPT: tkinter mouse buttons are named "<Button-1>" (left),
        "<Button-2>" (middle), "<Button-3>" (right). `command=` ONLY fires for
        the default left click, so right-click needs an explicit .bind(). The
        bound handler receives a tkinter `event` object as its first argument
        (like an EventArgs in C#) — you'll need to swallow it in your lambda:

            button.bind("<Button-3>", lambda event, r=row, c=col: self.on_right_click(r, c))
        """
        self.game.flag_cell(row, col)
        self.refresh()
        # raise NotImplementedError("TODO-3: self.game.flag_cell(row, col), then self.refresh()")

    def refresh(self) -> None:
        """
        TODO-4: Sync every button's label/state with self.game.board

        CONCEPT: tkinter has no data-binding (no WPF-style INotifyPropertyChanged
        equivalent) — nothing redraws automatically when self.game.board changes.
        After every move you must manually push state onto each widget with
        button.config(...).

        IMPLEMENTATION — loop over self.game.board (same shape as `display()` in
        minesweeper.py) and for each cell/button pair:
        - flagged            -> text="F"
        - unrevealed          -> text=""   (blank button, still clickable)
        - revealed + mine     -> text="*"
        - revealed + count>0  -> text=str(adjacent_mines)
        - revealed + count==0 -> text=""
        - if cell.revealed: button.config(state="disabled") so it can't be re-clicked

        Finish by checking self.game.game_over / self.game.is_complete and
        calling self.show_end_game_dialog(...) if either is true (TODO-5).
        """

        for row in self.game.board:
            for cell in row:
                button = self.buttons[cell.r][cell.c]
                button_disabled = cell.revealed
                button_text = ""
                if cell.flagged:
                    button_text = "F"
                elif cell.revealed and cell.is_mine:
                    button_text = "*"
                elif cell.revealed and cell.adjacent_mines > 0:
                    button_text = str(cell.adjacent_mines)
                else:
                    button_text = ""

                button.config(text=button_text)
                if cell.revealed:
                    button.config(state="disabled")

        if self.game.game_over or self.game.is_complete:
            self.show_end_game_dialog(self.game.is_complete)


        # raise NotImplementedError("TODO-4: push cell state onto each button via button.config(...)")

    def show_end_game_dialog(self, won: bool) -> None:
        """
        TODO-5: Pop a win/lose dialog using tkinter.messagebox.

        TEACHING EXAMPLE:
            from tkinter import messagebox
            messagebox.showinfo("Minesweeper", "You win!")
            messagebox.showerror("Minesweeper", "Game over!")

        Optional stretch: after the dialog closes, disable every remaining
        button so the board is frozen instead of still-clickable.
        """
        if won:
            messagebox.showinfo("Minesweeper", "You win!!")
        else:
            messagebox.showerror("Minesweeper", "Game over...")
        # raise NotImplementedError("TODO-5: messagebox.showinfo/showerror based on `won`")

    def run(self) -> None:
        """Starts tkinter's event loop — blocks until the window is closed.
        Nothing to implement here; this is just the entry point."""
        self.root.mainloop()


def main() -> None:
    gui = MinesweeperGUI(width=10, height=10, num_mines=10)
    gui.run()


if __name__ == "__main__":
    main()
