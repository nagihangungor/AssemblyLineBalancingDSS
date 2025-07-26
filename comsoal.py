import random
from collections import defaultdict

def comsoal(tasks, precedences, cycle_time, num_iterations=100):
    """
    COMSOAL algorithm for assembly line balancing.

    Parameters:
        tasks: dict {task_id: duration}
        precedences: dict {task_id: [predecessor_ids]}
        cycle_time: int or float
        num_iterations: int, number of repeated random solutions

    Returns:
        best_solution: List of stations with assigned tasks
        best_station_count: Number of stations in best solution
    """
    best_solution = None
    best_station_count = float('inf')

    # Step 1: Create A list with task and number of immediate predecessors
    pred_count = {task: len(precedences.get(task, [])) for task in tasks}

    # Build predecessor map for quick lookup
    all_preds = defaultdict(set)
    for task, preds in precedences.items():
        for pred in preds:
            all_preds[task].add(pred)

    for _ in range(num_iterations):
        assigned = set()
        solution = []
        A = pred_count.copy()

        while len(assigned) < len(tasks):
            # Step 2: Create B list - tasks with no unassigned predecessors
            B = [t for t in tasks if t not in assigned and all(p in assigned for p in all_preds.get(t, []))]

            station = []
            station_time = 0

            while B:
                # Step 3-4: Randomly pick a task that fits in cycle time
                random.shuffle(B)
                for t in B:
                    if station_time + tasks[t] <= cycle_time:
                        station.append(t)
                        station_time += tasks[t]
                        assigned.add(t)
                        break
                else:
                    break  # no task fits, break out to start next station

                # Recompute B
                B = [t for t in tasks if t not in assigned and all(p in assigned for p in all_preds.get(t, []))]

            solution.append(station)

        # Step 7: Choose best (minimum station count)
        if len(solution) < best_station_count:
            best_station_count = len(solution)
            best_solution = solution

    return best_solution, best_station_count