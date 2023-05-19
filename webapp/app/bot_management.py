import docker
from flask import request
from app import db, resource_utils
from .settings import client


def create_containers(
    bots_number,
    cpu_cores,
    memory_limit,
    memory_unit,
    packet_loss,
    bandwidth,
    bandwidth_unit,
    delay,
):
    memory_limit_bytes = resource_utils.get_memory_limit(memory_limit, memory_unit)
    container_config = get_container_config(
        cpu_cores, memory_limit_bytes, packet_loss, bandwidth, bandwidth_unit, delay
    )
    for i in range(bots_number):
        container = client.containers.run(**container_config)
        db.bot_insert(
            container.id,
            cpu_cores,
            memory_limit,
            memory_unit,
            packet_loss,
            bandwidth,
            bandwidth_unit,
            delay,
        )
    return "Bots created successfully"


def get_container_config(
    cpu_cores, memory_limit_bytes, packet_loss, bandwidth, bandwidth_unit, delay
):
    command = f"{get_tc_command(packet_loss, bandwidth, bandwidth_unit, delay)} && sleep infinity"

    container_config = {
        "image": "kralluk/ubuntu_for_ddos:v1.2",
        "entrypoint": ["/bin/bash", "-c"],
        "command": [command],
        "network": "testbed",
        "mem_limit": str(memory_limit_bytes) + "b",
        "memswap_limit": memory_limit_bytes,
        "cpu_period": 100000,
        "cpu_quota": int(cpu_cores * 100000),
        "cap_add": "NET_ADMIN",
        "detach": True,
    }

    return container_config


def get_container_edit_config(
    cpu_cores, memory_limit_bytes, packet_loss, bandwidth, bandwidth_unit, delay
):
    container_config = {
        "mem_limit": str(memory_limit_bytes) + "b",
        "memswap_limit": memory_limit_bytes,
        "cpu_period": 100000,
        "cpu_quota": int(cpu_cores * 100000),
    }

    return container_config


def edit_all_bots(
    cpu_cores, memory_limit, memory_unit, packet_loss, bandwidth, bandwidth_unit, delay
):
    memory_limit_bytes = resource_utils.get_memory_limit(memory_limit, memory_unit)

    bots = db.get_bot_ids()
    command = f"{get_tc_command(packet_loss, bandwidth, bandwidth_unit, delay)}"
    edited_config = get_container_edit_config(
        cpu_cores,
        memory_limit_bytes,
        packet_loss,
        bandwidth,
        bandwidth_unit,
        delay,
    )
    for i in bots:
        container = client.containers.get(i["container_id"])
        container.update(**edited_config)
        container.exec_run(
            "tc qdisc del dev eth0 root"
        )  # deleting old network configuration
        container.exec_run(command)
        db.bot_update(
            cpu_cores,
            memory_limit,
            memory_unit,
            packet_loss,
            bandwidth,
            bandwidth_unit,
            delay,
            i["container_id"],
        )
    return "Botnet edited"


def edit_bot(
    container_id,
    cpu_cores,
    memory_limit,
    memory_unit,
    packet_loss,
    bandwidth,
    bandwidth_unit,
    delay,
):
    memory_limit_bytes = resource_utils.get_memory_limit(memory_limit, memory_unit)

    command = f"{get_tc_command(packet_loss, bandwidth, bandwidth_unit, delay)}"
    edited_config = get_container_edit_config(
        cpu_cores,
        memory_limit_bytes,
        packet_loss,
        bandwidth,
        bandwidth_unit,
        delay,
    )

    container = client.containers.get(container_id)
    container.update(**edited_config)
    container.exec_run(
        "tc qdisc del dev eth0 root"
    )  # deleting old network configuration
    container.exec_run(command)
    db.bot_update(
        cpu_cores,
        memory_limit,
        memory_unit,
        packet_loss,
        bandwidth,
        bandwidth_unit,
        delay,
        container_id,
    )
    return "Bot edited"


def remove_botnet():
    bots = db.get_bot_ids()
    for i in bots:
        try:
            container = client.containers.get(i["container_id"])
            container.kill()
            container.remove()
        except docker.errors.DockerException as ex:
            print("Error")
    db.remove_bots()
    return "nothing"


def remove_bot(container_id):
    try:
        container = client.containers.get(container_id)
        container.kill()
        container.remove()
    except docker.errors.DockerException as ex:
        print("Error")
    db.remove_bot(container_id)
    return "nothing"


def get_tc_command(packet_loss, bandwidth, bandwidth_unit, delay):
    tc_command = "tc qdisc add dev eth0 root netem"
    if packet_loss:
        tc_command += f" loss {packet_loss}%"
    if bandwidth:
        if bandwidth_unit == "MB":
            bandwidth = f"{float(bandwidth) * 1000000}bps"
        elif bandwidth_unit == "KB":
            bandwidth = f"{float(bandwidth) * 1000}bps"
        elif bandwidth_unit == "GB":
            bandwidth = f"{float(bandwidth) * 1000000000}bps"
        tc_command += f" rate {bandwidth}"
    if delay:
        tc_command += f" delay {delay}ms"

    return tc_command
