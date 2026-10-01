from datetime import datetime
import json
import platform
import psutil

def get_size(bytes, suffix="Б"):
    factor = 1024
    for unit in ["", "К", "М", "Г", "Т", "П"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor

system_info = {}
boot_time_timestamp = psutil.boot_time()
bt = datetime.fromtimestamp(boot_time_timestamp)
uptime = datetime.now() - bt

system_info["время"] = {
    "время_запуска": bt.strftime('%Y-%m-%d %H:%M:%S'),
    "время_работы": str(uptime).split('.')
}

uname = platform.uname()
system_info["система"] = {
    "ось": uname.system,
    "имя_узла": uname.node,
    "выпуск": uname.release,
    "версия": uname.version,
    "архитектура": uname.machine,
    "процессор": uname.processor
}

cpufreq = psutil.cpu_freq()
system_info["процессор"] = {
    "физические_ядра": psutil.cpu_count(logical=False),
    "всего_ядер": psutil.cpu_count(logical=True),
    "макс_частота_мгц": f"{cpufreq.max:.2f}" if cpufreq else "Н/Д",
    "мин_частота_мгц": f"{cpufreq.min:.2f}" if cpufreq else "Н/Д",
    "текущая_частота_мгц": f"{cpufreq.current:.2f}" if cpufreq else "Н/Д"
}

svmem = psutil.virtual_memory()
system_info["память"] = {
    "объем": get_size(svmem.total),
    "доступно": get_size(svmem.available),
    "используется": get_size(svmem.used),
    "процент": svmem.percent
}

system_info["диски"] = []
partitions = psutil.disk_partitions()
for partition in partitions:
    disk_data = {
        "устройство": partition.device,
        "тип_файловой_системы": partition.fstype,
        "общий_объем": "Н/Д",
        "используется": "Н/Д",
        "свободно": "Н/Д",
        "процент": "Н/Д"
    }
    try:
        partition_usage = psutil.disk_usage(partition.mountpoint)
        disk_data["общий_объем"] = get_size(partition_usage.total)
        disk_data["используется"] = get_size(partition_usage.used)
        disk_data["свободно"] = get_size(partition_usage.free)
        disk_data["процент"] = partition_usage.percent
    except PermissionError:
        pass

    system_info["диски"].append(disk_data)

battery = psutil.sensors_battery()
if battery:
    system_info["батарея"] = {
        "есть_батарея": True,
        "процент": battery.percent,
        "устройство_заряжается": battery.power_plugged
    }
else:
    system_info["батарея"] = {"есть_батарея": False}

file_name = "system_info.json"
with open(file_name, "w", encoding="utf-8") as f:
    json.dump(system_info, f, ensure_ascii=False, indent=4)

print(f"Результат: {file_name}")