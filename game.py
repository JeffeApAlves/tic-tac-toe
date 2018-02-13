import numpy as np
import numpy as np
import itertools
import matplotlib.pyplot as plt

from register import *
from player import *

locale.setlocale(locale.LC_ALL, '')

EMPTY_CELL = 0
NO_WINNER  = 0

class Game(object):

    count = 0

    def __init__(self):
        self._board = self.create_board()
        self._players = None

    @property
    def seq_turn(self):
        return [p.id for p in self._players]

    @property
    def winner(self):
        return Game.evaluate(self._board,self._players)

    @property
    def players(self):
        return self._players

    @players.setter
    def players(self, value):
        self._players = value

    @property
    def board(self):
        return self._board

    @board.setter
    def board(self, value):
        self._board = value


    def create_board(self):
        """
        Cria o tabuleiro e iniciliza todas as posições com zero
        """

        return np.zeros((3,3),dtype=int)

    def opponent(self,player):
        """
        Retorna o oponente do player
        """

        P1 = self._players[0]
        P2 = self._players[1]
        
        return P2 if player.id == Player.PLAYER_1 else P1

    def start(self):
        """
        Reinicia o jogo novo
        """

        # contador de jogos
        Game.count +=1

        # Cria um novo tabuleiro
        self._board = self.create_board()

        # inicia a estrategia de cada jogador
        for player in self._players:
            player.strategy.start()

        # registra o inicio da partida       
        register_begin_game(self)


    def is_game_over(self):
        """
        Verifca se o jogo acabou
        """
        
        return np.all(self._board!=0)

    def possibilities_games(self):
        """
        Lista todas as sequencias de jogads disponiveis de um tabuleiro
        """

        all_empty   = self.empty_cells()
        return list(itertools.permutations(all_empty,len(all_empty)))

    def empty_cells(self):
        """
        Reorna a celulas vazias do board
        """

        return Game.possibilities_cells(self._board)

    @staticmethod
    def possibilities_cells(board):
        """
        Lista as celulas disponiveis de um board
        """

        x,y = np.where(board==EMPTY_CELL)
        return list(zip(x, y))

    def is_board_empty(self):
        return np.all(self._board == EMPTY_CELL )

    @staticmethod
    def row_win(board, player):
        """
        verifica se o jogador fechou uma linha
        """

        return np.any(np.all(board==player,axis=1))

    @staticmethod
    def col_win(board, player):
        """
        verifica se o jogador fechou uma coluna
        """

        return np.any(np.all(board==player,axis=0))

    @staticmethod
    def diag_win(board, player):
        """
        verifica se o jogador fechou as 2 diagonais
        """

        return np.all(board.diagonal()==player) or np.all(np.fliplr(board).diagonal()==player)

    @staticmethod
    def evaluate(board,players):
        """
        verifica se existe algum ganhador
        """

        winner = NO_WINNER
        for player in players:
            if Game.row_win(board,player.id) or Game.col_win(board,player.id) or Game.diag_win(board,player.id):
                winner = player.id
        if np.all(board!=0) and winner == NO_WINNER:
            winner = -1
        return winner


    def play(self):
        """
        Realiza uma partida completa
        """

        # inicia/reinicia o jogo/partida
        self.start()

        winner = 0
 
        # loop de uma partida
        while winner == NO_WINNER:

            for player in self._players:

                pos,set_by_seq = place_by_seq(self._board,player)

                score = 0

                if not set_by_seq:
                    pos,score   = player.pos_by_strategy()
                    place(self._board, player, pos)

                winner = self.winner

                if winner != 0:
                    break
                else:
                    register_turn(self, player,pos,score)

        register_end_game(self)

        return winner


def place(board, player = 0 , position = None):
    """
    Realiza uma jogada
    """

    if position is not None and board[position] == EMPTY_CELL:
        board[position] = player.id
        return True
    return False

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

            if place(board, player , pos):
                flag_ok = True
                break


    return pos , flag_ok


def board_out(board,players,resumo=None,tabs=0):
    """
    Converte um tabuleiro em string usando cracteres unicode
    Resumo é otexto que sera mostrado na lateral do tabuleiro. Distribuido nas 7 linhas 
    Tabela unicode: https://www.rapidtables.com/code/text/unicode-characters.html
    """

    b = board2str(board,players) 
    
    if resumo is not None:
        lines  = resumo.split("\n")
    else:
        lines  = []

    # Completa com linhas vazias para evitar index invalido
    for i in range(7 -len(lines)):
        lines.append("")

    tab1 = " " * tabs * SIZE_TAB

    lines = "\n".join((
"{}╔═════╦═════╦═════╗ {}".format( tab1,lines[0] ),
"{}║{:^5}║{:^5}║{:^5}║ {}".format( tab1,b[(0,0)],b[(0,1)],b[(0,2)],lines[1] ),
"{}╠═════╬═════╬═════╣ {}".format( tab1,lines[2] ),
"{}║{:^5}║{:^5}║{:^5}║ {}".format( tab1,b[(1,0)],b[(1,1)],b[(1,2)],lines[3] ),
"{}╠═════╬═════╬═════╣ {}".format( tab1,lines[4] ),
"{}║{:^5}║{:^5}║{:^5}║ {}".format( tab1,b[(2,0)],b[(2,1)],b[(2,2)],lines[5] ),
"{}╚═════╩═════╩═════╝ {}".format( tab1,lines[6] )
    ))
                                    
    return lines
    
def board_out_simple(board,players,col=0):

    tab1    = "┆                   " * (9-col)
    tab2    = "┆                   " * (col)

    b = board2str(board,players)

    lines = "\n".join((
"{}┆{:^3} {:^3} {:^3}        {}".format(tab1,b[(0,0)],b[(0,1)],b[(0,2)],tab2),
"{}┆{:^3} {:^3} {:^3}        {}".format(tab1,b[(1,0)],b[(1,1)],b[(1,2)],tab2),
"{}┆{:^3} {:^3} {:^3}        {}".format(tab1,b[(2,0)],b[(2,1)],b[(2,2)],tab2)
    ))

    return lines

def board2str(board,players):
    """
    Retorna uma versão do tabuleiro usando texto 
    Player 1 = X, Player 2 = O,None     = "-"
    """

    b = np.empty(board.shape,dtype=str)

    for p in players:
        np.place(b,board==p.id , p.mark)

    np.place(b,board==0 , "-")

    return b

def statistic(result):
    """
    Plot o gráfico da estaticas dos resultados
    """

    plt.hist(result, bins = np.linspace(-1, 3, 16) )
    plt.show()
    plt.savefig("resumo.pdf")


def register_begin_game(game):
    """
    Registra no aruivo trrace o inicio da partida
    """        
    
    resumo = "\n".join((
"╔═════════════════════════════════════════ Game Start ═══════════════════════════════════════╗",
"║Sequence:%-83s║"                                                                                % (str(game.seq_turn)),
"║Game: %-10d                                                                            ║"       % (game.count),
"║                                                                                            ║",
"║                                                                                            ║",
"║                                                                                            ║",
"╚════════════════════════════════════════════════════════════════════════════════════════════╝"
    )) + "\n"

    register_board(game.board, game.players, resumo)

def register_end_game(game):
    """
    Registra o resumo da partida
    """

    players = game.players

    resumo = "\n".join((
"╔═════════════════════════════════════════ Game over ════════════════════════════════════════╗",
"║Strategy of player 1: %-70s║"                                                                  % (players[0].strategy.name),
"║Strategy of player 2: %-70s║"                                                                  % (players[1].strategy.name),
"║Game result: %-4d                                                                           ║" % (game.winner),
"║                                                                                            ║",
"╚════════════════════════════════════════════════════════════════════════════════════════════╝"
    )) + "\n"

    register_board(game.board , game.players , resumo)


def register_turn(game,player,pos,score):
    """
    Registra uma jogada
    """

    resumo = "\n".join((
"Player:   %d  - Turn"                 % (player.id),
"Strategy: %s"                       % (player.strategy.name) ,
"Played on Position: %s Score: %f"   % (str(pos),score)
    )) + "\n"

    register_board(game.board, game.players, resumo)


def register_board(board,players,resumo = None,tabs = 0):
    """
    Registra um tabuleiro no arquivo trace
    """

    lines = board_out(board,players,resumo,tabs) + "\n"

    debug_file.write(lines)

    if verbose_activate:
        print(lines)

def register_resumo(game,start,stop,result):

    # Tempo final do processamento
    
    t = stop - start

    total = len(result)

    lines = "\n".join((
"Overview",
"Run Total time: %ds" % (t),
"Player 1: Performance %2.1f%%" % float(len(result[np.where(result==Player.PLAYER_1)])*100/total),
"Player 2: Performance %2.1f%%" % float(len(result[np.where(result==Player.PLAYER_2)])*100/total),
"Draw:     Performance %2.1f%%" % float(len(result[np.where(result<=0)])*100/total),
    )) + "\n"

    print(lines)
    debug_file.write(lines)

def register_start(players,sequences,ntimes):

    lines = "\n".join((

"Input options",
"Players: %s"           % str(players),
"Initial sequence: %s"  % str(sequences),
"Start %d games"        % ntimes,

    )) + "\n"

    print(lines)
    debug_file.write(lines)
