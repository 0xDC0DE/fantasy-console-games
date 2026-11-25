"""Validate photographed layouts and find a shortest solution for each board."""

from collections import deque
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ORDER = "GHP RBY".replace(" ", "")
GOALS = {"G": 0, "H": 1, "P": 2, "R": 6, "B": 7, "Y": 8}


def parse_wall(code):
    if len(code) != 3 or code[0] not in "hv" or not code[1:].isdigit():
        raise ValueError(f"bad wall: {code}")
    r, c = int(code[1]), int(code[2])
    if code[0] == "h" and 0 <= r < 3 and 0 <= c < 2:
        a, b = r * 3 + c, r * 3 + c + 1
    elif code[0] == "v" and 0 <= r < 2 and 0 <= c < 3:
        a, b = r * 3 + c, (r + 1) * 3 + c
    else:
        raise ValueError(f"out-of-range wall: {code}")
    return tuple(sorted((a, b)))


def neighbors(cell):
    r, c = divmod(cell, 3)
    for dr, dc in ((-1, 0), (0, 1), (1, 0), (0, -1)):
        nr, nc = r + dr, c + dc
        if 0 <= nr < 3 and 0 <= nc < 3:
            yield nr * 3 + nc, dr, dc


def solve(level):
    board = "".join(level["rows"])
    names = tuple(name for name in ORDER if name in board)
    start = tuple(board.index(name) for name in names)
    target = tuple(GOALS[name] for name in names)
    walls = {parse_wall(code) for code in level["walls"]}
    if start == target:
        return 0
    seen = {start}
    queue = deque([(start, 0)])
    while queue:
        state, steps = queue.popleft()
        occupied = set(state)
        for index, name in enumerate(names):
            old = state[index]
            for adjacent, dr, dc in neighbors(old):
                if tuple(sorted((old, adjacent))) in walls:
                    continue
                destination = adjacent
                if adjacent in occupied:
                    if name != "H":
                        continue
                    ar, ac = divmod(adjacent, 3)
                    lr, lc = ar + dr, ac + dc
                    if not (0 <= lr < 3 and 0 <= lc < 3):
                        continue
                    destination = lr * 3 + lc
                    if (destination in occupied or
                            tuple(sorted((adjacent, destination))) in walls):
                        continue
                next_state = state[:index] + (destination,) + state[index + 1:]
                if next_state == target:
                    return steps + 1
                if next_state not in seen:
                    seen.add(next_state)
                    queue.append((next_state, steps + 1))
    return None


def validate():
    levels = json.loads((HERE / "levels.json").read_text())
    assert len(levels) == 48, f"expected 48 levels, got {len(levels)}"
    for number, level in enumerate(levels, 1):
        rows = level["rows"]
        assert len(rows) == 3 and all(len(row) == 3 for row in rows), number
        board = "".join(rows)
        assert set(board) <= set(ORDER + "."), number
        animals = [char for char in board if char != "."]
        assert len(animals) == len(set(animals)), number
        assert 2 <= len(animals) <= 6, number
        walls = [parse_wall(code) for code in level["walls"]]
        assert len(walls) == len(set(walls)), number
        shortest = solve(level)
        assert shortest is not None, f"level {number} cannot be solved"
        assert shortest == level["moves"], (
            f"level {number}: found {shortest} moves, book says {level['moves']}"
        )
        print(f"{number:02d}: {shortest} moves (book {level['moves']})")


if __name__ == "__main__":
    validate()
