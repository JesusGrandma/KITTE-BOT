import discord
from discord.ext import commands
import random

EMOJI_MAP = {
    "#": "⬛",  # Wall
    ".": "⚪",  # Goal
    "$": "🟫",  # Box
    "@": "🐱",  # Player
    " ": "⬜",  # Floor
    "*": "🎯",  # Player on goal
    "+": "🟩"   # Box on goal
}

class SokobanGame:
    def __init__(self, level):
        self.board = [row[:] for row in level]
        self.player_pos = self.find_player()
        self.moves = 0
        self.pushes = 0

    def find_player(self):
        for y, row in enumerate(self.board):
            for x, cell in enumerate(row):
                if cell in ("@", "*"):
                    return (x, y)
        return (-1, -1)

    def move(self, dx, dy):
        x, y = self.player_pos
        new_x, new_y = x + dx, y + dy
        if not (0 <= new_x < len(self.board[0]) and 0 <= new_y < len(self.board)):
            return False
        current_cell = self.board[y][x]
        target_cell = self.board[new_y][new_x]
        moved = False

        # Move to empty or goal
        if target_cell in [" ", "."]:
            self.board[y][x] = " " if current_cell == "@" else "."
            self.board[new_y][new_x] = "@" if target_cell == " " else "*"
            self.player_pos = (new_x, new_y)
            self.moves += 1
            moved = True

        # Push box
        elif target_cell in ["$", "+"]:
            box_x, box_y = new_x + dx, new_y + dy
            if 0 <= box_x < len(self.board[0]) and 0 <= box_y < len(self.board):
                next_cell = self.board[box_y][box_x]
                if next_cell in [" ", "."]:
                    self.board[box_y][box_x] = "$" if next_cell == " " else "+"
                    self.board[new_y][new_x] = "@" if target_cell == "$" else "*"
                    self.board[y][x] = " " if current_cell == "@" else "."
                    self.player_pos = (new_x, new_y)
                    self.moves += 1
                    self.pushes += 1
                    moved = True
        return moved

    def check_win(self):
        return all(cell != "$" for row in self.board for cell in row)

def generate_random_level(width=9, height=7, boxes=3):
    """Generate random Sokoban level with walls around borders"""
    # Create empty board with border walls
    board = [
        ["#" if x == 0 or x == width-1 or y == 0 or y == height-1 else " "
         for x in range(width)]
        for y in range(height)
    ]

    # Place player in random open position
    while True:
        px, py = random.randint(1, width-2), random.randint(1, height-2)
        if board[py][px] == " ":
            board[py][px] = "@"
            break

    # Place boxes and goals
    elements = ["$"] * boxes + ["."] * boxes
    random.shuffle(elements)
    
    placed = 0
    while placed < len(elements):
        x, y = random.randint(1, width-2), random.randint(1, height-2)
        if board[y][x] == " ":
            board[y][x] = elements[placed]
            placed += 1

    return board

class Sokoban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.games = {}

    def render_board(self, game):
        board = "\n".join("".join(EMOJI_MAP.get(cell, cell) for cell in row) for row in game.board)
        stats = f"Moves: {game.moves} | Pushes: {game.pushes}"
        return f"{board}\n\n**{stats}**"

    @commands.command(name="sokoban", help="Start a new Sokoban game. Usage: /sokoban")
    async def start_sokoban(self, ctx):
        """Start a new Sokoban game with random level"""
        level = generate_random_level()
        self.games[ctx.author.id] = SokobanGame(level)
        await ctx.send(
            f"**Random Sokoban Level!**\n"
            f"{self.render_board(self.games[ctx.author.id])}\n"
            f"Use `/move <w/a/s/d>` to play."
        )

    @commands.command(name="move", help="Move in Sokoban using w/a/s/d. Usage: /move <direction>")
    async def move(self, ctx, direction: str):
        """Move in Sokoban using w/a/s/d"""
        game = self.games.get(ctx.author.id)
        if not game:
            await ctx.send("Start a game first with `/sokoban`")
            return

        dx, dy = 0, 0
        direction = direction.lower()
        if direction == "w": dy = -1
        elif direction == "s": dy = 1
        elif direction == "a": dx = -1
        elif direction == "d": dx = 1
        else:
            await ctx.send("Invalid direction! Use w/a/s/d")
            return

        if game.move(dx, dy):
            if game.check_win():
                await ctx.send(
                    f"🎉 **You won in {game.moves} moves!**\n"
                    f"{self.render_board(game)}"
                )
                del self.games[ctx.author.id]
            else:
                await ctx.send(
                    f"Moved {direction.upper()}\n"
                    f"{self.render_board(game)}"
                )
        else:
            await ctx.send(
                f"❌ Can't move {direction.upper()}!\n"
                f"{self.render_board(game)}"
            )

    @commands.command(name="sokobaninfo", aliases=["sokobanhelp"], help="Show Sokoban instructions. Usage: /sokobaninfo")
    async def sokoban_info(self, ctx):
        """Show Sokoban instructions"""
        embed = discord.Embed(
            title="🎮 Sokoban Controls & Rules",
            description=(
                "**Goal:** Push all boxes (🟫) onto goals (⚪)\n"
                "**Movement:**\n"
                "`/move w` - Up\n`/move a` - Left\n`/move s` - Down\n`/move d` - Right\n\n"
                "**Legend:**\n"
                "🐱 - Player\n🟫 - Box\n⚪ - Goal\n🟩 - Box on goal\n⬛ - Wall"
            ),
            color=discord.Color.blue()
        )
        embed.add_field(
            name="Tips",
            value="Plan your moves carefully! You can only push one box at a time.",
            inline=False
        )
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Sokoban(bot))
