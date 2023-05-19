from flask import render_template, request, jsonify
import docker, sqlite3
from app import app, db, bot_management, attacks, resource_utils, victim
from .settings import client


@app.route("/")
def index():
    victim_data = db.get_victim_data()
    slowloris_data = db.get_attack_args("slowloris")
    slow_read_data = db.get_attack_args("slow_read")
    icmp_flood_data = db.get_attack_args("icmp_flood_full")
    return render_template(
        "index.html",
        victim_data=victim_data,
        slow_read_data=slow_read_data,
        slowloris_data=slowloris_data,
        icmp_flood_data=icmp_flood_data,
    )


@app.route("/generate_botnet", methods=["POST", "GET"])
def generate_botnet():
    bots_number = int(request.form["bots_number"])
    cpu_cores_per_container = float(request.form["cpu_cores_per_container"])
    memory_limit = int(request.form["memory_limit"])
    memory_unit = request.form["memory_unit"]
    packet_loss = request.form.get("packet_loss")
    bandwidth = request.form.get("bandwidth")
    bandwidth_unit = request.form.get("bandwidth_unit")
    delay = request.form.get("delay")

    resource_check, message = resource_utils.check_resources(
        cpu_cores_per_container, memory_limit, memory_unit
    )
    if not resource_check:
        return message
    return bot_management.create_containers(
        bots_number,
        cpu_cores_per_container,
        memory_limit,
        memory_unit,
        packet_loss,
        bandwidth,
        bandwidth_unit,
        delay,
    )


@app.route("/remove_botnet")
def remove_botnet():
    return bot_management.remove_botnet()


@app.route("/remove_bot", methods=["POST"])
def remove_bot():
    bot_id = request.form.get("container_id")
    return bot_management.remove_bot(bot_id)


@app.route("/icmp_flood", methods=["POST"])
def icmp_flood():
    spoof = request.form.get("spoof_select")
    if spoof == "yes":
        ip_address = request.form["ip_address"]
        db.icmp_flood_insert(spoof, ip_address)
    else:
        db.icmp_flood_insert(spoof)
    return "nothing"


@app.route("/slowloris", methods=["POST"])
def slowloris():
    number_of_connections = int(request.form["number_of_connections"])
    connection_rate = int(request.form["connection_rate"])
    attack_duration = int(request.form["attack_duration"])
    db.slowloris_insert(number_of_connections, connection_rate, attack_duration)
    return "nothing"


@app.route("/slow_read", methods=["POST"])
def slowl_read():
    number_of_connections = int(request.form["number_of_connections"])
    connection_rate = int(request.form["connection_rate"])
    attack_duration = int(request.form["attack_duration"])
    request_multiplier = int(request.form["request_multiplier"])
    read_interval = int(request.form["read_interval"])
    read_bytes = int(request.form["read_bytes"])
    window_size_start = int(request.form["window_size_start"])
    window_size_end = int(request.form["window_size_end"])
    db.slow_read_insert(
        number_of_connections,
        connection_rate,
        attack_duration,
        request_multiplier,
        read_interval,
        read_bytes,
        window_size_start,
        window_size_end,
    )

    return "nothing"


@app.route("/execute_attacks", methods=["POST", "GET"])
def execute_attacks():
    icmp_flood_bot_count = int(request.form["icmp_flood_bot_count"])
    slowloris_bot_count = int(request.form["slowloris_bot_count"])
    slow_read_bot_count = int(request.form["slow_read_bot_count"])
    attack_duration = int(request.form["attack_duration"])
    attack_info = {
        "icmp_flood": {
            "bots": icmp_flood_bot_count,
        },
        "slowloris": {
            "bots": slowloris_bot_count,
        },
        "slow_read": {
            "bots": slow_read_bot_count,
        },
    }
    db.change_attack_duration(attack_duration)
    attacks.execute_attacks(attack_info, attack_duration)
    return "nothing"


@app.route("/show_botnet")
def show_botnet():
    bot_data = db.get_all_bot_data()
    return render_template("show_botnet.html", bot_data=bot_data)


@app.route("/stop_attack")
def stop_attack():
    attacks.execute_attack(attacks.stop_attack)
    return "nothing"


@app.route("/edit_victim", methods=["POST", "GET"])
def edit_victim():
    apache_version = request.form["apache_version"]
    victim_cpu_cores = float(request.form["victim_cpu_cores"])
    victim_memory_limit = int(request.form["victim_memory_limit"])
    memory_unit = request.form["memory_unit"]
    resource_check, message = resource_utils.check_resources(
        victim_cpu_cores, victim_memory_limit, memory_unit
    )
    if not resource_check:
        return message
    return victim.edit_victim(
        apache_version, victim_cpu_cores, victim_memory_limit, memory_unit
    )


@app.route("/victim_data")
def victim_data():
    victim_data = db.get_victim_data()
    return jsonify(victim_data=victim_data)


@app.route("/count_bots", methods=["GET", "POST"])
def count_bots():
    bot_count = db.count_bots()
    return str(bot_count)


@app.route("/show_bot_count")
def show_bot_count():
    show_bot_count = db.count_bots()
    return jsonify(show_bot_count=show_bot_count)


@app.route("/limit_network_all", methods=["GET", "POST"])
def limit_network_all():
    if request.method == "POST":
        packet_loss = request.form.get("packet_loss")
        bandwidth = request.form.get("bandwidth")
        bandwidth_unit = request.form.get("bandwidth_unit")
        delay = request.form.get("delay")
    return "nothing"


@app.route("/edit_all_bots", methods=["POST", "GET"])
def edit_all_bots():
    cpu_cores_per_container = float(request.form["cpu_cores_per_container"])
    memory_limit = int(request.form["memory_limit"])
    memory_unit = request.form["memory_unit"]
    packet_loss = request.form.get("packet_loss")
    bandwidth = request.form.get("bandwidth")
    bandwidth_unit = request.form.get("bandwidth_unit")
    delay = request.form.get("delay")

    resource_check, message = resource_utils.check_resources(
        cpu_cores_per_container, memory_limit, memory_unit
    )
    if not resource_check:
        return message
    return bot_management.edit_all_bots(
        cpu_cores_per_container,
        memory_limit,
        memory_unit,
        packet_loss,
        bandwidth,
        bandwidth_unit,
        delay,
    )


@app.route("/edit_bot", methods=["POST", "GET"])
def edit_bot():
    container_id = request.form["container_id"]
    cpu_cores_per_container = float(request.form["cpu_cores_per_container"])
    memory_limit = int(request.form["memory_limit"])
    memory_unit = request.form["memory_unit"]
    packet_loss = request.form.get("packet_loss")
    bandwidth = request.form.get("bandwidth")
    bandwidth_unit = request.form.get("bandwidth_unit")
    delay = request.form.get("delay")

    resource_check, message = resource_utils.check_resources(
        cpu_cores_per_container, memory_limit, memory_unit
    )
    if not resource_check:
        return message
    return bot_management.edit_bot(
        container_id,
        cpu_cores_per_container,
        memory_limit,
        memory_unit,
        packet_loss,
        bandwidth,
        bandwidth_unit,
        delay,
    )
