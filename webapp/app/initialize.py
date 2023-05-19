# This module provides processes at the beginning and end of the program run

from app import db, bot_management, victim
import docker, subprocess, atexit, os, socket, resource
from .settings import client


def before_first_request_funcs(app):
    @app.before_first_request
    def run_docker_compose():
        os.chdir("configurations")
        subprocess.run(["docker-compose", "up", "-d"])

    @app.before_first_request
    def set_resource_limit():
        soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
        if soft < 5000:
            resource.setrlimit(resource.RLIMIT_NOFILE, (5000, hard))

    @app.before_first_request
    def create_db():
        db.create_db()
        db.victim_insert(
            "2.2.34", 1, 500, "MB"
        )  # inserting default victim resources specified in docker-compose.yaml to db
        db.icmp_flood_insert("no")
        db.slowloris_insert(50, 50, 30)
        db.slow_read_insert(50, 50, 30, 1, 1, 5, 1, 512)


def at_exit_funcs(app):
    @atexit.register
    def remove_botnet_and_compose_down():
        bot_management.remove_botnet()
        victim.remove()
        compose_down()

    def compose_down():
        subprocess.run(["docker-compose", "down"])
