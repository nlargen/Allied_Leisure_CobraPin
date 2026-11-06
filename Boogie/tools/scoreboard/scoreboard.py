
import queue
import socket
import threading
import tkinter as tk

from mpf.core.bcp.bcp_socket_client import (
    encode_command_string,
    decode_command_string,
)
from mpf._version import (
    __version__,
    __bcp_version__,
    __gmc_version__,
)


# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

BCP_HOST = "127.0.0.1"
BCP_PORT = 5052

RECONNECT_DELAY = 3
UPDATE_INTERVAL = 50

PLAYER_COUNT = 4


# ------------------------------------------------------------
# Shared state
# ------------------------------------------------------------

messages = queue.Queue()
shutdown = threading.Event()

scores = [0] * PLAYER_COUNT
player_count = 0
current_player = 0
ball = 0

game_active = False
connected = False


# ------------------------------------------------------------
# BCP networking
# ------------------------------------------------------------

def send_bcp(sock, command, **kwargs):
    """Encode and send one BCP command."""
    message = encode_command_string(command, **kwargs)
    sock.sendall((message + "\n").encode("utf-8"))


def bcp_listener():
    """Maintain the connection to MPF and forward messages to Tk."""
    while not shutdown.is_set():

        sock = None

        try:
            messages.put(("connection", False))

            sock = socket.create_connection(
                (BCP_HOST, BCP_PORT),
                timeout=5
            )

            sock.settimeout(None)

            messages.put(("connection", True))

            # BCP handshake
            send_bcp(
                sock,
                "hello",
                version=__bcp_version__,
                controller_name="Boogie HDMI Scoreboard",
                controller_version=__version__,
                gmc_version=__gmc_version__,
            )

            # Subscribe to player variable changes and game events.
            send_bcp(
                sock,
                "monitor_start",
                category="player_vars"
            )

            send_bcp(
                sock,
                "monitor_start",
                category="core_events"
            )

            # Receive newline-delimited BCP messages.
            buffer = b""

            while not shutdown.is_set():

                data = sock.recv(4096)

                if not data:
                    raise ConnectionError("MPF closed the connection")

                buffer += data

                while b"\n" in buffer:
                    line, buffer = buffer.split(b"\n", 1)

                    if not line:
                        continue

                    command, kwargs = decode_command_string(
                        line.decode("utf-8")
                    )

                    messages.put((command, kwargs))

        except Exception as error:
            if not shutdown.is_set():
                messages.put(("connection_error", str(error)))

        finally:
            if sock:
                try:
                    sock.close()
                except OSError:
                    pass

            messages.put(("connection", False))

        shutdown.wait(RECONNECT_DELAY)


# ------------------------------------------------------------
# Scoreboard UI
# ------------------------------------------------------------

root = tk.Tk()
root.title("Boogie Scoreboard")
root.configure(bg="black")
root.attributes("-fullscreen", True)

root.bind("<Escape>", lambda event: root.destroy())

header = tk.Label(
    root,
    text="ALLIED LEISURE  •  BOOGIE",
    font=("DejaVu Sans", 28, "bold"),
    fg="white",
    bg="black"
)
header.pack(pady=20)

score_labels = []

for i in range(PLAYER_COUNT):

    label = tk.Label(
        root,
        text=f"PLAYER {i + 1}       0",
        font=("DejaVu Sans", 34, "bold"),
        fg="white",
        bg="black",
        width=25
    )

    label.pack(pady=8)
    score_labels.append(label)


status = tk.Label(
    root,
    text="WAITING FOR GAME",
    font=("DejaVu Sans", 30),
    fg="white",
    bg="black"
)
status.pack(pady=25)


connection_label = tk.Label(
    root,
    text="CONNECTING TO MPF...",
    font=("DejaVu Sans", 12),
    fg="gray",
    bg="black"
)
connection_label.pack(side="bottom", pady=12)


# ------------------------------------------------------------
# Display updates
# ------------------------------------------------------------

def update_display():

    for i, label in enumerate(score_labels):

        if i < player_count:
            color = (
                "yellow"
                if i + 1 == current_player
                else "white"
            )

            label.config(
                text=f"PLAYER {i + 1}       {scores[i]:,}",
                fg=color
            )

        else:
            label.config(
                text="",
                fg="white"
            )

    if game_active:
        status.config(
            text=f"PLAYER {current_player}  •  BALL {ball}"
        )
    else:
        status.config(text="WAITING FOR GAME")


# ------------------------------------------------------------
# BCP message processing
# ------------------------------------------------------------

def process_message(command, kwargs):

    global player_count
    global current_player
    global ball
    global game_active
    global connected

    if command == "connection":

        connected = kwargs if isinstance(kwargs, bool) else False

        if connected:
            connection_label.config(
                text="CONNECTED TO MPF",
                fg="green"
            )
        else:
            connection_label.config(
                text="DISCONNECTED - RECONNECTING",
                fg="red"
            )

        return

    if command == "connection_error":
        connection_label.config(
            text=f"BCP ERROR: {kwargs}",
            fg="red"
        )
        return

    # A new player has been added.
    if command == "player_added":

        number = int(kwargs.get("player_num", 0))

        if number == 1:
            # First player means a new game.
            for i in range(PLAYER_COUNT):
                scores[i] = 0

            player_count = 0
            current_player = 0
            ball = 0
            game_active = True

        if 1 <= number <= PLAYER_COUNT:
            player_count = max(player_count, number)

    # A player's turn has started.
    elif command == "player_turn_start":

        current_player = int(kwargs.get("player_num", 0))
        game_active = True

    # A new ball has started.
    elif command == "ball_start":

        current_player = int(kwargs.get("player_num", 0))
        ball = int(kwargs.get("ball", 0))
        game_active = True

    # A ball has ended.
    elif command == "ball_end":
        pass

    # Player variable update.
    elif command == "player_variable":

        name = kwargs.get("name", "").lower()

        player_num = int(kwargs.get("player_num", 0))
        value = kwargs.get("value")

        if 1 <= player_num <= PLAYER_COUNT:

            if name == "score":
                scores[player_num - 1] = int(value)
                player_count = max(player_count, player_num)

            elif name == "ball":
                # Useful if the scoreboard connects after a turn begins.
                ball = int(value)
                player_count = max(player_count, player_num)

    update_display()


# ------------------------------------------------------------
# Tk event loop
# ------------------------------------------------------------

def poll_messages():

    while True:
        try:
            command, kwargs = messages.get_nowait()
        except queue.Empty:
            break

        process_message(command, kwargs)

    root.after(UPDATE_INTERVAL, poll_messages)


def close_scoreboard():

    shutdown.set()
    root.destroy()


root.protocol("WM_DELETE_WINDOW", close_scoreboard)

# Start the BCP listener in the background.
network_thread = threading.Thread(
    target=bcp_listener,
    daemon=True
)
network_thread.start()

update_display()
poll_messages()

root.mainloop()

shutdown.set()
