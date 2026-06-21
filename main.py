import json
import os
import random

import discord

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

active_games = {}

with open("categories.json", 'r') as file:
    categories = json.load(file)

def code_to_scores(string: str) -> dict:

    scores = {category: {} for category in categories.keys()}
    for i, category in enumerate(categories.keys()):

        number = int(string.split('n')[i], 16)
        j = 0
        while number > 1:
            scores[category][list(categories[category].keys())[j]] = number % 4
            number >>= 2
            j += 1

    return scores

def scores_to_code(scores: dict) -> str:
    numbers = []
    for category in scores.keys():
        number = 1
        for country in scores[category].keys():
            number <<= 2
            number += scores[category][country]
        numbers.append(number)
    return 'n'.join([hex(number)[2:] for number in numbers])

def normalise(string: str | list[str]):
    alphabet = [chr(i) for i in range(97,123)] + [' ']

    if type(string) == str:
        string = string.lower()
        string = ''.join([l if l in alphabet else '' for l in string])
        return string
    elif type(string) == list:
        return [normalise(substring) for substring in string]

def gen_question(user_id: str, category: str):
    with open("user_scores.json", 'r') as f:
        scores = json.load(f)
        user_scores = code_to_scores(scores[user_id])

    capitals = categories[category]

    picked, country = False, None
    while not picked:
        country, p = random.choice(list(capitals.keys())), random.random()
        score = user_scores[category][country]
        if  score == 0 and p < 1.00 or\
            score == 1 and p < 0.85 or\
            score == 2 and p < 0.55 or\
            score == 3 and p < 0.25:
            picked = True

    return country

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

    if message.content == "!viewvariables":
        print(json.dumps(active_games, indent=2))

    if message.content.startswith("!play"):

        author_id = str(message.author.id)
        with open("user_scores.json", 'r') as f:
            scores = json.load(f)


            if author_id not in scores:
                scores[author_id] = '1000000000000000000000000000n1000000000000000000000000n40000000000000000000000n400000000000n1000000n10000000n40000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'
                with open("user_scores.json", 'w') as f:
                    json.dump(scores, f, indent=2)

        if message.content[6:] not in categories.keys():
            category = "Europe"
        else:
            category = message.content[6:]
        question_country = gen_question(author_id, category)
        question = await message.reply(f"Test question: {question_country}")
        active_games[message.author.id] = {
            "id": question.id,
            "country": question_country,
            "answer": categories[category][question_country],
            "category": category
        }
        return

    if message.reference and message.author.id in active_games.keys():

        if message.reference.message_id == active_games[message.author.id]["id"] and message.author != client.user:

            author_id = str(message.author.id)

            with open("user_scores.json", 'r') as f:
                scores = json.load(f)
                user_scores = code_to_scores(scores[author_id])

            game = active_games[message.author.id]
            if message.content.lower() == "stop":
                await message.reply("alright cunt")
            elif normalise(message.content.lower()) in normalise(game["answer"]):
                current_score = user_scores[game["category"]][game["country"]]
                if current_score < 3:
                    user_scores[game["category"]][game["country"]] += 1
                await message.reply("Correct, good ladx")
            else:
                if len(game["answer"]) == 1:
                    await message.reply(f"Incorrect, it's {game["answer"][0]}")
                else:
                    await message.reply(f"Incorrect, would've accepted {', '.join(game["answer"][:-1])} or {game["answer"][-1]}.")

            with open("user_scores.json", 'w') as f:
                scores[author_id] = scores_to_code(user_scores)
                json.dump(scores, f, indent=2)

        del active_games[message.author.id]

    if message.content.startswith("!score"):
        with open("user_scores.json", 'r') as f:
            scores = json.load(f)
        if str(message.author.id) not in scores.keys():
            await message.reply("You've not played any games faggot. use !play to start")
        else:
            user_scores = code_to_scores(scores[str(message.author.id)])
            score_response = ">>> "
            for category in user_scores.keys():
                score_response += "\n### " + category if category != "Africa" else "### " + category
                total_score = {0:0, 1:0, 2:0, 3:0}
                for country in user_scores[category].keys():
                    total_score[user_scores[category][country]] += 1
                score_response += f"\n-# Proficiency 0: {total_score[0]} countries"
                score_response += f"\n-# Proficiency 1: {total_score[1]} countries"
                score_response += f"\n-# Proficiency 2: {total_score[2]} countries"
                score_response += f"\n-# Proficiency 3: {total_score[3]} countries"

            score_response += "\bEvery time you guess a correct capital, your proficiency in that country increases, reducing its frequency, up to a maximum of 3. Getting an incorrect answer resets your proficiency in that country to zero. Proficiency is not shared between the continent and world categories."
            await message.channel.send(score_response)

client.run(os.getenv('DISCORD_TOKEN_COUNTRIES_BOT'))
