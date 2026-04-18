import discord
from discord.ext import commands
import random
import string
import os
import sys
import json
from pathlib import Path
from colorama import Fore
from Helper import *

# --- 1. LOAD CONFIGURATION ---
try:
    with open('config.json', 'r') as f:
        config = json.load(f)
except FileNotFoundError:
    print("Error: config.json not found!")
    sys.exit()

# Environment Variables & Config setup
TOKEN = os.getenv("BOT_TOKEN") or config.get("token")
OWNER_ID = int(os.getenv("OWNER_ID", config.get("owner_id", 0)))
GUILD_ID = int(os.getenv("SERVER_ID", config.get("server_id", 0)))

# Extracting data
free_gen_role = config["free_gen"]["free_gen_role"]
free_gen_channel_id = config["free_gen"]["free_gen_channel"]
free_gen_cooldown = config["free_gen"]["free_gen_cooldown"]
free_gen_status = config["free_gen"]["free_gen_status"]
status_logs = config["free_gen"]["status_log_channel"]

boost_gen_role = config["boost_gen"]["boost_gen_role"]
boost_gen_channel_id = config["boost_gen"]["boost_gen_channel"]
boost_gen_cooldown = config["boost_gen"]["boost_gen_cooldown"]

premium_gen_role = config["premium_gen"]["premium_gen_role"]
premium_gen_channel_id = config["premium_gen"]["premium_gen_channel"]
premium_gen_cooldown = config["premium_gen"]["premium_gen_cooldown"]

# Webhooks
freegenhook = config["logs"]["free_gen_log_webhook"]
boostgenhook = config["logs"]["booster_gen_log_webhook"]
premiumgenhook = config["logs"]["premium_gen_log_webhook"]
admincommandshook = config["logs"]["admin_commands_log_webhook"]

# --- 2. BOT SETUP ---
activity = discord.Activity(type=discord.ActivityType.playing, name=config["bot_status"])
intents = discord.Intents.default()
intents.members = True
intents.presences = True
intents.message_content = True 

bot = commands.Bot(
    command_prefix=["F.", "B.", "V.", "D.", "C.", "M."], 
    activity=activity, 
    status=discord.Status.online, 
    intents=intents,
    help_command=None
)

# --- 3. HELPERS ---
def generate_ticket():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=9))

def save_ticket(ticket_code, service):
    Path("assets").mkdir(exist_ok=True)
    with open("assets/tickets.txt", "a") as f:
        f.write(f"{ticket_code}:{service}\n")

# --- 4. EVENTS ---
@bot.event
async def on_ready():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f'{Fore.LIGHTMAGENTA_EX}Logged in as {bot.user}')
    print("Prefixes active: F., B., V., D., M.")
    
    # Send instructions to channels
    embed_configs = [
        (free_gen_channel_id, "Free gen", "F.gen [service]", free_gen_cooldown),
        (boost_gen_channel_id, "Booster gen", "B.gen [service]", boost_gen_cooldown),
        (premium_gen_channel_id, "Premium gen", "V.gen [service]", premium_gen_cooldown)
    ]

    for ch_id, title, cmd, cd in embed_configs:
        ch = bot.get_channel(ch_id)
        if ch:
            try: await ch.purge(limit=5)
            except: pass
            embed = discord.Embed(title=f"How to use {title}:", color=0xf43f5e)
            embed.description = f"Commands: `{cmd}`\n\nCooldown: {cd} seconds.\n\nTicket system active."
            embed.set_footer(text="Redeem tickets using F.redeem [code]")
            await ch.send(embed=embed)

@bot.event
async def on_presence_update(before, after):
    if after.bot or not after.guild: return
    role = after.guild.get_role(free_gen_role)
    if not role: return

    has_status = any(isinstance(a, discord.CustomActivity) and str(a) == free_gen_status for a in after.activities)
    
    if has_status:
        await after.add_roles(role)
    else:
        await after.remove_roles(role)

# --- 5. COMMANDS ---

@bot.command(name="help")
async def help_cmd(ctx):
    embed = discord.Embed(title="Nexus Commands", color=0xba67f6)
    embed.add_field(name="F. (General)", value="`F.redeem [code]`\n`F.gen [service]`\n`F.stock`", inline=False)
    embed.add_field(name="B. (Booster)", value="`B.gen [service]`", inline=False)
    embed.add_field(name="V. (VIP)", value="`V.gen [service]`", inline=False)
    embed.add_field(name="D. (Admin)", value="`D.restart`", inline=False)
    await ctx.send(embed=embed)

@bot.command(name="restart")
async def restart(ctx):
    if ctx.prefix == "D." and ctx.author.id == OWNER_ID:
        await ctx.send("♻️ Restarting system...")
        os.execv(sys.executable, ['python'] + sys.argv)

@bot.command(name="gen")
@commands.cooldown(1, 30, commands.BucketType.user) # Default safety cooldown
async def combined_gen(ctx, service: str = None):
    if not service: return await ctx.send(f"Usage: `{ctx.prefix}gen [service]`")
    
    # VIP Check
    if ctx.prefix == "V.":
        role = ctx.guild.get_role(premium_gen_role)
        if not role or role not in ctx.author.roles:
            embed = discord.Embed(title="VIP Required", description="Price: $5 or 200 Ruby", color=0xf43f5e)
            return await ctx.send(embed=embed)
    
    # Booster Check
    elif ctx.prefix == "B.":
        role = ctx.guild.get_role(boost_gen_role)
        if not role or role not in ctx.author.roles: return await ctx.send("Booster role required!")
    
    # Free Check
    elif ctx.prefix == "F.":
        if ctx.channel.id != free_gen_channel_id: return
        role = ctx.guild.get_role(free_gen_role)
        if not role or role not in ctx.author.roles: return await ctx.send("Status required!")

    ticket = generate_ticket()
    save_ticket(ticket, service)
    try:
        await ctx.author.send(f"🎟️ Your **{service}** ticket: `{ticket}`\nRedeem with `F.redeem {ticket}`")
        await ctx.send("✅ Ticket sent to DMs!", delete_after=10)
    except:
        await ctx.send("❌ Please open your DMs to receive the ticket!")

@bot.command(name="redeem")
async def redeem(ctx, code: str):
    if ctx.prefix != "F.": return
    
    found = False
    service_name = None
    lines = []

    if os.path.exists("assets/tickets.txt"):
        with open("assets/tickets.txt", "r") as f:
            lines = f.readlines()
        
        with open("assets/tickets.txt", "w") as f:
            for line in lines:
                if line.startswith(code) and not found:
                    try:
                        service_name = line.split(":")[1].strip()
                        found = True
                    except IndexError:
                        continue
                else:
                    f.write(line)
                    
    if found:
        # Stock location
        stock_file = Path(f"Premium_gen/{service_name}.txt")
        if stock_file.exists():
            with open(stock_file, "r") as f:
                accounts = [l for l in f.readlines() if l.strip()]
            if accounts:
                acc = random.choice(accounts).strip()
                remaining = [a for a in accounts if a.strip() != acc]
                with open(stock_file, "w") as f:
                    f.writelines(remaining)
                try:
                    await ctx.author.send(f"🎁 **{service_name} Account:** `{acc}`")
                    return await ctx.send("✅ Redeemed! Check your DMs.")
                except:
                    return await ctx.send("❌ I couldn't DM you your account!")
        await ctx.send(f"❌ Valid ticket, but **{service_name}** is out of stock!")
    else:
        await ctx.send("❌ Invalid or expired ticket.")

@bot.slash_command(name="setticket", description="Manually create a ticket for a service", guild_ids=[GUILD_ID])
async def setticket(ctx, service: str):
    if not await Utils.isWhitelisted(ctx): return await ctx.respond("Unauthorized.", ephemeral=True)
    ticket = generate_ticket()
    save_ticket(ticket, service)
    await ctx.respond(f"✅ Ticket for **{service}**: `{ticket}`", ephemeral=True)

@combined_gen.error
async def gen_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"⏳ Cooldown! Wait {round(error.retry_after, 2)}s.", delete_after=5)

if TOKEN:
    bot.run(TOKEN)
