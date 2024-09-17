import subprocess
import datetime
import re


def parse_ps_output(output):
    lines = output.strip().split('\n')
    users = set()
    process_count = len(lines) - 1
    user_processes = {}
    total_memory = 0.0
    total_cpu = 0.0
    max_memory_process = ("", 0.0)
    max_cpu_process = ("", 0.0)

    for line in lines[1:]:
        parts = re.split(r'\s+', line)
        if len(parts) < 11:
            continue
        user = parts[0]
        cpu = float(parts[2])
        memory = float(parts[3])
        command = ' '.join(parts[10:])

        users.add(user)
        user_processes[user] = user_processes.get(user, 0) + 1
        total_memory += memory
        total_cpu += cpu

        if memory > max_memory_process[1]:
            max_memory_process = (command[:20], memory)

        if cpu > max_cpu_process[1]:
            max_cpu_process = (command[:20], cpu)

    return {"users": users,
            "process_count": process_count,
            "user_processes": user_processes,
            "total_memory": total_memory,
            "total_cpu": total_cpu,
            "max_memory_process": max_memory_process,
            "max_cpu_process": max_cpu_process}


def main():
    result = subprocess.run(['ps', 'aux'], stdout=subprocess.PIPE, text=True)
    output = result.stdout

    stats = parse_ps_output(output)

    now = datetime.datetime.now()
    filename = now.strftime("%d-%m-%Y-%H:%M-scan.txt")

    report = f"Отчёт о состоянии системы:\n"
    report += f"Пользователи системы: {', '.join(stats['users'])}\n"
    report += f"Процессов запущено: {stats['process_count']}\n\n"

    report += "Пользовательских процессов:\n"
    for user, count in stats["user_processes"].items():
        report += f"{user}: {count}\n"

    report += f"\nВсего памяти используется: {stats['total_memory']:.1f}%\n"
    report += f"Всего CPU используется: {stats['total_cpu']:.1f}%\n"
    report += (
        f"Больше всего памяти использует: ({stats['max_memory_process'][0]}, {stats['max_memory_process'][1]:.1f}"
        f"%)\n")
    report += f"Больше всего CPU использует: ({stats['max_cpu_process'][0]}, {stats['max_cpu_process'][1]:.1f}%)\n"

    print(report)

    with open(filename, 'w', encoding='utf-8') as file:
        file.write(report)


if __name__ == "__main__":
    main()
