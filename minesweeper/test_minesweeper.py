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
from collections.abc import Callable
import pytest

from minesweeper import Minesweeper, Cell


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
        # sequence = iter([0, 0, 0, 0, 1, 1])
        # monkeypatch.setattr("minesweeper.random.randint", lambda a, b: next(sequence))
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
    def test_incomplete_while_non_mine_cells_remain_unrevealed(self, empty_game: Minesweeper):
        assert empty_game.is_complete is False

    def test_complete_once_all_non_mine_cells_are_revealed(self):
        game = Minesweeper(width=3, height=3, num_mines=2)
        for row in game.board:
            for cell in row:
                if not cell.is_mine:
                    cell.revealed = True
        assert game.is_complete is True

    def test_not_complete_if_game_is_already_over(self):
        game = Minesweeper(width=3, height=3, num_mines=2)
        game.game_over = True
        for row in game.board:
            for cell in row:
                cell.revealed = True
        assert game.is_complete is False
