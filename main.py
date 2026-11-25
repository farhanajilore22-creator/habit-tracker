# main.py - Glue code
import data
import tracking
import display

def main():
    habits = data.load_habits()       # Member C
    settings = data.load_settings()   # Member C

    while True:
        print("\n--- HABIT TRACKER ---")
        print("1. Add habit")
        print("2. Mark habit done (today or past date)")
        print("3. Show today's status")
        print("4. Rename / Remove habit")
        print("5. Weekly summary")
        print("6. Insights")
        print("7. Calendar")
        print(f"8. Toggle streak freeze (Currently: {'ON' if settings['streak_freeze'] else 'OFF'})")
        print("9. Export CSV")
        print("0. Save & Exit")

        choice = input("Menu choice: ").strip()

        if choice == "1":
            display.add_habit(habits)

        elif choice == "2":
            name = display.choose_habit(habits)
            if name:
                d = display.get_valid_date()
                if tracking.mark_done(habits, name, d):
                    print(f"Marked '{name}' done for {d}")
                else:
                    print("Already marked done for that day!")

        elif choice == "3":
            display.show_today(habits, settings)

        elif choice == "4":
            name = display.choose_habit(habits)
            if name:
                action = input("Rename (r) or Remove (d)? ").lower().strip()
                if action == "r":
                    new_name = input("New name: ").strip()
                    if new_name and new_name not in habits:
                        habits[new_name] = habits.pop(name)
                        print("Renamed.")
                    else:
                        print("Invalid or duplicate name.")
                elif action == "d":
                    del habits[name]
                    print("Removed.")

        elif choice == "5":
            display.weekly_summary(habits, settings)

        elif choice == "6":
            display.show_insights(habits, settings)

        elif choice == "7":
            display.show_calendar(habits)

        elif choice == "8":
            settings["streak_freeze"] = not settings["streak_freeze"]
            data.save_settings(settings)
            print(f"Streak freeze is now {'ON' if settings['streak_freeze'] else 'OFF'}")

        elif choice == "9":
            stats = tracking.get_all_stats(habits, settings)
            data.export_csv(habits, stats)

        elif choice == "0":
            data.save_habits(habits)
            data.save_settings(settings)
            print("Saved. Goodbye!")
            break
        else:
            print("Invalid choice. Try again.")

        # Auto-save after every action
        data.save_habits(habits)

if __name__ == "__main__":
    main()
    