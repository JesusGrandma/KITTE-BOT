import random
import asyncio
from discord.ext import commands

WORDS = [
    "apple", "banana", "grape", "orange", "cherry", "mango", "pineapple",
    "blueberry", "strawberry", "raspberry", "pear", "watermelon", "kiwi",
    "apricot", "peach", "plum", "fig", "pomegranate", "papaya", "lemon",
    "lime", "cantaloupe", "melon", "tomato", "carrot", "spinach", "lettuce",
    "broccoli", "cauliflower", "cabbage", "onion", "garlic", "potato", "sweetpotato",
    "zucchini", "pepper", "cucumber", "asparagus", "mushroom", "corn", "peas",
    "pumpkin", "squash", "eggplant", "chili", "beet", "radish", "turnip", "celery",
    "cabbage", "artichoke", "parsnip", "mustard", "sunflower", "lily", "daisy", "rose",
    "orchid", "tulip", "lavender", "jasmine", "violet", "lilac", "hydrangea", "daffodil",
    "petunia", "carnation", "sunflower", "peony", "camellia", "honeysuckle", "marigold",
    "poppy", "begonia", "bamboo", "oak", "pine", "maple", "birch", "cedar", "redwood",
    "spruce", "fir", "willow", "sequoia", "palm", "coconut", "mango", "banana", "apple",
    "tangerine", "apricot", "pear", "grapefruit", "melon", "watermelon", "cantaloupe",
    "cherry", "blueberry", "strawberry", "raspberry", "fig", "blackberry", "currant",
    "grape", "nectarine", "plum", "kiwi", "papaya", "coconut", "lime", "lemon", "orange",
    "tangerine", "plum", "pear", "peach", "pineapple", "apricot", "mango", "coconut",
    "almond", "cashew", "pistachio", "walnut", "pecan", "hazelnut", "macadamia",
    "peanut", "cherry", "watermelon", "melon", "cantaloupe",
    "fig", "date", "raisin", "sultana", "currant", "cranberry", "grape", "plum", "cherry",
    "peach", "apricot", "fig", "guava", "lychee", "jackfruit", "papaya", "mango", "kiwi",
    "pineapple", "melon", "banana", "apple", "pear", "persimmon", "quince", "apricot", "plum",
    "nectarine", "lemon", "lime", "orange", "pomegranate", "tangerine", "lime", "grapefruit",
    "starfruit", "fig", "jackfruit", "grapes", "blackberry", "cranberry", "strawberry",
    "blueberry", "gooseberry", "currant", "tomato", "avocado", "cucumber",
    "pumpkin", "carrot", "beetroot", "radish", "parsnip", "turnip", "chard", "spinach", "lettuce",
    "cabbage", "broccoli", "cauliflower", "artichoke", "asparagus", "zucchini", "eggplant",
    "chili", "pepper", "garlic", "onion", "leek", "shallot", "celery", "pea", "corn", "soybean",
    "lentil", "chickpea", "fava", "pinto", "kidney", "mung", "adzuki",
    "butternut", "sweetpotato", "yam", "potato", "cassava", "yucca", "jicama", "tarot", "mushroom",
    "truffle", "oyster", "shiitake", "portobello", "chanterelle",  "morel", "enoki",
    "caviar", "sushi", "taco", "burrito", "pizza", "pasta", "bagel",
    "toast", "croissant", "donut", "muffin", "cookie", "pie", "cake", "brownie", "cupcake",
    "icecream", "chocolate", "truffle", "tart", "cheesecake", "pudding", "pancake", "waffle",
    "smoothie", "milkshake", "mocha", "latte", "espresso", "cappuccino", "americano", "tea",
    "green", "black", "oolong", "chai", "matcha", "mint", "ginger", "chamomile",
    "honey", "syrup", "coffee", "latte", "frappuccino", "macchiato", "mocha", "cappuccino",
    "decaf", "americano", "iced", "smoothie", "soda", "water", "juice", "lemonade",
    "cocktail", "mocktail", "wine", "beer", "whiskey", "vodka", "rum", "tequila", "gin", "champagne",
    "brandy", "scotch", "brandy", "mead", "vodka", "cider", "whiskey", "cognac", "rum", "beer",
    "wine", "brandy", "champagne", "spirits", "liqueur", "absinthe", "moonshine", "shot", "margarita",
    "cocktail", "pina", "colada", "mojito", "mimosa", "bloodymary", "bellini", "caipirinha", "negroni",
    "martini", "cosmopolitan", "manhattan",
    "shandy", "highball", "lowball", "negroni", "mint", "lemon", "lime", "syrup",
    "ginger", "coke", "tonic", "lemonade", "gingerale", "carbonated", "nonalcoholic", "soda", "seltzer",
    "mocktail", "sangria", "splash", "beer", "cider", "brandy", "rum", "vodka", "gin"
]


class WordUnscramble(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="unscramble", help="An unscramble game! Usage: /unscramble")
    async def unscramble(self, ctx):
        await ctx.send("KITTE will win, but lets play.")
        word = random.choice(WORDS)
        scrambled = ''.join(random.sample(word, len(word)))

        while scrambled == word:
            scrambled = ''.join(random.sample(word, len(word)))

        await ctx.send(f"Unscramble this word: **{scrambled}**\n You have 20 seconds!")

        def check(m):
            return m.channel == ctx.channel and m.author == ctx.author

        try:
            msg = await self.bot.wait_for('message', timeout=20.0, check=check)
            if msg.content.lower() == word:
                await ctx.send("Correct! Wow, you're smart... but not as smart as me :)")
            else:
                await ctx.send(f"Nope! The correct word was **{word}**. You're not as smart as me.")
        except asyncio.TimeoutError:
            await ctx.send(f"Time's up! The correct word was **{word}**.")

async def setup(bot):
    await bot.add_cog(WordUnscramble(bot))
