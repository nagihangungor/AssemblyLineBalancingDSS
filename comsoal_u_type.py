import random



def comsoal_u_type(tasks: dict, precedences:dict, cycle_time:float, num_iterations=30) -> list:
    from collections import defaultdict
    """
    U-Tipi COMSOAL algoritması – hem ön hem arka atama mantığıyla.
    """

    # 🧼 1. Öncelik sözlüğünü temizle (anahtarları ve değerleri int'e çevir)
    # Tüm task anahtarlarını int'e, değerleri float'a çevir
    tasks = {int(k): float(v) for k, v in tasks.items() if isinstance(k, (str, int))}

    # Tüm precedence anahtar ve değerlerini int'e çevir
    clean_precedences = {}
    for k, v in precedences.items():
        try:
            key = int(k)
            clean_precedences[key] = [int(x) for x in v]
        except Exception as e:
            print(f"Hatalı anahtar/değer: {k}: {v} - Hata: {e}")

    # 🧼 2. Görev anahtarlarını da garanti altına al (int tipine çevir)

    best_solution = None
    best_station_count = float('inf')

    # Öncelik haritası
    all_preds = defaultdict(list)
    for task, preds in precedences.items():
        for pred in preds:
            all_preds[task].append(pred)

    for _ in range(num_iterations):
        assigned = set()
        solution = []

        while len(assigned) < len(tasks):
            B = [t for t in tasks if t not in assigned and all(p in assigned for p in all_preds[t])]
            if not B:
                break  # sonsuz döngü engellenir

            random.shuffle(B)

            station = {'front': [], 'back': []}
            front_time = 0
            back_time = 0

            for task in B[:]:  # kopya üzerinden döngü
                task_time = tasks[task]
                total_time = front_time + back_time + task_time

                if total_time <= cycle_time:
                    if front_time <= back_time:
                        station['front'].append(task)
                        front_time += task_time
                    else:
                        station['back'].append(task)
                        back_time += task_time

                    assigned.add(task)
                    B.remove(task)

            solution.append(station)

        # En iyi çözüm güncelle
        if len(solution) < best_station_count and len(assigned) == len(tasks):
            best_solution = solution
            best_station_count = len(solution)

    # 🔁 Düzleştir: front + back birleştirilmiş olarak gösterilecek
    flattened = []
    for s in best_solution:
        merged = []
        merged.extend(s.get('front', []))
        merged.extend(s.get('back', []))
        flattened.append([str(t) for t in merged])  # GUI uyumlu: ['1', '2', ...]

    return flattened
