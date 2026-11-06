import tkinter as tk

root = tk.Tk()
root.title("Boogie Scoreboard")
root.configure(bg="black")
root.attributes("-fullscreen", True)

scores = [0, 0, 0, 0]
current_player = 1
ball = 1

tk.Label(
    root,
    text="ALLIED LEISURE  •  BOOGIE",
    font=("DejaVu Sans", 28, "bold"),
    fg="white",
    bg="black"
).pack(pady=25)

score_labels = []

for i in range(4):
    label = tk.Label(
        root,
        text=f"PLAYER {i + 1}       0",
        font=("DejaVu Sans", 34, "bold"),
        fg="white",
        bg="black",
        width=25
    )
    label.pack(pady=10)
    score_labels.append(label)

status = tk.Label(
    root,
    text="BALL 1",
    font=("DejaVu Sans", 30),
    fg="white",
    bg="black"
)
status.pack(pady=30)

def update_display():
    for i, label in enumerate(score_labels):
        color = "yellow" if i + 1 == current_player else "white"
        label.config(
            text=f"PLAYER {i + 1}       {scores[i]:,}",
            fg=color
        )

    status.config(text=f"PLAYER {current_player}  •  BALL {ball}")

update_display()
root.mainloop()