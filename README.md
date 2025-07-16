# KITTE-BOT

---

**A modular, feature-rich Discord bot with games, AI, music, trivia, fun commands, and more.**

---

## Features

| Category      | Highlights                                                                 |
|--------------|----------------------------------------------------------------------------|
| Music        | YouTube playback, queue, skip, stop, loop                                  |
| AI           | ChatGPT, image generation, roasts, compliments, haiku, TTS                 |
| Games        | Connect Four, Blackjack, Unscramble, Roulette, Trivia, Would You Rather    |
| Fun & Info   | Jokes, memes, GIFs, cat/dog pics, Urban Dictionary, weather, lyrics        |
| Utility      | Server stats, currency, Steam, last seen, feed the AI cat                  |
| Custom Cogs  | Easily add your own Python cogs                                            |

---

## Quick Start

```sh
git clone https://github.com/JesusGrandma/KITTE-BOT
cd KITTE-BOT
pip install -r requirements.txt
```

Create a `.env` file in the root directory:
```env
DISCORD_TOKEN=your_discord_bot_token
OPENAI_API_KEY=your_openai_api_key
REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT, GENIUS_ACCESSS_TOKEN, STEAM_API_KEY, WEATHER_API_KEY, LASTFM_API_KEY, and ELEVENLABS_API_KEY are all supported
# Add other API keys as needed 
```

Run the bot:
```sh
python bot.py
```

---

## Major Commands & Cogs

### General
- `/ping` — Pong reply
- `/status` — Bot status and info
- `/info` — Creator and support info
- `/invite` — Bot invite link

### Music
- `/play <song>` — Play a song from YouTube
- `/stop` — Stop music and leave VC
- `/skip` — Skip current song
- `/queue` — Show song queue
- `/loop` — Toggle looping

### AI & Fun
- `/ask <question>` — Ask ChatGPT
- `/image <prompt>` — Generate an AI image
- `/wyr` — Unhinged Would You Rather question
- `/roast <user>` — AI roast a user
- `/compliment <user>` — AI compliment a user
- `/haiku [topic]` — Generate a haiku
- `/ktts <text>` — AI text-to-speech in VC

### Games
- `/connect4 @user` — Play Connect Four
- `/blackjack` — Play blackjack
- `/hit` — Draw a card in blackjack
- `/stand` — Stand in blackjack
- `/unscramble` — Unscramble a word
- `/roulette <amount> <color>` — Play roulette
- `/sokoban` — Sokoban puzzle game
- `/type` — Typing race
- `/virtualplant` — Adopt and care for a virtual plant (`/padopt`, `/pwater`, `/psunlight`, `/pfertilize`, `/pstatus`, `/pname`, `/pcustomize`, `/pleaderboard`, `/ptalk`, `/pinfo`)
- `/trivia [category] [difficulty]` — Trivia game (see `/triviacat` and `/triviadif` for options)

### Fun & Info
- `/joke` — Random joke
- `/catfact` — Random cat fact
- `/define <word>` — Dictionary definition
- `/urban <word>` — Urban Dictionary definition
- `/urbanrandom` — Random Urban Dictionary entry
- `/gif` — Fun GIFs
- `/reddit <subreddit>` — Random Reddit meme
- `/randomcat` — Random cat image
- `/randomdog` — Random dog image
- `/weather <city>` — Weather info
- `/lyrics <song>` — Song lyrics
- `/serverstats` — Server statistics
- `/steamprofile <id>` — Steam profile info
- `/feed <item>` — Feed the AI cat

### Currency
- `/balance [user]` — Check coin balance
- `/give <user> <amount>` — Give coins

### Other
- `/lastseen [user]` — Last seen online
- `/theme` — Play bot theme song
- `/rushb` — Play Rush B sound

---

## Trivia Categories & Difficulties

- `/triviacat` — List trivia categories
- `/triviadif` — List trivia difficulties

---

## Adding/Removing Cogs

Add your Python cog files to the `cogs/` directory. They will be loaded automatically if imported in `bot.py`.

---

## Contributing

Pull requests and suggestions are welcome! Please open an issue or PR for feedback or new features.

---

## License

MIT 
