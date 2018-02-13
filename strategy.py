import random
import numpy as np
import copy
from math import inf as infinity

from register import *
from game import *

class StrategyGame(object):

    RANDOM      = 'random'
    MINIMAX     = 'minimax'
    ALPHA_BETA  = 'alpha_beta'
    HUMAN       = 'human'

    game        = None

    def __init__(self,game,player):
        StrategyGame.game = game
        self._player = player
        self._name = ""
        self._current_sequence = []
        self._sequence = []

    def start(self):
        self._current_sequence = copy.deepcopy(self._sequence)

    def move(self):
        raise NotImplementedError()

    @property
    def current_sequence(self):
        return self._current_sequence

    @property
    def sequence(self):
        return self._sequence

    @sequence.setter
    def sequence(self, value):
        self._sequence = value

    @property
    def name(self):
        return self._name

    @staticmethod
    def options():
        return [StrategyGame.RANDOM,StrategyGame.MINIMAX,StrategyGame.ALPHA_BETA,StrategyGame.HUMAN]

class StrategyHuman(StrategyGame):

    def __init__(self,game,player):
        super().__init__(game, player)
        self._name = StrategyGame.HUMAN

    def move(self):

        print(board_out(StrategyGame.game.board,StrategyGame.game.players))
        
        pos = input("Enter the row,col \n")
        pos = tuple(int(x.strip()) for x in pos.split(','))

        return pos,0

class StrategyRandom(StrategyGame):


    def __init__(self,game,player):
        super().__init__(game, player)
        self._name = StrategyGame.RANDOM

    def move(self):
        """
        Sem nenhuma strategy
        """

        empty_cells = StrategyGame.game.empty_cells()
        pos = random.choice(empty_cells)
        
        return pos,0

class StrategyMinimax(StrategyGame):

    # Registra o número de interações feitas
    count_minimax = 0

    def __init__(self,game,player):
        super().__init__(game, player)
        self._name = StrategyGame.MINIMAX

    def move(self):
        """
        Estrategia minimax
        """

        deph = len(StrategyGame.game.empty_cells())

        StrategyMinimax.count_minimax = 0

        register_begin_minimax(StrategyGame.game,self._player)

        register_header_tree(deph)

        pos,score   =  StrategyMinimax.minimax(StrategyGame.game.board,deph,self._player)

        register_end_strategy(StrategyGame.game,self._player,pos,score)

        return pos,score

    @staticmethod
    def minimax(origin,deph,player,maximizingPlayer=True):
        """
        Algoritmo minimax: https://en.wikipedia.org/wiki/Minimax 
        Retorna o melhor score com a posição
        """

        StrategyMinimax.count_minimax+=1

        board = np.copy(origin)

        winner = Game.evaluate(board,StrategyGame.game.players)
        
        if deph<=0 or winner !=0:
            score = calc_score(board,player)
            register_result(board,player,deph,winner,score)
            return None,score

        # Incializa bestValue com o valor do limite oposto
        best =  -infinity if maximizingPlayer else  infinity
        move = None,best

        for pos in Game.possibilities_cells(board):

            place(board, player, pos)

            register_loop_minimax(board, player,deph,pos)
            register_node(board,player,deph,pos)

            p,score = StrategyMinimax.minimax(board,deph-1,StrategyGame.game.opponent(player),not maximizingPlayer)

            if maximizingPlayer:
                # max
                if score > best:
                    best = score
                    move = pos,best
            else:
                # min
                if score < best:
                    best = score
                    move = pos,best

        return move

class StrategyAlphaBeta(StrategyGame):

    # Registra o número de interações feitas
    count_minimax = 0

    def __init__(self,game,player):
        super().__init__(game, player)
        self._name = StrategyGame.MINIMAX


    def move(self):
        """
        Estrategia alpha beta
        """

        deph = len(StrategyGame.game.empty_cells())

        StrategyMinimax.count_minimax = 0

        register_begin_minimax(StrategyGame.game,self._player)

        register_header_tree(deph)

        pos, score  = StrategyAlphaBeta.alpha_beta(StrategyGame.game.board , deph , self._player)

        register_end_strategy(StrategyGame.game,self._player,pos,score)

        return pos,score


    @staticmethod
    def alpha_beta(origin,deph , player , alpha = -infinity,beta = infinity , maximizingPlayer = True):
        """
        Algoritmo alpha beta pruning: https://en.wikipedia.org/wiki/Alpha%E2%80%93beta_pruning 
        Retorna o melhor score com a posição
        """

        StrategyMinimax.count_minimax+=1

        board = np.copy(origin)

        winner = Game.evaluate(board,StrategyGame.game.players)
        
        if deph<=0 or winner !=0:
            score = calc_score(board,player)
            register_result(board,player,deph,winner,score)
            return None,score

        # Incializa bestValue com o valor do limite oposto
        move = None,-infinity if maximizingPlayer else  infinity

        if maximizingPlayer:
            for pos in Game.possibilities_cells(board):

                place(board, player, pos)
                register_loop_minimax(board, player,deph,pos)
                register_node(board,player,deph,pos)

                p,score = StrategyAlphaBeta.alpha_beta(board,deph-1,StrategyGame.game.opponent(player),alpha,beta, not maximizingPlayer)

                if score  > alpha :
                    alpha = score
                    move = pos,alpha
    
                if beta <= alpha:
                    break
        else:
            for pos in Game.possibilities_cells(board):

                place(board, player, pos)
                register_loop_minimax(board, player,deph,pos)
                register_node(board,player,deph,pos)

                p,score = StrategyAlphaBeta.alpha_beta(board,deph-1,StrategyGame.game.opponent(player),alpha,beta, not maximizingPlayer)

                if score < beta:
                    beta = score
                    move = pos,beta

                if beta <= alpha:
                    break

        return move

def calc_score(board,player):
    """
    Function to heuristic evaluation of state.
    :param state: the state of the current board
    :Retorn +1 se o player  ganhar ; -1 se o player não ganhar ; 0  nas demais situações
    """

    winner = Game.evaluate(board,StrategyGame.game.players)

    if winner == player.id:
        score = +10
    elif winner == StrategyGame.game.opponent(player).id:
        # Oponente ganhou
        score = -10
    else:
        score = 0

    return score

def register_begin_minimax(game,player):
    """
    Registra o inicio da estrategia minimax
    """

    resumo = "\n".join((

"Player: %d - Start strategy"       % (player.id) ,
"Strategy: Minimax",
"Empty cells: %s"                   % (str(game.empty_cells())) ,
"Games possibilities: %d"           % (len(game.possibilities_games()))
    
    )) + "\n"

    register_board(game.board,game.players,resumo,1)


def register_end_strategy(game,player,pos,score):


    resumo = "\n".join((

"Player: %d  - End Strategy" % (player.id),
"Number of loops: %-10d"     % (StrategyMinimax.count_minimax),
"Position: %s Score: %f"     % (str(pos),score)
    
    )) + "\n"
    
    register_board(game.board,game.players,resumo,1 )


def register_result(board,player,deph,winner,score):

    tab1    = "┆                   " * (9-deph)
    tab2    = "┆                   " * (deph)

    lines = "\n".join((

"{}┆┄{:<1}) Count: {:<8}{}"    .format(tab1,deph,StrategyMinimax.count_minimax,tab2),
"{}┆ P{:<1} Win:{:<2} {:<8}{}" .format(tab1,player.id,winner,score,tab2),
board_out_simple(board,StrategyGame.game.players,deph)
    
    )) + "\n"

    tree_file.write(lines)


def register_header_tree(deph):

    max_deph = 10

    lines = "\n".join((

"".join(["%d                   " % (9-i) for i in range(max_deph)]),
"┆                   " * max_deph
    
    )) + "\n"

    tree_file.write(lines)


def register_loop_minimax(board,player,deph,pos):
    """
    Registra um node do minimax 
    """

    seq = Game.possibilities_cells(board)


    resumo = "\n".join((

"Player: %d - Minimax loop(%d)" % (player.id,StrategyMinimax.count_minimax),
"Options(%d): %s"               % (len(seq),str(seq)),
"Deph: %d Position: %s"         % (deph,str(pos))

    )) + "\n"

    register_board(board, StrategyGame.game.players,resumo,2)


def register_node(board,player,deph,pos):

    tab1    = "┆                   " * (9-deph)
    tab2    = "┆                   " * (deph)

    lines = "\n".join((

"{}┆┄{:<1}) Count: {:<8}{}"   .format(tab1,deph,StrategyMinimax.count_minimax,tab2),
"{}┆ P{:<1} {:<15}{}"         .format(tab1,player.id,str(pos),tab2),
board_out_simple(board,StrategyGame.game.players,deph)

    )) + "\n"

    tree_file.write(lines)
