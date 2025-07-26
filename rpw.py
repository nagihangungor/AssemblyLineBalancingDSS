from collections import defaultdict

def compute_positional_weights(tasks, precedences):
    successors = defaultdict(list)
    for task, preds in precedences.items():
        for p in preds:
            successors[p].append(task)

    memo = {}

    def dfs(node):
        if not successors.get(node):
            return tasks[node]
        if node in memo:
            return memo[node]
        max_path = max(dfs(s) for s in successors[node])
        memo[node] = tasks[node] + max_path
        return memo[node]

    return {t: dfs(t) for t in tasks}

def rpw_schedule(tasks, precedences, cycle_time):
    pw = compute_positional_weights(tasks, precedences)
    ranked = sorted(pw, key=lambda t: pw[t], reverse=True)

    assigned = set()
    stations = []

    while len(assigned) < len(tasks):
        load = 0
        station = []
        added = True
        while added:
            added = False
            for t in ranked:
                if t in assigned:
                    continue
                if any(pred not in assigned for pred in precedences.get(t, [])):
                    continue
                if load + tasks[t] <= cycle_time:
                    station.append(t)
                    assigned.add(t)
                    load += tasks[t]
                    added = True
                    break
        stations.append(station)

    return stations
