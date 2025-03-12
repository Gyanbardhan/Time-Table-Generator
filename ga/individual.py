import random
from config import load_data

data = load_data()
teachers = data["teachers"]
classrooms = data["classrooms"]
curriculum = data["curriculum"]
time_slots = ["9:00-10:00", "10:00-11:00", "11:00-12:00", "2:00-3:00", "3:00-4:00", "4:00-5:00"]
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday","Sunday"]

generation_warnings = []

class IndividualGenerator:
    def __init__(self):
        self.teachers = teachers
        self.classrooms = classrooms
        self.curriculum = curriculum
        self.time_slots = time_slots
        self.days = days
        self.warnings = generation_warnings

    def generate_individual(self):
        teacher_schedule = {t["name"]: set() for t in self.teachers}
        room_schedule = {r["name"]: set() for r in self.classrooms}
        individual = {}
        total_required = 0
        total_scheduled = 0
        
        for branch, sem_dict in self.curriculum.items():
            for semester, sections in sem_dict.items():
                for section, subj_dict in sections.items():
                    section_timetable = {
                        day: {slot: "" for slot in self.time_slots} for day in self.days
                    }
                    for subject, required_classes in subj_dict.items():
                        total_required += required_classes
                        candidate_teachers = [
                            t for t in self.teachers if subject in t["subjects_can_teach"]
                        ]
                        random.shuffle(candidate_teachers)
                        assigned = False
                        teacher_issue = False
                        room_issue = False
                        for teacher in candidate_teachers:
                            teacher_name = teacher["name"]
                            if len(teacher_schedule[teacher_name]) >= teacher["total_classes"]:
                                teacher_issue = True
                                continue
                            local_assignments = []
                            attempts = 0
                            max_attempts = 1000
                            teacher_avail_times = [t for t in teacher["available_times"] if t in self.time_slots]
                            if not teacher_avail_times:
                                teacher_issue = True
                                continue
                            while len(local_assignments) < required_classes and attempts < max_attempts:
                                attempts += 1
                                day_choice = random.choice(self.days)
                                time_choice = random.choice(teacher_avail_times)
                                if section_timetable[day_choice][time_choice]:
                                    continue
                                if (day_choice, time_choice) in teacher_schedule[teacher_name]:
                                    continue
                                if len(teacher_schedule[teacher_name]) + len(local_assignments) >= teacher["total_classes"]:
                                    teacher_issue = True
                                    break
                                available_rooms = [
                                    r for r in self.classrooms
                                    if time_choice in r["available_times"]
                                    and (day_choice, time_choice) not in room_schedule[r["name"]]
                                ]
                                if not available_rooms:
                                    room_issue = True
                                    continue
                                room = random.choice(available_rooms)
                                local_assignments.append((day_choice, time_choice, room["name"]))
                            if len(local_assignments) == required_classes:
                                for (day_choice, time_choice, room_name) in local_assignments:
                                    entry = f"{subject} ({teacher_name}, {room_name})"
                                    section_timetable[day_choice][time_choice] = entry
                                    teacher_schedule[teacher_name].add((day_choice, time_choice))
                                    room_schedule[room_name].add((day_choice, time_choice))
                                total_scheduled += required_classes
                                assigned = True
                                break  
                        if not assigned:
                            if teacher_issue and room_issue:
                                msg = (f"WARNING: Could not schedule {required_classes} classes for subject '{subject}' "
                                       f"in Branch {branch} Semester {semester} Section {section} due to insufficient "
                                       f"teacher capacity and classroom availability.")
                            elif teacher_issue:
                                msg = (f"WARNING: Could not schedule {required_classes} classes for subject '{subject}' "
                                       f"in Branch {branch} Semester {semester} Section {section} due to insufficient teacher capacity.")
                            elif room_issue:
                                msg = (f"WARNING: Could not schedule {required_classes} classes for subject '{subject}' "
                                       f"in Branch {branch} Semester {semester} Section {section} due to insufficient classroom availability.")
                            else:
                                msg = (f"WARNING: Could not schedule {required_classes} classes for subject '{subject}' "
                                       f"in Branch {branch} Semester {semester} Section {section}.")
                            #print(msg)
                            self.warnings.append(msg)
                    individual[(branch, semester, section)] = section_timetable
        with open("log.txt", "w") as file:
            for item in self.warnings:
                file.write(item + "\n")
        #print(f"Total classes required: {total_required}")
        #print(f"Total classes scheduled: {total_scheduled}")
        #print(f"Total classes NOT scheduled: {total_required - total_scheduled}")
        return individual
