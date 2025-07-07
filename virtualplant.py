from discord.ext import commands, tasks
from datetime import datetime, timedelta
import discord

class VirtualPlant(commands.Cog):
    """A virtual plant game where users can adopt, care for, and customize their own plant!"""

    # Predefined plant types
    PLANT_TYPES = ["cactus", "bonsai", "sunflower", "fern", "rose", "orchid", "succulent"]

    # ASCII art for each growth stage (cat with plant)
    PLANT_ASCII = {
        'Seed': """
 /\_/\\  
( o.o ) 
 > ^ <  🪴
""",
        'Sprout': """
 /\_/\\  
( o.o ) 
 > ^ <   🌱
   |     
  / \\    
""",
        'Young Plant': """
 /\_/\\  
( o.o ) 
 > ^ <   🌿
   |     
  /|\\    
   |     
""",
        'Mature Plant': """
 /\_/\\  
( o.o ) 
 > ^ <   🌳
   |     
  /|\\    
  / \\    
""",
        'Flowering': """
 /\_/\\  
( o.o ) 
 > ^ <   🌸
  \\ | /  
   \\|/   
    |    
   / \\   
"""
    }

    def __init__(self, bot):
        self.bot = bot
        self.user_plants = {}
        self.GROWTH_STAGES = ['Seed', 'Sprout', 'Young Plant', 'Mature Plant', 'Flowering']
        self.WATER_THRESHOLD = 3
        self.SUNLIGHT_THRESHOLD = 3
        self.FERTILIZE_THRESHOLD = 2
        self.REMINDER_INTERVAL = 60 * 60 * 6  # 6 hours
        self.reminder_loop.start()

    class Plant:
        def __init__(self, plant_type, name=None):
            self.plant_type = plant_type
            self.name = name or f"{plant_type}"
            self.water = 0
            self.sunlight = 0
            self.fertilize = 0
            self.growth_stage = 0
            self.last_care_time = datetime.utcnow()
            self.alive = True
            self.mood = 'Happy'
            self.accessories = []
            self.days_alive = 0

        def care(self, action):
            if not self.alive:
                return "Your plant is no longer alive."
            self.last_care_time = datetime.utcnow()
            if action == 'water':
                self.water += 1
            elif action == 'sunlight':
                self.sunlight += 1
            elif action == 'fertilize':
                self.fertilize += 1
            self.check_growth()
            return f"You {action}ed your plant."

        def check_growth(self):
            if (self.water >= 3 and
                self.sunlight >= 3 and
                self.fertilize >= 2 and
                self.growth_stage < 4):
                self.growth_stage += 1
                self.water = 0
                self.sunlight = 0
                self.fertilize = 0

        def status(self):
            if not self.alive:
                return f"{self.name} the {self.plant_type} has sadly died."
            stage = ['Seed', 'Sprout', 'Young Plant', 'Mature Plant', 'Flowering'][self.growth_stage]
            art = VirtualPlant.PLANT_ASCII[stage]
            return (
                f"{art}\n"
                f"{self.name} the {self.plant_type} is at the '{stage}' stage.\n"
                f"Water: {self.water}, Sunlight: {self.sunlight}, Fertilize: {self.fertilize}\n"
                f"Mood: {self.mood}"
            )

        def name_plant(self, new_name):
            self.name = new_name
            return f"Your plant is now named {self.name}."

        def add_accessory(self, accessory):
            self.accessories.append(accessory)
            return f"Added {accessory} to your plant."

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Cog {self.__class__.__name__} is ready!')

    @commands.command(name='padopt', help="Adopt a new plant. Usage: /padopt [plant_type]")
    async def adopt(self, ctx, plant_type: str):
        """Adopt a new plant of the specified type."""
        user_id = ctx.author.id
        if user_id in self.user_plants:
            await ctx.send("You already have a plant. Use /pstatus to check on it.")
            return
        plant_type = plant_type.lower()
        if plant_type not in self.PLANT_TYPES:
            await ctx.send(
                f"Invalid plant type. Available types: {', '.join(self.PLANT_TYPES)}"
            )
            return
        plant = self.Plant(plant_type)
        self.user_plants[user_id] = plant
        await ctx.send(
            f"You have adopted a {plant_type}! Use /pwater, /psunlight, and /pfertilize to care for it."
        )

    @commands.command(name='pwater', help="Water your plant. Usage: /pwater")
    async def water(self, ctx):
        """Water your plant to help it grow."""
        user_id = ctx.author.id
        if user_id not in self.user_plants:
            await ctx.send("You don't have a plant yet. Use !padopt to get one.")
            return
        response = self.user_plants[user_id].care('water')
        await ctx.send(response)

    @commands.command(name='psunlight', help="Give sunlight to your plant. Usage: /psunlight")
    async def sunlight(self, ctx):
        """Give sunlight to your plant."""
        user_id = ctx.author.id
        if user_id not in self.user_plants:
            await ctx.send("You don't have a plant yet. Use /padopt to get one.")
            return
        response = self.user_plants[user_id].care('sunlight')
        await ctx.send(response)

    @commands.command(name='pfertilize', help="Fertilize your plant. Usage: /pfertilize")
    async def fertilize(self, ctx):
        """Fertilize your plant for faster growth."""
        user_id = ctx.author.id
        if user_id not in self.user_plants:
            await ctx.send("You don't have a plant yet. Use /padopt to get one.")
            return
        response = self.user_plants[user_id].care('fertilize')
        await ctx.send(response)

    @commands.command(name='pstatus', help="Check the status of your plant. Usage: /pstatus")
    async def status(self, ctx):
        """Check the current status of your plant."""
        user_id = ctx.author.id
        if user_id not in self.user_plants:
            await ctx.send("You don't have a plant yet. Use /padopt to get one.")
            return
        response = self.user_plants[user_id].status()
        await ctx.send(response)

    @commands.command(name='pname', help="Name your plant. Usage: /pname [name]")
    async def name(self, ctx, *, new_name: str):
        """Give your plant a name."""
        user_id = ctx.author.id
        if user_id not in self.user_plants:
            await ctx.send("You don't have a plant yet. Use /padopt to get one.")
            return
        response = self.user_plants[user_id].name_plant(new_name)
        await ctx.send(response)

    @commands.command(name='pcustomize', help="Add an accessory to your plant. Usage: /pcustomize [accessory]")
    async def customize(self, ctx, *, accessory: str):
        """Add an accessory to your plant."""
        user_id = ctx.author.id
        if user_id not in self.user_plants:
            await ctx.send("You don't have a plant yet. Use !padopt to get one.")
            return
        response = self.user_plants[user_id].add_accessory(accessory)
        await ctx.send(response)

    @commands.command(name='pleaderboard', help="See the top plant caretakers. Usage: !pleaderboard")
    async def leaderboard(self, ctx):
        """See the top plant caretakers in the server."""
        if not self.user_plants:
            await ctx.send("No plants have been adopted yet.")
            return
        sorted_plants = sorted(
            self.user_plants.items(),
            key=lambda x: (x[1].growth_stage, x[1].days_alive),
            reverse=True
        )
        leaderboard_msg = "**Plant Care Leaderboard**\n"
        for i, (user_id, plant) in enumerate(sorted_plants[:10], 1):
            user = await self.bot.fetch_user(user_id)
            leaderboard_msg += (
                f"{i}. {user.name} - {plant.name} ({plant.plant_type}), "
                f"Stage: {self.GROWTH_STAGES[plant.growth_stage]}\n"
            )
        await ctx.send(leaderboard_msg)

    @commands.command(name='ptalk', help="Talk to your plant. Usage: !ptalk [message]")
    async def talk(self, ctx, *, message: str):
        """Talk to your plant and see how it feels."""
        user_id = ctx.author.id
        if user_id not in self.user_plants:
            await ctx.send("You don't have a plant yet. Use !padopt to get one.")
            return
        msg_lower = message.lower()
        if any(word in msg_lower for word in ['love', 'nice', 'good', 'happy', 'great']):
            self.user_plants[user_id].mood = 'Happy'
            await ctx.send(f"{self.user_plants[user_id].name} seems happy! 🌿😊")
        elif any(word in msg_lower for word in ['sad', 'bad', 'angry', 'upset']):
            self.user_plants[user_id].mood = 'Sad'
            await ctx.send(f"{self.user_plants[user_id].name} seems sad. 🌿😢")
        else:
            await ctx.send(f"{self.user_plants[user_id].name} doesn't understand, but appreciates your attention. 🌿")

    @commands.command(name='pinfo', help="Get info about the VirtualPlant cog. Usage: !pinfo")
    async def pinfo(self, ctx):
        """Get information about the VirtualPlant cog and its commands."""
        ascii_art = (
            "Cat & Plant Stages:\n"
            "Seed:\n"
            f"{self.PLANT_ASCII['Seed']}\n"
            "Sprout:\n"
            f"{self.PLANT_ASCII['Sprout']}\n"
            "Young Plant:\n"
            f"{self.PLANT_ASCII['Young Plant']}\n"
            "Mature Plant:\n"
            f"{self.PLANT_ASCII['Mature Plant']}\n"
            "Flowering:\n"
            f"{self.PLANT_ASCII['Flowering']}\n"
        )
        description = (
            f"``````"
            "**VirtualPlant Cog**\n"
            "Adopt, care for, and customize your own virtual plant!\n\n"
            f"**Available Plant Types:** {', '.join(self.PLANT_TYPES)}\n\n"
            "**Commands:**\n"
            "`!padopt [plant_type]` — Adopt a new plant.\n"
            "`!pwater` — Water your plant.\n"
            "`!psunlight` — Give sunlight to your plant.\n"
            "`!pfertilize` — Fertilize your plant.\n"
            "`!pstatus` — Check your plant's status.\n"
            "`!pname [name]` — Name your plant.\n"
            "`!pcustomize [accessory]` — Add an accessory.\n"
            "`!pleaderboard` — See the plant leaderboard.\n"
            "`!ptalk [message]` — Talk to your plant.\n"
            "`!pinfo` — Show this info message."
        )
        await ctx.send(description)

    @tasks.loop(seconds=60*60*6)  # 6 hours
    async def reminder_loop(self):
        now = datetime.utcnow()
        for user_id, plant in self.user_plants.items():
            if plant.alive and (now - plant.last_care_time) > timedelta(seconds=self.REMINDER_INTERVAL):
                user = self.bot.get_user(user_id)
                if user:
                    try:
                        await user.send(f"Your plant {plant.name} needs some care! Don't forget to water, give sunlight, or fertilize it.")
                    except Exception as e:
                        print(f"Could not send DM to {user_id}: {e}")

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Missing required argument. Please check the command usage with `!help [command]`.")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("Invalid argument provided. Please check your input.")
        elif isinstance(error, commands.CommandInvokeError):
            await ctx.send(f"An error occurred: {error.original}")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send("This command is on cooldown. Please wait before trying again.")
        elif isinstance(error, commands.CheckFailure):
            await ctx.send("You do not have permission to use this command.")
        else:
            await ctx.send(f"An unexpected error occurred: {error}")
            raise error  # Optionally log or re-raise for debugging

async def setup(bot):
    await bot.add_cog(VirtualPlant(bot))
