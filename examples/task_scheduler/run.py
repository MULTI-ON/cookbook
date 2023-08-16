#!/usr/bin/env python3

import os
import platform
import subprocess


def run_script_in_background():
    script_path = "scheduler_application.py"
    os_type = platform.system()

    if os_type == "Linux" or os_type == "Darwin":  # For Linux and Mac
        command = f"nohup python3 {script_path} &"
        process = subprocess.Popen(command, shell=True)
        print(f"Script {script_path} started in background with PID {process.pid}")

    elif os_type == "Windows":  # For Windows
        command = f"start python {script_path}"
        subprocess.Popen(command, shell=True)
        print(f"Script {script_path} started in background")

    else:
        print("Unsupported OS")


if __name__ == "__main__":
    run_script_in_background()
