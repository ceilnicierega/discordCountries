import json
import os
import random

"""
Africa:         54
Asia  :         48
Europe:         45
North America:  23
South America:  12
Oceania:        14
World:          195
"""

def normalise(string: str | list[str]) -> str | list[str]:
    if type(string) == str:
        string = string.lower()
        string = string.replace("\'", "")
        return string
    elif type(string) == list:
        return [normalise(substring) for substring in string]



def question(category: str, recents: list) -> list:

    with open("scores.json", 'r') as f:
        scores = json.load(f)

    if category == "World":
        capitals = countries
    else: capitals = continents[category]

    picked, country = False, None
    while not picked or country in recents:
        country, p = random.choice(list(capitals.keys())), random.random()
        score = scores[category][country]
        if  score == 0 and p < 1.00 or\
            score == 1 and p < 0.85 or\
            score == 2 and p < 0.55 or\
            score == 3 and p < 0.25:
            picked = True

    score_totals = {0: 0, 1: 0, 2: 0, 3: 0}
    for c in capitals.keys():
        score = scores[category][c]
        score_totals[score] += 1

    print(f"Scores so far for {category}: 0:{score_totals[0]} | 1:{score_totals[1]} | 2:{score_totals[2]} | 3:{score_totals[3]}")
    print(f"What is the capital of {country}? [{str(round(p, 2))}]")
    guess = input(">>> ").lower()
    answer = capitals[country]

    if guess.lower() == "exit":
        exit()
    elif normalise(guess) in normalise(answer):
        scores[category][country] += 1 if scores[category][country] != 3 else 0
        os.system('cls')
        print("Correct!")
    else:
        scores[category][country] = 0
        os.system('cls')
        if len(answer) == 1:
            print(f"Incorrect. The correct answer is {answer[0]}.")
        else:
            print(f"Incorrect. The correct answers are {', '.join(answer[:-1])} and {answer[-1]}.")

    recents.append(country)
    if len(recents) > 5:
        recents.pop(0)

    with open("scores.json", 'w') as f:
        json.dump(scores, f, indent=2)

    return recents

def load_scores(category, scores_value):
    pass
