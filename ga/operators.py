import random
from config import load_data

data = load_data()
time_slots = ["9:00-10:00", "10:00-11:00", "11:00-12:00", "2:00-3:00", "3:00-4:00", "4:00-5:00"]
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday","Sunday"]

class Operators:
    @staticmethod
    def crossover(ind1, ind2):
        for key in ind1.keys():
            if random.random() < 0.5:
                day = random.choice(days)
                slot = random.choice(time_slots)
                ind1[key][day][slot], ind2[key][day][slot] = ind2[key][day][slot], ind1[key][day][slot]
        return ind1, ind2

    @staticmethod
    def mutate(individual, indpb=0.2):
        for key, timetable in individual.items():
            if random.random() < indpb:
                day1, day2 = random.sample(days, 2)
                slot1, slot2 = random.choice(time_slots), random.choice(time_slots)
                timetable[day1][slot1], timetable[day2][slot2] = timetable[day2][slot2], timetable[day1][slot1]
        return individual,
