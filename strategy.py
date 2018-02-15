import random
import numpy as np
import copy
from math import inf as infinity
from scipy.special import factorial

from game import Game
from register import RegisterStrategy

class StrategyGame(object):

    RANDOM      = 'random'
    MINIMAX     = 'minimax'
    ALPHA_BETA  = 'alpha_beta'
    HUMAN       = 'human'

    game        = None

    def __init__(self,game,player,verbose=False):
        StrategyGame.game = game
        self._player    = player
        self._name      = ""
        self._current_sequence = []
        self._sequence  = []
        # Registra o número de interações feitas
        self._count     = 0
        self._register  = RegisterStrategy(game.size,"strategyP{}.txt".format(self._player.id),verbose)

    @property
    def count(self):
        """
        Contador de testes da estrategia
        """
        return self._count

    @property
    def current_sequence(self):
        return self._current_sequence

    @property
    def sequence(self):
        """
        Seuencia de jogadas recebida via a opção --sequence na CL
        """
        return self._sequence

    @sequence.setter
    def sequence(self, value):
        self._sequence = value

    @property
    def name(self):
        """
        Nome da estrategia
        """
        return self._name

    def start(self):
        self._current_sequence = copy.deepcopy(self._sequence)

    def move(self):
        raise NotImplementedError()

    @staticmethod
    def options():
        return [StrategyGame.RANDOM,StrategyGame.MINIMAX,StrategyGame.ALPHA_BETA,StrategyGame.HUMAN]

    def _calc_score(self,board,player):
        """
        Faz a avaliação theuristica do estado que está o tabuleiro.
        :Retorna +10 se o player  ganhar ; -1 0 se o adversário ganhar ; e 0  nas demais situações
        """

        winner = StrategyGame.game.evaluate(board)

        if winner == player.id:
            score = +10
        elif winner == StrategyGame.game.opponent(player).id:
            # Oponente ganhou
            score = -10
        else:
            score = 0

        return score

    def possibilities_games(self):
        """
        Calcula o fatorial da quantidade de celualas vazias para verificar o número de possíveis status do tabuleiro
        """

        #all_empty   = self.empty_cells()
        #return list(itertools.permutations(all_empty,len(all_empty)))

        # With exact=False the factorial is approximated using the gamma function:
        return factorial(len(StrategyGame.game.empty_cells()),exact = True)


    def deinit(self):
        """
        Finaliza a estrategia
        """

        self._register.close()


class StrategyHuman(StrategyGame):

    def __init__(self,game,player,verbose=False):
        super().__init__(game, player,verbose)
        self._name = StrategyGame.HUMAN

    def move(self):

        print(self._player.board_out(StrategyGame.game.board,StrategyGame.game.players))
        
        pos = input("Enter the row,col \n")
        pos = tuple(int(x.strip()) for x in pos.split(','))

        return (pos,0)

class StrategyRandom(StrategyGame):


    def __init__(self,game,player,verbose=False):
        super().__init__(game, player,verbose)
        self._name = StrategyGame.RANDOM

    def move(self):
        """
        Sem nenhuma strategy
        """

        empty_cells = StrategyGame.game.empty_cells()
        pos = random.choice(empty_cells)
        
        return (pos,0)

class StrategyMinimax(StrategyGame):


    def __init__(self,game,player,verbose=False):
        super().__init__(game, player,verbose)
        self._name = StrategyGame.MINIMAX


    def move(self):
        """
        Estrategia minimax
        """

        self._count = 0

        self._register.header_tree(self.game.size)

        deph = len(StrategyGame.game.empty_cells())

        strategy_result   =  self.__minimax(StrategyGame.game.board,deph,self._player)

        return strategy_result


    def __minimax(self,origin,deph,player,maximizingPlayer=True):
        """
        Algoritmo minimax: https://en.wikipedia.org/wiki/Minimax 
        Retorna o melhor score com a posição
        """

        self._count += 1

        board   = np.copy(origin)

        winner  = StrategyGame.game.evaluate(board)
        
        if deph<=0 or winner !=0:
            score = self._calc_score(board,player)
            self._register.result(StrategyGame.game,self,board,player,deph,winner,score)
            return (None,score)

        # Incializa bestValue com o valor do limite oposto
        best =  -infinity if maximizingPlayer else  infinity
        move = (None,best)

        for pos in Game.possibilities_cells(board):

            Game.place(board, player, pos)

            StrategyGame.game.register.loop_strategy(StrategyGame.game,self,board, player,deph,pos)
            self._register.node(StrategyGame.game,self,board,player,deph,pos)

            (p,score) = self.__minimax(board,deph-1,StrategyGame.game.opponent(player),not maximizingPlayer)

            if maximizingPlayer:
                # max
                if score > best:
                    best = score
                    move = (pos,best)
            else:
                # min
                if score < best:
                    best = score
                    move = (pos,best)

        return  move

class StrategyAlphaBeta(StrategyMinimax):


    def __init__(self,game,player,verbose=False):
        super().__init__(game, player,verbose)
        self._name = StrategyGame.ALPHA_BETA


    def move(self):
        """
        Estrategia alpha beta
        """

        self._count = 0

        self._register.header_tree(self.game.size)

        deph = len(StrategyGame.game.empty_cells())

        strategy_result  = self.__alpha_beta(StrategyGame.game.board , deph , self._player)


        return strategy_result


    def __alpha_beta(self,origin,deph , player , alpha = -infinity,beta = infinity , maximizingPlayer = True):
        """
        Algoritmo alpha beta pruning: https://en.wikipedia.org/wiki/Alpha%E2%80%93beta_pruning 
        Retorna o melhor score com a posição
        """

        self._count += 1

        board = np.copy(origin)

        winner = StrategyGame.game.evaluate(board)
        
        if deph<=0 or winner !=0:
            score = self._calc_score(board,player)
            self._register.result(StrategyGame.game,self,board,player,deph,winner,score)
            return (None,score)

        # Incializa bestValue com o valor do limite oposto
        move = (None,-infinity if maximizingPlayer else  infinity)

        for pos in Game.possibilities_cells(board):

            Game.place(board, player, pos)

            StrategyGame.game.register.loop_strategy(StrategyGame.game,self,board, player,deph,pos)
            
            self._register.node(StrategyGame.game,self,board,player,deph,pos)

            (p,score)= self.__alpha_beta(board,deph-1,StrategyGame.game.opponent(player),alpha,beta, not maximizingPlayer)

            if maximizingPlayer:

                if score  > alpha :
                    alpha = score
                    move = (pos,alpha)
            else:

                if score < beta:
                    beta = score
                    move = (pos,beta)

            if beta <= alpha:
                break

        return move

def create_strategy(strategy,game,player,verbose):
    """
    Cria a estrategia que será adotada no jogo para o player
    """

    if strategy == StrategyGame.RANDOM:
        strategy = StrategyRandom(game,player,verbose)
    elif strategy == StrategyGame.MINIMAX:
        strategy = StrategyMinimax(game,player,verbose)
    elif strategy == StrategyGame.ALPHA_BETA:
        strategy = StrategyAlphaBeta(game,player,verbose)
    elif strategy == StrategyGame.HUMAN:
        strategy = StrategyHuman(game,player)

    return strategy
