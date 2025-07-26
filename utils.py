def find_min_cycle_time(tasks, precedences, target_station_count, algorithm_fn, epsilon=0.05, max_cycle=200):
    """
    Tip-2 hedefi için en küçük çevrim süresini bulur. U tipi ve düz tip algoritmalarla uyumludur.
    """
    cycle_time = max(tasks.values())
    while cycle_time < max_cycle:
        stations = algorithm_fn(tasks, precedences, cycle_time)

        # U tipi kontrolü: front-back içeren dict formatı
        if stations and isinstance(stations[0], dict):
            station_count = len(stations)
        else:
            station_count = len(stations)

        if station_count <= target_station_count:
            return cycle_time, stations

        cycle_time += epsilon

    return None, []
