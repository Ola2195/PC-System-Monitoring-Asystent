from app import app
import os
import json
from flask import render_template, request, redirect, url_for, flash, jsonify
from .systeminfo import *
from .database import *

def load_config():
    """
    Load the application configuration from the 'alerts_config.json' file.

    Returns:
        dict: The configuration data as a dictionary.
        If an error occurs, returns an empty dictionary.
    """
    try:
        config_path = os.path.join(os.getcwd(), 'alerts_config.json')
        with open(config_path, 'r') as file:
            config = json.load(file)
        return config
    except Exception as e:
        print(f"Error loading file alerts_config.json: {e}")
        return {}

@app.route('/api/config')
def get_config():
    """
    API route to fetch the application configuration.

    Returns:
        Response: JSON representation of the configuration.
    """
    config = load_config()
    return jsonify(config)

@app.route('/config', methods=['GET', 'POST'])
def config():
    """
    Route to view and update application configuration settings.

    Handles both GET and POST requests:
    - GET: Displays the current configuration.
    - POST: Updates the configuration file with new values.

    Returns:
        Response: Rendered HTML page for GET requests or a redirect to '/config' after POST.
    """
    config_data = load_config()

    if request.method == 'POST':
        # Update configuration with data from the form
        config_data['cpu']['danger_temp'] = int(request.form['cpu_temp_high'])
        config_data['cpu']['warning_temp'] = int(request.form['cpu_temp_warning'])
        config_data['cpu']['danger_percent'] = int(request.form['cpu_usage_high'])
        config_data['cpu']['warning_percent'] = int(request.form['cpu_usage_warning'])
        config_data['ram']['danger_percent'] = int(request.form['ram_usage_high'])
        config_data['ram']['warning_percent'] = int(request.form['ram_usage_warning'])
        config_data['battery']['danger_percent'] = int(request.form['battery_low'])
        config_data['battery']['warning_percent'] = int(request.form['battery_warning'])
        config_data['uptime']['warning_days'] = int(request.form['uptime_warning'])
        config_data['uptime']['danger_days'] = int(request.form['uptime_danger'])
        config_data['disk']['warning_percent'] = int(request.form['disk_warning'])
        config_data['disk']['danger_percent'] = int(request.form['disk_danger'])
        config_data['gpu']['warning_temp'] = int(request.form['gpu_warning'])
        config_data['gpu']['danger_temp'] = int(request.form['gpu_danger'])

        try:
            # Save updated configuration to the file
            config_path = os.path.join(os.getcwd(), 'alerts_config.json')
            with open(config_path, 'w') as file:
                json.dump(config_data, file, indent=4)
        except Exception as e:
            print(f"Error saving configuration: {e}")

        return redirect(url_for('config'))

    return render_template('config.html', config=config_data)

@app.route('/')
def index():
    """
    Route to display the main dashboard with system information.

    Returns:
        Response: Rendered HTML page for the index view.
    """
    context = {
        'platform_info': get_platform_info(),
        'user_info': get_user_info(),
        'power_info': get_power_info(),
    }
    return render_template("index.html", context=context)

@app.route('/api/index_data')
def api_index_data():
    """
    API route to fetch system information for the index page.

    Returns:
        Response: JSON representation of platform, user, and power info.
    """
    data = {
        'platform_info': get_platform_info(),
        'user_info': get_user_info(),
        'power_info': get_power_info(),
    }
    return jsonify(data)

@app.route('/cpu')
def cpu():
    """
    Route to display CPU information.

    Returns:
        Response: Rendered HTML page for CPU details.
    """
    context = {
        'cpu_info': get_cpu_info(),
    }
    return render_template("cpu.html", context=context)

@app.route('/api/cpu_data')
def api_cpu_data():
    """
    API route to fetch CPU information.

    Returns:
        Response: JSON representation of CPU details.
    """
    data = {
        'cpu_info': get_cpu_info(),
    }
    return jsonify(data)

@app.route('/ram')
def ram():
    """
    Route to display RAM (memory) information.

    Returns:
        Response: Rendered HTML page for RAM details.
    """
    context = {
        'memory_info': get_memory_info(),
    }
    return render_template("ram.html", context=context)

@app.route('/api/ram_data')
def api_ram_data():
    """
    API route to fetch RAM (memory) information.

    Returns:
        Response: JSON representation of RAM details.
    """
    data = {
        'memory_info': get_memory_info(),
    }
    return jsonify(data)

@app.route('/gpu')
def gpu():
    """
    Route to display GPU information.

    Returns:
        Response: Rendered HTML page for GPU details.
    """
    context = {
        'gpu_info': get_gpu_info(),
    }
    return render_template("gpu.html", context=context)

@app.route('/api/gpu_data')
def api_gpu_data():
    """
    API route to fetch GPU information.

    Returns:
        Response: JSON representation of GPU details.
    """
    data = {
        'gpu_info': get_gpu_info(),
    }
    return jsonify(data)

@app.route('/disks')
def disks():
    """
    Route to display disk information.

    Returns:
        Response: Rendered HTML page for disk details.
    """
    context = {
        'disk_info': get_disks_info(),
    }
    return render_template("disks.html", context=context)

@app.route('/api/disks_data')
def api_disks_data():
    """
    API route to fetch disk information.

    Returns:
        Response: JSON representation of disk details.
    """
    data = {
        'disk_info': get_disks_info(),
    }
    return jsonify(data)

@app.route('/network')
def network():
    """
    Route to display network information.

    Returns:
        Response: Rendered HTML page for network details.
    """
    context = {
        'network_info': get_network_info(),
    }
    return render_template("network.html", context=context)

@app.route('/api/network_data')
def api_network_data():
    """
    API route to fetch network information.

    Returns:
        Response: JSON representation of network details.
    """
    data = {
        'network_info': get_network_info(),
    }
    return jsonify(data)

@app.route('/api/main_data')
def api_all_data():
    """
    API route to fetch all system information and save it to the database.

    Returns:
        Response: JSON representation of all system information.
    """
    data = {
        'platform_info': get_platform_info(),
        'user_info': get_user_info(),
        'power_info': get_power_info(),
        'cpu_info': get_cpu_info(),
        'memory_info': get_memory_info(),
        'gpu_info': get_gpu_info(),
        'disk_info': get_disks_info(),
        'network_info': get_network_info(),
    }
    
    save_to_database(data)

    return jsonify(data)
