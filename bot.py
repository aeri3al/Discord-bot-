import discord
from discord.ext import commands
import json
import random
import string
from datetime import datetime, timedelta

TOKEN = "DEIN_DISCORD_BOT_TOKEN_HIER"

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

LICENSE_FILE = "licenses.json"

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

@bot.event
async def on_ready():
    print(f"✅ Bot online als {bot.user}")

@bot.command()
async def gen(ctx, duration: str):
    duration = duration.lower()
    if duration not in ["day", "week", "month", "life"]:
        await ctx.reply("❌ Benutze: `!gen day`, `!gen week`, `!gen month` oder `!gen life`")
        return

    key, expires = make_license(duration)
    if key is None:
        await ctx.reply("❌ Fehler beim Erstellen der Lizenz.")
        return

    licenses = load_licenses()

    licenses[key] = {
        "type": duration.upper(),
        "expires": expires.isoformat() if expires else None,
        "hwid": None
    }

    save_licenses(licenses)

    try:
        await ctx.author.send(
            f"🔑 **Your Euphoric License Key**\n\n"
            f"**Key:** `{key}`\n"
            f"**Duration:** {duration.upper()}\n\n"
            f"Do not share this key."
        )
        await ctx.reply("✅ Ich hab dir den Key per DM geschickt!")
    except:
        await ctx.reply("❌ Ich konnte dir keine DM senden. Öffne deine DMs!")

bot.run(TOKEN)
