CREATE DATABASE system_monitoring;

CREATE TABLE systems (
    id SERIAL PRIMARY KEY,
    node_name VARCHAR(100) NOT NULL,
    os_name VARCHAR(100) NOT NULL,
    release_version VARCHAR(20),
    architecture VARCHAR(20),
    processor_type VARCHAR(100)
);

CREATE TABLE systems_dynamic (
    id SERIAL PRIMARY KEY,
    system_id INT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    boot_time INTERVAL,
    FOREIGN KEY (system_id) REFERENCES systems(id) ON DELETE CASCADE
);

CREATE TABLE cpu_static (
    id SERIAL PRIMARY KEY,
    system_id INT NOT NULL,
    processor_name VARCHAR(100),
    architecture VARCHAR(20),
    cpu_count SMALLINT,
    cpu_freq DECIMAL(6,2),
    FOREIGN KEY (system_id) REFERENCES systems(id) ON DELETE CASCADE
);

CREATE TABLE cpu_dynamic (
    id SERIAL PRIMARY KEY,
    cpu_static_id INT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    cpu_percent DECIMAL(5,2),
    cpu_temp DECIMAL(5,2),
    cpu_ctx_switches BIGINT,
    cpu_interrupts BIGINT,
    cpu_soft_interrupts BIGINT,
    cpu_syscalls BIGINT,
    FOREIGN KEY (cpu_static_id) REFERENCES cpu_static(id) ON DELETE CASCADE
);

CREATE TABLE gpu_static (
    id SERIAL PRIMARY KEY,
    system_id INT NOT NULL,
    gpu_model VARCHAR(50),
    memory_total INT,
    FOREIGN KEY (system_id) REFERENCES systems(id) ON DELETE CASCADE
);

CREATE TABLE gpu_dynamic (
    id SERIAL PRIMARY KEY,
    gpu_static_id INT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    gpu_usage DECIMAL(5,2),
    gpu_temp DECIMAL(5,2),
    memory_used INT,
    bandwidth DECIMAL(6,2),
    FOREIGN KEY (gpu_static_id) REFERENCES gpu_static(id) ON DELETE CASCADE
);

CREATE TABLE memory_static (
    id SERIAL PRIMARY KEY,
    system_id INT NOT NULL,
    total_memory VARCHAR(20),
    swap_memory VARCHAR(20),
    FOREIGN KEY (system_id) REFERENCES systems(id) ON DELETE CASCADE
);

CREATE TABLE memory_dynamic (
    id SERIAL PRIMARY KEY,
    memory_static_id INT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    used_percent DECIMAL(5,2),
    swap_used_percent DECIMAL(5,2),
    FOREIGN KEY (memory_static_id) REFERENCES memory_static(id) ON DELETE CASCADE
);

CREATE TABLE disk_static (
    id SERIAL PRIMARY KEY,
    system_id INT NOT NULL,
    device VARCHAR(50),
    type VARCHAR(20),
    fstype VARCHAR(20),
    total_space VARCHAR(20),
    FOREIGN KEY (system_id) REFERENCES systems(id) ON DELETE CASCADE
);

CREATE TABLE disk_dynamic (
    id SERIAL PRIMARY KEY,
    disk_static_id INT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    used_space VARCHAR(20),
    free_space VARCHAR(20),
    used_percentage DECIMAL(5,2),
    status VARCHAR(20),
    FOREIGN KEY (disk_static_id) REFERENCES disk_static(id) ON DELETE CASCADE
);

CREATE TABLE network_static (
    id SERIAL PRIMARY KEY,
    system_id INT NOT NULL,
    interface_name VARCHAR(50),
    ip_address VARCHAR(39),
    FOREIGN KEY (system_id) REFERENCES systems(id) ON DELETE CASCADE
);

CREATE TABLE network_dynamic (
    id SERIAL PRIMARY KEY,
    network_static_id INT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    sent_bytes VARCHAR(20),
    received_bytes VARCHAR(20),
    is_up BOOLEAN,
    speed INT,
    FOREIGN KEY (network_static_id) REFERENCES network_static(id) ON DELETE CASCADE
);

CREATE TABLE battery_static (
    id SERIAL PRIMARY KEY,
    system_id INT NOT NULL,
    FOREIGN KEY (system_id) REFERENCES systems(id) ON DELETE CASCADE
);

CREATE TABLE battery_dynamic (
    id SERIAL PRIMARY KEY,
    battery_static_id INT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    battery_percent DECIMAL(5,2),
    time_remaining VARCHAR(20),
    power_source VARCHAR(20),
    FOREIGN KEY (battery_static_id) REFERENCES bat-tery_static(id) ON DELETE CASCADE
);

CREATE TABLE user_sessions (
    id SERIAL PRIMARY KEY,
    system_id INT NOT NULL,
    name VARCHAR(50),
    terminal VARCHAR(50),
    host VARCHAR(50),
    started TIMESTAMP,
    pid INT,
    FOREIGN KEY (system_id) REFERENCES systems(id) ON DELETE CASCADE
);