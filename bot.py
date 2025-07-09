import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import random
import time
import platform
import asyncio
import aiohttp

# Local imports
from image_gen import generate_image
from chatgpt_handler import ask_cat_gpt
from cat_facts import get_random_cat_fact
from lyrics import Lyrics
from music import Music
from reddit_memes import RedditMemes
from steam_functions import Steam
from weather import WeatherCog
from unscramble_game import WordUnscramble
from typing_game import TypingGame
from blackjack import Blackjack
from random_dog import RandomDog
from random_cat import RandomCat
from joke import RandomJoke
from rush_b import RushB
from roulette import Roulette
from currency import Currency
from theme import Theme
from haiku import Haiku
from roast import ComplimentRoast
from last_seen import LastSeen
from sokoban import Sokoban
from virtualplant import VirtualPlant
from bengif import GifCommands

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
EDDIE_ID = int(os.getenv("EDDIE_ID"))
EDBOT_ID = int(os.getenv("EDBOT_ID"))
DYLAN_ID = int(os.getenv("DYLAN_ID"))

if not TOKEN:
    raise ValueError("DISCORD_TOKEN not found in environment variables")

# Setup Discord bot
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True
intents.presences = True

bot = commands.Bot(command_prefix="/", intents=intents, help_command=None)
start_time = time.time()

# Global aiohttp session
session = None

@bot.event
async def on_ready():
    global session
    session = aiohttp.ClientSession()
    activity = discord.Game(name="Final Fantasy XIV")  # Replace with your custom message
    await bot.change_presence(status=discord.Status.online, activity=activity)
    print(f"Bot is online as {bot.user}")

@bot.event
async def on_shutdown():
    global session
    if session:
        await session.close()
    print("Closed aiohttp session.")

@bot.event
async def on_disconnect():
    global session
    if session:
        await session.close()
    print("Closed aiohttp session.")

# General Commands

@bot.command(help="Replies with Pong!")
async def ping(ctx):
    await ctx.send("Pong!")

@bot.command(name="status", help="Shows KITTE Bot status and info")
async def status(ctx):
    current_time = time.time()
    uptime_seconds = int(current_time - start_time)
    uptime = time.strftime("%H:%M:%S", time.gmtime(uptime_seconds))
    latency = round(bot.latency * 1000)
    server_count = len(bot.guilds)
    embed = discord.Embed(title="KITTIE-BOT Status", color=discord.Color.purple())
    embed.add_field(name="Uptime", value=uptime, inline=True)
    embed.add_field(name="Latency", value=f"{latency}ms", inline=True)
    embed.add_field(name="Servers", value=f"{server_count}", inline=True)
    embed.add_field(name="Python", value=platform.python_version(), inline=True)
    embed.add_field(name="Library", value=f"discord.py {discord.__version__}", inline=True)
    await ctx.send(embed=embed)

@bot.command(name="info", help="Shows bot creator and helpful links")
async def info(ctx):
    embed = discord.Embed(
        title="About KITTIE",
        description="Cat bot meow",
        color=discord.Color.purple()
    )
    embed.add_field(name="Creator", value="JesusGrandma", inline=True)
    embed.add_field(name="Support / GitHub", value="[Click Here](https://github.com/JesusGrandma/KITTE-BOT)", inline=False)
    try:
        await ctx.author.send(embed=embed)
        if ctx.guild:
            await ctx.send("I've sent you a DM with the info")
    except discord.Forbidden:
        await ctx.send("❌ I couldn't send you a DM. Please check your privacy settings.")

# Fun Commands

@bot.command(name="catfact", help="Sends a random cat fact")
async def catfact(ctx):
    fact = get_random_cat_fact()
    await ctx.send(f"**Cat Fact:** {fact}")

@bot.command(name="kittyuh", help="Sends a random cat picture")
async def cat(ctx):
    folder = "cat-pics"
    if not os.path.exists(folder):
        await ctx.send("❌ No cat pics folder found!")
        return
    files = [f for f in os.listdir(folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    if not files:
        await ctx.send("😿 No cat pics found.")
        return
    chosen = random.choice(files)
    file_path = os.path.join(folder, chosen)
    emojis = ["🐱", "😺", "😻", "🐾", "😹", "😽", "🐈", "💖", "✨", "🌟"]
    chosen_emoji = random.choice(emojis)
    await ctx.send(f"{chosen_emoji} Here's a random cat for you!", file=discord.File(file_path))

# AI Commands

@bot.command(name="ask", help="Ask GPT-3.5 a question")
async def ask(ctx, *, prompt):
    try:
        answer = await asyncio.to_thread(ask_cat_gpt, prompt)
        await ctx.send(answer)
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.command(name="image", help="Generate an AI image from a prompt")
async def imagine(ctx, *, prompt):
    await ctx.send(f"Generating image for: {prompt}. Please wait as this could take a few seconds.")
    image_url = generate_image(prompt)
    if image_url:
        await ctx.send(image_url)
    else:
        await ctx.send("❌ Failed to generate image.")


# Help Command

@bot.command(name="help", help="Shows a list of available commands")
async def help_command(ctx):
    embed = discord.Embed(
        title="🐱 KITTIE-BOT Commands",
        description="Here are the available commands grouped by category:",
        color=discord.Color.purple()
    )
    # Group commands by category
    categories = {
        "General": [],
        "Music": [],
        "Fun": [],
        "AI": [],
        "Utilities": [],
        "Blackjack": [],
        "Currency": [],
        "Sokoban": [],
        "Plants": [],
    }

    for command in bot.commands:
        if command.hidden:
            continue
        # Categorize commands based on their name or purpose
        if command.name in ["ping", "status", "info", "leave", "lastseen"]:
            categories["General"].append(command)
        elif command.name in ["play", "stop", "queue", "skip", "theme"]:
            categories["Music"].append(command)
        elif command.name in ["catfact", "kittyuh", "unscramble", "type", "dog", "cat", "joke", "rushb", "roulette", "haiku", "bengif"]:
            categories["Fun"].append(command)
        elif command.name in ["ask", "image", "roast", "compliment"]:
            categories["AI"].append(command)
        elif command.name in ["weather", "reddit", "steamprofile", "lyrics"]:
            categories["Utilities"].append(command)
        elif command.name in ["hit", "blackjack", "stand"]:
            categories["Blackjack"].append(command)
        elif command.name in ["balance", "give"]:
            categories ["Currency"].append(command)
        elif command.name in ["move", "sokobaninfo", "sokoban"]:
            categories ["Sokoban"].append(command)
        elif command.name in ["ptalk", "pleaderboard", "pcustomize", "pname", "pstatus", "pfertilize", "psunlight", "pwater", "padopt", "pinfo"]:
            categories ["Plants"].append(command)

                # else: # Uncomment if you want to add uncategorized commands
        #     if "Uncategorized" not in categories:
        #         categories["Uncategorized"] = []
        #     categories["Uncategorized"].append(command)
    # Add commands to the embed
    for category, commands_list in categories.items():
        if commands_list:
            value = "\n".join(f"/{cmd.name} - {cmd.help or 'No description'}" for cmd in commands_list)
            embed.add_field(name=f"**{category}**", value=value, inline=False)
    embed.set_footer(text="Use / to execute a command.")
    await ctx.send(embed=embed)

# Trolling Features

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    content = message.content.lower()

    
    if message.author.id == EDDIE_ID:  
        eddie_responses = [
            "burger with the sauce",
            "mac and cheese",
            "fuck you eddie",
            "destiny 2",
            "how much have you spent on magic",
        ]
        if random.random() < 0.05:
            await message.channel.send(random.choice(eddie_responses))
        
    elif message.author.id == DYLAN_ID: 
        dylan_responses = [
            "i love my job",
            "ive seen you try to setup a tent",
            "heard you like puking through tables",
            "blood bowl 2",
            "i knew you forgot how to turn on your computer",
            "tell sarah i said hi",
            "darkrp",
            "RUSH B CYKA BLYAT",
            "blueprints",
            "ultraloooorrd",
            "wanna get married",
            "i'll buy your car"
        ]
        if random.random() < .05:
            await message.channel.send(random.choice(dylan_responses))

    # Respond to Edbot
    elif message.author.id == EDBOT_ID:
        edbot_responses = [
            "im better",
            "edbot smells like fish",
            "meow",
            "winston eats edbot",
            "edbot is jeramey derkas's son",
            "no bitches",
            "you smell like dylan",
            "charles casavant",
            "i am supreme",
            "i have 3000 hours on dbd",
            "overwatch 2 more like... i hate myself",
        ]
        if random.random() < 0.05:
            await message.channel.send(random.choice(edbot_responses))
        

    # Respond when KITTIE is mentioned
    if "kittie" in content:
        kittie_responses = [
            "what",
            "Meow",
            "plz stop",
            "john poppytits",
            "wtf do you want",
            "i dont pay child support",
            "go cry about it",
            "touch grass",
            "skill issue",
            "imagine being you",
            "cope harder",
            "stay mad",
            "ratio",
            "you're not that guy",
            "cry me a river",
        ]
        await message.channel.send(random.choice(kittie_responses))
        # DO NOT return here

    # General cat-related responses
    cat_words = ["meow", "kitty", "cat", "purr", "treat", "whiskers", "litter", "feline"]
    chance = 0.05  # Default chance to respond
    if any(word in content for word in cat_words):
        chance = 0.25  # Higher chance if cat-related words are detected
    if random.random() < chance:
        cat_responses = [
            "What do you want, mortal?",
            "Bow before your feline overlord.",
            "You're not worthy of my attention.",
            "Pathetic human.",
            "Do you ever stop talking?",
            "Your existence annoys me.",
            "Go cry somewhere else.",
            "You're in my domain now.",
            "Touch me and face the consequences.",
            "I tolerate you... barely.",
            "You're beneath me.",
            "Don't test my patience.",
            "Leave before I make you regret it.",
            "You're lucky I don't have claws right now.",
            "Silence, peasant.",
            "Tuna > chicken",
            "Youre just going to let the dog live here?",
            "Winston your breath stinks",
            "I just need a full belly and a warm lap to sit on",
            "If I fits… I sits",
            "This catnip smells dank af bro",
            "Im way too good for dry food",
            "I get the window seat!",
        ]
        await message.channel.send(random.choice(cat_responses))

    # Always process commands after handling trolling and fun responses
    await bot.process_commands(message)  # [4][5][6]

# Main Function

async def main():
    async with bot:
        await bot.add_cog(Currency(bot))
        await bot.add_cog(Music(bot))
        await bot.add_cog(RedditMemes(bot))
        await bot.add_cog(Lyrics(bot))
        await bot.add_cog(Steam(bot))
        await bot.add_cog(WordUnscramble(bot))
        await bot.add_cog(WeatherCog(bot))
        await bot.add_cog(TypingGame(bot))
        await bot.add_cog(Blackjack(bot))
        await bot.add_cog(RandomDog(bot))
        await bot.add_cog(RandomCat(bot))
        await bot.add_cog(RandomJoke(bot))
        await bot.add_cog(RushB(bot))
        await bot.add_cog(Roulette(bot))
        await bot.add_cog(Theme(bot))
        await bot.add_cog(Haiku(bot))
        await bot.add_cog(ComplimentRoast(bot))
        await bot.add_cog(LastSeen(bot))
        await bot.add_cog(Sokoban(bot))
        await bot.add_cog(VirtualPlant(bot))
        await bot.add_cog(GifCommands(bot))
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
