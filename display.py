# display.py - Member B
from datetime import date, timedelta, datetime
import calendar
import tracking

def parse_date(text):
    try:
        return datetime.strptime(text.strip(), "%Y-%m-%d").date()
    except ValueError:
        return None

def get_valid_date(prompt="Enter date (YYYY-MM-DD) or press Enter for today: "):
    # Level 2: validate format + reject future dates
    while True:
        text = input(prompt).strip()
        if text == "":
            return date.today()
        d = parse_date(text)
        if d is None:
            print("Invalid format. Use YYYY-MM-DD, e.g. 2026-11-23")
            continue
        if d > date.today():
            print("Future dates are not allowed.")
            continue
        return d

def show_today(habits, settings):
    # Level 4: Sort by current streak, highest first
    stats = tracking.get_all_stats(habits, settings)
    sorted_names = sorted(habits, key=lambda n: stats[n]["streak"], reverse=True)

    print(f"\nToday: {date.today().strftime('%a %d %b %Y')}")
    print(f"{'Habit':<25} {'Today':<7} {'Streak':<10} {'Longest':<10} {'7-Day %'}")
    print("-" * 65)

    if not sorted_names:
        print("No habits yet. Add one first.")
        return

    for i, name in enumerate(sorted_names, 1):
        habit = habits[name]
        mark = "[x]" if tracking.today_str() in habit["done_dates"] else "[ ]"
        s = stats[name]
        print(f"{i}. {name:<22} {mark:<7} {s['streak']} days   {s['longest']} days   {s['rate7']:.0f}%")

    # Level 4: List habits still not done today
    not_done = [n for n in sorted_names if tracking.today_str() not in habits[n]["done_dates"]]
    if not_done:
        print("\nStill not done today:")
        for n in not_done:
            print(f" - {n}")

def weekly_summary(habits, settings):
    # Level 3: Monday to Sunday grid
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    week_days = [monday + timedelta(days=i) for i in range(7)]

    print("\nWeekly Summary (Mon - Sun)")
    print(f"{'Habit':<22} M  T  W  T  F  S  S   Target Met?")
    print("-" * 55)

    for name, habit in habits.items():
        done = tracking.get_done_set(habit)
        row = ""
        for d in week_days:
            row += "x  " if d.isoformat() in done else "-  "
        count = tracking.count_this_week(habit)
        target = habit.get("target_per_week", 7)
        # Level 3: 30-day % + target check
        rate30 = tracking.completion_rate(habit, 30)
        met = "YES" if count >= target else f"NO ({count}/{target})"
        print(f"{name:<22} {row} {met}  | 30-day: {rate30:.0f}%")

def show_calendar(habits):
    # Level 4: Text calendar, * = all habits done
    try:
        year = int(input("Enter year (e.g. 2026): "))
        month = int(input("Enter month (1-12): "))
        if not 1 <= month <= 12:
            print("Month must be 1-12.")
            return
        cal = calendar.monthcalendar(year, month)
        print(f"\n{calendar.month_name[month]} {year} - * = All habits done")
        print("Mo Tu We Th Fr Sa Su")
        for week in cal:
            line = ""
            for day in week:
                if day == 0:
                    line += "   "
                else:
                    d_str = date(year, month, day).isoformat()
                    all_done = len(habits) > 0 and all(d_str in h["done_dates"] for h in habits.values())
                    mark = "*" if all_done else " "
                    line += f"{day:2}{mark}"
                line += " "
            print(line)
    except ValueError:
        print("Invalid year/month. Enter numbers.")

def show_insights(habits, settings):
    data = tracking.get_insights(habits, settings)
    if not data:
        print("\n--- Insights ---\nNo data yet.")
        return
    print("\n--- Insights ---")
    name, rate = data["most_consistent"]
    print(f"Most consistent habit: {name} ({rate:.1f}% in last 30 days)")
    name2, missed = data["most_missed"]
    print(f"Habit with most missed days (30 days): {name2} ({missed} missed)")
    print("Favourite weekday per habit:")
    for name, fav in data["fav_weekday"].items():
        print(f" - {name}: most often done on {fav}")

def choose_habit(habits, prompt="Habit number: "):
    if not habits:
        print("No habits yet.")
        return None
    names = list(habits.keys())
    for i, n in enumerate(names, 1):
        print(f"{i}. {n}")
    while True:
        try:
            choice = int(input(prompt))
            if 1 <= choice <= len(names):
                return names[choice-1]
            print("Invalid number.")
        except ValueError:
            print("Please enter a number.")

def add_habit(habits):
    # Level 2: Reject empty + duplicate
    while True:
        name = input("Enter new habit name: ").strip()
        if not name:
            print("Name cannot be empty.")
            continue
        if name in habits:
            print("That habit already exists.")
            continue
        break
    while True:
        try:
            target = int(input("Target days per week (1-7): "))
            if 1 <= target <= 7:
                break
            print("Must be 1-7.")
        except ValueError:
            print("Enter a number.")
    habits[name] = {"target_per_week": target, "done_dates": []}
    print(f"Added: {name}")
    