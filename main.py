import random
from deap import base, creator, tools
from config import load_data
from ga.individual import IndividualGenerator
from ga.fitness import FitnessCalculator
from ga.operators import Operators
from saver.timetable_saver import TimetableSaver
from saver.subject_schedule_saver import SubjectScheduleSaver
from flask import Flask, render_template, jsonify

app = Flask(__name__)

data = load_data()
time_slots = ["9:00-10:00", "10:00-11:00", "11:00-12:00", "2:00-3:00", "3:00-4:00", "4:00-5:00"]
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Sunday"]
curriculum = data["curriculum"]

individual_gen = IndividualGenerator()
fitness_calc = FitnessCalculator()
operators = Operators()
timetable_saver = TimetableSaver(time_slots, days)
subject_saver = SubjectScheduleSaver(time_slots, days, curriculum)

creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", dict, fitness=creator.FitnessMax)
toolbox = base.Toolbox()
toolbox.register("individual", tools.initIterate, creator.Individual, individual_gen.generate_individual)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("evaluate", lambda ind: (fitness_calc.calculate(ind),))
toolbox.register("mate", operators.crossover)
toolbox.register("mutate", operators.mutate)
toolbox.register("select", tools.selTournament, tournsize=3)

def run_ga():
    pop = toolbox.population(n=100)
    ngen, cxpb, mutpb = 100, 0.7, 0.2
    invalid_ind = [ind for ind in pop if not ind.fitness.valid]
    for ind in invalid_ind:
        ind.fitness.values = toolbox.evaluate(ind)
    for _ in range(ngen):
        offspring = toolbox.select(pop, len(pop))
        offspring = list(map(toolbox.clone, offspring))
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < cxpb:
                toolbox.mate(child1, child2)
                del child1.fitness.values, child2.fitness.values
        for mutant in offspring:
            if random.random() < mutpb:
                toolbox.mutate(mutant)
                del mutant.fitness.values
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        for ind in invalid_ind:
            ind.fitness.values = toolbox.evaluate(ind)
        pop[:] = offspring
    best_ind = max(pop, key=lambda ind: ind.fitness.values[0])
    return best_ind

@app.route("/")
def index():
    return render_template("index.html", title="Timetable Generator")

@app.route("/generate")
def generate_schedule():
    best_ind = run_ga()
    return render_template("timetable.html",
                           timetable=best_ind,
                           title="Generated Timetable",
                           time_slots=time_slots,
                           days=days)

@app.route("/subject_schedule")
def subject_schedule():
    best_ind = run_ga()
    schedule_data = {}
    for (branch, semester, section), grid in best_ind.items():
        section_dict = {}
        subj_info = curriculum[branch][semester][section]
        for subject in subj_info.keys():
            subject_grid = {day: {slot: "" for slot in time_slots} for day in days}
            for day in days:
                for slot in time_slots:
                    entry = grid[day][slot]
                    if entry and subject in entry:
                        subject_grid[day][slot] = entry
            section_dict[subject] = subject_grid
        schedule_data[f"Branch_{branch}_Semester_{semester}_Section_{section}"] = section_dict
    return render_template("subject_schedule.html",
                           schedule=schedule_data,
                           title="Subject-Wise Timetable",
                           time_slots=time_slots,
                           days=days)

@app.route("/flowchart")
def flowchart():
    return render_template("flowchart.html", title="Flowchart")

@app.route("/api/timetable")
def api_timetable():
    best_ind = run_ga()
    timetable_data = {}
    #print(best_ind)
    #import json
    from not_sch import find_missing_classes,transform_schedule_tt
    missing = find_missing_classes(best_ind, curriculum)
    #nots={}
    #nots["not_scheduled"]=missing
    #print(json.dumps(nots, indent=2))

    for (branch, semester, section), grid in best_ind.items():
        timetable_data[f"Branch_{branch}_Semester_{semester}_Section_{section}"] = grid
    timetable_data=transform_schedule_tt(timetable_data)
    timetable_data['not_scheduled']=missing
    return jsonify(timetable_data)

@app.route("/api/subject_schedule")
def api_subject_schedule():
    best_ind = run_ga()
    schedule_data = {}
    from not_sch import find_missing_classes,transform_schedule_sw
    missing = find_missing_classes(best_ind, curriculum)
    for (branch, semester, section), grid in best_ind.items():
        section_dict = {}
        subj_info = curriculum[branch][semester][section]
        for subject in subj_info.keys():
            subject_grid = {day: {slot: "" for slot in time_slots} for day in days}
            for day in days:
                for slot in time_slots:
                    entry = grid[day][slot]
                    if entry and subject in entry:
                        subject_grid[day][slot] = entry
            section_dict[subject] = subject_grid
        schedule_data[f"Branch_{branch}_Semester_{semester}_Section_{section}"] = section_dict
    print(schedule_data)
    schedule_data=transform_schedule_sw(schedule_data)
    schedule_data['not_scheduled']=missing
    return jsonify(schedule_data)

if __name__ == "__main__":
    app.run(debug=True)
