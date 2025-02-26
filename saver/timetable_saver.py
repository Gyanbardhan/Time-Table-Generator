import json

class TimetableSaver:
    def __init__(self, time_slots, days):
        self.time_slots = time_slots
        self.days = days
        self.cell_width = 20

    def save_txt(self, timetable, filename="timetable.txt"):
        with open(filename, "w") as f:
            for (branch, semester, section), grid in timetable.items():
                f.write(f"\nTimetable for Branch {branch}, Semester {semester}, Section {section}\n")
                f.write("+" + "+".join(["-" * self.cell_width] * (len(self.time_slots) + 1)) + "+\n")
                f.write("| " + "Day".ljust(self.cell_width) + "|" + "|".join(slot.ljust(self.cell_width) for slot in self.time_slots) + "|\n")
                f.write("+" + "+".join(["-" * self.cell_width] * (len(self.time_slots) + 1)) + "+\n")
                for day in self.days:
                    row = f"| {day.ljust(self.cell_width-1)}|"
                    row += "|".join(grid[day][slot].ljust(self.cell_width) if grid[day][slot] else " ".ljust(self.cell_width) for slot in self.time_slots)
                    row += "|\n"
                    f.write(row)
                    f.write("+" + "+".join(["-" * self.cell_width] * (len(self.time_slots) + 1)) + "+\n")

    def save_json(self, timetable, filename="timetable.json"):
        timetable_data = {}
        for (branch, semester, section), grid in timetable.items():
            timetable_data[f"Branch_{branch}_Semester_{semester}_Section_{section}"] = grid
        with open(filename, "w") as json_file:
            json.dump(timetable_data, json_file, indent=4)
