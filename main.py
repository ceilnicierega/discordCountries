import json
import os
import random
import time
from dataclasses import dataclass
import asyncio
import discord
from capitals_functions import Game, normalise

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

ACTIVE_GAMES = {}
FILE_LOCK = asyncio.Lock()
admin = lambda message: message.author.id == 675982984251441173

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
        print("ENDGAME TRIGGERED", message.id)
        author = str(message.author.id)
        if author not in ACTIVE_GAMES:

            print("SENDING REPLY")
            await message.reply("You can't end a game when you haven't started one! Try `!startgame [category]` to have a go!")
        else:
            final_message  = f"Your final scores for **{ACTIVE_GAMES[author]["game"].category}**: **{ACTIVE_GAMES[author]["game"].get_score_totals_text()}**\n\n"
            final_message += "Thanks for playing! Continue whenever you want with `!startgame [category]`."

            ACTIVE_GAMES.pop(author)
            await message.reply(final_message)

    if message.content.lower().startswith("!startgame") and message.author != client.user:
        category = normalise(message.content[len("!startgame "):])

        author = str(message.author.id)
        print(category, normalise(Game.category_names))
        if author in ACTIVE_GAMES.keys():
            await message.reply("Please only play one game at once! To end your current game, try `!endgame`. :)")
        else:
            if category not in normalise(Game.category_names):
                category_message = "You didn't specify a valid category, so it has been defaulted to Europe. Bloody Eurocentrism! For more info, try `!categories`.\n"
                category = "europe"
            else:
                category_message = f"{category.title()} selected. "

            ACTIVE_GAMES[author] = {"game": Game(author, category, lock=FILE_LOCK), "ref": None, "question": None}
            await ACTIVE_GAMES[author]["game"].get_user_scores()

            question = ACTIVE_GAMES[author]["game"].make_question()
            ACTIVE_GAMES[author]["question"] = question

            score_message = f"Scores so far for {ACTIVE_GAMES[author]["game"].category}: {ACTIVE_GAMES[author]["game"].get_score_totals_text()}\n"

            if question.std_question:
                question_message = f"What is the capital of {question.country}?"
            else:
                determiner = "the" if len(question.answers) == 1 else "a"
                answer = random.choice(question.answers) if isinstance(question.answers, list) else question.answers[0]
                question_message = f"{answer} is {determiner} capital of which country?"
            ACTIVE_GAMES[author]["ref"] = (await message.reply(category_message+score_message+question_message)).id
            print(ACTIVE_GAMES)

    if message.reference and (str(message.author.id) in ACTIVE_GAMES):
        replied_to = message.reference.message_id
        author = str(message.author.id)

        print(message.reference, message.author.id, replied_to)
        print(ACTIVE_GAMES)

        if ACTIVE_GAMES[author]["ref"] == replied_to and "!endgame" not in normalise(message.content):
            guess = normalise(message.content)

            correct = await ACTIVE_GAMES[author]["game"].process_answer(guess, ACTIVE_GAMES[author]["question"])

            if correct:
                success_message = "Correct! "
            elif ACTIVE_GAMES[author]["question"].std_question:
                if len(ACTIVE_GAMES[author]["question"].answers) == 1:
                    success_message = f"Incorrect. The correct answer is {ACTIVE_GAMES[author]["question"].answers[0]}. "
                else:
                    success_message =  f"Incorrect. The correct answers are {', '.join(ACTIVE_GAMES[author]["question"].answers[:-1])} and {ACTIVE_GAMES[author]["question"].answers[-1]}. "
            else:
                success_message = f"Incorrect. The correct answer is {ACTIVE_GAMES[author]["question"].country}. "

            question = ACTIVE_GAMES[author]["game"].make_question()
            ACTIVE_GAMES[author]["question"] = question

            score_message = f"Scores so far for {ACTIVE_GAMES[author]["game"].category}: {ACTIVE_GAMES[author]["game"].get_score_totals_text()}\n"

            if question.std_question:
                question_message = f"What is the capital of {question.country}?"
            else:
                determiner = "the" if len(question.answers) == 1 else "a"
                answer = random.choice(question.answers) if isinstance(question.answers, list) else question.answers[0]
                question_message = f"{answer} is {determiner} capital of which country?"
            ACTIVE_GAMES[author]["ref"] = (await message.reply(success_message + score_message + question_message)).id

    if message.content.lower().startswith("!categories") and message.author != client.user:
        await message.reply("""You can play the capitals game on a variety of categories: 
Africa: 54 countries
Asia: 48
Europe: 45
North America: 23
South America: 12
Oceania: 14
World: 195
Try `!startgame South America` to get started.
""")

    if message.content.lower() == "!active_games" and admin(message):
        await message.reply(ACTIVE_GAMES)

    if message.content.lower().startswith("!scores") and message.author != client.user:
        async with FILE_LOCK:
            with open("userscores.json", 'r') as f:
                userscores = json.load(f)

        print(userscores.keys())
        scores = Game.code_to_scores(userscores[str(message.author.id)])

        print(userscores, scores)

        return_messages = []

        for category in normalise(Game.category_names):
            return_message = f">>> ## {category.title()}\n"

            st = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0}

            for c in scores[category].keys():
                score = scores[category][c]
                st[score] += 1

            return_message += f"- Proficiency **0**: **{st[0]}**\n"
            return_message += f"- Proficiency **1**: **{st[1]}**\n"
            return_message += f"- Proficiency **2**: **{st[2]}**\n"
            return_message += f"- Proficiency **3**: **{st[3]}**\n"
            return_message += f"- Proficiency **4**: **{st[4]}**\n"
            return_message += f"- Proficiency **5**: **{st[5]}**"

            return_messages.append(return_message)

        print(return_messages)

        await message.reply(return_messages[0])
        for i, return_message in enumerate(return_messages[0:-1]):
            await message.channel.send(return_messages[i+1])

    if message.content.lower().startswith("!cls ") and admin(message) and message.author != client.user:
        content = message.content[len("!cls "):].split()
        valid = False
        if len(content) in [2,3]:
            user, category = content[0], ' '.join(content[1:])
            valid = True
        elif len(content) == 1:
            user, category = content[0], None
            valid = True
        else:
            print(content, len(content))
            await message.reply("Invalid formatting. Try `!cls [user_id] [category | leave blank for all]`")

        if valid:
            await Game.clearuser(user, FILE_LOCK, normalise(category))
            await message.reply(f"@silent User <@{user}>'s progress successfully reset.")

client.run(os.getenv('DISCORD_TOKEN_COUNTRIES_BOT'))
