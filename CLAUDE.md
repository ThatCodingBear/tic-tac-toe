# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the game

```bash
python tic_tac_toe.py
```

## Architecture

Single-file terminal game (`tic_tac_toe.py`) with these logical layers:

- **Board**: flat 9-element list (row-major, 0-indexed internally, 1-indexed for players). All board operations (`apply_move`, `available_moves`) are non-destructive — they return new lists.
- **Win detection**: `lines_through(index)` returns only the row, column, and diagonal(s) that pass through the last move, avoiding a full board scan every turn.
- **AI**: `minimax` with alpha-beta pruning. `choose_ai_move` is the entry point. Scores are depth-adjusted (`±10 ∓ depth`) so the AI prefers faster wins and slower losses.
- **Game loop**: `run_game(mode)` handles a single game; `main()` wraps it with replay and mode selection. Mode 1 = Human vs AI, Mode 2 = Human vs Human.
