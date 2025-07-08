import discord
from discord.ext import commands
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

class ComplimentRoast(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client = OpenAI()  # Uses API key from environment

    async def generate_response(self, prompt):
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            temperature=0.8
        )
        return response.choices[0].message.content.strip()

    @commands.command(help="Roast a server member")
    async def roast(self, ctx, member: discord.Member):
        prompt = f"Roast for someone named {member.display_name}."
        roast = await self.generate_response(prompt)
        await ctx.send(f"{member.mention} {roast}")

    @commands.command(help="Compliment a server member")
    async def compliment(self, ctx, member: discord.Member):
        prompt = f"Compliment for someone named {member.display_name}."
        compliment = await self.generate_response(prompt)
        await ctx.send(f"{member.mention} 💖 {compliment}")

def setup(bot):
    bot.add_cog(ComplimentRoast(bot))
