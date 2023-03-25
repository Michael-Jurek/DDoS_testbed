# This module provides processes at the beginning and end of the program run

from app import db, bot_management
import docker, subprocess, atexit
from .settings import client


def before_first_request_funcs(app):
    @app.before_first_request
    def run_docker_compose():
        subprocess.run(["docker-compose", "up", "-d"])

    @app.before_first_request
    def create_db():
        db.create_db()
        db.victim_insert(1, 500, 'MB') # inserting default victim resources specified in docker-compose.yaml to db

def at_exit_funcs(app):
    @atexit.register
    def remove_botnet_and_compose_down():
        bot_management.remove_botnet()
        compose_down()

    def compose_down():
        subprocess.run(["docker-compose", "down"])
