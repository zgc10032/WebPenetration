import configparser
import subprocess
import os
from flask import Flask, jsonify
import requests
from app.api import api


def load_config(file_path='bin/GyoiThon/config.ini'):
    config = configparser.ConfigParser()
    config.read(file_path)
    print(config['Common']['proxy'])
    return config['Common']['proxy']


# Function to check if Python packages match requirements.txt
def check_python_packages():
    with open('requirements.txt', 'r') as f:
        requirements = f.readlines()

    installed = subprocess.run(['pip', 'freeze'], capture_output=True, text=True).stdout.splitlines()

    installed_packages = {pkg.split('==')[0]: pkg.split('==')[1] for pkg in installed}
    missing_packages = []

    for requirement in requirements:
        if '==' in requirement:
            pkg, version = requirement.strip().split('==')
            if pkg not in installed_packages or installed_packages[pkg] != version:
                missing_packages.append(requirement.strip())
        else:
            pkg = requirement.strip()
            if pkg not in installed_packages:
                missing_packages.append(requirement.strip())

    return missing_packages


# Function to check Node.js version
def check_node_version(min_version='14.0.0'):
    result = subprocess.run(['node', '--version'], capture_output=True, text=True)
    version_str = result.stdout.strip().lstrip('v')
    major_version = int(version_str.split('.')[0])
    return major_version >= int(min_version.split('.')[0])


# Function to check network connectivity
def check_network_connectivity(proxy_url=None):
    proxies = {"http": proxy_url, "https": proxy_url} if proxy_url else None
    try:
        response = requests.get('https://www.google.com', proxies=proxies, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False


@api.route('/check', methods=['GET'])
def check():
    proxy_url = load_config()

    missing_python_packages = check_python_packages()
    python_packages_ok = len(missing_python_packages) == 0
    node_version_ok = check_node_version()
    network_connectivity_ok = check_network_connectivity(proxy_url)

    status = {
        'python_packages': python_packages_ok,
        'missing_python_packages': missing_python_packages,
        'node_version': node_version_ok,
        'network_connectivity': network_connectivity_ok
    }
    return jsonify(status)