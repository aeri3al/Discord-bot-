import discord
from discord import app_commands
from discord.ext import commands
import json
import random
import string
from datetime import datetime, timedelta

TOKEN = "TOKEN"
LICENSE_FILE = "licenses.json"

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# ========== Utils ==========

def is_admin(interaction: discord.Interaction):
    return interaction.user.guild_permissions.administrator

def load_licenses():
    try:
        with open(LICENSE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_licenses(data):
    with open(LICENSE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def gen_key():
    parts = []
    for _ in range(4):
        part = "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
        parts.append(part)
    return "EUPH-" + "-".join(parts)

def make_license(duration):
    now = datetime.utcnow()

    if duration == "day":
        expires = now + timedelta(days=1)
    elif duration == "week":
        expires = now + timedelta(weeks=1)
    elif duration == "month":
        expires = now + timedelta(days=30)
    elif duration == "life":
        expires = None
    else:
        return None, None

    key = gen_key()
    return key, expires

# ========== Events ==========

@bot.event
async def on_ready():
    print(f"✅ Bot online als {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"🔁 {len(synced)} Slash-Commands synchronisiert.")
    except Exception as e:
        print("❌ Sync-Fehler:", e)

# ========== Commands ==========

@bot.tree.command(name="gen", description="Generiert einen Lizenz-Key (Admin only)")
@app_commands.describe(duration="day, week, month oder life")
async def gen(interaction: discord.Interaction, duration: str):
    if not is_admin(interaction):
        await interaction.response.send_message("❌ Kein Zugriff (Admin only).", ephemeral=True)
        return

    duration = duration.lower()
    if duration not in ["day", "week", "month", "life"]:
        await interaction.response.send_message(
            "❌ Benutze: /gen day | week | month | life",
            ephemeral=True
        )
        return

    key, expires = make_license(duration)
    licenses = load_licenses()

    licenses[key] = {
        "type": duration.upper(),
        "expires": expires.isoformat() if expires else None,
        "hwid": None,
        "created": datetime.utcnow().isoformat()
    }

    save_licenses(licenses)

    embed = discord.Embed(
        title="🔑 Your Euphoric License Key",
        color=0x9b59ff
    )
    embed.add_field(name="Key", value=f"`{key}`", inline=False)
    embed.add_field(name="Duration", value=duration.upper(), inline=False)
    embed.set_footer(text="Do not share this key.")

    try:
        await interaction.user.send(embed=embed)
        await interaction.response.send_message("✅ Key wurde per DM gesendet.", ephemeral=True)
    except:
        await interaction.response.send_message("❌ Konnte keine DM senden.", ephemeral=True)

# ========== Reset Key ==========

@bot.tree.command(name="reset_key", description="Löscht eine Lizenz komplett (Admin only)")
@app_commands.describe(key="Der Lizenz-Key")
async def reset_key(interaction: discord.Interaction, key: str):
    if not is_admin(interaction):
        await interaction.response.send_message("❌ Kein Zugriff (Admin only).", ephemeral=True)
        return

    licenses = load_licenses()

    if key not in licenses:
        await interaction.response.send_message("❌ Key nicht gefunden.", ephemeral=True)
        return

    del licenses[key]
    save_licenses(licenses)

    await interaction.response.send_message(f"✅ Key `{key}` wurde gelöscht.", ephemeral=True)

# ========== Reset HWID ==========

@bot.tree.command(name="reset_hwid", description="Setzt die HWID-Bindung eines Keys zurück (Admin only)")
@app_commands.describe(key="Der Lizenz-Key")
async def reset_hwid(interaction: discord.Interaction, key: str):
    if not is_admin(interaction):
        await interaction.response.send_message("❌ Kein Zugriff (Admin only).", ephemeral=True)
        return

    licenses = load_licenses()

    if key not in licenses:
        await interaction.response.send_message("❌ Key nicht gefunden.", ephemeral=True)
        return

    licenses[key]["hwid"] = None
    save_licenses(licenses)

    await interaction.response.send_message(f"✅ HWID von `{key}` wurde zurückgesetzt.", ephemeral=True)

# ========== Run ==========

bot.run(TOKEN)
