# Memento Mori Calendar

A small Python desktop app that shows a life calendar for someone born on April 16, 2000.

Each square can be one day or one week. The app starts in daily view:

- Gray: days or weeks already lived
- Gold: the current day or week
- Teal: days or weeks ahead

The app includes modern summary cards, a progress bar, hover hints for each day or week, a jump-to-current-period button, and a copyable summary. You can edit the birth date, calendar date, assumed lifespan, or age. Use `Set Date From Age` when you want the app to calculate the calendar date from the age fields.

Daily view is wider than the screen, so use the bottom scrollbar or `Shift` + mouse wheel to move left and right.

## Run

```powershell
python .\memento_mori_calendar.py
```

On this machine you can also double-click:

```text
run_memento_mori_calendar.bat
```

The app defaults to a 90-year calendar. You can adjust the assumed lifespan and the date used for the calculation.

## Website

Open `index.html` in a browser to use the animated web version. It has a dark dashboard layout inspired by modern life-calendar apps, with a left icon rail, control sidebar, stat cards, personal countdown cards, and a dot-grid calendar. It includes editable birth date, calendar date, age, lifespan, day/week views, and personal countdown dates that show both days and weeks left. The lifespan target can be set from 1 to 150 years, so you can make the calendar feel more urgent.
