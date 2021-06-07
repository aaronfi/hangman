#!/usr/bin/env python

# See https://pypi.org/project/inquirer/
# This library gives us a succinct way of obtaining all kinds of 
# user input from the command-line.
import inquirer
import random
import string
import os
import sys

# See https://docs.python.org/3/howto/curses.html
# This library adds a "cursor" ability to the text we print in our 
# terminal.  By cursor, I mean something like a mouse cursor: we
# can change the location where the next character will be printed.
# In doing so, we can overwrite previous text, even "refresh" the screen! 
import curses
from curses import wrapper

# See https://docs.python.org/3/library/enum.html
# This kind of class gives us the ability to create enumerated lists.
# This allows for cleaner programming.
from enum import Enum

class DifficultyLevel(Enum):
    easy     = "1-5",   lambda x: len(x) <= 5
    medium   = "6-9",   lambda x: 6 <= len(x) <= 9
    hard     = "10-15", lambda x: 10 <= len(x) <= 15
    insane   = "16+",   lambda x: len(x) >= 16
    surprise = "1+",    lambda x: True


class Guess(Enum):
    unguessed = 1,
    correct = 2,
    incorrect = 3


class Hangman:
    def __init__(self, screen, name, level):
        self.screen = screen
        self.player_name = name  # TODO not currently using player_name for anything.  Fix this!
        self.difficulty_level = level

    def init_game(self):
        self.screen.clear()

        check_length = DifficultyLevel[self.difficulty_level].value[1]
        
        with open('dictionary.txt') as f:
            words = [word for word in f.read().splitlines() if check_length(word)]
            if not words:
                raise ValueError(
                    "Couldn't find any words whose length matched "
                    f"the requirements of difficulty level '#{self.difficulty_level}'."
                )

            self.target_word = random.choice(words)

        self.revealed_word = ['-'] * len(self.target_word)
        self.num_strikes_remaining = 10
        self.num_unrevealed_letters = len(self.target_word)
        self.guesses = { letter: Guess.unguessed for letter in string.ascii_lowercase }
        self.moves = []  # TODO never ended up using this.  Put it to use or remove!
        # TODO ideas:  print out the "score" - number of strikes made
        # TODO ideas:  add support for compound phrases, e.g. movie titles
        # TODO ideas:  add level of difficulty support for number of words, not just length of individual word
        # TODO ideas:  add an "insults.txt" file, randomly draw from it and spit out a cheeky insult to the user when they make a mistake
        # TODO ideas:  track player history across multiple games. When they're done, print out their win/loss record and percertage win rate.

    def print_board(self):
        self.screen.clear()
        self.screen.move(2,3)
        for letter in self.revealed_word:
            if letter == '-':
                self.screen.addstr(' - ', curses.color_pair(0))
            else:
                self.screen.addstr(f' {letter} ', curses.color_pair(3)) 
        self.screen.move(4,4)
        self.screen.addstr(f'guesses remaining: {self.num_strikes_remaining}', curses.color_pair(0))
        self.screen.move(6,1)

        count = 0
        for letter in sorted(self.guesses.keys()):
            guess = self.guesses[letter]
            count += 1

            if guess == Guess.unguessed:
                self.screen.addstr(f'   {letter}   ', curses.color_pair(0))
            elif guess == Guess.correct:
                self.screen.addstr(f'   {letter}   ', curses.color_pair(3))
            elif guess == Guess.incorrect:
                self.screen.addstr(f'   {letter}   ', curses.color_pair(2))
            else:
                raise ValueError("Programming error.")

            if count == 13:
                self.screen.move(7,1)

        self.screen.move(9,4)
        self.screen.addstr("What's your next letter? ")

    def get_and_process_next_guess(self):
        while True:
            guess = chr(self.screen.getch())  # reads one character of input from the user
            if guess.isalpha():
                if guess in self.target_word:
                    for i in [pos for pos, char in enumerate(self.target_word) if char == guess]:
                        self.num_unrevealed_letters -= 1
                        self.revealed_word[i] = guess
                        self.guesses[guess] = Guess.correct
                elif self.guesses[guess] == Guess.unguessed:
                    self.guesses[guess] = Guess.incorrect
                    self.num_strikes_remaining -= 1
                return

    def play_game(self):
        while True:
            self.init_game()
            self.print_board()

            while self.num_strikes_remaining > 0 and self.num_unrevealed_letters > 0:
                self.get_and_process_next_guess()
                self.print_board()

            self.print_board()
            self.screen.move(9,4)
            if self.num_strikes_remaining == 0:
                self.screen.addstr(f"You lose!  The word was {self.target_word}")
            elif self.num_unrevealed_letters == 0:
                self.screen.addstr("You win!                         ")
            self.screen.refresh()
            self.screen.move(11,4)

            self.screen.addstr("Would you like to play again? ")
            while True:
                answer = chr(self.screen.getch())
                if answer == 'n':
                    return
                elif answer == 'y':
                    break

def main(screen, name, level):
    # boilerplate code to initialize our colors
    curses.start_color()
    curses.use_default_colors()
    for i in range(0, curses.COLORS):
        curses.init_pair(i + 1, i, -1)

    # now we create and begin our game!
    hangman = Hangman(screen=screen, name=name, level=level)
    hangman.play_game()


questions = [
    inquirer.Text('name', message='What is your name?'),
    inquirer.List(
        'level',
        message="How many letters should the word be?",
        choices=[(f'{e.name} ({e.value[0]})', e.name) for e in DifficultyLevel],
        carousel=True
    ),
]
os.system('cls || clear')  # clears the screen, works on either Windows or Mac/Linux
answers = inquirer.prompt(questions)
os.system('cls || clear')

# This wrapper() method from the curses library initializes our screen.
# See https://docs.python.org/3/library/curses.html#curses.wrapper
wrapper(main, answers['name'], answers['level'])  
