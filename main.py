import os
import random
import discord
from unicodedata import category

from capitals_functions import Game, normalise

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

ACTIVE_GAMES = {}

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):


    if "foid" in message.content.lower() and message.author != client.user and random.random() < .05:
        await message.reply("why must you inflict such grievances on me you evil foid")

    if "kirk" in message.content.lower() and message.author != client.user and random.random() < .11:
        await message.reply(file=discord.File("kirk.png"))

    if "makima" in message.content.lower() and message.author != client.user and random.random() < .12:
        await message.reply(file=discord.File("reze.mp4"))

    if "femboy" in message.content.lower() and message.author != client.user and random.random() < .07:
        await message.reply("Kill femboys. Behead femboys. Roundhouse kick a femboys into the concrete. Slam dunk a femboys into the trashcan. Crucify filthy femboys. Defecate in a femboys food. Launch femboys into the sun. Stir fry femboys in a wok. Toss femboys into active volcanoes. Urinate into a femboys gas tank. Judo throw femboys into a wood chipper. Twist femboys head off. Report femboys to the IRS. Karate chop femboys in half. Curb stomp pregnant femboys. Trap femboys in quicksand. Crush femboys in the trash compactor. Liquefy femboys in a vat of acid. Eat femboys. Dissect femboys. Exterminate femboysin the gas chamber. Stomp femboys skulls with steel toed boots. Cremate femboys in the oven. Lobotomize femboys. Mandatory abortions for femboys. Grind femboys in the garbage disposal. Drown femboys in fried chicken grease. Vaporize femboys with a ray gun. Kick old femboys down the stairs. Feed femboys to alligators. Slice femboys with a katana.")

    if message.content.lower().startswith("!endgame") and message.author != client.user:
        author = message.author
        if author not in ACTIVE_GAMES.keys():
            message.reply("You can't end a game when you haven't started one! Try `!startgame [category]` to have a go!")
        else:
            final_message  = f"Your final scores for **{ACTIVE_GAMES[author].category}**: **{ACTIVE_GAMES[author].get_score_totals_text()}**"
            final_message += "Thanks for playing! Continue whenever you want with `!startgame [category]`."

            ACTIVE_GAMES[author].get_score_totals_text()

    if message.content.lower().startswith("!startgame") and message.author != client.user:
        content = normalise(message.content.split())
        command, category = content if len(content) > 1 else content, None
        author = message.author

        if author in ACTIVE_GAMES.keys():
            message.reply("Please only play one game at once! To end your current game, try `!endgame`. :)")
        else:
            if category not in normalise(Game.category_names):
                message.reply("You didn't specify a valid category, so it has been defaulted to Europe. Bloody Eurocentrism! For more info, try `!categories`.")
                category = "europe"
            ACTIVE_GAMES[author] = Game(author, category)
            message.reply("WIP - game should go here. :3")

    if message.content.lower().startswith("!categories") and message.author != client.user:
        message.reply("WIP", file=discord.File("itsnogame.mp3"))


client.run(os.getenv('DISCORD_TOKEN_COUNTRIES_BOT'))
