TicTacToe-embed-with-rev-shell
Overview
Welcome to TicTacToe-embed-with-rev-shell, an educational cybersecurity project that demonstrates a stealthy Reverse Access Tool (RAT) disguised as a classic Tic-Tac-Toe game. Upon execution, the Tic-Tac-Toe frontend seamlessly operates as a decoy, while secretly establishing a reverse shell connection to an attacker’s server, all without the victim’s knowledge. This project serves as a powerful example for learning about cybersecurity principles, ethical hacking, and the importance of secure software practices.

Project Purpose
This repository is created for educational purposes only, providing a practical example of cybersecurity concepts, including network security, stealth techniques, and RAT development. It is intended to enhance understanding of potential vulnerabilities and foster awareness of secure coding practices. Any misuse or malicious application of this code is strictly prohibited and not the responsibility of the author/uploader.

How It Works
When the TicTacToe.exe executable is launched on a victim’s machine, it displays a fully functional Tic-Tac-Toe game interface built with Tkinter. Unbeknownst to the victim, the application establishes a reverse shell connection to a predefined attacker server, allowing remote control and data extraction. The game serves as a decoy, ensuring the RAT operates silently in the background, evading casual detection.

Commands to Use
The attacker can interact with the victim’s machine using the following reverse shell commands via the server script:

quit: Terminates the connection and closes the backdoor session.
sysinfo: Retrieves system information (e.g., OS, version, hostname, IP).
download [filename]: Downloads a specified file from the victim’s machine (sent in hex format).
upload [filename] [file_data]: Uploads a file to the victim’s machine (receives hex data).
screenshot: Captures and sends a screenshot of the victim’s screen (in hex).
webcam: Captures and sends an image from the victim’s webcam (in hex).
audio [duration]: Records audio for the specified duration (e.g., audio 500 records for 5 minutes) and sends it (in hex).
location: Retrieves the victim’s geographical location using an API (sent as data).
clipboard: Extracts and sends the current contents of the victim’s clipboard.
ps: Lists currently running processes on the victim’s machine.
env: Collects and sends the victim’s environment variables.
wifi: Retrieves and sends the SSID of the connected Wi-Fi network.
Build Instructions
To compile the project into an executable, use PyInstaller with the following command:


""pyinstaller --onefile --noconsole --icon=game.ico TicTacToe.pyw"""
detail:
--onefile: Creates a single .exe file for portability.
--noconsole: Ensures the executable runs without a console window (since TicTacToe.pyw uses Tkinter).
--icon=game.ico: Embeds a custom icon (game.ico) for the executable, enhancing its appearance as a game.
Ensure game.ico (or a Tic-Tac-Toe/game-related icon) is in the same directory as TicTacToe.pyw, or provide the full path.

Educational Use Only
This project is strictly for educational and research purposes to demonstrate cybersecurity concepts and ethical hacking techniques. It is not intended for any malicious or unauthorized use. The author/uploader bears no responsibility for any misuse, damage, or legal consequences resulting from the application of this code. Users are encouraged to adhere to ethical guidelines, legal standards, and institutional policies when exploring or extending this project.
