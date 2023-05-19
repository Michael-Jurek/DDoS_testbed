import sqlite3

DATABASE_FILE = "database.db"


def connect_db():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def create_db():
    with connect_db() as conn:
        conn.execute("DROP TABLE IF EXISTS bots")
        conn.execute(
            """
            CREATE TABLE bots (
                id INTEGER PRIMARY KEY,
                container_id INTEGER,
                cpu_cores INTEGER,
                memory_limit INTEGER,
                memory_unit TEXT,
                packet_loss TEXT,
                bandwidth TEXT,
                bandwidth_unit TEXT,
                delay TEXT
            )
        """
        )

        conn.execute("DROP TABLE IF EXISTS victim")
        conn.execute(
            """
            CREATE TABLE victim (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                apache_version TEXT,
                cpu_cores INTEGER,
                memory_limit INTEGER,
                memory_unit TEXT
            )
        """
        )

        conn.execute("DROP TABLE IF EXISTS icmp_flood")
        conn.execute(
            """
            CREATE TABLE icmp_flood (
                id INTEGER PRIMARY KEY,
                spoof_select TEXT,
                ip_address TEXT
            )
        """
        )

        conn.execute("DROP TABLE IF EXISTS slowloris")
        conn.execute(
            """
            CREATE TABLE slowloris (
                id INTEGER PRIMARY KEY,
                number_of_connections INTEGER,
                connection_rate INTEGER,
                attack_duration INTEGER
            )
        """
        )

        conn.execute("DROP TABLE IF EXISTS slow_read")
        conn.execute(
            """
            CREATE TABLE slow_read (
                id INTEGER PRIMARY KEY,
                number_of_connections INTEGER,
                connection_rate INTEGER,
                attack_duration INTEGER,
                request_multiplier INTEGER, 
                read_interval INTEGER,
                read_bytes INTEGER,
                window_size_start INTEGER,
                window_size_end INTEGER
            )
        """
        )


def icmp_flood_insert(spoof_select, ip_address=""):
    with connect_db() as conn:
        conn.execute("DELETE FROM icmp_flood")
        conn.execute(
            """
            INSERT INTO icmp_flood (spoof_select, ip_address)
            VALUES (?,?)
        """,
            (
                spoof_select,
                ip_address,
            ),
        )


def slowloris_insert(number_of_connections, connection_rate, attack_duration):
    with connect_db() as conn:
        conn.execute("DELETE FROM slowloris")
        conn.execute(
            """
            INSERT INTO slowloris (number_of_connections, connection_rate, attack_duration)
            VALUES (?, ?, ?)
        """,
            (number_of_connections, connection_rate, attack_duration),
        )


def slow_read_insert(
    number_of_connections,
    connection_rate,
    attack_duration,
    request_multiplier,
    read_interval,
    read_bytes,
    window_size_start,
    window_size_end,
):
    with connect_db() as conn:
        conn.execute("DELETE FROM slow_read")
        conn.execute(
            """
            INSERT INTO slow_read (number_of_connections, connection_rate, attack_duration, request_multiplier, read_interval, read_bytes, window_size_start, window_size_end)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                number_of_connections,
                connection_rate,
                attack_duration,
                request_multiplier,
                read_interval,
                read_bytes,
                window_size_start,
                window_size_end,
            ),
        )


def get_attack_args(attack_name):
    with connect_db() as conn:
        if attack_name == "icmp_flood":
            result = conn.execute("SELECT ip_address FROM icmp_flood").fetchone()
            if result:
                return result
            else:
                return None
        elif attack_name == "icmp_flood_full":
            result = conn.execute(
                "SELECT spoof_select, ip_address FROM icmp_flood"
            ).fetchone()
            if result:
                return result
            else:
                return None
        elif attack_name == "slowloris":
            result = conn.execute(
                "SELECT number_of_connections, connection_rate, attack_duration FROM slowloris"
            ).fetchone()
            if result:
                return result
            else:
                return None
        elif attack_name == "slow_read":
            result = conn.execute(
                "SELECT number_of_connections, connection_rate, attack_duration, request_multiplier, read_interval, read_bytes, window_size_start, window_size_end FROM slow_read"
            ).fetchone()
            if result:
                return result
            else:
                return None
        else:
            return None


def change_attack_duration(attack_duration):
    attacks = ["slowloris", "slow_read"]
    with connect_db() as conn:
        for attack in attacks:
            conn.execute(
                f"UPDATE {attack} SET attack_duration = ? WHERE id = 1",
                (attack_duration,),
            )


def victim_insert(apache_version, cpu_cores, memory_limit, memory_unit):
    with connect_db() as conn:
        conn.execute(
            """
            INSERT INTO victim (apache_version, cpu_cores, memory_limit, memory_unit)
            VALUES (?, ?, ?, ?)
        """,
            (apache_version, cpu_cores, memory_limit, memory_unit),
        )


def victim_update(apache_version, cpu_cores, memory_limit, memory_unit):
    with connect_db() as conn:
        conn.execute(
            """
            UPDATE victim
            SET apache_version = ?,
                cpu_cores = ?,
                memory_limit = ?,
                memory_unit = ?
            WHERE id = 1
        """,
            (apache_version, cpu_cores, memory_limit, memory_unit),
        )


def get_victim_data():
    with connect_db() as conn:
        cursor = conn.execute(
            "SELECT apache_version, cpu_cores, memory_limit, memory_unit FROM victim LIMIT 1"
        )
        row = cursor.fetchone()
        if row is None:
            return None
        else:
            return {
                "apache_version": row[0],
                "cpu_cores": row[1],
                "memory_limit": row[2],
                "memory_unit": row[3],
            }


def bot_insert(
    id,
    cpu_cores,
    memory_limit,
    memory_unit,
    packet_loss,
    bandwidth,
    bandwidth_unit,
    delay,
):
    if bandwidth == "":
        bandwidth_unit = ""
    with connect_db() as conn:
        conn.execute(
            "INSERT INTO bots (container_id, cpu_cores, memory_limit, memory_unit, packet_loss, bandwidth, bandwidth_unit, delay) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                id,
                cpu_cores,
                memory_limit,
                memory_unit,
                packet_loss,
                bandwidth,
                bandwidth_unit,
                delay,
            ),
        )
        conn.commit()


def bot_update(
    cpu_cores,
    memory_limit,
    memory_unit,
    packet_loss,
    bandwidth,
    bandwidth_unit,
    delay,
    container_id,
):
    if bandwidth == "":
        bandwidth_unit = ""
    with connect_db() as conn:
        conn.execute(
            "UPDATE bots SET cpu_cores=?, memory_limit=?, memory_unit=?, packet_loss=?, bandwidth=?, bandwidth_unit=?, delay=? WHERE container_id=?",
            (
                cpu_cores,
                memory_limit,
                memory_unit,
                packet_loss,
                bandwidth,
                bandwidth_unit,
                delay,
                container_id,
            ),
        )
        conn.commit()


def remove_bots():
    with connect_db() as conn:
        conn.execute("DELETE FROM bots")
        conn.commit()


def remove_bot(container_id):
    with connect_db() as conn:
        conn.execute("DELETE FROM bots WHERE container_id=?", (container_id,))
        conn.commit()


def get_bot_ids():
    with connect_db() as conn:
        bots = conn.execute("SELECT container_id FROM bots").fetchall()
    return bots


def get_all_bot_data():
    with connect_db() as conn:
        bots = conn.execute("SELECT * FROM bots").fetchall()
    return bots


def count_bots():
    with connect_db() as conn:
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM bots")
        result = c.fetchone()
        bot_count = result[0]
    return bot_count
