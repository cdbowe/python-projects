"""
Tests for minesweeper.py

CONCEPT: pytest vs NUnit/xUnit
- No [TestFixture]/[Test] attributes needed — any function named test_* is a test.
- `assert` is the only assertion API; pytest rewrites it to show rich failure diffs
  (no Assert.AreEqual(expected, actual) with separate methods per comparison type).
- Fixtures (@pytest.fixture) replace [SetUp]/constructor injection — a test just
  declares a fixture as a parameter and pytest supplies it.

Run with: pytest  (from repo root, or `pytest minesweeper` — see pyproject.toml)
"""
from collections.abc import Callable, Generator
import pytest

from minesweeper import Minesweeper, Cell, CellState


@pytest.fixture
def empty_game() -> Minesweeper:
    """A 5x5 board with zero mines — a deterministic starting point.

    CONCEPT: fixtures are just functions. pytest calls this once per test that
    requests it (by naming it as a parameter) and passes the return value in.
    """
    return Minesweeper(width=5, height=5, num_mines=0)

RandintPatcher = Callable[[list[int]], None]

@pytest.fixture
def patch_randint_sequence(monkeypatch: pytest.MonkeyPatch) -> RandintPatcher:
    def _patch(values: list[int]) -> None:
        sequence = iter(values)
        monkeypatch.setattr("minesweeper.random.randint", lambda _, __: next(sequence))

    return _patch

InputPatcher = Callable[[str], None]

@pytest.fixture
def patch_next_input_line(monkeypatch: pytest.MonkeyPatch) -> InputPatcher:
    def _patch(line: str) -> None:
        monkeypatch.setattr("builtins.input", lambda _: line)

    return _patch


class TestPlaceMines:
    def test_places_exact_mine_count(self):
        game = Minesweeper(width=10, height=10, num_mines=10)
        mine_count = sum(cell.is_mine for row in game.board for cell in row)
        assert mine_count == 10

    def test_all_mines_are_in_bounds(self):
        game = Minesweeper(width=6, height=4, num_mines=5)
        for row in game.board:
            for cell in row:
                if cell.is_mine:
                    assert 0 <= cell.r < 4
                    assert 0 <= cell.c < 6

    def test_avoids_duplicate_positions(self, patch_randint_sequence: RandintPatcher):
        """CONCEPT: monkeypatch (like a manual Moq/NSubstitute setup, but a fixture)
        replaces random.randint with a scripted sequence so we can prove the
        while+set loop in _place_mines actually retries on a duplicate instead
        of silently placing fewer mines than requested.

        _random_board_position() calls random.randint twice per attempt (row, then
        col). Scripting [0,0, 0,0, 1,1] means: (0,0), (0,0) again [duplicate,
        rejected by the set], then (1,1) — so 2 unique mines requires 3 attempts.
        """
        patch_randint_sequence([0, 0, 0, 0, 1, 1])

        game = Minesweeper(width=3, height=3, num_mines=2)

        mine_positions = {(c.r, c.c) for row in game.board for c in row if c.is_mine}
        assert mine_positions == {(0, 0), (1, 1)}


class TestComputeAdjacentMines:
    def test_counts_a_single_neighboring_mine(self, empty_game: Minesweeper):
        empty_game.board[2][2].is_mine = True
        empty_game._compute_adjacent_mines()

        assert empty_game.board[1][1].adjacent_mines == 1  # diagonal neighbor
        assert empty_game.board[1][2].adjacent_mines == 1  # directly above
        assert empty_game.board[3][3].adjacent_mines == 1  # diagonal on the other side
        assert empty_game.board[0][0].adjacent_mines == 0  # too far away

    def test_mine_cells_are_skipped_not_counted(self, empty_game: Minesweeper):
        empty_game.board[2][2].is_mine = True
        empty_game._compute_adjacent_mines()
        # implementation `continue`s on mine cells, leaving adjacent_mines untouched
        assert empty_game.board[2][2].adjacent_mines == 0


class TestGetNeighbors:
    @pytest.mark.parametrize(
        "row,col,expected_count",
        [
            (0, 0, 3),  # corner
            (0, 2, 5),  # top edge
            (2, 2, 8),  # fully interior
            (4, 4, 3),  # opposite corner
        ],
    )
    def test_neighbor_count_respects_board_edges(self, empty_game: Minesweeper, row, col, expected_count):
        assert len(empty_game.get_neighbors(row, col)) == expected_count

    def test_neighbors_exclude_the_cell_itself(self, empty_game: Minesweeper):
        assert (2, 2) not in empty_game.get_neighbors(2, 2)


class TestFlagCell:
    def test_toggles_flag_on_unrevealed_cell(self, empty_game: Minesweeper):
        empty_game.flag_cell(0, 0)
        assert empty_game.board[0][0].flagged is True

        empty_game.flag_cell(0, 0)
        assert empty_game.board[0][0].flagged is False

    def test_cannot_flag_an_already_revealed_cell(self, empty_game: Minesweeper):
        empty_game.board[0][0].revealed = True
        empty_game.flag_cell(0, 0)
        assert empty_game.board[0][0].flagged is False


class TestRevealCell:
    def test_revealing_a_mine_sets_game_over(self, empty_game: Minesweeper):
        empty_game.board[1][1].is_mine = True
        empty_game.reveal_cell(1, 1)
        assert empty_game.game_over is True
        assert empty_game.board[1][1].revealed is True

    def test_flood_fill_reveals_every_zero_cell(self, empty_game: Minesweeper):
        # No mines anywhere -> every adjacent_mines is 0 -> the whole board floods open
        empty_game.reveal_cell(0, 0)
        assert all(cell.revealed for row in empty_game.board for cell in row)

    def test_flood_fill_stops_at_a_numbered_cell(self, empty_game: Minesweeper):
        empty_game.board[2][2].is_mine = True
        empty_game._compute_adjacent_mines()

        empty_game.reveal_cell(0, 0)

        assert empty_game.board[1][1].revealed is True  # numbered cell: revealed, but a stopping point
        assert empty_game.board[2][2].revealed is False  # the mine itself is never auto-revealed

    def test_out_of_bounds_is_a_noop(self, empty_game: Minesweeper):
        empty_game.reveal_cell(-1, 0)
        empty_game.reveal_cell(0, 99)
        assert not any(cell.revealed for row in empty_game.board for cell in row)


class TestIsComplete:
    def test_not_complete_while_non_mine_cells_remain_unrevealed(self, empty_game: Minesweeper):
        assert empty_game.is_complete is False

    def test_incomplete_once_all_non_mine_cells_are_revealed_but_mines_unflagged(self):
        game = Minesweeper(width=3, height=3, num_mines=2)
        for row in game.board:
            for cell in row:
                if not cell.is_mine:
                    cell.revealed = True

        assert game.is_complete is False

    def test_complete_once_all_non_mine_cells_are_revealed_and_mines_flagged(self):
        game = Minesweeper(width=3, height=3, num_mines=2)
        for row in game.board:
            for cell in row:
                if not cell.is_mine:
                    cell.revealed = True
                else:
                    cell.flagged = True

        assert game.is_complete is True

    def test_not_complete_if_game_is_already_over(self):
        game = Minesweeper(width=3, height=3, num_mines=2)
        game.game_over = True
        for row in game.board:
            for cell in row:
                cell.revealed = True

        assert game.is_complete is False

    def test_fully_mined_board_is_complete_before_any_reveal(self):
        """Edge case: construct a board where num_mines == width * height, so
        every single cell is a mine. Check `is_complete` WITHOUT calling
        reveal_cell first. Is the result what you'd expect? If not, is that
        a bug in `is_complete`, or is it actually fine given how the game
        would really be played?
        """

        # Fully mined board with no flags should NOT be complete
        game = Minesweeper(5, 5, 25)
        assert game.is_complete == False

        # Having at least 1 unflagged mine should NOT be complete
        for c in range(5):
            game.flag_cell(0, c)
        assert game.is_complete == False

        # Flagging every single mine should be complete
        for r in range(1, 5):
            for c in range(0, 5):
                game.flag_cell(r, c)
        assert game.is_complete == True
        


class TestCellRepr:
    """Cell.__repr__ decides what display() prints for each cell, so it's worth
    locking down directly rather than only indirectly through display() output.
    It has a priority order — check minesweeper.py to see which state wins
    when more than one could apply (e.g. a cell that's both flagged AND a
    revealed mine).

    Hint: you can construct a bare Cell directly — Minesweeper isn't required:
        cell = Cell(r=0, c=0, is_mine=True, revealed=True)
    """

    def test_unrevealed_cell_shows_dot(self):
        """Should show a dot whether there is a mine or not"""
        cell1 = Cell(r=0, c=0, is_mine=True, revealed=False)
        assert str(cell1) is CellState.UNREVEALED.value

        cell2 = Cell(r=1, c=1, is_mine=False, revealed=False)
        assert str(cell2) is CellState.UNREVEALED.value

    def test_flagged_unrevealed_cell_shows_f(self):
        cell = Cell(r=0, c=0, is_mine=True, revealed=False, flagged=True)
        assert str(cell) is CellState.FLAGGED.value

    def test_flagged_takes_priority_over_revealed(self):
        cell = Cell(r=0, c=0, is_mine=True, revealed=True, flagged=True)
        assert str(cell) is CellState.FLAGGED.value

    def test_revealed_mine_shows_asterisk(self):
        cell = Cell(r=0, c=0, is_mine=True, revealed=True)
        assert str(cell) is CellState.MINE.value

    def test_revealed_cell_with_zero_adjacent_mines_shows_a_space(self):
        cell = Cell(r=0, c=0, is_mine=False, revealed=True, adjacent_mines=0)
        assert str(cell) is CellState.REVEALED.value

    def test_revealed_cell_with_adjacent_mines_shows_the_count(self):
        cell = Cell(r=1, c=1, is_mine=False, revealed=True, adjacent_mines=5)
        assert str(cell) == str(5)


class TestRevealNeighbors:
    """The 'chord' action — reveal_neighbors(row, col) auto-reveals a numbered
    cell's remaining neighbors once the player has flagged enough of them.
    Completely untested right now, and it has several independent guard
    clauses worth covering one at a time (see reveal_neighbors in
    minesweeper.py):
      - the target cell must already be revealed
      - the target cell's adjacent_mines must be > 0
      - the count of FLAGGED neighbors must exactly equal adjacent_mines
      - at least one neighbor must be unrevealed AND unflagged (otherwise
        there's nothing left to do)
    """

    def test_noop_if_the_cell_itself_is_not_revealed(self, empty_game: Minesweeper):
        empty_game.reveal_neighbors(0, 0)
        assert empty_game.board[0][0].revealed is False
        assert empty_game.board[1][0].revealed is False
        assert empty_game.board[0][1].revealed is False
        assert empty_game.board[1][1].revealed is False

    def test_noop_if_the_cell_has_zero_adjacent_mines(self, empty_game: Minesweeper):
        empty_game.board[0][0].revealed = True

        empty_game.reveal_neighbors(0, 0)
        assert empty_game.board[0][0].revealed is True
        assert empty_game.board[1][0].revealed is False
        assert empty_game.board[0][1].revealed is False
        assert empty_game.board[1][1].revealed is False

    def test_noop_if_flagged_neighbor_count_less_than_adjacent_mines(self, empty_game: Minesweeper):
        empty_game.board[0][0].revealed = True
        empty_game.board[0][0].adjacent_mines = 2
        empty_game.board[1][0].is_mine = True
        empty_game.board[0][1].is_mine = True
        empty_game.flag_cell(1, 0)

        empty_game.reveal_neighbors(0, 0)
        assert empty_game.board[0][0].revealed is True
        
        assert empty_game.board[1][0].revealed is False
        assert empty_game.board[1][0].flagged is True
        
        assert empty_game.board[0][1].revealed is False
        assert empty_game.board[0][1].flagged is False
        
        assert empty_game.board[1][1].revealed is False
        assert empty_game.board[1][1].flagged is False

    def test_noop_if_flagged_neighbor_count_greater_than_adjacent_mines(self, empty_game: Minesweeper):
        empty_game.board[0][0].revealed = True
        empty_game.board[0][0].adjacent_mines = 2
        empty_game.board[1][0].is_mine = True
        empty_game.board[0][1].is_mine = True
        empty_game.flag_cell(1, 0)
        empty_game.flag_cell(0, 1)
        empty_game.flag_cell(1, 1)

        empty_game.reveal_neighbors(0, 0)
        assert empty_game.board[0][0].revealed is True
        
        assert empty_game.board[1][0].revealed is False
        assert empty_game.board[1][0].flagged is True
        
        assert empty_game.board[0][1].revealed is False
        assert empty_game.board[0][1].flagged is True
        
        assert empty_game.board[1][1].revealed is False
        assert empty_game.board[1][1].flagged is True

    def test_reveals_remaining_unflagged_neighbors_once_flag_count_matches(self, empty_game: Minesweeper):
        empty_game.board[0][0].revealed = True
        empty_game.board[0][0].adjacent_mines = 2
        empty_game.board[1][0].is_mine = True
        empty_game.board[0][1].is_mine = True
        empty_game.flag_cell(1, 0)
        empty_game.flag_cell(0, 1)

        empty_game.reveal_neighbors(0, 0)
        assert empty_game.board[0][0].revealed is True

        assert empty_game.board[1][0].revealed is False
        assert empty_game.board[1][0].flagged is True
        
        assert empty_game.board[0][1].revealed is False
        assert empty_game.board[0][1].flagged is True
        
        assert empty_game.board[1][1].revealed is True
        assert empty_game.board[1][1].flagged is False

    def test_chording_past_a_misflagged_mine_triggers_game_over(self, empty_game: Minesweeper):
        """Set up a cell with 1 adjacent mine, but flag a *different*,
        non-mine neighbor instead (so flagged_count still equals
        adjacent_mines). Calling reveal_neighbors should walk into the real,
        still-unflagged mine."""
        empty_game.board[0][0].revealed = True
        empty_game.board[0][0].adjacent_mines = 1
        empty_game.board[1][0].is_mine = True
        empty_game.flag_cell(0, 1)

        empty_game.reveal_neighbors(0, 0)
        assert empty_game.board[0][0].revealed is True

        assert empty_game.board[0][1].revealed is False
        assert empty_game.board[0][1].flagged is True
        
        assert empty_game.board[1][0].revealed is True
        assert empty_game.board[1][0].flagged is False
        
        assert empty_game.board[1][1].revealed is True
        assert empty_game.board[1][1].flagged is False

        assert empty_game.is_complete is False
        assert empty_game.game_over is True


class TestPlay:
    """New pytest concepts, both built-in fixtures like monkeypatch:
      - capsys: captures everything written to stdout/stderr during a test,
        so you can assert on printed output instead of eyeballing terminal
        output. Call `capsys.readouterr()` to get a result with `.out`/`.err`.
      - monkeypatch can patch builtins too, not just your own modules — e.g.
        `monkeypatch.setattr("builtins.input", ...)` to script canned input
        the same way you scripted random.randint earlier.
    """

    def test_init_display_prints_grid_with_all_dots_and_headers(self, empty_game: Minesweeper, capsys: Generator[pytest.CaptureFixture[str], None, None]):
        empty_game.display()
        captured = capsys.readouterr()
        assert "  0 1 2 3 4" in captured.out
        assert "0 . . . . ." in captured.out
        assert "1 . . . . ." in captured.out
        assert "2 . . . . ." in captured.out
        assert "3 . . . . ." in captured.out
        assert "4 . . . . ." in captured.out

    def test_quitting_immediately_prints_exit_message(self, empty_game: Minesweeper, monkeypatch: pytest.MonkeyPatch, capsys: Generator[pytest.CaptureFixture[str], None, None], patch_next_input_line: InputPatcher):
        patch_next_input_line('q')
        empty_game.play()
        captured = capsys.readouterr()
        assert "Exiting game" in captured.out

    def test_winning_prints_win_message(self, capsys):
        game = Minesweeper(width=5, height=5, num_mines=10)
        for row in game.board:
            for cell in row:
                if not cell.is_mine:
                    cell.revealed = True
                else:
                    cell.flagged = True

        game.play()

        captured = capsys.readouterr()
        assert "YOU WIN!!" in captured.out
