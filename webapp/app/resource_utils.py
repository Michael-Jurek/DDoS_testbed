# Conditions or calculations for system resources used for bot or victim container creation

import psutil, subprocess


def check_resources(cpu_cores_per_container, memory_limit, memory_unit):
    if (
        memory_limit < 6 and memory_unit == "MB"
    ):  # the smallest value allowed by Docker is 6MB
        return (False, "Each container has to have at least 6MB of memory.")
    available_cpu_cores = psutil.cpu_count()
    available_memory = psutil.virtual_memory().available
    if cpu_cores_per_container > available_cpu_cores:
        return (
            False,
            f"Not enough CPU cores available, your host machine has only {available_cpu_cores} cores, please select a maximum of this number.",
        )
    if available_memory < get_memory_limit(memory_limit, memory_unit):
        return (
            False,
            f"Not enough memory on host, your host machine has only {int(available_memory)/ pow(1024,3)} GB available.",
        )
    else:
        return (True, "")


def get_memory_limit(memory_limit, memory_unit):
    if memory_unit == "MB":
        memory_limit_bytes = int(memory_limit) * pow(1024, 2)
    elif memory_unit == "GB":
        memory_limit_bytes = int(memory_limit) * pow(1024, 3)
    return memory_limit_bytes
