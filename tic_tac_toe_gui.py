"""
Tic-Tac-Toe — GUI version built with tkinter.

Reuses all core logic from tic_tac_toe.py.
X is rendered in black, O in red.
"""

import tkinter as tk
from tkinter import font as tkfont

from tic_tac_toe import (
    make_board, apply_move, is_full,
    has_won, choose_ai_move, lines_through,
    EMPTY, HUMAN, AI,
)


class TicTacToeApp:
    BG = "#f5f5f5"
    BOARD_GAP = 3
    CELL_BG = "white"
    CELL_HOVER_BG = "#e8e8e8"
    WIN_BG_X = "#d6eaff"
    WIN_BG_O = "#ffe0e0"

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Tic-Tac-Toe")
        self.root.resizable(False, False)
        self.root.configure(bg=self.BG)

        self.mode = 1
        self.board = make_board()
        self.current_mark = HUMAN
        self.game_over = False
        self.scores = {HUMAN: 0, AI: 0, "draw": 0}

        self._build_ui()
        self._refresh_status()

    def _build_ui(self) -> None:
        pad = dict(padx=14, pady=6)

        # Mode selection
        mode_row = tk.Frame(self.root, bg=self.BG)
        mode_row.pack(pady=(14, 2))
        tk.Label(mode_row, text="Mode:", bg=self.BG, font=("Arial", 11)).pack(side="left", padx=(0, 6))
        self._mode_var = tk.IntVar(value=1)
        for text, val in (("Human vs AI", 1), ("Human vs Human", 2)):
            tk.Radiobutton(
                mode_row, text=text, variable=self._mode_var, value=val,
                bg=self.BG, font=("Arial", 11), command=self._on_mode_change,
            ).pack(side="left", padx=4)

        # Scoreboard
        score_outer = tk.Frame(self.root, bg="#c8d4e8", bd=2, relief="groove")
        score_outer.pack(fill="x", padx=16, pady=(8, 2))
        score_inner = tk.Frame(score_outer, bg="#c8d4e8")
        score_inner.pack(fill="x")

        self._lbl_x = tk.Label(score_inner, text="X: 0", bg="#c8d4e8",
                                font=("Arial", 14, "bold"), fg="black")
        self._lbl_x.pack(side="left", **pad)

        self._lbl_draw = tk.Label(score_inner, text="Draws: 0", bg="#c8d4e8",
                                   font=("Arial", 12), fg="#555555")
        self._lbl_draw.pack(side="left", expand=True)

        self._lbl_o = tk.Label(score_inner, text="O: 0", bg="#c8d4e8",
                                font=("Arial", 14, "bold"), fg="red")
        self._lbl_o.pack(side="right", **pad)

        # Status banner
        self._status = tk.Label(self.root, text="", bg=self.BG,
                                 font=("Arial", 14, "bold"), height=1)
        self._status.pack(pady=(10, 2))

        # Board
        board_frame = tk.Frame(self.root, bg="#666666")
        board_frame.pack(padx=16, pady=6)

        cell_font = tkfont.Font(family="Arial", size=42, weight="bold")
        self._btns: list[tk.Button] = []
        for i in range(9):
            btn = tk.Button(
                board_frame,
                text="",
                font=cell_font,
                width=3,
                height=1,
                bg=self.CELL_BG,
                activebackground=self.CELL_HOVER_BG,
                relief="flat",
                bd=0,
                cursor="hand2",
                command=lambda idx=i: self._on_cell_click(idx),
            )
            r, c = divmod(i, 3)
            btn.grid(row=r, column=c, padx=self.BOARD_GAP, pady=self.BOARD_GAP)
            self._btns.append(btn)

        # Action buttons
        btn_row = tk.Frame(self.root, bg=self.BG)
        btn_row.pack(pady=(8, 18))

        tk.Button(
            btn_row, text="Reset Game", font=("Arial", 11),
            bg="#4a90d9", fg="white", activebackground="#357abd",
            relief="flat", padx=14, pady=5,
            command=self._reset_game,
        ).pack(side="left", padx=8)

        tk.Button(
            btn_row, text="Reset Scoreboard", font=("Arial", 11),
            bg="#e07b39", fg="white", activebackground="#c0612a",
            relief="flat", padx=14, pady=5,
            command=self._reset_scores,
        ).pack(side="left", padx=8)

    def _refresh_status(self) -> None:
        if self.game_over:
            return
        if self.mode == 1 and self.current_mark == AI:
            self._status.config(text="AI is thinking…", fg="red")
        elif self.current_mark == HUMAN:
            self._status.config(text="X's turn", fg="black")
        else:
            self._status.config(text="O's turn", fg="red")

    def _refresh_scores(self) -> None:
        self._lbl_x.config(text=f"X: {self.scores[HUMAN]}")
        self._lbl_o.config(text=f"O: {self.scores[AI]}")
        self._lbl_draw.config(text=f"Draws: {self.scores['draw']}")

    def _on_cell_click(self, index: int) -> None:
        if self.game_over or self.board[index] != EMPTY:
            return
        if self.mode == 1 and self.current_mark == AI:
            return
        self._place(index, self.current_mark)

    def _place(self, index: int, mark: str) -> None:
        self.board = apply_move(self.board, index, mark)
        color = "black" if mark == HUMAN else "red"
        self._btns[index].config(
            text=mark,
            fg=color,
            disabledforeground=color,
            state="disabled",
        )

        if has_won(self.board, index, mark):
            self._show_win(index, mark)
            return

        if is_full(self.board):
            self.game_over = True
            self.scores["draw"] += 1
            self._refresh_scores()
            self._status.config(text="It's a draw!", fg="#555555")
            return

        self.current_mark = AI if self.current_mark == HUMAN else HUMAN
        self._refresh_status()

        if self.mode == 1 and self.current_mark == AI:
            self.root.after(350, self._ai_move)

    def _ai_move(self) -> None:
        if self.game_over:
            return
        move = choose_ai_move(self.board)
        self._place(move, AI)

    def _show_win(self, last_index: int, mark: str) -> None:
        self.game_over = True
        self.scores[mark] += 1
        self._refresh_scores()

        win_bg = self.WIN_BG_O if mark == AI else self.WIN_BG_X
        for line in lines_through(last_index):
            if all(self.board[i] == mark for i in line):
                for i in line:
                    self._btns[i].config(bg=win_bg)
                break

        if self.mode == 1:
            msg = "AI wins!" if mark == AI else "You win!"
        else:
            msg = f"{'X' if mark == HUMAN else 'O'} wins!"
        color = "red" if mark == AI else "black"
        self._status.config(text=msg, fg=color)

    def _reset_game(self) -> None:
        self.board = make_board()
        self.current_mark = HUMAN
        self.game_over = False
        for btn in self._btns:
            btn.config(text="", state="normal", bg=self.CELL_BG)
        self._refresh_status()

    def _reset_scores(self) -> None:
        self.scores = {HUMAN: 0, AI: 0, "draw": 0}
        self._refresh_scores()

    def _on_mode_change(self) -> None:
        self.mode = self._mode_var.get()
        self._reset_game()


def main() -> None:
    root = tk.Tk()
    TicTacToeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
