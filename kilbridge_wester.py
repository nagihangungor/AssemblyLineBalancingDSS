from collections import defaultdict
from itertools import combinations

def build_columns(task_times, precedences):
    levels = {}
    def level(t):
        if t in levels:
            return levels[t]
        preds = precedences.get(t, [])
        levels[t] = 1 + max((level(p) for p in preds), default=0)
        return levels[t]
    for t in task_times:
        level(t)
    cols = defaultdict(list)
    for t, lvl in levels.items():
        cols[lvl].append(t)
    return [cols[i] for i in sorted(cols)]

def assign_kw(task_times, precedences, cycle_time):
    columns = build_columns(task_times, precedences)
    remaining = set(task_times)
    stations = []

    while remaining:
        station = []
        rem = cycle_time

        for col in columns:
            col_rem = [t for t in col if t in remaining]
            if not col_rem:
                continue
            total = sum(task_times[t] for t in col_rem)
            if total <= rem:
                station += col_rem
                rem -= total
            else:
                best_val = 0
                best_set = []
                for k in range(1, len(col_rem)+1):
                    for comb in combinations(col_rem, k):
                        s = sum(task_times[t] for t in comb)
                        if s <= rem and s > best_val:
                            best_val, best_set = s, comb
                if best_val > 0:
                    station += list(best_set)
                    rem -= best_val
                break

        stations.append(station)
        remaining -= set(station)

    return stations
