from app import resource_utils, db
from .settings import client
from flask import redirect
import os, docker


def edit_victim(apache_version, victim_cpu_cores, victim_memory_limit, memory_unit):
    memory_limit_bytes = resource_utils.get_memory_limit(
        victim_memory_limit, memory_unit
    )
    actual_apache_version = get_actual_image()
    victim_config = get_victim_config(
        apache_version, actual_apache_version, victim_cpu_cores, memory_limit_bytes
    )
    victim = client.containers.get("victim")

    if "httpd:" + apache_version != actual_apache_version:
        remove()
        new_victim = client.containers.run(**victim_config)

    else:
        victim.update(**victim_config)
    db.victim_update(apache_version, victim_cpu_cores, victim_memory_limit, memory_unit)
    return "Victim edited successfully"


def get_victim_config(
    apache_version, actual_apache_version, cpu_cores, memory_limit_bytes
):
    if "httpd:" + apache_version != actual_apache_version:
        httpd_conf_path = os.path.abspath(
            f"./apache_configs/httpd_{apache_version}.conf"
        )
        victim_config = {
            "name": "victim",
            "image": "httpd:" + apache_version,
            "network": "testbed",
            "mem_limit": str(memory_limit_bytes) + "b",
            "memswap_limit": memory_limit_bytes,
            "cpu_period": 100000,
            "cpu_quota": int(cpu_cores * 100000),
            "restart_policy": {"Name": "always"},
            "ports": {"80/tcp": 80},
            "volumes": {
                httpd_conf_path: {"bind": "/usr/local/apache2/conf/httpd.conf"}
            },
            "detach": True,
        }
    else:
        victim_config = {
            "mem_limit": str(memory_limit_bytes) + "b",
            "memswap_limit": memory_limit_bytes,
            "cpu_period": 100000,
            "cpu_quota": int(cpu_cores * 100000),
        }
    return victim_config


def remove():
    try:
        victim = client.containers.get("victim")
        if victim.status == "running":
            victim.kill()
            victim.wait()
        victim.remove()
        victim.wait()
    except docker.errors.NotFound:
        pass


def get_actual_image():
    try:
        victim = client.containers.get("victim")
    except docker.errors.NotFound:
        return None

    actual_image = victim.attrs["Config"]["Image"]
    return actual_image
