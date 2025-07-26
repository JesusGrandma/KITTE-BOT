import discord
from discord.ext import commands
from datetime import date
import os

class School(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Updated start dates
        self.people = {
            'dylan': date(2025, 8, 20),
            'kayla': date(2025, 8, 21),
            'ben': date(2025, 8, 21),
            'brittany': date(2025, 8, 21),
            'keegan': date(2025, 8, 14) 
        }
        # Fun messages for each teacher
        self.fun_messages = {
            'dylan': "Dylan, hope you enjoyed your last moments of peace—your students are already plotting your downfall.",
            'kayla': "Kayla, the only thing more chaotic than your classroom will be your caffeine withdrawal.",
            'ben': "Ben, brace yourself for a tidal wave of homework excuses and existential dread.",
            'brittany': "Brittany, time to trade your freedom for lesson plans and questionable cafeteria food.",
            'keegan': "Keegan, summer's over—prepare to dodge spitballs and rethink your life choices!"
        }
        self.user_ids = {
            'dylan': int(os.getenv('DYLAN_ID', 0)),
            'kayla': int(os.getenv('KAYLA_ID', 0)),
            'ben': int(os.getenv('BEN_ID', 0)),
            'brittany': int(os.getenv('BRITTANY_ID', 0)),
            'keegan': int(os.getenv('KEEGAN_ID', 0)), 
        }
        print("[School Cog] Loaded user IDs:", self.user_ids)

    @commands.command(name='school')
    async def days_until_school(self, ctx):
        if not ctx.message.mentions:
            await ctx.send("Please mention at least one user to check their school start date.")
            return
        today = date.today()
        for member in ctx.message.mentions:
            name = member.display_name.lower()
            # Try to match the member to a known person by user ID
            matched_name = None
            for key, uid in self.user_ids.items():
                if uid == member.id:
                    matched_name = key
                    break
            if not matched_name or matched_name not in self.people:
                await ctx.send(f"No school start date found for {member.mention}.")
                continue
            school_start = self.people[matched_name]
            delta = (school_start - today).days
            fun_message = self.fun_messages.get(matched_name, "Get ready for another year of teaching!")
            mention = member.mention
            if delta > 0:
                await ctx.send(f"\U0001F4DA There are {delta} days until school starts for {mention}! {fun_message}")
            elif delta == 0:
                await ctx.send(f"\U0001F392 School starts today for {mention}! {fun_message}")
            else:
                await ctx.send(f"\U0001F3EB School has already started for {mention}. {fun_message}")

async def setup(bot):
    await bot.add_cog(School(bot)) 