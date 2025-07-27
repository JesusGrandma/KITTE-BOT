import discord
from discord.ext import commands
import aiohttp
import random
import asyncio
from typing import Dict, List, Optional

class WordleGame:
    def __init__(self, word: str, max_attempts: int = 6):
        self.word = word.upper()
        self.max_attempts = max_attempts
        self.attempts = []
        self.game_over = False
        self.won = False
        
    def make_guess(self, guess: str) -> tuple[bool, str, List[str]]:
        """Make a guess and return (valid, message, feedback)"""
        guess = guess.upper()
        
        if len(guess) != 5:
            return False, "Guess must be exactly 5 letters long!", []
            
        if not guess.isalpha():
            return False, "Guess must contain only letters!", []
            
        if guess in self.attempts:
            return False, "You already tried that word!", []
            
        self.attempts.append(guess)
        
        if guess == self.word:
            self.game_over = True
            self.won = True
            return True, "🎉 Congratulations! You found the word!", self._get_feedback(guess)
            
        if len(self.attempts) >= self.max_attempts:
            self.game_over = True
            return True, f"Game Over! The word was: **{self.word}**", self._get_feedback(guess)
            
        return True, "Keep trying!", self._get_feedback(guess)
    
    def _get_feedback(self, guess: str) -> List[str]:
        """Get color feedback for a guess"""
        feedback = []
        word_letters = list(self.word)
        guess_letters = list(guess)
        
        # First pass: mark correct letters
        for i in range(5):
            if guess_letters[i] == word_letters[i]:
                feedback.append("🟩")  # Green
                word_letters[i] = None  # Mark as used
                guess_letters[i] = None  # Mark as used
            else:
                feedback.append("⬜")  # White (placeholder)
        
        # Second pass: mark yellow letters
        for i in range(5):
            if guess_letters[i] is not None:
                if guess_letters[i] in word_letters:
                    feedback[i] = "🟨"  # Yellow
                    # Remove the first occurrence from word_letters
                    word_letters[word_letters.index(guess_letters[i])] = None
                else:
                    feedback[i] = "⬛"  # Black
                    
        return feedback
    
    def get_display(self) -> str:
        """Get the current game display"""
        display = []
        for attempt in self.attempts:
            feedback = self._get_feedback(attempt)
            display.append(f"{' '.join(feedback)} | {attempt}")
        
        # Add empty rows for remaining attempts
        remaining = self.max_attempts - len(self.attempts)
        for _ in range(remaining):
            display.append("⬜ ⬜ ⬜ ⬜ ⬜ | _____")
            
        return "\n".join(display)

class Wordle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_games: Dict[int, WordleGame] = {}  # user_id -> game
        
    async def get_random_word(self) -> str:
        """Get a random 5-letter word from an API"""
        try:
            # Try multiple APIs for reliability
            apis = [
                "https://random-word-api.herokuapp.com/word?length=5",
                "https://api.api-ninjas.com/v1/randomword?type=noun&length=5",
                "https://wordsapiv1.p.rapidapi.com/words/?random=true&letters=5"
            ]
            
            async with aiohttp.ClientSession() as session:
                for api_url in apis:
                    try:
                        async with session.get(api_url, timeout=5) as resp:
                            if resp.status == 200:
                                data = await resp.json()
                                if isinstance(data, list):
                                    word = data[0]
                                elif isinstance(data, dict):
                                    word = data.get('word', '')
                                else:
                                    word = str(data)
                                
                                if len(word) == 5 and word.isalpha():
                                    return word.upper()
                    except:
                        continue
                        
            # Fallback to a curated list if APIs fail
            fallback_words = [
                "APPLE", "BEACH", "CHAIR", "DREAM", "EARTH", "FLAME", "GRAPE", "HEART",
                "IMAGE", "JUICE", "KNIFE", "LEMON", "MUSIC", "NIGHT", "OCEAN", "PEACE",
                "QUEEN", "RADIO", "SMILE", "TABLE", "UNITY", "VOICE", "WATER", "YOUTH",
                "ZEBRA", "BRAVE", "CLOUD", "DANCE", "EAGLE", "FAITH", "GLORY", "HAPPY",
                "IDEAL", "JOYCE", "KARMA", "LIGHT", "MAGIC", "NOBLE", "OPERA", "PRIDE",
                "QUIET", "RADAR", "SHINE", "TRUTH", "UNITE", "VALUE", "WORLD", "YIELD"
            ]
            return random.choice(fallback_words)
            
        except Exception as e:
            print(f"Error getting random word: {e}")
            # Ultimate fallback
            return "HELLO"
    
    @commands.command(name="kwordle", help="Start a new Wordle game! Guess the 5-letter word in 6 attempts.")
    async def wordle(self, ctx):
        user_id = ctx.author.id
        
        if user_id in self.active_games:
            await ctx.send("You already have an active Wordle game! Use `/wordleguess <word>` to continue or `/wordlegiveup` to start over.")
            return
            
        word = await self.get_random_word()
        game = WordleGame(word)
        self.active_games[user_id] = game
        
        embed = discord.Embed(
            title="🎯 Wordle Game Started!",
            description="I'm thinking of a 5-letter word. You have 6 attempts to guess it!\n\nUse `/wordleguess <word>` to make a guess.\nUse `/wordlegiveup` to give up.",
            color=discord.Color.green()
        )
        embed.add_field(name="How to play", value="🟩 = Correct letter, correct position\n🟨 = Correct letter, wrong position\n⬛ = Letter not in word", inline=False)
        embed.set_footer(text=f"Game started by {ctx.author.display_name}")
        
        await ctx.send(embed=embed)
    
    @commands.command(name="wordleguess", help="Make a guess in your Wordle game. Usage: /wordleguess <5-letter word>")
    async def wordleguess(self, ctx, *, guess: str):
        user_id = ctx.author.id
        
        if user_id not in self.active_games:
            await ctx.send("You don't have an active Wordle game! Use `/wordle` to start one.")
            return
            
        game = self.active_games[user_id]
        
        if game.game_over:
            await ctx.send("This game is already over! Use `/wordle` to start a new game.")
            return
            
        valid, message, feedback = game.make_guess(guess)
        
        if not valid:
            await ctx.send(f"❌ {message}")
            return
            
        # Create embed for the guess result
        embed = discord.Embed(
            title="Wordle Guess",
            description=game.get_display(),
            color=discord.Color.blue()
        )
        
        if game.won:
            embed.color = discord.Color.green()
            embed.title = "🎉 Wordle Won!"
            embed.description += f"\n\n{message}"
            del self.active_games[user_id]
        elif game.game_over:
            embed.color = discord.Color.red()
            embed.title = "💀 Wordle Lost!"
            embed.description += f"\n\n{message}"
            del self.active_games[user_id]
        else:
            embed.title = f"Wordle - Attempt {len(game.attempts)}/{game.max_attempts}"
            embed.description += f"\n\n{message}"
            
        embed.set_footer(text=f"Guessed by {ctx.author.display_name}")
        await ctx.send(embed=embed)
    
    @commands.command(name="wordlegiveup", help="Give up your current Wordle game and reveal the word.")
    async def wordlegiveup(self, ctx):
        user_id = ctx.author.id
        
        if user_id not in self.active_games:
            await ctx.send("You don't have an active Wordle game!")
            return
            
        game = self.active_games[user_id]
        word = game.word
        
        embed = discord.Embed(
            title="🏳️ Wordle Game Given Up",
            description=f"The word was: **{word}**\n\n{game.get_display()}",
            color=discord.Color.orange()
        )
        embed.set_footer(text=f"Given up by {ctx.author.display_name}")
        
        del self.active_games[user_id]
        await ctx.send(embed=embed)
    
    @commands.command(name="wordlestatus", help="Check the status of your current Wordle game.")
    async def wordlestatus(self, ctx):
        user_id = ctx.author.id
        
        if user_id not in self.active_games:
            await ctx.send("You don't have an active Wordle game! Use `/wordle` to start one.")
            return
            
        game = self.active_games[user_id]
        
        embed = discord.Embed(
            title="📊 Wordle Game Status",
            description=game.get_display(),
            color=discord.Color.blue()
        )
        embed.add_field(name="Attempts", value=f"{len(game.attempts)}/{game.max_attempts}", inline=True)
        embed.add_field(name="Status", value="Active" if not game.game_over else "Game Over", inline=True)
        embed.set_footer(text=f"Game status for {ctx.author.display_name}")
        
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Wordle(bot)) 