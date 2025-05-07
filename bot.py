import discord
from discord.ext import commands
from dotenv import load_dotenv
from cat_facts import get_random_cat_fact
import os
from image_gen import generate_image
from chatgpt_handler import ask_cat_gpt
import random
import time
import platform
import asyncio

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise ValueError("DISCORD_TOKEN not found in environment variables")

# Setup Discord bot
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True

bot = commands.Bot(command_prefix="/", intents=intents, help_command=None)
start_time = time.time()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name="welcome")
    if channel:
        await channel.send(f"🎉 Welcome to the server, {member.mention}! We're glad to have you here! 🐱")

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

@bot.command(name="image", help="Generate an AI image from a prompt")
async def image(ctx, *, prompt):
    await ctx.send(f"Generating image for: `{prompt}`. Please be patient it may take a second... ")

    image_url = generate_image(prompt)

    if image_url:
        embed = discord.Embed(
            title="Generated Image",
            description=f"Prompt: *{prompt}*",
            color=discord.Color.purple()
        )
        embed.set_image(url=image_url)
        await ctx.send(embed=embed)
    else:
        await ctx.send("❌ Failed to generate image.")


@bot.command(name="kittyuh", help="Sends a random cat picture")
async def cat(ctx):
    folder = "cat-pics"
    
    # Check if the folder exists
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

@bot.command(name="ask", help="Ask GPT-3.5 a question")
async def ask(ctx, *, prompt):
    try:
        # Run the GPT-3.5 ask function asynchronously
        answer = await asyncio.to_thread(ask_cat_gpt, prompt)
        await ctx.send(answer)
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.command(name="help", help="General help command")
async def help_command(ctx):
    embed = discord.Embed(title="🐱 KITTIE-BOT Commands", color=discord.Color.purple())
    
    cogs = {}
    for command in bot.commands:
        if command.hidden:
            continue
        cog_name = command.cog_name or "General"
        if cog_name not in cogs:
            cogs[cog_name] = []
        cogs[cog_name].append(command)

    for cog_name, commands_list in cogs.items():
        value = "\n".join(f"`/{cmd.name}` - {cmd.help or 'No description'}" for cmd in commands_list)
        embed.add_field(name=f"🐱 {cog_name}", value=value, inline=False)

    await ctx.send(embed=embed)

@bot.command(name="catfact", help="Sends a random cat fact ")
async def catfact(ctx):
    fact = get_random_cat_fact()
    await ctx.send(f"**Cat Fact:** {fact}")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
        
    if message.content.startswith("/"):
        await bot.process_commands(message)
        return

    content = message.content.lower()
    cat_words = ["meow", "kitty", "cat", "purr", "treat", "whiskers", "litter", "feline"]

    if "edbot" in content:
        edbot_responses = [
            "fuck edbot",
            "kitte better than edbot",
            "pffft, Edbot wishes it had whiskers like mine.",
            "*curls up on Edbot's keyboard and takes a nap*",
            "Edbot smells like expired tuna.",
            "I'm the real purr-fessional here, not Edbot"
        ]
        if random.random() < 0.75:
            await message.channel.send(random.choice(edbot_responses))
            return

    chance = 0.05
    if any(word in content for word in cat_words):
        chance = 0.25

    if random.random() < chance:
        cat_responses = [
            "Meow? ", 
            "*licks paw*",  
            "*purrs loudly* ", 
            "Did you say... tuna? ", 
            "*knocks cup off table* ", 
            "*stares at you silently from the corner*"
        ]
        await message.channel.send(random.choice(cat_responses))

    await bot.process_commands(message)

def load_extensions():
    bot.load_extension("music")
    bot.load_extension("reddit_memes")

if __name__ == "__main__":
    load_extensions()
    bot.run(TOKEN)
