import json

class SubjectScheduleSaver:
    def __init__(self, time_slots, days, curriculum):
        self.time_slots = time_slots
        self.days = days
        self.curriculum = curriculum
        self.cell_width = 20

    def save_txt(self, timetable, filename="subject_schedule.txt"):
        with open(filename, "w") as f:
            for (branch, semester, section), grid in timetable.items():
                subj_info = self.curriculum[branch][semester][section]
                f.write(f"\n{'='*40}\nBranch {branch} - Semester {semester} - Section {section}\n{'='*40}\n")
                for subject in subj_info.keys():
                    subject_grid = {day: {slot: "" for slot in self.time_slots} for day in self.days}
                    for day in self.days:
                        for slot in self.time_slots:
                            entry = grid[day][slot]
                            if entry and subject in entry:
                                subject_grid[day][slot] = entry
                    f.write(f"\nSubject: {subject}\n")
                    f.write("+" + "+".join(["-" * self.cell_width] * (len(self.time_slots) + 1)) + "+\n")
                    f.write("| " + "Day".ljust(self.cell_width) + "|" + "|".join(slot.ljust(self.cell_width) for slot in self.time_slots) + "|\n")
                    f.write("+" + "+".join(["-" * self.cell_width] * (len(self.time_slots) + 1)) + "+\n")
                    for day in self.days:
                        row = f"| {day.ljust(self.cell_width-1)}|"
                        row += "|".join(subject_grid[day][slot].ljust(self.cell_width) if subject_grid[day][slot] else " ".ljust(self.cell_width) for slot in self.time_slots)
                        row += "|\n"
                        f.write(row)
                        f.write("+" + "+".join(["-" * self.cell_width] * (len(self.time_slots) + 1)) + "+\n")
                    f.write("\n")

    def save_json(self, timetable, filename="subject_schedule.json"):
        schedule_data = {}
        for (branch, semester, section), grid in timetable.items():
            section_dict = {}
            subj_info = self.curriculum[branch][semester][section]
            for subject in subj_info.keys():
                subject_grid = {day: {slot: "" for slot in self.time_slots} for day in self.days}
                for day in self.days:
                    for slot in self.time_slots:
                        entry = grid[day][slot]
                        if entry and subject in entry:
                            subject_grid[day][slot] = entry
                section_dict[subject] = subject_grid
            schedule_data[f"Branch_{branch}_Semester_{semester}_Section_{section}"] = section_dict
        with open(filename, "w") as outfile:
            json.dump(schedule_data, outfile, indent=4)
