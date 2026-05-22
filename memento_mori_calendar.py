from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date, datetime
import tkinter as tk
from tkinter import ttk


BIRTH_DATE = date(2000, 4, 16)
DEFAULT_LIFESPAN_YEARS = 90


@dataclass(frozen=True)
class LifeStats:
    today: date
    birth_date: date
    lifespan_years: int
    age_years: int
    age_days_after_birthday: int
    days_lived: int
    total_days: int
    weeks_lived: int
    total_weeks: int
    days_remaining: int
    next_birthday: date

    @property
    def progress(self) -> float:
        return min(1.0, max(0.0, self.days_lived / self.total_days))

    @property
    def death_date(self) -> date:
        return safe_replace_year(self.birth_date, self.birth_date.year + self.lifespan_years)


def safe_replace_year(value: date, year: int) -> date:
    try:
        return value.replace(year=year)
    except ValueError:
        return value.replace(year=year, day=28)


def calculate_life_stats(
    birth_date: date = BIRTH_DATE,
    today: date | None = None,
    lifespan_years: int = DEFAULT_LIFESPAN_YEARS,
) -> LifeStats:
    today = today or date.today()
    birthday_this_year = safe_replace_year(birth_date, today.year)

    if today >= birthday_this_year:
        age_years = today.year - birth_date.year
        last_birthday = birthday_this_year
        next_birthday = safe_replace_year(birth_date, today.year + 1)
    else:
        age_years = today.year - birth_date.year - 1
        last_birthday = safe_replace_year(birth_date, today.year - 1)
        next_birthday = birthday_this_year

    death_date = safe_replace_year(birth_date, birth_date.year + lifespan_years)
    days_lived = max(0, (today - birth_date).days)
    total_days = max(1, (death_date - birth_date).days)
    days_remaining = max(0, (death_date - today).days)

    return LifeStats(
        today=today,
        birth_date=birth_date,
        lifespan_years=lifespan_years,
        age_years=age_years,
        age_days_after_birthday=max(0, (today - last_birthday).days),
        days_lived=days_lived,
        total_days=total_days,
        weeks_lived=days_lived // 7,
        total_weeks=lifespan_years * 52,
        days_remaining=days_remaining,
        next_birthday=next_birthday,
    )


class MementoMoriApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Memento Mori Calendar")
        self.geometry("1240x800")
        self.minsize(980, 680)
        self.configure(bg="#0f1115")

        self.lifespan_years = tk.IntVar(value=DEFAULT_LIFESPAN_YEARS)
        self.birth_date_string = tk.StringVar(value=BIRTH_DATE.isoformat())
        self.today_string = tk.StringVar(value=date.today().isoformat())
        self.age_years = tk.IntVar(value=26)
        self.age_days = tk.IntVar(value=0)
        self.calendar_mode = tk.StringVar(value="day")
        self.status = tk.StringVar()
        self.stats = calculate_life_stats(lifespan_years=self.lifespan_years.get())
        self.card_values: dict[str, tk.Label] = {}
        self.grid_metrics: dict[str, int | str] = {}

        self._build_styles()
        self._build_layout()
        self._draw_calendar()

    def _build_styles(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background="#0f1115")
        style.configure("Panel.TFrame", background="#171a21")
        style.configure("TLabel", background="#0f1115", foreground="#f8fafc")
        style.configure("Muted.TLabel", background="#0f1115", foreground="#a1a1aa")
        style.configure("Panel.TLabel", background="#171a21", foreground="#f8fafc")
        style.configure("MutedPanel.TLabel", background="#171a21", foreground="#a1a1aa")
        style.configure("TButton", padding=(12, 8), background="#2563eb", foreground="#ffffff", borderwidth=0)
        style.map("TButton", background=[("active", "#1d4ed8")])
        style.configure("Secondary.TButton", padding=(12, 8), background="#2f3542", foreground="#f8fafc", borderwidth=0)
        style.map("Secondary.TButton", background=[("active", "#3f4654")])
        style.configure("TEntry", fieldbackground="#20242d", foreground="#f8fafc", insertcolor="#f8fafc")
        style.configure("Horizontal.TScale", background="#171a21", troughcolor="#343a46")
        style.configure("TRadiobutton", background="#171a21", foreground="#f8fafc")
        style.map("TRadiobutton", background=[("active", "#171a21")], foreground=[("active", "#f8fafc")])

    def _build_layout(self) -> None:
        root = ttk.Frame(self, padding=20)
        root.pack(fill=tk.BOTH, expand=True)
        root.columnconfigure(0, weight=0)
        root.columnconfigure(1, weight=1)
        root.rowconfigure(0, weight=1)

        sidebar = ttk.Frame(root, style="Panel.TFrame", padding=22)
        sidebar.grid(row=0, column=0, sticky="nsw", padx=(0, 20))

        title = ttk.Label(
            sidebar,
            text="Memento Mori",
            style="Panel.TLabel",
            font=("Segoe UI", 26, "bold"),
        )
        title.pack(anchor="w")

        subtitle = ttk.Label(
            sidebar,
            text="A week-by-week life calendar you can tune by date or age.",
            style="MutedPanel.TLabel",
            font=("Segoe UI", 10),
            wraplength=260,
        )
        subtitle.pack(anchor="w", pady=(3, 22))

        self.progress_canvas = tk.Canvas(sidebar, width=270, height=16, bg="#171a21", highlightthickness=0)
        self.progress_canvas.pack(anchor="w", fill=tk.X, pady=(0, 18))

        self.summary_label = ttk.Label(
            sidebar,
            text="",
            style="Panel.TLabel",
            font=("Segoe UI", 11),
            justify=tk.LEFT,
            wraplength=270,
        )
        self.summary_label.pack(anchor="w", fill=tk.X)

        ttk.Separator(sidebar).pack(fill=tk.X, pady=18)

        ttk.Label(sidebar, text="Assumed lifespan", style="MutedPanel.TLabel").pack(anchor="w")
        scale = ttk.Scale(
            sidebar,
            from_=60,
            to=110,
            variable=self.lifespan_years,
            command=lambda _value: self._refresh_from_controls(),
            orient=tk.HORIZONTAL,
            length=260,
        )
        scale.pack(anchor="w", pady=(4, 2))
        self.lifespan_label = ttk.Label(sidebar, text="", style="Panel.TLabel", font=("Segoe UI", 11, "bold"))
        self.lifespan_label.pack(anchor="w", pady=(0, 14))

        ttk.Label(sidebar, text="View", style="MutedPanel.TLabel").pack(anchor="w")
        view_row = ttk.Frame(sidebar, style="Panel.TFrame")
        view_row.pack(anchor="w", pady=(4, 14), fill=tk.X)
        ttk.Radiobutton(
            view_row,
            text="Days",
            value="day",
            variable=self.calendar_mode,
            command=self._draw_calendar,
        ).pack(side=tk.LEFT)
        ttk.Radiobutton(
            view_row,
            text="Weeks",
            value="week",
            variable=self.calendar_mode,
            command=self._draw_calendar,
        ).pack(side=tk.LEFT, padx=(14, 0))

        ttk.Label(sidebar, text="Birth date", style="MutedPanel.TLabel").pack(anchor="w")
        birth_entry = ttk.Entry(sidebar, textvariable=self.birth_date_string, width=18)
        birth_entry.pack(anchor="w", pady=(4, 10))
        birth_entry.bind("<Return>", lambda _event: self._refresh_from_controls())

        ttk.Label(sidebar, text="Calendar date", style="MutedPanel.TLabel").pack(anchor="w")
        today_entry = ttk.Entry(sidebar, textvariable=self.today_string, width=18)
        today_entry.pack(anchor="w", pady=(4, 10))
        today_entry.bind("<Return>", lambda _event: self._refresh_from_controls())

        actions = ttk.Frame(sidebar, style="Panel.TFrame")
        actions.pack(anchor="w", pady=(0, 14), fill=tk.X)
        ttk.Button(actions, text="Update", command=self._refresh_from_controls).pack(side=tk.LEFT)
        ttk.Button(actions, text="Today", style="Secondary.TButton", command=self._use_today).pack(side=tk.LEFT, padx=(8, 0))

        ttk.Label(sidebar, text="Age", style="MutedPanel.TLabel").pack(anchor="w")
        age_row = ttk.Frame(sidebar, style="Panel.TFrame")
        age_row.pack(anchor="w", pady=(4, 8), fill=tk.X)
        ttk.Entry(age_row, textvariable=self.age_years, width=6).pack(side=tk.LEFT)
        ttk.Label(age_row, text="years", style="MutedPanel.TLabel").pack(side=tk.LEFT, padx=(6, 10))
        ttk.Entry(age_row, textvariable=self.age_days, width=6).pack(side=tk.LEFT)
        ttk.Label(age_row, text="days", style="MutedPanel.TLabel").pack(side=tk.LEFT, padx=(6, 0))

        ttk.Button(
            sidebar,
            text="Set Date From Age",
            style="Secondary.TButton",
            command=self._set_date_from_age,
        ).pack(anchor="w", pady=(0, 16))

        extra_actions = ttk.Frame(sidebar, style="Panel.TFrame")
        extra_actions.pack(anchor="w", pady=(0, 16), fill=tk.X)
        ttk.Button(extra_actions, text="Jump to Now", style="Secondary.TButton", command=self._jump_to_current_period).pack(side=tk.LEFT)
        ttk.Button(extra_actions, text="Copy Summary", style="Secondary.TButton", command=self._copy_summary).pack(side=tk.LEFT, padx=(8, 0))

        legend = ttk.Frame(sidebar, style="Panel.TFrame")
        legend.pack(anchor="w", fill=tk.X, pady=(6, 0))
        self._legend_item(legend, "#71717a", "Already lived")
        self._legend_item(legend, "#f59e0b", "Current day or week")
        self._legend_item(legend, "#14b8a6", "Still ahead")

        ttk.Label(
            sidebar,
            textvariable=self.status,
            style="MutedPanel.TLabel",
            wraplength=270,
            justify=tk.LEFT,
        ).pack(anchor="w", pady=(22, 0))

        main = ttk.Frame(root)
        main.grid(row=0, column=1, sticky="nsew")
        main.rowconfigure(3, weight=1)
        main.columnconfigure(0, weight=1)

        self.header_label = ttk.Label(main, text="", font=("Segoe UI", 20, "bold"))
        self.header_label.grid(row=0, column=0, sticky="w")

        self.progress_label = ttk.Label(main, text="", style="Muted.TLabel", font=("Segoe UI", 11))
        self.progress_label.grid(row=1, column=0, sticky="w", pady=(4, 14))

        cards = ttk.Frame(main)
        cards.grid(row=2, column=0, sticky="ew", pady=(0, 16))
        for column in range(4):
            cards.columnconfigure(column, weight=1)
        self._stat_card(cards, 0, "Age", "age")
        self._stat_card(cards, 1, "Life used", "used")
        self._stat_card(cards, 2, "Days left", "left")
        self._stat_card(cards, 3, "Next birthday", "birthday")

        canvas_wrap = ttk.Frame(main)
        canvas_wrap.grid(row=3, column=0, sticky="nsew")
        canvas_wrap.rowconfigure(0, weight=1)
        canvas_wrap.columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(
            canvas_wrap,
            background="#0f1115",
            highlightthickness=0,
            bd=0,
            scrollregion=(0, 0, 1000, 1600),
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")

        y_scroll = ttk.Scrollbar(canvas_wrap, orient=tk.VERTICAL, command=self.canvas.yview)
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll = ttk.Scrollbar(canvas_wrap, orient=tk.HORIZONTAL, command=self.canvas.xview)
        x_scroll.grid(row=1, column=0, sticky="ew")
        self.canvas.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        self.canvas.bind("<Configure>", lambda _event: self._draw_calendar())
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Button-4>", self._on_mousewheel)
        self.canvas.bind("<Button-5>", self._on_mousewheel)
        self.canvas.bind("<Shift-MouseWheel>", self._on_shift_mousewheel)
        self.canvas.bind("<Motion>", self._show_period_hint)

    def _stat_card(self, parent: ttk.Frame, column: int, title: str, key: str) -> None:
        card = tk.Frame(parent, bg="#171a21", highlightthickness=1, highlightbackground="#262b36")
        card.grid(row=0, column=column, sticky="ew", padx=(0 if column == 0 else 8, 0), ipady=12)
        tk.Label(card, text=title.upper(), bg="#171a21", fg="#a1a1aa", font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=14)
        value = tk.Label(card, text="", bg="#171a21", fg="#f8fafc", font=("Segoe UI", 16, "bold"))
        value.pack(anchor="w", padx=14, pady=(3, 0))
        self.card_values[key] = value

    def _legend_item(self, parent: ttk.Frame, color: str, text: str) -> None:
        row = ttk.Frame(parent, style="Panel.TFrame")
        row.pack(anchor="w", pady=3)
        swatch = tk.Canvas(row, width=18, height=18, bg="#171a21", highlightthickness=0)
        swatch.create_rectangle(3, 3, 15, 15, fill=color, outline="")
        swatch.pack(side=tk.LEFT)
        ttk.Label(row, text=text, style="MutedPanel.TLabel").pack(side=tk.LEFT, padx=(8, 0))

    def _use_today(self) -> None:
        self.today_string.set(date.today().isoformat())
        self._refresh_from_controls()

    def _refresh_from_controls(self) -> None:
        lifespan = int(round(self.lifespan_years.get()))
        self.lifespan_years.set(lifespan)
        try:
            birth_date = datetime.strptime(self.birth_date_string.get().strip(), "%Y-%m-%d").date()
            selected_today = datetime.strptime(self.today_string.get().strip(), "%Y-%m-%d").date()
        except ValueError:
            self.status.set("Use date format YYYY-MM-DD, for example 2000-04-16 or 2026-05-15.")
            return

        if selected_today < birth_date:
            self.status.set("Calendar date must be on or after birth date.")
            return

        self.stats = calculate_life_stats(birth_date=birth_date, today=selected_today, lifespan_years=lifespan)
        self._sync_age_inputs()
        self._draw_calendar()

    def _set_date_from_age(self) -> None:
        try:
            birth_date = datetime.strptime(self.birth_date_string.get().strip(), "%Y-%m-%d").date()
            age_years = int(self.age_years.get())
            age_days = int(self.age_days.get())
        except (ValueError, tk.TclError):
            self.status.set("Use a valid birth date plus whole numbers for age years and days.")
            return

        if age_years < 0 or age_days < 0:
            self.status.set("Age years and days cannot be negative.")
            return

        selected_today = safe_replace_year(birth_date, birth_date.year + age_years)
        selected_today = date.fromordinal(selected_today.toordinal() + age_days)
        self.today_string.set(selected_today.isoformat())
        self._refresh_from_controls()

    def _sync_age_inputs(self) -> None:
        self.age_years.set(self.stats.age_years)
        self.age_days.set(self.stats.age_days_after_birthday)

    def _copy_summary(self) -> None:
        self.clipboard_clear()
        self.clipboard_append(self._summary_text())
        self.status.set("Summary copied to clipboard.")

    def _jump_to_current_period(self) -> None:
        target_year = min(self.stats.age_years, self.stats.lifespan_years - 1)
        _, _, _, bottom = self.canvas.bbox("all") or (0, 0, 0, 1)
        visible_height = max(1, self.canvas.winfo_height())
        row_height = max(1, bottom / max(1, self.stats.lifespan_years))
        target_top = max(0, target_year * row_height - visible_height * 0.42)
        self.canvas.yview_moveto(min(1, target_top / max(1, bottom - visible_height)))
        if self.calendar_mode.get() == "day":
            self._center_current_day()
        self.status.set("Centered the calendar around now.")

    def _draw_calendar(self) -> None:
        width = max(self.canvas.winfo_width(), 740)
        self.canvas.delete("all")
        stats = self.stats
        progress_pct = stats.progress * 100

        self.lifespan_label.configure(text=f"{stats.lifespan_years} years")
        self.header_label.configure(text=f"Your life calendar")
        self.progress_label.configure(
            text=(
                f"Born {format_date(stats.birth_date)}. "
                f"Today is {format_date(stats.today)}."
            )
        )
        self.summary_label.configure(text=self._summary_text())
        self.card_values["age"].configure(text=f"{stats.age_years}y {stats.age_days_after_birthday}d")
        self.card_values["used"].configure(text=f"{progress_pct:.1f}%")
        self.card_values["left"].configure(text=f"{stats.days_remaining:,}")
        self.card_values["birthday"].configure(text=format_short_date(stats.next_birthday))
        self._draw_progress_bar(progress_pct)
        mode_label = "day" if self.calendar_mode.get() == "day" else "week"
        self.status.set(f"Scroll the calendar or hover a square to inspect a {mode_label}.")

        if self.calendar_mode.get() == "day":
            self._draw_day_calendar(width)
        else:
            self._draw_week_calendar(width)

    def _draw_week_calendar(self, width: int) -> None:
        stats = self.stats

        left = 54
        top = 24
        year_label_width = 42
        gap = 4
        columns = 52
        available = max(450, width - left - year_label_width - 34)
        cell = min(12, max(7, int((available - (columns - 1) * gap) / columns)))
        row_gap = 9
        label_color = "#a1a1aa"
        content_width = left + year_label_width + columns * (cell + gap) + 130

        self.grid_metrics = {
            "mode": "week",
            "left": left,
            "top": top,
            "year_label_width": year_label_width,
            "gap": gap,
            "cell": cell,
            "row_gap": row_gap,
            "columns": columns,
        }

        for year in range(stats.lifespan_years):
            y = top + year * (cell + row_gap)
            age = year
            self.canvas.create_text(
                left,
                y + cell / 2,
                text=f"{age:02d}",
                fill=label_color if age % 5 == 0 else "#585858",
                anchor="e",
                font=("Segoe UI", 8 if age % 5 else 9, "bold" if age % 5 == 0 else "normal"),
            )

            for week in range(columns):
                index = year * columns + week
                x = left + year_label_width + week * (cell + gap)
                fill, outline = self._period_colors(index, stats.weeks_lived)
                self.canvas.create_rectangle(
                    x,
                    y,
                    x + cell,
                    y + cell,
                    fill=fill,
                    outline=outline,
                    width=1,
                )

        current_year_y = top + min(stats.age_years, stats.lifespan_years - 1) * (cell + row_gap)
        self.canvas.create_text(
            left + year_label_width + columns * (cell + gap) + 12,
            current_year_y + cell / 2,
            text="you are here",
            fill="#f59e0b",
            anchor="w",
            font=("Segoe UI", 9, "bold"),
        )

        bottom = top + stats.lifespan_years * (cell + row_gap) + 24
        self.canvas.configure(scrollregion=(0, 0, max(width, content_width), bottom))

    def _draw_day_calendar(self, width: int) -> None:
        stats = self.stats
        left = 54
        top = 24
        year_label_width = 42
        gap = 1
        columns = 366
        cell = 3
        row_gap = 5
        label_color = "#a1a1aa"
        content_width = left + year_label_width + columns * (cell + gap) + 130

        self.grid_metrics = {
            "mode": "day",
            "left": left,
            "top": top,
            "year_label_width": year_label_width,
            "gap": gap,
            "cell": cell,
            "row_gap": row_gap,
            "columns": columns,
        }

        for year in range(stats.lifespan_years):
            y = top + year * (cell + row_gap)
            birthday = safe_replace_year(stats.birth_date, stats.birth_date.year + year)
            next_birthday = safe_replace_year(stats.birth_date, stats.birth_date.year + year + 1)
            days_this_life_year = (next_birthday - birthday).days
            year_start_index = (birthday - stats.birth_date).days

            self.canvas.create_text(
                left,
                y + cell / 2,
                text=f"{year:02d}",
                fill=label_color if year % 5 == 0 else "#585858",
                anchor="e",
                font=("Segoe UI", 8 if year % 5 else 9, "bold" if year % 5 == 0 else "normal"),
            )

            for day in range(days_this_life_year):
                index = year_start_index + day
                if index >= stats.total_days:
                    break
                x = left + year_label_width + day * (cell + gap)
                fill, outline = self._period_colors(index, stats.days_lived)
                self.canvas.create_rectangle(
                    x,
                    y,
                    x + cell,
                    y + cell,
                    fill=fill,
                    outline=outline,
                    width=1,
                )

        current_year_y = top + min(stats.age_years, stats.lifespan_years - 1) * (cell + row_gap)
        self.canvas.create_text(
            left + year_label_width + columns * (cell + gap) + 12,
            current_year_y + cell / 2,
            text="you are here",
            fill="#f59e0b",
            anchor="w",
            font=("Segoe UI", 9, "bold"),
        )

        bottom = top + stats.lifespan_years * (cell + row_gap) + 24
        self.canvas.configure(scrollregion=(0, 0, max(width, content_width), bottom))

    def _period_colors(self, index: int, current_index: int) -> tuple[str, str]:
        if index < current_index:
            return "#71717a", "#71717a"
        if index == current_index:
            return "#f59e0b", "#fbbf24"
        return "#14b8a6", "#0f766e"

    def _summary_text(self) -> str:
        stats = self.stats
        return (
            f"Born: {format_date(stats.birth_date)}\n"
            f"Age: {stats.age_years} years and {stats.age_days_after_birthday} days\n"
            f"Days lived: {stats.days_lived:,}\n"
            f"Days left: {stats.days_remaining:,} in a {stats.lifespan_years}-year calendar\n"
            f"Next birthday: {format_date(stats.next_birthday)}"
        )

    def _draw_progress_bar(self, progress_pct: float) -> None:
        self.progress_canvas.delete("all")
        width = max(1, self.progress_canvas.winfo_width())
        height = 16
        fill_width = max(6, int(width * progress_pct / 100))
        self.progress_canvas.create_rectangle(0, 0, width, height, fill="#272b35", outline="")
        self.progress_canvas.create_rectangle(0, 0, fill_width, height, fill="#2563eb", outline="")
        self.progress_canvas.create_text(
            width / 2,
            height / 2,
            text=f"{progress_pct:.1f}% used",
            fill="#f8fafc",
            font=("Segoe UI", 8, "bold"),
        )

    def _on_mousewheel(self, event: tk.Event) -> None:
        if getattr(event, "num", None) == 4:
            self.canvas.yview_scroll(-3, "units")
        elif getattr(event, "num", None) == 5:
            self.canvas.yview_scroll(3, "units")
        else:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_shift_mousewheel(self, event: tk.Event) -> None:
        self.canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")

    def _center_current_day(self) -> None:
        metrics = self.grid_metrics
        if metrics.get("mode") != "day":
            return
        cell = int(metrics["cell"])
        gap = int(metrics["gap"])
        left = int(metrics["left"])
        year_label_width = int(metrics["year_label_width"])
        current_x = left + year_label_width + self.stats.age_days_after_birthday * (cell + gap)
        _, _, right, _ = self.canvas.bbox("all") or (0, 0, 1, 1)
        visible_width = max(1, self.canvas.winfo_width())
        target_left = max(0, current_x - visible_width * 0.5)
        self.canvas.xview_moveto(min(1, target_left / max(1, right - visible_width)))

    def _show_period_hint(self, event: tk.Event) -> None:
        if not self.grid_metrics:
            return
        left = int(self.grid_metrics["left"])
        year_label_width = int(self.grid_metrics["year_label_width"])
        top = int(self.grid_metrics["top"])
        gap = int(self.grid_metrics["gap"])
        cell = int(self.grid_metrics["cell"])
        row_gap = int(self.grid_metrics["row_gap"])
        columns = int(self.grid_metrics["columns"])
        mode = str(self.grid_metrics["mode"])
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        grid_x = x - left - year_label_width
        grid_y = y - top
        if grid_x < 0 or grid_y < 0:
            return

        column = int(grid_x // (cell + gap))
        row = int(grid_y // (cell + row_gap))
        if not (0 <= column < columns and 0 <= row < self.stats.lifespan_years):
            return
        if grid_x % (cell + gap) > cell or grid_y % (cell + row_gap) > cell:
            return

        if mode == "day":
            birthday = safe_replace_year(self.stats.birth_date, self.stats.birth_date.year + row)
            next_birthday = safe_replace_year(self.stats.birth_date, self.stats.birth_date.year + row + 1)
            days_this_life_year = (next_birthday - birthday).days
            if column >= days_this_life_year:
                return
            index = (birthday - self.stats.birth_date).days + column
            if index >= self.stats.total_days:
                return
            state = self._period_state(index, self.stats.days_lived)
            day_date = date.fromordinal(self.stats.birth_date.toordinal() + index)
            self.status.set(f"Age {row}, day {column + 1}: {state} day, {format_date(day_date)}.")
            return

        index = row * 52 + column
        state = "future"
        state = self._period_state(index, self.stats.weeks_lived)
        self.status.set(f"Age {row}, week {column + 1}: {state} week.")

    def _period_state(self, index: int, current_index: int) -> str:
        if index < current_index:
            return "lived"
        if index == current_index:
            return "current"
        return "future"


def format_date(value: date) -> str:
    return f"{calendar.month_name[value.month]} {value.day}, {value.year}"


def format_short_date(value: date) -> str:
    return f"{calendar.month_abbr[value.month]} {value.day}, {value.year}"


def main() -> None:
    app = MementoMoriApp()
    app.mainloop()


if __name__ == "__main__":
    main()
