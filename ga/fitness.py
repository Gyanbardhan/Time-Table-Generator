from config import load_data

data = load_data()
curriculum = data["curriculum"]
time_slots = ["9:00-10:00", "10:00-11:00", "11:00-12:00", "2:00-3:00", "3:00-4:00", "4:00-5:00"]
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday","Sunday"]
teachers = data["teachers"]

class FitnessCalculator:
    def __init__(self):
        self.curriculum = curriculum
        self.time_slots = time_slots
        self.days = days
        self.teachers = teachers

    def calculate(self, individual):
        score = 0
        teacher_global = {}
        room_global = {}
        teacher_assignment_count = {}
        for (branch, semester, section), timetable in individual.items():
            subj_info = self.curriculum[branch][semester][section]
            for subject, required in subj_info.items():
                count = 0
                teacher_used = None
                inconsistent = False
                for day in self.days:
                    for tslot in self.time_slots:
                        entry = timetable[day][tslot]
                        if entry and subject in entry:
                            count += 1
                            try:
                                teacher_part = entry.split(" (")[1]
                                teacher_name = teacher_part.split(",")[0]
                            except IndexError:
                                teacher_name = None
                            if teacher_used is None:
                                teacher_used = teacher_name
                            elif teacher_used != teacher_name:
                                inconsistent = True
                if count == required and not inconsistent:
                    score += 10
                else:
                    score -= abs(required - count) * 5
                    if inconsistent:
                        score -= 5
            for day in self.days:
                for tslot in self.time_slots:
                    entry = timetable[day][tslot]
                    if entry:
                        try:
                            teacher_part = entry.split(" (")[1]
                            teacher_name = teacher_part.split(",")[0]
                            room = teacher_part.split(",")[1].rstrip(")")
                        except IndexError:
                            teacher_name, room = None, None
                        if teacher_name:
                            key = (teacher_name, day, tslot)
                            teacher_global[key] = teacher_global.get(key, 0) + 1
                            teacher_assignment_count[teacher_name] = teacher_assignment_count.get(teacher_name, 0) + 1
                        if room:
                            key = (room, day, tslot)
                            room_global[key] = room_global.get(key, 0) + 1
        for key, cnt in teacher_global.items():
            if cnt > 1:
                score -= (cnt - 1) * 10
        for key, cnt in room_global.items():
            if cnt > 1:
                score -= (cnt - 1) * 10
        for teacher in self.teachers:
            teacher_name = teacher["name"]
            assigned = teacher_assignment_count.get(teacher_name, 0)
            limit = teacher["total_classes"]
            if assigned > limit:
                score -= (assigned - limit) * 50
        return score
