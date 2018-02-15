import ast

from strategy import create_strategy

class Player(object):

    def __init__(self,id,mark):
        self.strategy   = None
        self.id         = id
        self.mark       = mark

    def pos_by_strategy(self):
        '''
        Retorna  a movimentação que devera ser feita baseado na estratégia
        '''

        return self.strategy.move()


def create_players(game,players,sequences,verbose):
    """
    Cria um jogador com sua respectiva estrategia com os parametros passado via CL
    """

    l = [] 
    for player in players:
        index,strategy_name,mark    = player
        player                      = Player(index,mark)
        # estrategia em função da opção --sequence via CL
        player.strategy             = create_strategy(strategy_name,game,player,verbose)
        # adiciona na lista de retorno
        l.append(player)

    # literal para  list da sequencia passada via CL
    if sequences is not None:
        for player,seq in sequences:
            l[player-1].strategy.sequence = ast.literal_eval("[" + seq + "]")

    return l
 