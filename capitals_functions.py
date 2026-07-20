import json
import os
import random
from dataclasses import dataclass
import asyncio

"""
Africa:         54
Asia  :         48
Europe:         45
North America:  23
South America:  12
Oceania:        14
World:          195
"""

def normalise(string: str | list) -> None | list[str | list] | str:
    if isinstance(string, str):
        string = string.lower()
        string = string.replace("\'", "")
        return string
    elif isinstance(string, list):
        return [normalise(substring) for substring in string]

class Game:

    @dataclass
    class Question:
        country: str
        answers: list[str]
        std_question: bool
    category_names = ["Africa", "Asia", "Europe", "North America", "South America", "Oceania", "World"]
    with open("categories.json", 'r') as f:
        categories = json.load(f)
    weights = {
        0: 1.00,
        1: 0.90,
        2: 0.75,
        3: 0.55,
        4: 0.30,
        5: 0.10,
    }

    def __init__(self, user: str, category: str, lock: asyncio.Lock=None) -> None:
        self.user = user
        self.category = category
        self.lock = lock
        self.capitals = self.categories[category]
        self.recents = []
        self.scores = None
        self.score_totals = None

    @staticmethod
    async def clearuser(user: str, lock: asyncio.Lock=None, category: str=None) -> None:
        if lock:
            async with lock:
                with open("userscores.json", 'r') as f:
                    userscores = json.load(f)
        else:
            with open("userscores.json", 'r') as f:
                userscores = json.load(f)

        scores = Game.code_to_scores(userscores[user])
        if category:
            for country in scores[category].keys():
                scores[category][country] = 0
        else:
            for category in normalise(Game.category_names):
                for country in scores[category].keys():
                    scores[category][country] = 0

        userscores[user] = Game.scores_to_code(scores)
        if lock:
            async with lock:
                with open("userscores.json", 'w') as f:
                    json.dump(userscores, f, indent=2)
        else:
            with open("userscores.json", 'w') as f:
                json.dump(userscores, f, indent=2)

    @staticmethod
    def code_to_scores(string: str) -> dict:

        scores = {category: {} for category in Game.categories.keys()}
        for i, category in enumerate(Game.categories.keys()):

            number = int(string.split('n')[i], 16)
            j = 0
            while number > 1:
                scores[category][list(Game.categories[category].keys())[j]] = number % 4
                number >>= 2
                j += 1

        return scores

    @staticmethod
    def scores_to_code(scores: dict) -> str:
        numbers = []
        for category in scores.keys():
            number = 1
            for country in scores[category].keys():
                number <<= 2
                number += scores[category][country]
            numbers.append(number)
        return 'n'.join([hex(number)[2:] for number in numbers])

    async def get_user_scores(self) -> None:
        if self.lock:
            async with self.lock:
                self.scores = Game._get_user_scores(self.user)
        else:
            self.scores = Game._get_user_scores(self.user)
        self.update_score_totals()

    @staticmethod
    def _get_user_scores(user: str) -> dict:
        with open("userscores.json", 'r') as f:
            user_scores = json.load(f)
        if user in user_scores.keys():
            return Game.code_to_scores(user_scores[user])
        else:
            user_scores[user] = "1000000000000000000000000000n1000000000000000000000000n40000000000000000000000n400000000000n1000000n10000000n40000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
            with open("userscores.json", 'w') as f:
                json.dump(user_scores, f, indent=2)
            return Game.code_to_scores(user_scores[user])

    def get_score_totals_text(self):
        return (f"0:{self.score_totals[0]} | "
        f"1:{self.score_totals[1]} | "
        f"2:{self.score_totals[2]} | "
        f"3:{self.score_totals[3]} | "
        f"4:{self.score_totals[4]} | "
        f"5:{self.score_totals[5]}")

    async def update_scores(self) -> None:
        if self.lock:
            async with self.lock:
                self._update_scores()
        else:
            self._update_scores()

    def _update_scores(self) -> None:
        self.update_score_totals()
        with open("userscores.json", 'r') as f:
            user_scores = json.load(f)
        user_scores[self.user] = self.scores_to_code(self.scores)
        with open("userscores.json", 'w') as f:
            json.dump(user_scores, f, indent=2)

    def update_score_totals(self) -> None:
        score_totals = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0}

        for c in self.capitals.keys():
            score = self.scores[self.category][c]
            score_totals[score] += 1
        self.score_totals = score_totals

    def make_question(self) -> Question:
        choices = [c for c in self.capitals.keys() if c not in self.recents]

        country = random.choices(choices, weights=[Game.weights[self.scores[self.category][c]] for c in choices])[0]

        answer = self.capitals[country]

        std_question = bool(random.random() < 0.6)

        self.recents.append(country)

        return Game.Question(country, answer, std_question)

    async def process_answer(self, guess: str, question: Question) -> bool:
        prev_score = self.scores[self.category][question.country]

        if question.std_question:
            if normalise(guess) in normalise(question.answers):
                self.scores[self.category][question.country] += 1 if prev_score != 5 else 0
                await self.update_scores()
                return True
            else:
                self.scores[self.category][question.country] = 0
                await self.update_scores()
                return False
        else:
            if normalise(guess) == normalise(question.country):
                self.scores[self.category][question.country] += 1 if prev_score != 5 else 0
                await self.update_scores()
                return True
            else:
                self.scores[self.category][question.country] = 0
                await self.update_scores()
                return False

    def ask_question(self):
        question = self.make_question()

        print(f"Scores so far for {self.category}: {self.get_score_totals_text()}")

        if question.std_question:
            print(f"What is the capital of {question.country}?")
        else:
            determiner = "the" if len(question.answers) == 1 else "a"
            answer = random.choice(question.answers) if isinstance(question.answers, list) else question.answers[0]
            print(f"{answer} is {determiner} capital of which country?")

        guess = input(">>> ").lower()

        correct = self.process_answer(guess, question)
        os.system("cls")

        if correct:
            print("Correct!")
        elif question.std_question:
            if len(question.answers) == 1:
                print(f"Incorrect. The correct answer is {question.answers[0]}.")
            else:
                print(f"Incorrect. The correct answers are {', '.join(question.answers[:-1])} and {question.answers[-1]}.")
        else:
            print(f"Incorrect. The correct answer is {question.country}.")
