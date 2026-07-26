import os
import random
import threading
import tkinter as tk

try:
    import winsound
except ImportError:
    winsound = None

# Path to the clipped audio file (1:48-2:20 of Balisong Transformed)
_CLIP_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "balisong_clip.wav")



class SnakeGame:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Snake")
        self.root.resizable(False, False)
        self.root.configure(bg="#0f172a")

        self.cell_size = 24
        self.cols = 20
        self.rows = 20
        self.width = self.cols * self.cell_size
        self.height = self.rows * self.cell_size

        self.canvas = tk.Canvas(
            self.root,
            width=self.width,
            height=self.height,
            bg="#0f172a",
            highlightthickness=0,
        )
        self.canvas.pack()

        self.status = tk.Label(
            self.root,
            text="Score: 0",
            font=("Segoe UI", 14, "bold"),
            fg="#e2e8f0",
            bg="#0f172a",
            pady=6,
        )
        self.status.pack()

        # Floating lyric card windows (created on canvas during game-over)
        self._lyric_card_ids = []   # canvas window IDs to clean up on reset
        self._lyric_widgets = []    # tk.Label references kept alive

        # Lyrics synced to the clip (1:45-2:20). Delay = song_timestamp - 105s.
        # Clip now starts at 1:45 so each lyric has +3s of lead-in time.
        # [delay_from_clip_start, typing_speed_per_char, lyric_text]
        self._lyrics = [
            # 1:47 = 107s → 107-105 = 2.0s  — 2s buffer so user can see it fully
            [2.0,  0.04, "Have I been more sure"],
            # 1:51 = 111s → 111-105 = 6.0s
            [6.0,  0.04, "You're everything I wanted"],
            # 1:55 = 115s → 115-105 = 10.0s
            [10.0, 0.04, "You are my sun in my skies"],
            # 1:58 = 118s → 118-105 = 13.0s
            [13.0, 0.04, "You are the days in my nights, baby"],
            # 2:03 = 123s → 123-105 = 18.0s
            [18.0, 0.04, "You're everything I wanted"],
            # 2:07 = 127s → 127-105 = 22.0s
            [22.0, 0.04, "You are the reason I smile"],
            # 2:09 = 129s → 129-105 = 24.0s
            [24.0, 0.04, "You put the worth in my while, baby"],
            # 2:14 = 134s → 134-105 = 29.0s
            [29.0, 0.04, "You're everything I wanted"],
        ]

        # Card style: alternating cream / orange-ish
        self._card_styles = [
            {"bg": "#fefce8", "fg": "#1e1b4b"},   # cream
            {"bg": "#fed7aa", "fg": "#7c2d12"},   # orange
            {"bg": "#ffffff", "fg": "#1e1b4b"},   # white
            {"bg": "#fca5a5", "fg": "#7f1d1d"},   # rose
        ]

        self.snake = []
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.food = (0, 0)
        self.score = 0
        self.game_over = False

        self.root.bind("<KeyPress>", self.on_key)
        self.reset()
        self.root.mainloop()

    def reset(self):
        self.snake = [(10, 10), (9, 10), (8, 10)]
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.food = self.spawn_food()
        self.score = 0
        self.game_over = False
        self._clear_lyric_cards()
        self.canvas.configure(bg="#0f172a")
        self.status.config(text="Score: 0")
        self.draw()
        self.root.after(140, self.loop)

    def spawn_food(self):
        while True:
            pos = (random.randint(0, self.cols - 1), random.randint(0, self.rows - 1))
            if pos not in self.snake:
                return pos

    def loop(self):
        if self.game_over:
            return

        self.direction = self.next_direction
        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)

        if (
            new_head[0] < 0
            or new_head[0] >= self.cols
            or new_head[1] < 0
            or new_head[1] >= self.rows
            or new_head in self.snake
        ):
            self.end_game()
            return

        self.snake.insert(0, new_head)
        if new_head == self.food:
            self.score += 1
            self.food = self.spawn_food()
        else:
            self.snake.pop()

        self.draw()
        speed = max(70, 150 - self.score * 6)
        self.root.after(speed, self.loop)

    def draw(self):
        self.canvas.delete("all")

        if self.game_over:
            # White screen — lyrics will appear as floating cards on top
            self.canvas.configure(bg="white")
            self.canvas.create_rectangle(
                0, 0, self.width, self.height, fill="white", outline=""
            )
            # Small restart hint at the bottom
            self.canvas.create_text(
                self.width / 2,
                self.height - 16,
                text="Press R to restart",
                fill="#9ca3af",
                font=("Segoe UI", 10),
            )
            self.status.config(text="")
            return

        # Normal game rendering
        self.canvas.configure(bg="#0f172a")
        self.canvas.create_rectangle(0, 0, self.width, self.height, fill="#0f172a", outline="")

        for x in range(self.cols):
            for y in range(self.rows):
                self.canvas.create_rectangle(
                    x * self.cell_size,
                    y * self.cell_size,
                    (x + 1) * self.cell_size,
                    (y + 1) * self.cell_size,
                    outline="#1e293b",
                    width=1,
                )

        for x, y in self.snake:
            self.canvas.create_rectangle(
                x * self.cell_size + 2,
                y * self.cell_size + 2,
                (x + 1) * self.cell_size - 2,
                (y + 1) * self.cell_size - 2,
                fill="#22c55e",
                outline="#16a34a",
                width=2,
            )

        food_x, food_y = self.food
        self.canvas.create_oval(
            food_x * self.cell_size + 4,
            food_y * self.cell_size + 4,
            (food_x + 1) * self.cell_size - 4,
            (food_y + 1) * self.cell_size - 4,
            fill="#ef4444",
            outline="#dc2626",
            width=2,
        )

        self.status.config(text=f"Score: {self.score}")

    def end_game(self):
        self.game_over = True
        self.draw()
        self.play_sad_song()

    # ------------------------------------------------------------------ #
    #  Floating lyric card helpers                                        #
    # ------------------------------------------------------------------ #

    def _clear_lyric_cards(self):
        """Remove all lyric card canvas windows."""
        for cid in self._lyric_card_ids:
            try:
                self.canvas.delete(cid)
            except Exception:
                pass
        self._lyric_card_ids.clear()
        self._lyric_widgets.clear()

    def _spawn_card(self, text, index):
        """Create a floating lyric card on the canvas and typewrite into it."""
        style = self._card_styles[index % len(self._card_styles)]

        # Alternate left / right columns and stagger vertically
        col   = index % 2          # 0 = left, 1 = right
        row   = (index // 2) % 4  # 0-3 rows
        card_w = 168
        card_h = 70
        margin = 10
        x = margin + col * (self.width - card_w - margin * 2)
        y = margin + row * (card_h + 8)
        # Clamp inside canvas
        x = max(margin, min(x, self.width  - card_w - margin))
        y = max(margin, min(y, self.height - card_h - margin))

        lbl = tk.Label(
            self.canvas,
            text="",
            font=("Segoe UI", 10, "bold"),
            fg=style["fg"],
            bg=style["bg"],
            wraplength=card_w - 16,
            justify="left",
            padx=8,
            pady=8,
            relief="flat",
            width=18,
            height=3,
        )
        cid = self.canvas.create_window(x, y, window=lbl, anchor="nw")
        self._lyric_card_ids.append(cid)
        self._lyric_widgets.append(lbl)
        return lbl

    def _typewrite_card(self, lbl, text, speed):
        """Type characters one-by-one into a card label using after()."""
        buf = [""]

        def _next(i=0):
            if i < len(text):
                buf[0] += text[i]
                try:
                    lbl.config(text=buf[0])
                except Exception:
                    return
                self.root.after(int(speed * 1000), _next, i + 1)

        _next()

    # ------------------------------------------------------------------ #
    #  Timed lyric cards + audio                                          #
    # ------------------------------------------------------------------ #

    def play_sad_song(self):
        """Play the Balisong clip and schedule lyric cards at ham.py timecodes."""
        # Play audio in a background thread so UI stays responsive
        threading.Thread(target=self._play_audio, daemon=True).start()

        # Schedule lyric cards on the main thread via root.after()
        card_index = [0]
        for delay, speed, text in self._lyrics:
            ms = int(delay * 1000)
            idx = card_index[0]
            card_index[0] += 1

            def _show(t=text, s=speed, i=idx):
                if not self.game_over:
                    return
                lbl = self._spawn_card(t, i)
                self._typewrite_card(lbl, t, s)

            self.root.after(ms, _show)

    def _play_audio(self):
        """Play balisong_clip.wav (1:50-2:10) using winsound."""
        if winsound is None:
            return
        if not os.path.exists(_CLIP_PATH):
            return
        winsound.PlaySound(_CLIP_PATH, winsound.SND_FILENAME)

    def on_key(self, event):
        key = event.keysym.lower()
        moves = {
            "left": (-1, 0),
            "a": (-1, 0),
            "right": (1, 0),
            "d": (1, 0),
            "up": (0, -1),
            "w": (0, -1),
            "down": (0, 1),
            "s": (0, 1),
            "r": None,
        }

        if key == "r" and self.game_over:
            self.reset()
            return

        if key in moves:
            direction = moves[key]
            if direction is None:
                return
            if direction != (-self.direction[0], -self.direction[1]):
                self.next_direction = direction


if __name__ == "__main__":
    SnakeGame()
