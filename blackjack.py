import random
import discord
from discord.ext import commands

# Card values and suits
suits = ['♠', '♥', '♦', '♣']
ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
values = {'A': 11, '2':2, '3':3, '4':4, '5':5, '6':6, '7':7, '8':8, '9':9, '10':10, 'J':10, 'Q':10, 'K':10}

def deal_card(deck):
    return deck.pop()

def calculate_hand(hand):
    value = sum(values[card[0]] for card in hand)
    # Adjust for Aces
    aces = sum(1 for card in hand if card[0] == 'A')
    while value > 21 and aces:
        value -= 10
        aces -= 1
    return value

def hand_str(hand):
    return ' | '.join([f"{rank}{suit}" for rank, suit in hand])

def create_deck():
    deck = [(rank, suit) for suit in suits for rank in ranks]
    random.shuffle(deck)
    return deck

class BlackjackGame:
    def __init__(self):
        self.deck = create_deck()
        self.player_hand = [deal_card(self.deck), deal_card(self.deck)]
        self.dealer_hand = [deal_card(self.deck), deal_card(self.deck)]
        self.over = False
        self.result = ""

    def player_hit(self):
        self.player_hand.append(deal_card(self.deck))
        if calculate_hand(self.player_hand) > 21:
            self.over = True
            self.result = "Bust! You lose."

    def player_stand(self):
        while calculate_hand(self.dealer_hand) < 17:
            self.dealer_hand.append(deal_card(self.deck))
        self.over = True
        player_score = calculate_hand(self.player_hand)
        dealer_score = calculate_hand(self.dealer_hand)
        if dealer_score > 21:
            self.result = "Dealer busts! You win!"
        elif player_score > dealer_score:
            self.result = "You win!"
        elif player_score < dealer_score:
            self.result = "You lose!"
        else:
            self.result = "It's a tie!"

    def get_status(self, reveal_dealer=False):
        desc = f"**Your hand** ({calculate_hand(self.player_hand)}): {hand_str(self.player_hand)}\n"
        if reveal_dealer or self.over:
            desc += f"**Dealer's hand** ({calculate_hand(self.dealer_hand)}): {hand_str(self.dealer_hand)}\n"
        else:
            desc += f"**Dealer's hand**: {self.dealer_hand[0][0]}{self.dealer_hand[0][1]} | ??\n"
        return desc

class Blackjack(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.games = {}  # Store ongoing games per user

    @commands.command(name='blackjack')
    async def start_blackjack(self, ctx):
        """Start a new game of blackjack."""
        self.games[ctx.author.id] = BlackjackGame()
        game = self.games[ctx.author.id]
        msg = f"🎲 **Blackjack!**\n{game.get_status()}\nType `/hit` to draw or `/stand` to hold."
        await ctx.send(msg)

    @commands.command(name='hit')
    async def hit(self, ctx):
        """Draw a card."""
        game = self.games.get(ctx.author.id)
        if not game or game.over:
            await ctx.send("You have no ongoing game. Start with `!blackjack`.")
            return
        game.player_hit()
        if game.over:
            msg = f"{game.get_status(reveal_dealer=True)}\n**{game.result}**"
            del self.games[ctx.author.id]
        else:
            msg = f"{game.get_status()}\nType `/hit` or `/stand`."
        await ctx.send(msg)

    @commands.command(name='stand')
    async def stand(self, ctx):
        """Stand and let the dealer play."""
        game = self.games.get(ctx.author.id)
        if not game or game.over:
            await ctx.send("You have no ongoing game. Start with `/blackjack`.")
            return
        game.player_stand()
        msg = f"{game.get_status(reveal_dealer=True)}\n**{game.result}**"
        del self.games[ctx.author.id]
        await ctx.send(msg)

async def setup(bot):
    await bot.add_cog(Blackjack(bot))
