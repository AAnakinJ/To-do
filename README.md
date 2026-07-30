# Weekly To-Do

A day-by-day to-do list in pure Python (tkinter only, nothing to install), with
a graphical report at the end of every week. Available in French and English.

## Run

```bash
python todo_semaine.py
```

Start directly in English (the choice is remembered afterwards):

```bash
python todo_semaine.py --lang en
```

Run the self-tests:

```bash
python todo_semaine.py --test
```

Requirements: Python 3.9+ with tkinter (bundled with the official Windows and
macOS installers; on Debian/Ubuntu install `python3-tk`). No third-party
package is used — the charts are drawn on a tkinter `Canvas`.

## Usage

| Action | How |
| --- | --- |
| Add a task | Click the field at the bottom of a day, type, press `Enter` (or use `+`) |
| Tick / untick | Click the task |
| Delete | Click the `✕` on the right of the task |
| Rename / move to next day | Right-click the task |
| Change week | `◀` `▶` buttons, or `Ctrl+←` / `Ctrl+→` |
| Back to the current week | `Today` button |
| Open a report anytime | `This week's report` button |
| Review a past week | `History`, then double-click a week |
| Switch language | The `English` / `Français` button in the header, or `Ctrl+L` |

## Language option

The header button toggles between French and English and rebuilds the whole
window, so every label, day name, month name and date format switches at once.
The chosen language is saved in the data file and reused on the next launch.
`--lang fr` / `--lang en` overrides it from the command line.

Date formats follow the language: `27/07` and `27 juillet` in French,
`Jul 27` and `27 July` in English.

## Nothing is ever reset

Every task is stored under its own date in `todo_data.json`, next to the
script. No list is ever cleared: past weeks stay available indefinitely through
`◀` or the `History` window. Saving happens on every change, using an atomic
write, so nothing is lost if the app is closed abruptly.

## The Monday 00:01 report

On launch and then every 30 seconds, the app checks whether **Monday 00:01**
has passed. If it has, and the report for the week that just ended has not been
shown yet, a window opens automatically with:

- a **donut chart** showing the **percentage of completed tasks**;
- a **day-by-day bar chart** (percentage and `done/total` for each day);
- the totals: tasks created, completed, unfinished, and the best day.

Behaviour details:

- the report appears **only once** per week (tracked by `dernier_bilan` in the
  JSON file);
- on Sunday at 23:59 the week in progress is not reported yet;
- if the app stayed closed for several weeks, the report shown is the one for
  the most recent week that actually contains tasks; the others remain in
  `History`;
- a week without a single task opens no window.

The app has to be running (or started again) for the report to show up: if the
computer is off at Monday 00:01, the report waits for the next launch.

## Data format

```json
{
  "version": 1,
  "langue": "en",
  "dernier_bilan": "2026-W30",
  "taches": {
    "2026-07-27": [
      {
        "id": "a1b2c3d4e5f6",
        "texte": "Review report",
        "fait": true,
        "cree_le": "2026-07-27T09:12:03",
        "fait_le": "2026-07-27T18:40:11"
      }
    ]
  }
}
```

An unreadable file is renamed to `todo_data.json.corrompu` instead of being
overwritten.

Note: the code, its comments and the JSON keys are in French; only the user
interface is translated.
