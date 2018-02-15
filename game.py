import numpy as np
import itertools
import matplotlib.pyplot as plt
import time
from register import RegisterGame

EMPTY_CELL      = 0
NO_WINNER       = 0
EVALUATE_SIZE   = 4

class Game(object):

    def __init__(self,shape=(3,3),verbose=False):

        self._count            = 0
        self._ntimes           = 1
        self._shape            = shape
        self._board            = self.create_board()
        self._players          = None
        self._result           = None
        self._total_time       = 0
        self._game_start_time  = 0
        self._game_end_time    = 0
        self._register         = RegisterGame("game.txt",verbose)

    @property
    def register(self):
        """
        Registrador de eventos
        """
        return self._register

    @property
    def count(self):
        """
        Número da joga corrente
        """
        return self._count

    @property
    def ntimes(self):
        """
        Quantidade de jogadas a serem realizadas
        """
        return self._ntimes

    @property
    def total_time(self):
        """
        Tempo acumulado de execução
        """

        return self._total_time

    @property
    def game_time(self):
        """
        Tempo de execução da partida corrente
        """
        return self._game_end_time - self._game_start_time if self._game_end_time > self._game_start_time else 0

    @property
    def size(self):
        """
        Formato do board
        """
        return self.board.size

    @property
    def shape(self):
        """
        Formato do board
        """
        return self._shape

    @shape.setter
    def shape(self, value):
        self._shape = value
        self._board = self.create_board()

    @property
    def result(self):
        """
        Lista do resultados dos jogos
        """
        return self._result

    @result.setter
    def result(self, value):
        self._result = value

    @property
    def seq_turn(self):
        """
        Sequencia em que osjogadres irá jogar
        """
        return [p.id for p in self._players]

    @property
    def winner(self):
        """
        Resultado da partida em execução
        """
        return self.evaluate()

    @property
    def players(self):
        """
        Lista de jogadores
        """

        return self._players

    @players.setter
    def players(self, value):
        self._players = value

    @property
    def board(self):
        """
        Tabuleiro do jogo
        """
        return self._board

    @board.setter
    def board(self, value):
        self._board = value


    def create_board(self):
        """
        Cria o tabuleiro e iniciliza todas as posições com zero
        """

        return np.zeros(self._shape,dtype=int)

    def opponent(self,player):
        """
        Retorna o oponente do player
        """

        P1 = self._players[0]
        P2 = self._players[1]
        
        return P2 if player.id == P1.id else P1

    def start(self):
        """
        Inicia/Reinicia a partida
        """

        # contador de partidas
        self._count +=1

        # Cria um novo tabuleiro para a partida
        self._board = self.create_board()

        # inicia a estrategia de cada jogador
        for player in self._players:
            player.strategy.start()
        
        # registra no trace o inicio da partida
        self._register.begin_game(self)


    def is_game_over(self):
        """
        Verifca se a partida acabou verificando se o tabuleiro esta completo
        """
        
        return np.all(self._board!=0)

    def empty_cells(self):
        """
        Retorna a celulas vazias do board
        """

        return Game.possibilities_cells(self._board)

    @staticmethod
    def possibilities_cells(board):
        """
        Lista as celulas disponiveis de um board
        """

        (x,y) = np.where(board==EMPTY_CELL)
        return list(zip(x, y))

    def is_board_empty(self):
        """
        Retorna True se o tabuleiro estiver vazio
        """

        return np.all(self._board == EMPTY_CELL )

    @staticmethod
    def __row_win(board, player):
        """
        verifica se o jogador fechou uma linha
        """

        return np.any(np.all(board==player,axis=1))
 
    @staticmethod
    def __col_win(board, player):
        """
        verifica se o jogador fechou uma coluna
        """

        # board is less than size_max x size_max
        return np.any(np.all(board==player,axis=0))

    @staticmethod   
    def __diag_win(board, player):
        """
        verifica se o jogador fechou as 2 diagonais
        """

        return np.all(board.diagonal()==player) or np.all(np.fliplr(board).diagonal()==player)

    #@staticmethod
    def evaluate(self,board = None):
        """
        verifica se existe algum ganhador
        """

        if board is None:
            board   = self._board 

        winner  = NO_WINNER

        for player in self._players:
            if board.size <= (EVALUATE_SIZE * EVALUATE_SIZE ):
                # board is less than size_max x size_max
                if Game.__row_win(board,player.id) or Game.__col_win(board,player.id) or Game.__diag_win(board,player.id):
                    winner = player.id
            else:
                # board is bigegr than size_max x size_max
                for row in range(board.shape[0]- EVALUATE_SIZE + 1):
                    for col in range(board.shape[1] - EVALUATE_SIZE + 1):
                        t = board[row:row + EVALUATE_SIZE , col:col + EVALUATE_SIZE ]

                        winner = self.evaluate(t)

        if np.all(board!=0) and winner == NO_WINNER:
            winner = -1

        return winner

    def play(self,ntimes = 1):
        '''
        Realiza N partidas para criação da estatisiticas
        Preenche o array result com os resultados de todos os jogos
        '''

        self._ntimes = ntimes

        # Zera o acumulado do tempo total de processamento
        self._total_time = 0

        # Registra no arquivo de log os parametros de entrada
        self._register.begin_game(self,True)


        self._result = np.array([self.__play_onetime() for i in range(self._ntimes)])

        # Registra no arquivo de log a estatitisca das partidas
        self._register.end_game(self,True)


    def __play_onetime(self):
        """
        Realiza uma  unicapartida completa
        """

        # inicia/reinicia o jogo/partida
        self.start()

        self._game_start_time = time.time()

        winner = 0
 
        # loop de uma partida
        while winner == NO_WINNER:

            for player in self._players:

                pos,set_by_seq = Game.place_by_seq(self._board,player)

                score = 0

                # executa a estrategia caso não exista nenhuma lista de sequencia
                if not set_by_seq:
                    
                    self._register.begin_strategy(self,player)

                    pos,score   = player.pos_by_strategy()
                    
                    Game.place(self._board, player, pos)

                    self._register.end_strategy(self,player.strategy,player,(pos,score))

                winner = self.winner

                if winner != 0:
                    break
                else:
                    self._register.turn(self, player,pos,score)


        self._game_end_time = time.time()

        # Tempo final de processamento acumulado
        self._total_time += self.game_time

        self._register.end_game(self)

        return winner

    @staticmethod
    def place(board, player = 0 , position = None):
        """
        Realiza uma jogada
        """

        if position is None:
            input(" OPSSSSSSSSSSSSSSSSSSSSSSSSSSSSS - Deu ruim")

        if position is not None and board[position] == EMPTY_CELL:
            board[position] = player.id
            return True
        return False

    @staticmethod
    def place_by_seq(board,player):
        """
        Realiza uma jogada baseado na primeira posição da lista como sendo a proxima. 
        Caso  esteja indispoinivel o local vai para a proxima
        Apos a jogada e retirado da lista
        """

        flag_ok     = False
        positions   = player.strategy.current_sequence
        pos         = None

        if positions is not None:

            while len(positions) > 0 and not flag_ok:

                pos = positions[0]

                positions.remove(pos)

                if Game.place(board, player , pos):
                    flag_ok = True
                    break


        return pos , flag_ok

    def deinit(self):
        """
        Finaliza o jogo
        """

        self._register.close()
 
        for player in self._players:
            player.strategy.deinit()

    def show_statistic(self):
        """
        Plot o gráfico e cria um pdfcom as estaticas dos resultados
        """

        plt.hist(self._result, bins = np.linspace(-1, 3, 16) )
        plt.show()
        plt.savefig("result.pdf")

    def score_player(self,player):
        x = len(self._result[np.where(self._result==player)])
        return (x,float(x*100/len(self._result)))


def create_game(shape,verbose):
    """
    Cria o jogo (tabuleiro + jogadores)
    """

    # Cria o tabuleiro e inciailiza
    game = Game(shape,verbose)

    return game
