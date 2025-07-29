import discord
from discord.ext import commands, tasks
import socket
import asyncio
import random
import argparse

# ----- Argumentos por línea de comandos -----
parser = argparse.ArgumentParser(description="Bot de Discord para monitorear servidor WoW")
parser.add_argument('--token', required=True, help="Token del bot de Discord")
parser.add_argument('--ip', required=True, help="IP o dominio del servidor WoW")
parser.add_argument('--port', type=int, default=3724, help="Puerto del servidor WoW (default: 3724)")
parser.add_argument('--channel', type=int, required=True, help="ID del canal de Discord donde enviar mensajes")

args = parser.parse_args()

DISCORD_TOKEN = args.token
WOW_SERVER_IP = args.ip
WOW_SERVER_PORT = args.port
CHANNEL_ID = args.channel

# ----- Bot config -----
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

@bot.event
async def on_ready():
    print(f'🤖 Bot conectado como {bot.user}')
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        await channel.send(f"✅ Bot **{bot.user}** conectado y listo para monitorear **{WOW_SERVER_IP}:{WOW_SERVER_PORT}**")
    else:
        print(f"⚠️ No se encontró el canal con ID {CHANNEL_ID}")
    check_server_loop.start()

@tasks.loop(seconds=10)  # Intervalo base, luego se ajusta dinámicamente
async def check_server_loop():
    global server_was_online
    channel = bot.get_channel(CHANNEL_ID)
    try:
        online = is_server_online(WOW_SERVER_IP, WOW_SERVER_PORT)
        if online and not server_was_online:
            await channel.send(f"✅ El servidor WoW está **ONLINE** en {WOW_SERVER_IP}:{WOW_SERVER_PORT}")
            server_was_online = True
        elif not online and server_was_online:
            await channel.send(f"❌ El servidor WoW está **OFFLINE** en {WOW_SERVER_IP}:{WOW_SERVER_PORT}")
            server_was_online = False
    except Exception as e:
        print(f"Error comprobando el servidor: {e}")

    # Intervalo random entre 10 y 15 seg
    next_interval = random.randint(10, 15)
    check_server_loop.change_interval(seconds=next_interval)

@bot.command(name='serverstatus')
async def check_server_status(ctx):
    try:
        online = is_server_online(WOW_SERVER_IP, WOW_SERVER_PORT)
        if online:
            await ctx.send(f"✅ El servidor WoW está **ONLINE** en {WOW_SERVER_IP}:{WOW_SERVER_PORT}")
        else:
            await ctx.send(f"❌ El servidor WoW está **OFFLINE** en {WOW_SERVER_IP}:{WOW_SERVER_PORT}")
    except Exception as e:
        await ctx.send(f"Error al comprobar el estado del servidor: {e}")

bot.run(DISCORD_TOKEN)