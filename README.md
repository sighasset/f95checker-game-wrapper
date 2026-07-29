# F95Checker Play Time tracker

A small launcher script that tracks game play time and saves it to the game's notes in **F95Checker**. It can also be used to run `.exe` files through Locale Emulator.

## Usage

1. Update these paths:

   ```python
   EMULATOR_PATH = r"C:\Path\To\LEProc.exe"
   F95CHECKER_DB_PATH = r"C:\Users\<name>\AppData\Roaming\f95checker\db.sqlite3"
   ```

2. Place the script next to the game executable.

3. Rename the script to match the game executable:
   - `Game-.py` → launches `Game.exe` (or one of the supported formats: `.html`, `.htm`, `.swf`)
   - `Game+.py` → launches `Game.exe` using Locale Emulator

4. Set the script as the executable for the game in F95Checker.

After closing the game, the script will add or update play time as the first line in the game's notes:

```text
Play Time: 3h 12m 23s
```

## Requirements

- Python 3.10+ (standard library only)
- [F95Checker](https://github.com/WillyJL/F95Checker) installed
- (Optional) Locale Emulator for games requiring it

## Limitations

- The updated play time will not appear in F95Checker until it is restarted.
- Do not edit the game's notes in F95Checker before restarting it after closing the game. Any changes made before the update may overwrite and remove the latest session play time.
- Play time tracking works only for `.exe` applications. Other supported formats (such as `.html`, `.htm`, or `.swf`) are launched but their running time cannot be tracked reliably.