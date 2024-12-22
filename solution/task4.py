def pipeline():

    try:
        n = int(input("Введите количество станков: "))
        stages = []
        for i in range(n):
            stage_time = int(input(f"Введите время обработки на станке {i + 1}: "))
            stages.append(stage_time)

        m = int(input("Введите количество деталей: "))
        details = []
        for i in range(m):
            detail_time = int(input(f"Введите время поступления детали {i + 1}: "))
            details.append(detail_time)

        completion_times = calculate_completion_times(stages, details)
        print("Времена завершения обработки деталей:")
        for i, time in enumerate(completion_times):
            print(f"Деталь {i + 1}: {time}")
    except ValueError:
        print("Ошибка: Пожалуйста, вводите целые числа.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")


def calculate_completion_times(stages, details):
    n = len(stages)
    m = len(details)
    completion_times = [0] * m
    machine_available_times = [0] * n

    for detail_idx in range(m):
        start_time = details[detail_idx]

        for stage_idx in range(n):

            start_time = max(start_time, machine_available_times[stage_idx])

            finish_time = start_time + stages[stage_idx]


            machine_available_times[stage_idx] = finish_time


            start_time = finish_time

        completion_times[detail_idx] = finish_time

    return completion_times


if __name__ == "__main__":
    pipeline()