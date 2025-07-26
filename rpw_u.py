def rpw_u_schedule(tasks: dict, precedences: dict, cycle_time: float) -> list:
    from collections import defaultdict

    # Successor dictionary (needed for backward pass)
    successors = defaultdict(list)
    for task, preds in precedences.items():
        for pred in preds:
            successors[pred].append(task)

    # Compute forward positional weights (FPW)
    def compute_forward_weights(task, visited):
        if task in visited:
            return visited[task]
        succs = successors.get(task, [])
        weight = tasks[task] + max([compute_forward_weights(s, visited) for s in succs], default=0)
        visited[task] = weight
        return weight

    # Compute backward positional weights (BPW)
    def compute_backward_weights(task, visited):
        if task in visited:
            return visited[task]
        preds = precedences.get(task, [])
        weight = tasks[task] + max([compute_backward_weights(p, visited) for p in preds], default=0)
        visited[task] = weight
        return weight

    forward_weights = {}
    backward_weights = {}
    for task in tasks:
        compute_forward_weights(task, forward_weights)
        compute_backward_weights(task, backward_weights)

    # Decide on assignment type and priority weight
    task_priority = []
    for task in tasks:
        f = forward_weights[task]
        b = backward_weights[task]
        if f >= b:
            task_priority.append((task, f, 'Ileri'))
        else:
            task_priority.append((task, b, 'Geri'))

    # Sort by priority weight descending
    task_priority.sort(key=lambda x: -x[1])

    assigned = set()
    stations = []

    while len(assigned) < len(tasks):
        station = []
        time_left = cycle_time

        for task, _, direction in task_priority:
            if task in assigned:
                continue

            # Check precedence constraints (forward or backward based on direction)
            if direction == 'Ileri':
                preds = precedences.get(task, [])
                if not all(p in assigned for p in preds):
                    continue
            else:  # Geri
                succs = successors.get(task, [])
                if not all(s in assigned for s in succs):
                    continue

            if tasks[task] <= time_left:
                station.append(task)
                assigned.add(task)
                time_left -= tasks[task]

        stations.append(station)

    return stations