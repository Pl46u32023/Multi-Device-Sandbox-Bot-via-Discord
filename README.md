# Multi-Device-Sandbox-Bot-via-Discord

🧪 Multi-Device Sandbox Bot via Discord
⚠️ Disclaimer:
This project is for educational purposes and sandbox testing only.
The author of this repository does not condone or promote malicious activity and cannot be held responsible for any misuse or damages caused by this code. Use it at your own risk and in controlled environments only.

📌 Description
This is a Discord-based multi-device sandbox bot designed for cybersecurity experiments, monitoring system environments, and personal development testing. It features:

Device heartbeat monitoring

Keylogging with context

Clipboard and screenshot access

Webcam snapshot (if accessible)

File exploration and retrieval (with optional restrictions)

Scheduled log transmission

Controlled shutdown and cleanup

🚧 Educational Use Only
This project is intended solely for:

Sandbox environments

Controlled labs

Developer testing

Educational and ethical security research

Do not use this tool on machines or networks without proper authorization.

🛠️ Installation
⚠️ Requirements:

Windows OS

Python 3.8+

Discord bot token

Admin privileges (for full feature access)

1. Clone the Repository
bash
Copy
Edit
git clone https://github.com/yourusername/sandbox-discord-bot.git
cd sandbox-discord-bot
2. Install Dependencies
bash
Copy
Edit
pip install -r requirements.txt
3. Configure
In the script, set your Discord bot token:

python
Copy
Edit
TOKEN = 'YOUR_DISCORD_BOT_TOKEN'
4. Run
bash
Copy
Edit
python bot.py
🔐 Commands Overview
Command	Function
!unlock <pass>	Disable restricted mode
!status	Show system resource usage
!screenshot	Capture and upload screen
!camshot	Capture and upload webcam image
!clipboard	Upload clipboard text
!files [path]	List directory contents
!getfile <path>	Retrieve specific file (if allowed)
!logdump	Upload full keylog
!search <term>	Search keylog for term
!setinterval <s>	Set log upload interval
!selfdestruct	Cleanup and exit (if allowed)
!exit	Gracefully shut down

🧪 Safe Mode
Enabled by default to prevent sensitive operations. Disable it with:

bash
Copy
Edit
!unlock 780302
📜 License
This project is licensed under the MIT License.

❗ Legal Notice
By using this software, you agree:

It will only be used in legally authorized contexts.

You assume full responsibility for its use.

The authors are not liable for misuse, damage, or legal outcomes.
