import discord
from discord.ext import commands, tasks
import socket
import random
import os
from datetime import datetime

# Lee datos sensibles desde variables de entorno
DISCORD_TOKEN = os.environ['DISCORD_TOKEN']
WOW_SERVER_IP = os.environ['WOW_SERVER_IP']
WOW_SERVER_PORT = int(os.environ.get('WOW_SERVER_PORT', 3724))
CHANNEL_ID = int(os.environ['CHANNEL_ID'])

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

server_was_online = False

def is_server_online(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(3)
    try:
        s.connect((ip, port))
        s.shutdown(socket.SHUT_RDWR)
        return True
    except:
        return False
    finally:
        s.close()

def now():
    return datetime.now().strftime('%H:%M')

@bot.event
async def on_ready():
    print(f'✅ Bot conectado como {bot.user}')
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        await channel.send(f"[{now()}] 🤖 Monitoreando {WOW_SERVER_IP}:{WOW_SERVER_PORT}")
    check_server_loop.start()

@tasks.loop(seconds=10)
async def check_server_loop():
    global server_was_online
    channel = bot.get_channel(CHANNEL_ID)
    try:
        online = is_server_online(WOW_SERVER_IP, WOW_SERVER_PORT)
        if online and not server_was_online:
            await channel.send(f"[{now()}] 🟢 ONLINE")
            server_was_online = True
        elif not online and server_was_online:
            await channel.send(f"[{now()}] 🔴 OFFLINE")
            server_was_online = False
    except Exception as e:
        print(f"Error comprobando el servidor: {e}")

    next_interval = random.randint(10, 15)
    check_server_loop.change_interval(seconds=next_interval)

@bot.command(name='serverstatus')
async def check_server_status(ctx):
    try:
        online = is_server_online(WOW_SERVER_IP, WOW_SERVER_PORT)
        status = "🟢 ONLINE" if online else "🔴 OFFLINE"
        await ctx.send(f"[{now()}] {status}")
    except Exception as e:
        await ctx.send(f"[{now()}] ⚠️ Error: {e}")

bot.run(DISCORD_TOKEN)
