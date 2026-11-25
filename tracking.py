# tracking.py - Member A
from datetime import date, timedelta


def today_str():
    return date.today().isoformat()


def get_done_set(habit):
    return set(habit.get("done_dates", []))


def mark_done(habits, name, d):
    # d is a date object. Returns True if newly marked, False if already done
    date_str = d.isoformat()
    if date_str in habits[name]["done_dates"]:
        return False  # Level 2: stop double marking
    habits[name]["done_dates"].append(date_str)
    habits[name]["done_dates"].sort()
    return True


def current_streak(habit, settings):
    done = get_done_set(habit)
    if not done:
        return 0

    streak = 0
    current = date.today()
    freeze_used = False

    # If today not done yet, streak can still continue from yesterday
    if current.isoformat() not in done:
        current -= timedelta(days=1)

    while True:
        ds = current.isoformat()
        if ds in done:
            streak += 1
            current -= timedelta(days=1)
        elif settings.get("streak_freeze", False) and not freeze_used:
            # Level 4: One missed day per week does not break streak
            freeze_used = True
            current -= timedelta(days=1)
        else:
            break

        # Reset freeze on Monday (new week)
        # current is now the next day to check, if it's Monday, new week starts
        if current.weekday() == 0:
            freeze_used = False

        # Safety: don't loop forever
        if streak > 3650:
            break
    return streak


def longest_streak(habit):
    done_dates = sorted(get_done_set(habit))
    if not done_dates:
        return 0
    best = 1
    current = 1
    for i in range(1, len(done_dates)):
        prev = date.fromisoformat(done_dates[i - 1])
        curr = date.fromisoformat(done_dates[i])
        if (curr - prev).days == 1:
            current += 1
            best = max(best, current)
        else:
            current = 1
    return best


def completion_rate(habit, days=7):
    done = get_done_set(habit)
    count = 0
    for i in range(days):
        d = date.today() - timedelta(days=i)
        if d.isoformat() in done:
            count += 1
    return (count / days) * 100 if days > 0 else 0


def get_all_stats(habits, settings):
    # Used by display.py and data.py - one place to get everything
    stats = {}
    for name, habit in habits.items():
        stats[name] = {
            "streak": current_streak(habit, settings),
            "longest": longest_streak(habit),
            "rate7": completion_rate(habit, 7),
            "rate30": completion_rate(habit, 30),
        }
    return stats


def get_insights(habits, settings):
    # Returns data, display.py will print it. This keeps logic separate.
    if not habits:
        return None

    stats = get_all_stats(habits, settings)

    # Most consistent = highest 30-day %
    most_consistent = max(stats, key=lambda n: stats[n]["rate30"])

    # Most missed days in last 30 days
    missed = {}
    for name, habit in habits.items():
        done_count = sum(
            1
            for i in range(30)
            if (date.today() - timedelta(days=i)).isoformat() in get_done_set(habit)
        )
        missed[name] = 30 - done_count
    most_missed = max(missed, key=lambda n: missed[n])

    # Favourite weekday per habit
    weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    fav_weekday = {}
    for name, habit in habits.items():
        counts = [0] * 7
        for ds in habit["done_dates"]:
            counts[date.fromisoformat(ds).weekday()] += 1
        if sum(counts) > 0:
            fav_weekday[name] = weekdays[counts.index(max(counts))]
        else:
            fav_weekday[name] = "None yet"

    return {
        "most_consistent": (most_consistent, stats[most_consistent]["rate30"]),
        "most_missed": (most_missed, missed[most_missed]),
        "fav_weekday": fav_weekday,
        "stats": stats,
    }


def count_this_week(habit):
    # Helper for weekly target check
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    done = get_done_set(habit)
    count = 0
    for i in range(7):
        d = monday + timedelta(days=i)
        if d.isoformat() in done:
            count += 1
    return count
