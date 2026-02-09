import discord
from discord.ext import commands
import random
import string
import datetime
import os

# =====================
# CONFIG
# =====================
TOKEN = os.getenv("TOKEN")

# =====================
# BOT SETUP
# =====================
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

CHARS_4C = string.ascii_lowercase + string.digits
CHARS_4L = string.ascii_lowercase

def gen_4c():
    return "".join(random.choice(CHARS_4C) for _ in range(4))

def gen_4l():
    return "".join(random.choice(CHARS_4L) for _ in range(4))

def save_to_file(text):
    with open("generated.txt", "a", encoding="utf-8") as f:
        f.write(f"{datetime.datetime.now()} | {text}\n")

# =====================
# EVENTS
# =====================
@bot.event
async def on_ready():
    print(f"✅ Bot online als {bot.user}")

# =====================
# COMMANDS
# =====================
@bot.command()
async def gen4c(ctx, amount: int = 5):
    if amount > 50:
        await ctx.reply("❌ Maximal 50 auf einmal.")
        return

    names = [gen_4c() for _ in range(amount)]
    result = ", ".join(names)

    save_to_file(f"4C | {result}")
    await ctx.reply(f"🔢 **4C Namen:**\n`{result}`")

@bot.command()
async def gen4l(ctx, amount: int = 5):
    if amount > 50:
        await ctx.reply("❌ Maximal 50 auf einmal.")
        return

    names = [gen_4l() for _ in range(amount)]
    result = ", ".join(names)

    save_to_file(f"4L | {result}")
    await ctx.reply(f"🔤 **4L Namen:**\n`{result}`")

# =====================
# START
# =====================
bot.run(TOKEN)
