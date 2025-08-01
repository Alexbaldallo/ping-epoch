import discord
from discord.ext import commands, tasks
import socket
import random
import os
from datetime import datetime, timedelta

DISCORD_TOKEN = os.environ['DISCORD_TOKEN']
WOW_SERVER_IP = os.environ['WOW_SERVER_IP']
WOW_LOGIN_PORT = int(os.environ.get('WOW_LOGIN_PORT', 3724))
WOW_GURUBASHI_PORT = int(os.environ.get('WOW_GURUBASHI_PORT', 8086))
WOW_KEZAN_PORT = int(os.environ.get('WOW_KEZAN_PORT', 8085))
CHANNEL_ID = int(os.environ['CHANNEL_ID'])

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

login_online = False
gurubashi_online = False
kezan_online = False

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
    hora_local = datetime.utcnow() + timedelta(hours=2)  # Ajuste manual GMT+2
    return hora_local.strftime('%H:%M')

@bot.event
async def on_ready():
    print(f'✅ Bot conectado como {bot.user}')
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        await channel.send(
            f"[{now()}] 🤖 Monitoreando {WOW_SERVER_IP} en puertos "
            f"{WOW_LOGIN_PORT} (LoginServer), {WOW_GURUBASHI_PORT} (Gurubashi), {WOW_KEZAN_PORT} (Kezan)"
        )
    check_server_loop.start()

@tasks.loop(seconds=10)
async def check_server_loop():
    global login_online, gurubashi_online, kezan_online
    channel = bot.get_channel(CHANNEL_ID)
    try:
        online_login = is_server_online(WOW_SERVER_IP, WOW_LOGIN_PORT)
        if online_login != login_online:
            status = "🟢 ONLINE" if online_login else "🔴 OFFLINE"
            await channel.send(f"[{now()}] LoginServer ({WOW_LOGIN_PORT}): {status}")
            login_online = online_login
        
        online_gurubashi = is_server_online(WOW_SERVER_IP, WOW_GURUBASHI_PORT)
        if online_gurubashi != gurubashi_online:
            status = "🟢 ONLINE" if online_gurubashi else "🔴 OFFLINE"
            await channel.send(f"[{now()}] Realm Gurubashi ({WOW_GURUBASHI_PORT}): {status}")
            gurubashi_online = online_gurubashi

        online_kezan = is_server_online(WOW_SERVER_IP, WOW_KEZAN_PORT)
        if online_kezan != kezan_online:
            status = "🟢 ONLINE" if online_kezan else "🔴 OFFLINE"
            await channel.send(f"[{now()}] Realm Kezan ({WOW_KEZAN_PORT}): {status}")
            kezan_online = online_kezan

    except Exception as e:
        print(f"Error comprobando el servidor: {e}")

    next_interval = random.randint(10, 15)
    check_server_loop.change_interval(seconds=next_interval)

@bot.command(name='serverstatus')
async def check_server_status(ctx):
    try:
        online_login = is_server_online(WOW_SERVER_IP, WOW_LOGIN_PORT)
        online_gurubashi = is_server_online(WOW_SERVER_IP, WOW_GURUBASHI_PORT)
        online_kezan = is_server_online(WOW_SERVER_IP, WOW_KEZAN_PORT)
        msg = (
            f"[{now()}] LoginServer ({WOW_LOGIN_PORT}): {'🟢 ONLINE' if online_login else '🔴 OFFLINE'}\n"
            f"[{now()}] Realm Gurubashi ({WOW_GURUBASHI_PORT}): {'🟢 ONLINE' if online_gurubashi else '🔴 OFFLINE'}\n"
            f"[{now()}] Realm Kezan ({WOW_KEZAN_PORT}): {'🟢 ONLINE' if online_kezan else '🔴 OFFLINE'}"
        )
        await ctx.send(msg)
    except Exception as e:
        await ctx.send(f"[{now()}] ⚠️ Error: {e}")

bot.run(DISCORD_TOKEN)
