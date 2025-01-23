import psycopg2
import json

def get_db_connection():
    """
    Establishes and returns a connection to the PostgreSQL database.
    Configuration is read from db_config.json.

    Returns:
        psycopg2.extensions.connection: A connection object to the database.
    """
    # Wczytanie konfiguracji z pliku JSON
    with open("db_config.json", "r") as config_file:
        db_config = json.load(config_file)["DATABASE"]

    conn = psycopg2.connect(
        host=db_config["host"],
        database=db_config["database"],
        user=db_config["user"],
        password=db_config["password"],
        port=db_config.get("port", 5432)  # Domyślny port PostgreSQL to 5432
    )
    return conn

def get_last_record(cursor, table, columns, where_clause=None, params=None):
    """
    Retrieves the last record from the specified table, optionally with a WHERE clause.

    Args:
        cursor (psycopg2.extensions.cursor): The database cursor used to execute the query.
        table (str): The name of the table to query.
        columns (list): A list of column names to select.
        where_clause (str, optional): The WHERE condition to filter the records.
        params (tuple, optional): The parameters to bind to the WHERE clause.

    Returns:
        tuple: The last record matching the query (or None if no record found).
    """
    query = f"SELECT {', '.join(columns)} FROM {table}"
    if where_clause:
        query += f" WHERE {where_clause}"
    query += " ORDER BY id DESC LIMIT 1;"
    cursor.execute(query, params)
    return cursor.fetchone()

def has_changed(last_record, current_data, columns):
    """
    Compares the last record with the current data to determine if there has been a change.

    Args:
        last_record (tuple or None): The last record from the database.
        current_data (dict): The current data to compare with the last record.
        columns (list): The list of columns to compare.

    Returns:
        bool: True if any of the specified columns have changed, False otherwise.
    """
    if not last_record:
        return True
    for index, column in enumerate(columns):
        if current_data[column] != last_record[index]:
            return True
    return False

def insert_and_get_id(cursor, query, params):
    """
    Executes an INSERT query and returns the generated ID of the inserted record.

    Args:
        cursor (psycopg2.extensions.cursor): The database cursor used to execute the query.
        query (str): The SQL query to execute.
        params (tuple): The parameters to bind to the query.

    Returns:
        int: The ID of the newly inserted record.
    """
    cursor.execute(query, params)
    return cursor.fetchone()[0]

def save_to_database(data):
    """
    Saves system, CPU, memory, GPU, disk, network, and battery data to the database.
    The function checks if any data has changed before inserting or updating records.

    Args:
        data (dict): A dictionary containing system monitoring data, including keys like
                     'platform_info', 'cpu_info', 'memory_info', 'gpu_info', 'disk_info',
                     'network_info', and 'power_info'.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        system_data = data['platform_info']
        last_system = get_last_record(
            cursor,
            'systems',
            ['id', 'node_name', 'os_name', 'release_version', 'architecture', 'processor_type']
        )

        if has_changed(last_system, system_data, ['node_name', 'os_name', 'release_version', 'architecture', 'processor_type']):
            system_id = insert_and_get_id(cursor, """
                INSERT INTO systems (node_name, os_name, release_version, architecture, processor_type)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id;
            """, (system_data['node_name'], system_data['os_name'], system_data['release_version'],
                  system_data['architecture'], system_data['processor_type']))
        else:
            system_id = last_system[0]

        cursor.execute("""
            INSERT INTO systems_dynamic (system_id, timestamp, boot_time)
            VALUES (%s, NOW(), %s);
        """, (system_id, system_data['boot_time']))

        if 'cpu_info' in data:
            cpu_data = data['cpu_info']
            last_cpu_static = get_last_record(
                cursor,
                'cpu_static',
                ['id', 'processor_name', 'architecture', 'cpu_count', 'cpu_freq'],
                'system_id = %s',
                (system_id,)
            )

            if has_changed(last_cpu_static, cpu_data, ['processor_name', 'architecture', 'cpu_count', 'cpu_freq']):
                cpu_static_id = insert_and_get_id(cursor, """
                    INSERT INTO cpu_static (system_id, processor_name, architecture, cpu_count, cpu_freq)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id;
                """, (system_id, cpu_data['processor_name'], cpu_data['architecture'],
                      cpu_data['cpu_count'], cpu_data['cpu_freq']))
            else:
                cpu_static_id = last_cpu_static[0]

            last_cpu_dynamic = get_last_record(
                cursor,
                'cpu_dynamic',
                ['cpu_percent', 'cpu_temp', 'cpu_ctx_switches', 'cpu_interrupts', 'cpu_soft_interrupts', 'cpu_syscalls'],
                'cpu_static_id = %s',
                (cpu_static_id,)
            )

            if has_changed(last_cpu_dynamic, cpu_data, ['cpu_percent', 'cpu_temp', 'cpu_ctx_switches', 'cpu_interrupts', 'cpu_soft_interrupts', 'cpu_syscalls']):
                cursor.execute("""
                    INSERT INTO cpu_dynamic (cpu_static_id, timestamp, cpu_percent, cpu_temp, cpu_ctx_switches,
                                             cpu_interrupts, cpu_soft_interrupts, cpu_syscalls)
                    VALUES (%s, NOW(), %s, %s, %s, %s, %s, %s);
                """, (cpu_static_id, cpu_data['cpu_percent'], cpu_data['cpu_temp'],
                      cpu_data['cpu_ctx_switches'], cpu_data['cpu_interrupts'],
                      cpu_data['cpu_soft_interrupts'], cpu_data['cpu_syscalls']))

        if 'memory_info' in data:
            memory_data = data['memory_info']
            last_memory_static = get_last_record(
                cursor,
                'memory_static',
                ['id', 'total_memory', 'swap_memory'],
                'system_id = %s',
                (system_id,)
            )

            if has_changed(last_memory_static, memory_data, ['svmem_total', 'smem_total']):
                memory_static_id = insert_and_get_id(cursor, """
                    INSERT INTO memory_static (system_id, total_memory, swap_memory)
                    VALUES (%s, %s, %s)
                    RETURNING id;
                """, (system_id, memory_data['svmem_total'], memory_data['smem_total']))
            else:
                memory_static_id = last_memory_static[0]

            last_memory_dynamic = get_last_record(
                cursor,
                'memory_dynamic',
                ['used_percent', 'swap_used_percent'],
                'memory_static_id = %s',
                (memory_static_id,)
            )

            if has_changed(last_memory_dynamic, memory_data, ['svem_percent', 'smem_percent']):
                cursor.execute("""
                    INSERT INTO memory_dynamic (memory_static_id, timestamp, used_percent, swap_used_percent)
                    VALUES (%s, NOW(), %s, %s);
                """, (memory_static_id, memory_data['svem_percent'], memory_data['smem_percent']))

        if 'gpu_info' in data:
            gpu_data = data['gpu_info']
            if gpu_data['model']:
                last_gpu_static = get_last_record(
                    cursor,
                    'gpu_static',
                    ['id', 'gpu_model', 'memory_total'],
                    'system_id = %s',
                    (system_id,)
                )

                if has_changed(last_gpu_static, gpu_data, ['model', 'memory_total']):
                    gpu_static_id = insert_and_get_id(cursor, """
                        INSERT INTO gpu_static (system_id, gpu_model, memory_total)
                        VALUES (%s, %s, %s)
                        RETURNING id;
                    """, (system_id, gpu_data['model'], gpu_data['memory_total']))
                else:
                    gpu_static_id = last_gpu_static[0]

                last_gpu_dynamic = get_last_record(
                    cursor,
                    'gpu_dynamic',
                    ['gpu_usage', 'gpu_temp', 'memory_used', 'bandwidth'],
                    'gpu_static_id = %s',
                    (gpu_static_id,)
                )

                if has_changed(last_gpu_dynamic, gpu_data, ['usage', 'temp', 'memory_used', 'bandwidth']):
                    cursor.execute("""
                        INSERT INTO gpu_dynamic (gpu_static_id, timestamp, gpu_usage, gpu_temp, memory_used, bandwidth)
                        VALUES (%s, NOW(), %s, %s, %s, %s);
                    """, (gpu_static_id, gpu_data['usage'], gpu_data['temp'], gpu_data['memory_used'], gpu_data['bandwidth']))

        if 'disk_info' in data:
            for disk in data['disk_info'].values():
                last_disk_static = get_last_record(
                    cursor,
                    'disk_static',
                    ['id', 'device', 'type', 'fstype', 'total_space'],
                    'system_id = %s AND device = %s',
                    (system_id, disk['device'])
                )

                if has_changed(last_disk_static, disk, ['device', 'type', 'fstype', 'total']):
                    disk_static_id = insert_and_get_id(cursor, """
                        INSERT INTO disk_static (system_id, device, type, fstype, total_space)
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING id;
                    """, (system_id, disk['device'], disk['type'], disk['fstype'], disk['total']))
                else:
                    disk_static_id = last_disk_static[0]

                last_disk_dynamic = get_last_record(
                    cursor,
                    'disk_dynamic',
                    ['used_space', 'free_space', 'used_percentage', 'status'],
                    'disk_static_id = %s',
                    (disk_static_id,)
                )

                if has_changed(last_disk_dynamic, disk, ['used', 'free', 'used_percentage', 'status']):
                    cursor.execute("""
                        INSERT INTO disk_dynamic (disk_static_id, timestamp, used_space, free_space, used_percentage, status)
                        VALUES (%s, NOW(), %s, %s, %s, %s);
                    """, (disk_static_id, disk['used'], disk['free'], disk['used_percentage'], disk['status']))

        if 'network_info' in data:
            for network in data['network_info'].values():
                last_network_static = get_last_record(
                    cursor,
                    'network_static',
                    ['id', 'interface_name', 'ip_address'],
                    'system_id = %s AND interface_name = %s',
                    (system_id, network['name'])
                )

                if has_changed(last_network_static, network, ['name', 'ip_address']):
                    network_static_id = insert_and_get_id(cursor, """
                        INSERT INTO network_static (system_id, interface_name, ip_address)
                        VALUES (%s, %s, %s)
                        RETURNING id;
                    """, (system_id, network['name'], network['ip_address']))
                else:
                    network_static_id = last_network_static[0]

                last_network_dynamic = get_last_record(
                    cursor,
                    'network_dynamic',
                    ['sent_bytes', 'received_bytes', 'is_up', 'speed'],
                    'network_static_id = %s',
                    (network_static_id,)
                )

                if has_changed(last_network_dynamic, network, ['sent_bytes', 'received_bytes', 'is_up', 'speed']):
                    cursor.execute("""
                        INSERT INTO network_dynamic (network_static_id, timestamp, sent_bytes, received_bytes, is_up, speed)
                        VALUES (%s, NOW(), %s, %s, %s, %s);
                    """, (network_static_id, network['sent_bytes'], network['received_bytes'], network['is_up'], network['speed']))

        if 'power_info' in data:
            battery_data = data['power_info']
            last_battery_static = get_last_record(
                cursor,
                'battery_static',
                ['id'],
                'system_id = %s',
                (system_id,)
            )

            if not last_battery_static:
                battery_static_id = insert_and_get_id(cursor, """
                    INSERT INTO battery_static (system_id)
                    VALUES (%s)
                    RETURNING id;
                """, (system_id,))
            else:
                battery_static_id = last_battery_static[0]

            last_battery_dynamic = get_last_record(
                cursor,
                'battery_dynamic',
                ['battery_percent', 'time_remaining', 'power_source'],
                'battery_static_id = %s',
                (battery_static_id,)
            )

            if has_changed(last_battery_dynamic, battery_data, ['percent', 'time_remaining', 'power_source']):
                cursor.execute("""
                    INSERT INTO battery_dynamic (battery_static_id, timestamp, battery_percent, time_remaining, power_source)
                    VALUES (%s, NOW(), %s, %s, %s);
                """, (battery_static_id, battery_data['percent'], battery_data['time_remaining'], battery_data['power_source']))

        # Commit the transaction
        conn.commit()
        print("Data saved successfully!")

    except Exception as e:
        conn.rollback()
        print(f"Error saving data: {e}")
    finally:
        cursor.close()
        conn.close()
