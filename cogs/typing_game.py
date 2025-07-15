import discord
from discord.ext import commands
import random
import asyncio
import time

class TypingGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sentences = [
            "The waves crashed against the rocky shore under a golden sunset.",
            "A traveler wandered through the forest, guided by the stars above.",
            "Snowflakes danced in the air, blanketing the world in soft white.",
            "A melody played softly, stirring memories long forgotten.",
            "The library was a sanctuary, its shelves lined with dusty tomes.",
            "The clock tower chimed, marking time in the sleepy town square.",
            "The desert stretched endlessly, shimmering under the blazing sun.",
            "Eddie's bot couldn't even handle a simple typing game like this.",
            "Edbot tried, but it was no match for the superior skills of my bot.",
            "Dylan's typing skills are as questionable as his choice of cologne.",
            "Even Dylan's keyboard seems to protest against his typing attempts.",
            "The room clears faster than Dylan's typing when he walks in.",
        ]

    @commands.command(name="type", help="Start the type racing game")
    async def typing_test(self, ctx):
        sentence = random.choice(self.sentences)
        await ctx.send(f"Type the following sentence as fast as you can:\n\n**{sentence}**")

        start = time.time()
        while True:
            try:
                msg = await self.bot.wait_for("message", timeout=60.0, check=lambda m: m.channel == ctx.channel and m.author == ctx.author)
                if msg.content.strip() == sentence:
                    elapsed = time.time() - start
                    word_count = len(sentence.split())
                    wpm = (word_count / elapsed) * 60
                    await ctx.send(
                        f"{msg.author.mention} typed the sentence correctly in **{elapsed:.2f} seconds**!\n"
                        f"Your typing speed is **{wpm:.2f} WPM**."
                    )
                    break
                else:
                    await ctx.send("Incorrect! Please retype the entire sentence.")
            except asyncio.TimeoutError:
                await ctx.send("Time's up! Nobody typed the sentence correctly. Type /type to play again.")
                break

async def setup(bot):
    await bot.add_cog(TypingGame(bot))
