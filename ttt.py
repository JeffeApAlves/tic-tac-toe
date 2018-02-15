import os
import os.path
import locale
import sys
import click
import time, string, copy

from strategy import StrategyGame
from game import create_game
from player import create_players

locale.setlocale(locale.LC_ALL, '')

@click.group()
@click.option('--debug/--no-debug', default=False)
@click.option('--verbose/--no-verbose', default=False)
@click.pass_context
def cli(ctx, debug, verbose):

    global verbose_activate

    ctx.obj['DEBUG'] = debug
    ctx.obj['VERBOSE'] = verbose

@cli.command()
@click.option('--ntimes', default=1000)
@click.option('--shape', type = (int,int) ,  default=None)
@click.option('--player' , multiple=True , type = (int,click.Choice(StrategyGame.options()), str) , default=(1,"random","X"))
@click.option('--sequence' , multiple=True , type = (int,str) , default = None)
@click.pass_context
def play(ctx,ntimes,player,sequence,shape):

    verbose = ctx.obj['VERBOSE']

    # Cria o jogo
    game = create_game(shape,verbose)

    # Cria os jogadores
    game.players = create_players(game,player,sequence,verbose)

    # Realiza N partidas
    game.play(ntimes)

    # Cria um histogram e um arquiv opdf com a estatisitica de todos os jogos 
    game.show_statistic()

    # Finaliza o jogo
    game.deinit()
    
if __name__ == '__main__':
    cli(obj={})
