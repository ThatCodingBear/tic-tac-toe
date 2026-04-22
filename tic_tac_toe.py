"""
Tic-Tac-Toe — terminal game supporting Human vs AI and Human vs Human.

Board layout (flat list, row-major, 0-indexed internally / 1-indexed for the player):
    1 | 2 | 3
    ---------
    4 | 5 | 6
    ---------
    7 | 8 | 9

AI uses minimax search with alpha-beta pruning to play optimally.
Win detection only examines the lines that pass through the last move,
rather than re-checking all eight lines on every turn.
"""

EMPTY = ' '
HUMAN = 'X'
AI    = 'O'


# ---------------------------------------------------------------------------
# Board
# ---------------------------------------------------------------------------

def make_board():
    """Return a fresh empty 3×3 board as a flat nine-element list."""
    return [EMPTY] * 9


def apply_move(board, index, mark):
    """Return a new board with `mark` placed at `index` (non-destructive)."""
    new_board = board[:]
    new_board[index] = mark
    return new_board


def available_moves(board):
    return [i for i, cell in enumerate(board) if cell == EMPTY]


def is_full(board):
    return EMPTY not in board


# ---------------------------------------------------------------------------
# Win detection — only inspect lines that cross the last move
# ---------------------------------------------------------------------------

def lines_through(index):
    """
    Return the winning-line candidates that pass through `index`.

    Every position sits on exactly one row and one column.  Corner and edge
    positions sit on one diagonal; the centre sits on both.  Checking only
    these lines (instead of all eight) avoids redundant comparisons.
    """
    row, col = divmod(index, 3)
    candidates = []

    # Full row and full column that contain this position
    candidates.append([row * 3 + c for c in range(3)])
    candidates.append([r * 3 + col for r in range(3)])

    # Main diagonal (↘): positions 0, 4, 8 — only when row == col
    if row == col:
        candidates.append([i * 3 + i for i in range(3)])

    # Anti-diagonal (↙): positions 2, 4, 6 — only when row + col == 2
    if row + col == 2:
        candidates.append([i * 3 + (2 - i) for i in range(3)])

    return candidates


def has_won(board, last_index, mark):
    """Return True if `mark` has completed a line by playing at `last_index`."""
    return any(
        all(board[i] == mark for i in line)
        for line in lines_through(last_index)
    )


# ---------------------------------------------------------------------------
# AI — minimax with alpha-beta pruning
# ---------------------------------------------------------------------------

def minimax(board, depth, is_maximising, alpha, beta, last_index, last_mark):
    """
    Recursively evaluate board positions for the AI player ('O').

    Scores are depth-adjusted so the AI prefers faster wins and slower losses:
        +10 − depth  →  AI wins
        −10 + depth  →  Human wins
              0      →  Draw

    Alpha-beta pruning discards branches that cannot improve the current best,
    dramatically reducing the number of nodes evaluated compared with plain
    minimax — especially relevant for deeper plies in larger grids.
    """
    # Check the terminal conditions caused by the last move only.
    if last_index is not None:
        if has_won(board, last_index, last_mark):
            return (10 - depth) if last_mark == AI else (-10 + depth)
        if is_full(board):
            return 0

    moves = available_moves(board)

    if is_maximising:           # AI's turn — find the highest score
        best_score = -float('inf')
        for move in moves:
            score = minimax(
                apply_move(board, move, AI),
                depth + 1, False, alpha, beta, move, AI
            )
            best_score = max(best_score, score)
            alpha = max(alpha, best_score)
            if beta <= alpha:   # Prune: minimiser will never pick this branch
                break
        return best_score

    else:                       # Human's turn — find the lowest score
        best_score = float('inf')
        for move in moves:
            score = minimax(
                apply_move(board, move, HUMAN),
                depth + 1, True, alpha, beta, move, HUMAN
            )
            best_score = min(best_score, score)
            beta = min(beta, best_score)
            if beta <= alpha:   # Prune: maximiser will never pick this branch
                break
        return best_score


def choose_ai_move(board):
    """Select the move with the highest minimax score for the AI."""
    best_score = -float('inf')
    best_move  = None

    for move in available_moves(board):
        score = minimax(
            apply_move(board, move, AI),
            depth=0,
            is_maximising=False,
            alpha=-float('inf'),
            beta=float('inf'),
            last_index=move,
            last_mark=AI,
        )
        if score > best_score:
            best_score = score
            best_move  = move

    return best_move


# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------

CELL_SYMBOL = {EMPTY: '.', HUMAN: 'X', AI: 'O'}
ROW_SEPARATOR = '-' * 9


def render_board(board):
    """Print the current board state with row separators."""
    print()
    for row in range(3):
        cells = [CELL_SYMBOL[board[row * 3 + col]] for col in range(3)]
        print(' | '.join(cells))
        if row < 2:
            print(ROW_SEPARATOR)
    print()


def show_position_guide():
    """Print the 1-indexed position map so the player knows which number maps where."""
    print("\nBoard positions:")
    for row in range(3):
        labels = [str(row * 3 + col + 1) for col in range(3)]
        print(' | '.join(labels))
        if row < 2:
            print(ROW_SEPARATOR)
    print()


# ---------------------------------------------------------------------------
# Input helpers
# ---------------------------------------------------------------------------

def prompt_move(board, player_label):
    """
    Prompt `player_label` for a valid move (1–9) and return its 0-based index.
    Rejects positions that are already occupied or outside the valid range.
    """
    # Map the player-facing 1-indexed labels to 0-based indices for open cells
    open_positions = {str(i + 1): i for i in available_moves(board)}

    while True:
        raw = input(f"{player_label}, enter position (1-9): ").strip()
        if raw in open_positions:
            return open_positions[raw]
        print(f"  Invalid — available positions: {', '.join(sorted(open_positions))}")


def prompt_game_mode():
    """Ask the user which game mode they want and return 1 or 2."""
    print("Select game mode:")
    print("  1. Human (X) vs AI (O)")
    print("  2. Human (X) vs Human (O)")
    while True:
        choice = input("Enter 1 or 2: ").strip()
        if choice in ('1', '2'):
            return int(choice)
        print("  Please enter 1 or 2.")


# ---------------------------------------------------------------------------
# Game loop
# ---------------------------------------------------------------------------

def run_game(mode):
    """Execute a single game until a win or draw, then report the result."""
    board        = make_board()
    current_mark = HUMAN    # X always moves first
    last_move    = None

    show_position_guide()

    while True:
        render_board(board)

        # --- Determine and execute the current player's move ---
        if mode == 1 and current_mark == AI:
            print("AI is thinking…")
            move = choose_ai_move(board)
            print(f"AI plays position {move + 1}")
        else:
            player_label = "Player X" if current_mark == HUMAN else "Player O"
            move = prompt_move(board, player_label)

        board     = apply_move(board, move, current_mark)
        last_move = move

        # --- Check terminal conditions ---
        if has_won(board, last_move, current_mark):
            render_board(board)
            if mode == 1:
                print("AI wins — better luck next time!" if current_mark == AI else "You win — well played!")
            else:
                winner = "X" if current_mark == HUMAN else "O"
                print(f"Player {winner} wins!")
            return

        if is_full(board):
            render_board(board)
            print("It's a draw!")
            return

        # Alternate turns
        current_mark = AI if current_mark == HUMAN else HUMAN


def main():
    print("=== Tic-Tac-Toe ===")

    while True:
        mode = prompt_game_mode()
        run_game(mode)

        again = input("\nPlay again? (y/n): ").strip().lower()
        if again != 'y':
            break

    print("Thanks for playing!")


if __name__ == '__main__':
    main()
