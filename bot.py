import discord
from discord import app_commands
from discord.ext import commands
import os
import json
import random
import string
from datetime import datetime, timedelta

TOKEN = os.getenv("DISCORD_TOKEN")
LICENSE_FILE = "licenses.json"

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# ===== UTIL =====

def load_licenses():
    if not os.path.exists(LICENSE_FILE):
        return {}
    with open(LICENSE_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return {}

def save_licenses(data):
    with open(LICENSE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def generate_key():
    parts = [
        ''.join(random.choices(string.ascii_uppercase + string.digits, k=4)),
        ''.join(random.choices(string.ascii_uppercase + string.digits, k=4)),
        ''.join(random.choices(string.ascii_uppercase + string.digits, k=4)),
        ''.join(random.choices(string.ascii_uppercase + string.digits, k=4)),
    ]
    return "EUPH-" + "-".join(parts)

def is_admin(interaction: discord.Interaction):
    return interaction.user.guild_permissions.administrator

# ===== EVENTS =====

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ Bot online als {bot.user}")

# ===== COMMANDS =====

@bot.tree.command(name="genkey", description="Generate a license key")
@app_commands.describe(duration="1d, 7d, 30d, lifetime")
async def genkey(interaction: discord.Interaction, duration: str):
    if not is_admin(interaction):
        await interaction.response.send_message("❌ Keine Rechte.", ephemeral=True)
        return

    duration = duration.lower()
    now = datetime.utcnow()

    if duration == "1d":
        expires = now + timedelta(days=1)
    elif duration == "7d":
        expires = now + timedelta(days=7)
    elif duration == "30d":
        expires = now + timedelta(days=30)
    elif duration == "lifetime":
        expires = None
    else:
        await interaction.response.send_message("❌ Ungültig: nutze 1d, 7d, 30d, lifetime", ephemeral=True)
        return

    licenses = load_licenses()
    key = generate_key()

    licenses[key] = {
        "expires": expires.isoformat() if expires else None,
        "hwid": None,
        "created": now.isoformat()
    }

    save_licenses(licenses)

    await interaction.response.send_message(
        f"🔑 **Neuer Key erstellt:**\n`{key}`\n⏳ Laufzeit: **{duration}**",
        ephemeral=True
    )

@bot.tree.command(name="checkkey", description="Check a license key")
async def checkkey(interaction: discord.Interaction, key: str):
    licenses = load_licenses()

    if key not in licenses:
        await interaction.response.send_message("❌ Key nicht gefunden.", ephemeral=True)
        return

    data = licenses[key]
    expires = data["expires"]
    hwid = data["hwid"]

    if expires:
        exp_dt = datetime.fromisoformat(expires)
        if exp_dt < datetime.utcnow():
            status = "❌ Abgelaufen"
        else:
            status = f"✅ Gültig bis {exp_dt}"
    else:
        status = "♾️ Lifetime"

    await interaction.response.send_message(
        f"🔑 **Key:** `{key}`\n"
        f"📌 **Status:** {status}\n"
        f"💻 **HWID:** `{hwid}`",
        ephemeral=True
    )

@bot.tree.command(name="resethwid", description="Reset HWID of a key")
async def resethwid(interaction: discord.Interaction, key: str):
    if not is_admin(interaction):
        await interaction.response.send_message("❌ Keine Rechte.", ephemeral=True)
        return

    licenses = load_licenses()

    if key not in licenses:
        await interaction.response.send_message("❌ Key nicht gefunden.", ephemeral=True)
        return

    licenses[key]["hwid"] = None
    save_licenses(licenses)

    await interaction.response.send_message("✅ HWID wurde zurückgesetzt.", ephemeral=True)

@bot.tree.command(name="deletekey", description="Delete a license key")
async def deletekey(interaction: discord.Interaction, key: str):
    if not is_admin(interaction):
        await interaction.response.send_message("❌ Keine Rechte.", ephemeral=True)
        return

    licenses = load_licenses()

    if key not in licenses:
        await interaction.response.send_message("❌ Key nicht gefunden.", ephemeral=True)
        return

    del licenses[key]
    save_licenses(licenses)

    await interaction.response.send_message("🗑️ Key gelöscht.", ephemeral=True)

@bot.tree.command(name="bind", description="Bind HWID to a key")
async def bind(interaction: discord.Interaction, key: str, hwid: str):
    licenses = load_licenses()

    if key not in licenses:
        await interaction.response.send_message("❌ Key nicht gefunden.", ephemeral=True)
        return

    if licenses[key]["hwid"] is not None:
        await interaction.response.send_message("❌ Key ist bereits gebunden.", ephemeral=True)
        return

    licenses[key]["hwid"] = hwid
    save_licenses(licenses)

    await interaction.response.send_message("✅ HWID erfolgreich gebunden.", ephemeral=True)

# ===== START =====

if __name__ == "__main__":
    if not TOKEN:
        print("❌ DISCORD_TOKEN nicht gesetzt!")
    else:
        bot.run(TOKEN)
