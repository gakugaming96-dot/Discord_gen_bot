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
with open('config.json', 'r') as f:
    config = json.load(f)

# Environment Variables (For Railway Security)
TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", config.get("owner_id", 0)))
GUILD_ID = int(os.getenv("SERVER_ID", config.get("server_id", 0)))

# Extracting data from Config.json
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

bot = commands.Bot(command_prefix="F.", activity=activity, status=discord.Status.online, intents=intents)
bot.remove_command('help')

def generate_ticket():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=9))

# --- 3. EVENTS ---

@bot.event
async def on_ready():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f'{Fore.LIGHTMAGENTA_EX}Logged in as {bot.user}')
    
    # Clear channels and send instructions
    channel_ids = [free_gen_channel_id, boost_gen_channel_id, premium_gen_channel_id]
    for channel_id in channel_ids:
        channel = bot.get_channel(channel_id)
        if channel:
            try:
                await channel.purge(limit=100)
            except:
                pass

    # Instruction Embeds
    embed_configs = [
        (free_gen_channel_id, "Free gen", "F.gen [service]", free_gen_cooldown, "killarua"),
        (boost_gen_channel_id, "Booster gen", "B.[service]", boost_gen_cooldown, "killarua"),
        (premium_gen_channel_id, "Premium gen", "V.[service]", premium_gen_cooldown, "killa")
    ]

    for ch_id, title, cmd, cd, author in embed_configs:
        ch = bot.get_channel(ch_id)
        if ch:
            embed = discord.Embed(title=f"How to use {title}:", color=0xf43f5e)
            embed.description = (
                f"Commands:\n\n`{cmd}`\n\n"
                f"Settings:\n\nYou need to allow Direct Messages from server members to use this bot.\n\n"
                f"Cooldown:\n\nThe cooldown is {cd} seconds.\n"
            )
            embed.set_footer(text=f"Made by {author}")
            await ch.send(embed=embed)

@bot.event
async def on_message(message):
    if message.author.bot: return
    
    # Prefix Interceptor (Routing B., V., and D. to F.)
    content = message.content.upper()
    if content.startswith("B."):
        message.content = "F.bgen " + message.content[2:]
    elif content.startswith("V."):
        message.content = "F.vgen " + message.content[2:]
    elif content.startswith("D.RESTART"):
        message.content = "F.restart"
        
    await bot.process_commands(message)

@bot.event
async def on_presence_update(before, after):
    if after.bot or not after.guild: return
    role = after.guild.get_role(free_gen_role)
    channel = bot.get_channel(status_logs)
    if not role: return

    had_status = any(isinstance(a, discord.CustomActivity) and str(a) == free_gen_status for a in before.activities)
    has_status = any(isinstance(a, discord.CustomActivity) and str(a) == free_gen_status for a in after.activities)

    if had_status and not has_status:
        await after.remove_roles(role)
        if channel:
            embed = discord.Embed(title="Removed Free Gen", description=f"{after.mention} removed the status.", color=discord.Color.red())
            await channel.send(embed=embed)
    elif not had_status and has_status:
        await after.add_roles(role)
        if channel:
            embed = discord.Embed(title="Added Free Gen", description=f"{after.mention} added the status!", color=discord.Color.green())
            await channel.send(embed=embed)

# --- 4. ADMIN COMMANDS ---

@bot.command()
async def restart(ctx):
    if ctx.author.id == OWNER_ID:
        await ctx.send("♻️ Restarting the system...")
        os.execv(sys.executable, ['python'] + sys.argv)

@bot.command()
async def whitelist(ctx, user: discord.Member = None):
    if ctx.author.id != OWNER_ID:
        return await ctx.send(embed=discord.Embed(title="Error", description="Owner only command.", color=0xf667c6))
    if not user: return await ctx.send("Please mention a user.")
    
    Path("assets").mkdir(exist_ok=True)
    with open("assets/whitelist.txt", "a+") as f:
        f.seek(0)
        whitelisted = f.read().splitlines()
        if str(user.id) not in whitelisted:
            f.write(str(user.id) + "\n")
            log_action_webhook(admincommandshook, f"<@{ctx.author.id}> Whitelisted <@{user.id}>", "Admin")
            await ctx.send(embed=discord.Embed(title="Success", description=f"Whitelisted {user.name}", color=0xba67f6))
        else:
            await ctx.send("User is already whitelisted.")

@bot.command()
async def unwhitelist(ctx, user: discord.Member = None):
    if ctx.author.id != OWNER_ID: return
    if not user: return await ctx.send("Please mention a user.")

    if os.path.exists("assets/whitelist.txt"):
        with open("assets/whitelist.txt", "r") as f:
            lines = f.readlines()
        with open("assets/whitelist.txt", "w") as f:
            for line in lines:
                if line.strip() != str(user.id):
                    f.write(line)
        await ctx.send(embed=discord.Embed(title="Success", description=f"Removed {user.name}", color=0xba67f6))

@bot.command()
async def get_log_file(ctx):
    if not await Utils.isWhitelisted(ctx): return
    if os.path.exists("assets/logs.txt"):
        await ctx.send(file=discord.File("assets/logs.txt"))
    else:
        await ctx.send("Log file not found.")

# --- 5. GENERATOR COMMANDS ---

@bot.command()
@commands.cooldown(1, free_gen_cooldown, commands.BucketType.user)
async def gen(ctx, service: str = None):
    if ctx.channel.id != free_gen_channel_id: return
    if not service: return await ctx.send("Usage: `F.gen [service]`")
    
    role = ctx.guild.get_role(free_gen_role)
    if role not in ctx.author.roles:
        return await ctx.send("You don't have permission (Missing status).")

    ticket = generate_ticket()
    log_action_webhook(freegenhook, f"<@{ctx.author.id}> generated {service}", "Free Gen")
    
    embed = discord.Embed(title="Ticket Generated", description=f"**Service:** {service}\n**Code:** `{ticket}`", color=0xfa0ad6)
    try:
        await ctx.author.send(embed=embed)
        await ctx.send("Ticket sent to DMs!")
    except:
        await ctx.send("Please open your DMs!")

@bot.command()
@commands.cooldown(1, boost_gen_cooldown, commands.BucketType.user)
async def bgen(ctx, service: str = None):
    if ctx.channel.id != boost_gen_channel_id: return
    if not service: return await ctx.send("Usage: `B.[service]`")
    
    role = ctx.guild.get_role(boost_gen_role)
    if role not in ctx.author.roles:
        return await ctx.send("You don't have Booster role.")
    
    ticket = generate_ticket()
    log_action_webhook(boostgenhook, f"<@{ctx.author.id}> generated {service}", "Booster Gen")
    await ctx.author.send(f"Booster Ticket: `{ticket}`")
    await ctx.send("Booster ticket sent to DMs!")

@bot.command()
@commands.cooldown(1, premium_gen_cooldown, commands.BucketType.user)
async def vgen(ctx, service: str = None):
    if ctx.channel.id != premium_gen_channel_id: return
    if not service: return await ctx.send("Usage: `V.[service]`")
    
    role = ctx.guild.get_role(premium_gen_role)
    if not role or role not in ctx.author.roles:
        return await ctx.send("Buy VIP to use this command!")
    
    ticket = generate_ticket()
    log_action_webhook(premiumgenhook, f"<@{ctx.author.id}> generated {service}", "VIP Gen")
    await ctx.author.send(f"VIP Ticket: `{ticket}`")
    await ctx.send("VIP ticket sent to DMs!")

# Error Handler
@gen.error
@bgen.error
@vgen.error
async def gen_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(embed=discord.Embed(title="Cooldown", description=f"Wait {round(error.retry_after, 2)}s.", color=0xf667c6))

# --- 6. RUN ---
if TOKEN:
    bot.run(TOKEN)