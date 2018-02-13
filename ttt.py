import os
import os.path
import locale
import sys
import click
import ast
import time, string, copy

from strategy import *
from player import *
from game import *

locale.setlocale(locale.LC_ALL, '')

def create_strategy(strategy,game,player):
    """
    Cria a estrategia que será adotada no jogo para o player
    """

    if strategy == StrategyGame.RANDOM:
        strategy = StrategyRandom(game,player)
    elif strategy == StrategyGame.MINIMAX:
        strategy = StrategyMinimax(game,player)
    elif strategy == StrategyGame.ALPHA_BETA:
        strategy = StrategyAlphaBeta(game,player)
    elif strategy == StrategyGame.HUMAN:
        strategy = StrategyHuman(game,player)

    return strategy

def create_game(players,sequences):
    """
    Cria o jogo (tabuleiro + jogadores)
    """

    game = Game()
    game.players = create_players(game,players,sequences)

    return game

def create_players(game,players,sequences):
    """
    Cria um usuario com os parametros passado via CL
    """

    l = [] 
    for player in players:
        index,strategy_name,mark    = player
        player                      = Player(index,mark)
        player.strategy             = create_strategy(strategy_name,game,player)
        l.append(player)

    if sequences is not None:
        for player,seq in sequences:
            l[player-1].strategy.sequence = ast.literal_eval("[" + seq + "]")

    return l
 
@click.group()
@click.option('--debug/--no-debug', default=False)
@click.option('--verbose/--no-verbose', default=False)
@click.pass_context
def cli(ctx, debug, verbose):

    global verbose_activate

    ctx.obj['DEBUG'] = debug
    ctx.obj['VERBOSE'] = verbose
    verbose_activate = verbose


@cli.command()
@click.option('--ntimes', default=1000)
@click.option('--player' , multiple=True , type = (int,click.Choice(StrategyGame.options()), str) , default=(1,"random","X"))
@click.option('--sequence' , multiple=True , type = (int,str) , default = None)
@click.pass_context
def play(ctx,ntimes,player,sequence):

    open_all()

    register_start(player,sequence,ntimes)

    # Cria o jogo
    game = create_game(player,sequence)

    # Tempo inicial do processamento
    start = time.time()
 
    # Array com o resultados de todos os jogos
    # Realiza N partidas para criação da estatisiticas
    result = np.array([ game.play() for i in range(ntimes)])

    # Tempo final de processamento
    stop = time.time()

    # Registra no arquivo de log o resumo
    register_resumo(game,start,stop,result)

    # Cria um histogram e um arquiv pdf com a estatisitica de todos os jogos 
    statistic(result)

    close_all()

if __name__ == '__main__':
    cli(obj={})
