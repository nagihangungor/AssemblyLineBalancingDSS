from collections import defaultdict

def iuff_schedule(tasks, precedences, cycle_time):
    successor_counts = defaultdict(int)
    for task, preds in precedences.items():
        for pred in preds:
            successor_counts[pred] += 1
    for task in tasks:
        successor_counts[task] = successor_counts.get(task, 0)

    unassigned_tasks = set(tasks.keys())
    assigned_tasks = set()
    stations = []
    current_station = []
    current_time = 0.0

    def get_available_tasks():
        return [task for task in unassigned_tasks if all(p in assigned_tasks for p in precedences.get(task, []))]

    while unassigned_tasks:
        available_tasks = get_available_tasks()
        available_tasks.sort(key=lambda x: successor_counts[x], reverse=True)
        for task in available_tasks:
            if current_time + tasks[task] <= cycle_time:
                current_station.append(task)
                current_time += tasks[task]
                assigned_tasks.add(task)
                unassigned_tasks.remove(task)
                break
        else:
            stations.append(current_station)
            current_station = []
            current_time = 0.0

    if current_station:
        stations.append(current_station)

    return stations
