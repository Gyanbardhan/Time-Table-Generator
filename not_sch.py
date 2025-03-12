import json

def find_missing_classes(best_ind, curriculum):
    result = {}
    for dept, dept_data in curriculum.items():
        for year, year_data in dept_data.items():
            for section, classes in year_data.items():
                key_tuple = (dept, year, section)
                key_str = f"{dept}-{year}-{section}"
                
                scheduled_count = {}
                section_schedule = best_ind.get(key_tuple, {})
                for day, time_slots in section_schedule.items():
                    for time_slot, scheduled_str in time_slots.items():
                        if scheduled_str.strip():
                            class_name = scheduled_str.split(" (")[0].strip()
                            scheduled_count[class_name] = scheduled_count.get(class_name, 0) + 1
                missing = {}
                for class_name, expected in classes.items():
                    count = scheduled_count.get(class_name, 0)
                    if count < expected:
                        missing[class_name] = expected - count 
                if missing:
                    result[key_str] = missing  
    return result

def transform_schedule_tt(old_schedule):

    new_schedule = {}
    
    for section_key, days in old_schedule.items():
        new_schedule[section_key] = {}
        for day, time_slots in days.items():
            new_schedule[section_key][day] = {}
            for time_slot, cell in time_slots.items():
                cell_str = cell if isinstance(cell, str) else str(cell)
                
                if not cell_str.strip():
                    new_schedule[section_key][day][time_slot] = {
                        "Subject": "",
                        "Teacher": "",
                        "Room_No": ""
                    }
                else:
                    try:
                        subject_part, details = cell_str.split(" (", 1)
                        details = details.rstrip(")")
                        teacher, room_no = details.split(",", 1)
                        new_schedule[section_key][day][time_slot] = {
                            "Subject": subject_part.strip(),
                            "Teacher": teacher.strip(),
                            "Room_No": room_no.strip()
                        }
                    except Exception as e:
                        new_schedule[section_key][day][time_slot] = {
                            "Subject": cell_str.strip(),
                            "Teacher": "",
                            "Room_No": ""
                        }
    return new_schedule

def transform_schedule_sw(old_schedule):
    new_schedule = {}
    for section_key, subjects in old_schedule.items():
        new_schedule[section_key] = {}
        for subject_name, days in subjects.items():
            new_schedule[section_key][subject_name] = {}
            for day, time_slots in days.items():
                new_schedule[section_key][subject_name][day] = {}
                for time_slot, cell in time_slots.items():
                    if isinstance(cell, dict):
                        new_cell = {
                            "Subject": cell.get("Subject", ""),
                            "Teacher": cell.get("Teacher", ""),
                            "Room_No": cell.get("Room_No", "")
                        }
                    else:
                        cell_str = cell if isinstance(cell, str) else str(cell)
                        if not cell_str.strip():
                            new_cell = {"Subject": "", "Teacher": "", "Room_No": ""}
                        else:
                            try:
                                subject_part, details = cell_str.split(" (", 1)
                                details = details.rstrip(")")
                                teacher, room_no = details.split(",", 1)
                                new_cell = {
                                    "Subject": subject_part.strip(),
                                    "Teacher": teacher.strip(),
                                    "Room_No": room_no.strip()
                                }
                            except Exception as e:
                                new_cell = {"Subject": cell_str.strip(), "Teacher": "", "Room_No": ""}
                    new_schedule[section_key][subject_name][day][time_slot] = new_cell
    return new_schedule