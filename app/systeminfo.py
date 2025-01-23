import platform
import psutil
from datetime import datetime
from psutil._common import bytes2human
import GPUtil

def get_platform_info():
    """
    Retrieve general platform information.

    Returns:
        dict: Contains details about the OS, node name, system name,
              release version, architecture, processor type, and boot time.
    """
    uname = platform.uname()
    boot_time = psutil.boot_time()
    if psutil.MACOS:
        os_name = 'apple'
    elif psutil.WINDOWS:
        os_name = 'windows'
    elif psutil.LINUX:
        os_name = 'linux'
    else:
        os_name = 'Unknown'

    platform_info = {
        'os_name': os_name,
        'node_name': uname.node,
        'system_name': uname.system,
        'release_version': uname.release,
        'architecture': platform.architecture()[0],
        'processor_type': platform.processor(),
        'boot_time': str(datetime.now() - datetime.fromtimestamp(boot_time)),
    }

    return platform_info

def get_power_info():
    """
    Retrieve battery and power information.

    Returns:
        dict: Contains battery percentage, time remaining, and power source.
    """
    power_data = psutil.sensors_battery()

    if power_data.secsleft in (psutil.POWER_TIME_UNKNOWN, psutil.POWER_TIME_UNLIMITED):
        time_remaining = 'Calculating'
    else:
        time_remaining = str(round(power_data.secsleft / 3600, 2)) + ' hrs'

    power_info = {
        'percent': int(power_data.percent),
        'time_remaining': time_remaining,
        'power_source': 'AC Power' if power_data.power_plugged else 'Battery Power'
    }
    
    return power_info    

def get_user_info():
    """
    Retrieve information about logged-in users.

    Returns:
        dict: Contains details about each user, including name, terminal,
              host, session start time, and process ID (PID).
    """
    user_data = psutil.users()
    user_info = {}

    for count, user in enumerate(user_data):
        user_info[count] = {
            'name': user.name, 
            'terminal': user.terminal, 
            'host': user.host, 
            'started': datetime.fromtimestamp(user.started).strftime('%Y-%m-%d %H:%M:%S'),
            'pid': user.pid,
        }

    return user_info

def get_memory_info():
    """
    Retrieve information about system memory (RAM and swap).

    Returns:
        dict: Contains total and percentage usage for both virtual and swap memory.
    """
    vmemory_data = psutil.virtual_memory()
    smemory_data = psutil.swap_memory()

    memory_data = {
        'svmem_total': bytes2human(vmemory_data.total),
        'svem_percent': vmemory_data.percent,
        'smem_total': bytes2human(smemory_data.total),
        'smem_percent': smemory_data.percent
    }
    
    return memory_data

def get_cpu_info():
    """
    Retrieve detailed information about the CPU.

    Returns:
        dict: Contains CPU name, architecture, usage percentage, core count,
              frequency, context switches, interrupts, syscall count, and temperature.
    """
    cpu_temp = None
    if hasattr(psutil, "sensors_temperatures"):
        temps = psutil.sensors_temperatures()
        if "coretemp" in temps:
            cpu_temp = temps["coretemp"][0].current   

    cpu_data = {
        'processor_name': platform.processor(),
        'architecture': platform.architecture()[0],
        'cpu_percent': psutil.cpu_percent(interval=1),
        'cpu_count': psutil.cpu_count(logical=False),
        'cpu_freq': psutil.cpu_freq().current,
        'cpu_ctx_switches': psutil.cpu_stats().ctx_switches,
        'cpu_interrupts': psutil.cpu_stats().interrupts,
        'cpu_soft_interrupts': psutil.cpu_stats().soft_interrupts,
        'cpu_syscalls': psutil.cpu_stats().syscalls,
        'cpu_times': psutil.cpu_times(),
        'cpu_temp': cpu_temp,
    }

    return cpu_data

def get_gpu_info():
    """
    Retrieve detailed information about the GPU.

    Returns:
        dict: Contains GPU model, usage, temperature, memory usage,
              total memory, and bandwidth utilization.
    """
    gpus = GPUtil.getGPUs()
    gpu_data = {
        'model': None,
        'usage': 0,
        'temp': None,
        'memory_used': 0,
        'memory_total': 0,
        'bandwidth': 0
    }

    if gpus:
        gpu = gpus[0]
        gpu_data = {
            'model': gpu.name,
            'usage': gpu.load * 100,
            'temp': gpu.temperature,
            'memory_used': gpu.memoryUsed,
            'memory_total': gpu.memoryTotal,
            'bandwidth': gpu.memoryUtil * 100 
        }

    return gpu_data

def get_disks_info():
    """
    Retrieve information about system disks.

    Returns:
        dict: Contains details about each disk, including device name,
              mount point, type, file system, usage statistics, and status.
    """
    disk_data = {}
    disk_partitions = psutil.disk_partitions(all=False)
    for counter, partition in enumerate(disk_partitions):
        try:
            usage_data = psutil.disk_usage(partition.mountpoint)
            disk_type = 'Zewnętrzny' if 'removable' in partition.opts else 'Wbudowany'
            disk_data[counter] = {
                'device': partition.device,
                'mounted': partition.mountpoint,
                'type': disk_type,
                'fstype': partition.fstype,
                'total': bytes2human(usage_data.total),
                'used': bytes2human(usage_data.used),
                'free': bytes2human(usage_data.free),
                'used_percentage': round((usage_data.used / usage_data.total) * 100, 2),
                'status': "Online"
            }
        except PermissionError:
            disk_data[counter] = {
                'device': partition.device,
                'mounted': None,
                'type': None,
                'fstype': None,
                'total': None,
                'used': None,
                'free': None,
                'used_percentage': None,
                'status': "Offline",
                'message': "Niedostępny"
            }
        except Exception as e:
            disk_data[counter] = {
                'device': partition.device,
                'mounted': None,
                'type': None,
                'fstype': None,
                'total': None,
                'used': None,
                'free': None,
                'used_percentage': None,
                'status': "Error",
                'message': "Błąd dysku"
            }
    return disk_data

def get_network_info():
    """
    Retrieve information about network interfaces.

    Returns:
        dict: Contains details about each network interface, including
              IP address, status, speed, and data sent/received.
    """
    network_data = {}
    if_addrs = psutil.net_if_addrs()
    io_counter = psutil.net_io_counters(pernic=True)
    if_stats = psutil.net_if_stats()

    for interface_name, interface_addresses in if_addrs.items():
        for address in interface_addresses:
            if int(address.family) == 2:  # IPv4 addresses only
                if interface_name in io_counter:
                    io = io_counter[interface_name]
                    stats = if_stats[interface_name]
                    network_data[interface_name] = {
                        'name': interface_name,
                        'ip_address': address.address,
                        'is_up': stats.isup,
                        'speed': stats.speed,
                        'sent_bytes': bytes2human(io.bytes_sent),
                        'received_bytes': bytes2human(io.bytes_recv),
                    }

    return network_data
