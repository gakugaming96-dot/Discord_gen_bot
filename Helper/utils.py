from pathlib import Path
import discord
import os
import random
import json
import requests
from datetime import datetime
from colorama import Fore
from discord.ext import commands

# --- 1. LOAD CONFIG & VARIABLES ---
try:
    with open("c=onfig.json", "r", encoding="utf-8") as f:
        config = json.load(f)
except FileNotFoundError:
    config = {}

# Railway Environment Variables (Prioritized)
OWNER_ID = int(os.getenv("OWNER_ID", config.get('owner_id', 0)))
GUILD_ID = int(os.getenv("SERVER_ID", config.get('server_id', 0)))
BOT_TOKEN = os.getenv("BOT_TOKEN", config.get('bot_token'))
BOT_STATUS = os.getenv("BOT_STATUS", config.get('bot_status', 'Nexus Gen'))

# --- 2. BOT SETUP ---
activity = discord.Activity(type=discord.ActivityType.playing, name=BOT_STATUS)
intents = discord.Intents.default()
intents.members = True
intents.presences = True
intents.message_content = True 

bot = commands.Bot(command_prefix="*", activity=activity, status=discord.Status.online, intents=intents)

# --- 3. GENERATOR CONFIGURATIONS ---
# Free Gen
free_gen_config = config.get('free_gen', {})
free_gen_role = free_gen_config.get('free_gen_role')
free_gen_channel_id = free_gen_config.get('free_gen_channel')
free_gen_cooldown = free_gen_config.get('free_gen_cooldown', 360)
free_gen_status = free_gen_config.get('free_gen_status')
status_logs = free_gen_config.get('status_log_channel')
free_gen_folder = free_gen_config.get('free_gen_folder', 'assets/free')

# Booster Gen
boost_gen_config = config.get('boost_gen', {})
boost_gen_role = boost_gen_config.get('boost_gen_role')
boost_gen_channel_id = boost_gen_config.get('boost_gen_channel')
boost_gen_cooldown = boost_gen_config.get('boost_gen_cooldown', 120)
boost_gen_folder = boost_gen_config.get('boost_gen_folder', 'assets/boost')

# Premium Gen
premium_gen_config = config.get('premium_gen', {})
premium_gen_role = premium_gen_config.get('premium_gen_role')
premium_gen_channel_id = premium_gen_config.get('premium_gen_channel')
premium_gen_cooldown = premium_gen_config.get('premium_gen_cooldown', 240)
premium_gen_folder = premium_gen_config.get('premium_gen_folder', 'assets/premium')

# --- 4. WEBHOOKS ---
log_config = config.get('logs', {})
freegenhook = log_config.get('free_gen_log_webhook')
boostgenhook = log_config.get('booster_gen_log_webhook')
premiumgenhook = log_config.get('premium_gen_log_webhook')
admincommandshook = log_config.get('admin_commands_log_webhook')

# --- 5. UTILS CLASS ---
class Utils():
    @staticmethod
    async def isWhitelisted(ctx) -> bool:
        Path("assets").mkdir(exist_ok=True)
        whitelist_path = "assets/whitelist.txt"
        if not os.path.exists(whitelist_path):
            with open(whitelist_path, "w") as f: pass
            
        with open(whitelist_path, "r") as f:
            whitelisted = f.read().splitlines()
            
        if str(ctx.author.id) in whitelisted or ctx.author.id == OWNER_ID:  
            return True
        return False

# --- 6. STOCK HELPERS ---
def gen_get_stock(folder):
    path = Path(folder)
    path.mkdir(parents=True, exist_ok=True) # Creates folder if missing
    return [file.name for file in path.glob('*.txt')]

def count_stock(folder, file_name):
    try:
        with open(f"{folder}/{file_name}", 'r') as f:
            return len([line for line in f.readlines() if line.strip()])
    except FileNotFoundError:
        return 0

# --- 7. LOGGING ---
def log_action_webhook(webhook, message, logtype):
    if not webhook or "YOUR_WEBHOOK" in webhook:
        return
    payload = {
        "embeds": [{
            "title": f"{logtype} Log",
            "description": message,
            "color": 16056575,
            "footer": {"text": "Nexus System"}
        }]
    }
    requests.post(webhook, json=payload)

def log_action_file(message):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{Fore.RESET}[{Fore.GREEN}{now}{Fore.RESET}] {message}")
    Path("assets").mkdir(exist_ok=True)
    with open("assets/logs.txt", "a", encoding="utf-8") as f:
        f.write(f"[{now}] {message}\n")
