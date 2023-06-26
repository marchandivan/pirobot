import random

class EightBallGame(object):
    answers = [
        "It is certain.",
        "It is decidedly so.",
        "Without a doubt.",
        "Yes definitely.",
        "You may rely on it.",
        "As I see it, yes.",
        "Most likely.",
        "Outlook good.",
        "Yes.",
        "Signs point to yes.",
        "Reply hazy, try again.",
        "Ask again later.",
        "Better not tell you now.",
        "Cannot predict now.",
        "Concentrate and ask again.",
        "Don't count on it.",
        "My reply is no.",
        "My sources say no.",
        "Outlook not so good.",
        "Very doubtful.",
    ]

    @staticmethod
    def play(args):
        return random.choice(EightBallGame.answers)

class Dice(object):

    @staticmethod
    def play(args):
        if args:
            return random.choice(args)
        else:
            return random.choice([str(d) for d in range(1, 6)])

class Games(object):
    games = {
        "8ball": EightBallGame,
        "dice": Dice
    }

    @staticmethod
    def play(game, args):
        if game in Games.games:
            return Games.games[game].play(args)
