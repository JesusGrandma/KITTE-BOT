import discord
from discord.ext import commands
import os
import openai

class WouldYouRather(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    @commands.command(name="wyr", help="Generates a unique, unhinged 'Would You Rather' question using AI.")
    async def wyr(self, ctx):
        prompt = (
            "Generate a unique, wild, and unhinged 'Would You Rather' question. "
            "Make it bizarre, unexpected, and funny, but still safe for work. "
            "Format it as: 'Would you rather ... or ...?'"
        )
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=60,
                temperature=1.2,
            )
            wyr_question = response.choices[0].message.content.strip()
            await ctx.send(wyr_question)
        except Exception as e:
            await ctx.send(f"❌ Error generating question: {e}")

def setup(bot):
    bot.add_cog(WouldYouRather(bot)) 