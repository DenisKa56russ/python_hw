from datetime import datetime


def process_logs(logs: list[str]) -> tuple[int, list[str], list[int], list[int], list[set[str]]]:

    player_names = []
    player_online_times = {}
    player_block_counts = {}
    player_achievements = {}
    total_blocks_placed = 0
    player_last_connected = {}

    for log_entry in logs:
        parts = log_entry.split("] ", 1)
        timestamp_str, rest = parts[0][1:], parts[1]
        timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")

        player_name_part, event_part = rest.split(": ", 1)
        player_name = player_name_part.strip()
        event_parts = event_part.split(" ")
        event_name = event_parts[0]
        args = event_parts[1:] if len(event_parts) > 1 else []

        if player_name not in player_names:
            player_names.append(player_name)
            player_online_times[player_name] = 0
            player_block_counts[player_name] = 0
            player_achievements[player_name] = set()

        if event_name == "connected":
            player_last_connected[player_name] = timestamp
        elif event_name == "disconnected":
            if player_name in player_last_connected:
                time_online = (timestamp - player_last_connected[player_name]).total_seconds()
                player_online_times[player_name] += int(time_online)
                del player_last_connected[player_name]
        elif event_name == "block_placed":
            total_blocks_placed += 1
            player_block_counts[player_name] += 1
        elif event_name == "achivement_unlocked":
            achievement_name = " ".join(args)
            player_achievements[player_name].add(achievement_name)

    player_online_times_list = [player_online_times[name] for name in player_names]
    player_block_counts_list = [player_block_counts[name] for name in player_names]
    player_achievements_list = [player_achievements[name] for name in player_names]

    return total_blocks_placed, player_names, player_online_times_list, player_block_counts_list, player_achievements_list


if __name__ == '__main__':
    print(
        "Введите строки логов, по одной на строке. Для завершения ввода нажмите Ctrl+D (или Ctrl+Z, затем Enter на Windows):")
    logs = []
    try:
        while True:
            line = input()
            logs.append(line)
    except EOFError:
        pass

    total_blocks, players, online_times, block_counts, achievements = process_logs(logs)

    print("Результат:")
    print("(")
    print("   ", total_blocks, ",")
    print("   ", players, ",")
    print("   ", online_times, ",")
    print("   ", block_counts, ",")
    print("   ", achievements)
    print(")")