import subprocess
import sys

def install_frr():
    """Install FRRouting from official repository"""
    try:
        print("📦 Adding FRRouting repository...")
        subprocess.run([
            "curl", "-s", "https://deb.frrouting.org/frr/keys.gpg", "|",
            "sudo", "tee", "/usr/share/keyrings/frrouting.gpg", ">", "/dev/null"
        ], check=True)
        subprocess.run([
            "echo", "deb [signed-by=/usr/share/keyrings/frrouting.gpg] https://deb.frrouting.org/frr $(lsb_release -s -c) frr-stable",
            "|", "sudo", "tee", "-a", "/etc/apt/sources.list.d/frr.list"
        ], check=True)
        subprocess.run(["sudo", "apt", "update"], check=True)
        subprocess.run(["sudo", "apt", "install", "-y", "frr", "frr-pythontools"], check=True)
        with open("/etc/frr/daemons", "a") as f:
            f.write('watchfrr_options="--netns=dataplane"\n')
        subprocess.run(["sudo", "systemctl", "enable", "frr"], check=True)
        subprocess.run(["sudo", "systemctl", "start", "frr"], check=True)
        print("✅ FRRouting installed and enabled.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install FRRouting: {e}")
        sys.exit(1)
