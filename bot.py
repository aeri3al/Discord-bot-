import discord
from discord import app_commands
from discord.ext import commands
import os
import json
import random
import string
from datetime import datetime, timedelta

# === CONFIG ===
TOKEN = os.getenv("DISCORD_TOKEN")  # Token kommt von Railway Env Variable
LICENSE_FILE = "licenses.json"

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# === EVENTS ===
@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"✅ Bot online als {bot.user} | {len(synced)} Commands synchronisiert")
    except Exception as e:
        print("❌ Sync Fehler:", e)

# === SIMPLE TEST COMMAND ===
@bot.tree.command(name="ping", description="Test command")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("🏓 Pong!")

# === START ===
if __name__ == "__main__":
    if not TOKEN:
        print("❌ DISCORD_TOKEN ist nicht gesetzt!")
    else:
        bot.run(TOKEN)
