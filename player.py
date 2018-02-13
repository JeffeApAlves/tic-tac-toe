import os
import os.path
import locale
import sys

locale.setlocale(locale.LC_ALL, '')

class Player(object):

    PLAYER_1 = 1
    PLAYER_2 = 2

    def __init__(self,id,mark):
        self.strategy = None
        self.id = id
        self.mark = mark

    def pos_by_strategy(self):

        return self.strategy.move()
