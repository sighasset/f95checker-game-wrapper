import os
import sqlite3
import subprocess
import sys
import time
import traceback
from pathlib import Path

EMULATOR_PATH = r""
F95CHECKER_DB_PATH = r""


def main():
    start = time.monotonic()

    print("Measuring play time...")
    app_path = start_app()

    if app_path.suffix.lower() != ".exe":
        return

    session_time = round(time.monotonic() - start)

    try:
        update_game_time(session_time)
    except Exception:
        print(f"Session time: {seconds_to_text(session_time)} ({session_time}s)")
        traceback.print_exc()
        input("\nPress Enter to exit...")


def get_starter_path() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable)
    return Path(__file__)


LAUNCH_EXTENSIONS = [
    ".exe",
    ".html",
    ".htm",
    ".swf",
]


def find_app(starter: Path) -> Path:
    base = starter.parent / starter.stem[:-1]

    for ext in LAUNCH_EXTENSIONS:
        path = base.with_suffix(ext)
        if path.exists():
            return path

    raise FileNotFoundError(f"No launchable file found for {base}")


def start_app():
    starter_path = get_starter_path()
    app_path = find_app(starter_path)

    if app_path.suffix.lower() == ".exe":
        command = [str(app_path)]
        if starter_path.stem.endswith("+"):
            if not EMULATOR_PATH:
                raise RuntimeError("Please set EMULATOR_PATH in the script.")
            command = [EMULATOR_PATH, str(app_path)]
        subprocess.run(command, cwd=starter_path.parent, check=False)
    else:
        os.startfile(app_path)

    return app_path


TIME_PREFIX = "Play Time: "


def seconds_to_text(seconds: int) -> str:
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    parts = []
    if hours:
        parts.append(f"{hours}h")
    if hours or minutes:
        parts.append(f"{minutes}m")
    parts.append(f"{seconds}s")

    return " ".join(parts)


def text_to_seconds(text: str) -> int:
    total = 0
    for part in text.strip().split():
        value = int(part[:-1])

        if part.endswith("h"):
            total += value * 3600
        elif part.endswith("m"):
            total += value * 60
        elif part.endswith("s"):
            total += value
        else:
            raise ValueError(f"Invalid time component: {part!r}")

    return total


def update_play_time(current: str, session_time: int) -> str:
    if not current.startswith(TIME_PREFIX):
        raise ValueError(f"Invalid current play time: {current!r}")

    total = text_to_seconds(current[len(TIME_PREFIX) :]) + session_time
    return TIME_PREFIX + seconds_to_text(total)


def update_game_time(session_time: int) -> None:
    if not F95CHECKER_DB_PATH:
        err = f"Please set EMULATOR_PATH in the script. Current session time: {session_time}s"
        raise RuntimeError(err)
    starter = get_starter_path()
    executable = f"{starter.parent.name}/{starter.name}"

    with sqlite3.connect(F95CHECKER_DB_PATH, timeout=30) as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, notes
            FROM games
            WHERE executables LIKE ?
            """,
            (f"%{executable}%",),
        )

        row = cursor.fetchone()
        if row is None:
            raise RuntimeError(f"Couldn't find game with executable {executable!r}")

        id, notes = row
        notes = str(notes or "")

        lines = notes.splitlines()

        if lines and lines[0].startswith(TIME_PREFIX):
            lines[0] = update_play_time(lines[0], session_time)
        else:
            lines.insert(0, TIME_PREFIX + seconds_to_text(session_time))

        cursor.execute(
            "UPDATE games SET notes = ? WHERE id = ?",
            ("\n".join(lines), id),
        )

        conn.commit()


if __name__ == "__main__":
    main()
