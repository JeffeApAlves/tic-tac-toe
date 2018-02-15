import numpy as np

# Quantidade espaços que representa um tab
SIZE_TAB = 6

# Tamnaho do box do texto da mensagem do arquivo trace.txt
SIZE_BOX = 100

# Tamanho da coluna do treeview
SIZE_COL = 20

# Padrão da coluna separador + quantidade espaços
COL = "┆".ljust(SIZE_COL)


class Register(object):

    def __init__(self,file_name,verbose = False):

        self._verbose = verbose
        self._file  = open(file_name,"w")


    def close(self):
        """
        Fecha o arquivos
        """

        self._file.close()


    def start_game_resume(self,game):

        title   = " Game Start ({}/{}) ".format(game.count, game.ntimes).center(SIZE_BOX,"═")

        resumo  = "\n".join((

    "".join(["╔",                           title                                                                               ,"╗"]),
    "".join(["║","Players: {}"             .format(str([(p.id,p.mark,p.strategy.name) for p in game.players])).ljust(SIZE_BOX)  ,"║"]),
    "".join(["║","P1 Initial sequence: {}" .format(str(game.players[0].strategy.sequence)).ljust(SIZE_BOX)                      ,"║"]),
    "".join(["║","P2 Initial sequence: {}" .format(str(game.players[1].strategy.sequence)).ljust(SIZE_BOX)                      ,"║"]),
    "".join(["║","Shape: {}"               .format(str(game.shape)).ljust(SIZE_BOX)                                             ,"║"]),
    "".join(["║","Sequence: {}"            .format(str(game.seq_turn)).ljust(SIZE_BOX)                                          ,"║"]),
    "".join(["╚",                           (SIZE_BOX) * "═"                                                                    ,"╝"]),                                                  

        )) + "\n"

        return resumo

    def end_game_resume(self,game):

        if game.result is not None:
            p1      = game.score_player(1)
            p2      = game.score_player(2)
            rest    = game.score_player(-1)
        else:
            p1,p2,rest = (0,0),(0,0),(0,0)

        title   = " Game over ({}/{}) Time:{:.2f} ".format(game.count, game.ntimes,game.game_time).center(SIZE_BOX,"═")
        resumo  = "\n".join((

    "".join(["╔",                                         title                                                                               ,"╗"]),
    "".join(["║","Players: {}"                           .format(str([(p.id,p.mark,p.strategy.name) for p in game.players])).ljust(SIZE_BOX)  ,"║"]),
    "".join(["║","P1:   {} / {:>3.0f} % strategy: {}"    .format(p1[0],p1[1],str(game.players[0].strategy.name)).ljust(SIZE_BOX)              ,"║"]),
    "".join(["║","P2:   {} / {:>3.0f} % strategy: {}"    .format(p2[0],p2[1],str(game.players[1].strategy.name)).ljust(SIZE_BOX)              ,"║"]),
    "".join(["║","Draw: {} / {:>3.0f} %"                 .format(rest[0],rest[1]).ljust(SIZE_BOX)                                             ,"║"]),
    "".join(["║","Shape:{} Result: {} total time: {:.2f}".format(str(game.shape) , game.winner , game.total_time).ljust(SIZE_BOX)             ,"║"]),
    "".join(["╚",                                         (SIZE_BOX) * "═"                                                                    ,"╝"]),

        )) + "\n"

        return resumo


    def board_out(self,board,players = None,resumo = None,tabs = 0):
        """
        Converte um boar em string usando caracteres unicode
        Resumo é o texto que sera mostrado na lateral do tabuleiro. Distribuido nas 7 linhas 
        Tabela unicode: https://www.rapidtables.com/code/text/unicode-characters.html

        "{}╔═════╦═════╦═════╗ {}".format( tab1,lines[0] ),
        "{}║{:^5}║{:^5}║{:^5}║ {}".format( tab1,b[(0,0)],b[(0,1)],b[(0,2)],lines[1] ),
        "{}╠═════╬═════╬═════╣ {}".format( tab1,lines[2] ),
        "{}║{:^5}║{:^5}║{:^5}║ {}".format( tab1,b[(1,0)],b[(1,1)],b[(1,2)],lines[3] ),
        "{}╠═════╬═════╬═════╣ {}".format( tab1,lines[4] ),
        "{}║{:^5}║{:^5}║{:^5}║ {}".format( tab1,b[(2,0)],b[(2,1)],b[(2,2)],lines[5] ),
        "{}╚═════╩═════╩═════╝ {}".format( tab1,lines[6] )

        """

        tab1    = " " * tabs * SIZE_TAB
        b       = self.board2str(board,players) 
        
        if resumo is not None:
            text  = resumo.split("\n")
        else:
            text  = []

        # Completa com linhas vazias para evitar index invalido
        for i in range(20 -len(text)):
            text.append("")

        lines = [] 

        (x,y) = b.shape
        x -= 1
        y -= 1

        # Linha superior do quadro
        lines.append("".join( [ tab1, "╔" , "═════╦" * y , "═════╗" , text[0], "\n" ] ))
        i = 1

        for (row,col), value in np.ndenumerate(b):

            # Linhas de divisao entre as celulas
            if col == 0 and row >0:
                lines.append("".join( [ tab1 , "╠" , "═════╬" * y , "═════╣" , text[i] ,"\n"]  ))
                i+=1

            # Todas as celulas da linha
            lines.append( "".join( [ "".join( [tab1 , "║" ] ) if col == 0 else "",  "{:^5}║".format(value)  ])      )
            
            # Nova linha no fim do tabuleiro
            if (col+1) % (y+1) == 0:
                lines.append("".join([text[i] , "\n" ]))
                i+=1

        # Linha inferior do quadro
        lines.append("".join( [ tab1, "╚" , "═════╩" * y , "═════╝", text[i]  ] ) )
    
        return "".join(lines)
        
    def board_out_simple(self,board,players,col=0):
        """
        Monta dinamicamente o board com o layout abaixo

        "{}┆{:^1} {:^1} {:^1} {}".format(tab1,b[(0,0)],b[(0,1)],b[(0,2)],tab2),
        "{}┆{:^1} {:^1} {:^1} {}".format(tab1,b[(1,0)],b[(1,1)],b[(1,2)],tab2),
        "{}┆{:^1} {:^1} {:^1} {}".format(tab1,b[(2,0)],b[(2,1)],b[(2,2)],tab2)

        """

        tab1    = COL * (board.size-col)
        tab2    = COL * (col)
        b       = self.board2str(board,players)

        lines = [] 

        (x,y) = b.shape
        x -=1
        y -=1

        # Complemento em espcos para justificar a esquerda a tabela 
        s = "".center(SIZE_COL - 1 -  (b.shape[1] * 3), " ")


        for (row,col), value in np.ndenumerate(b):

            if col == 0:
                lines.append("".join( [tab1 , "┆" ] ))

            lines.append("{:^1}  ".format(value))
            
            if (col+1) % (y+1) == 0:
                lines.append("".join([s ,tab2  ]))

                if row < x:
                    lines.append("\n")

        return "".join(lines)

    def board2str(self,board,players):
        """
        Retorna uma versão do tabuleiro usando texto 
        Player 1 = X, Player 2 = O,None     = "-"
        """

        b = np.empty(board.shape,dtype=str)

        for p in players:
            np.place(b,board==p.id , p.mark)

        np.place(b,board==0 , "-")

        return b


class RegisterStrategy(Register):


    def __init__(self,deph = 9,file_name="tree.txt",verbose = False):

        super().__init__(file_name,verbose)

        self.__max_deph = deph


    def result(self,game,strategy,board,player,deph,winner,score):
        """
        Adiciona no treeview do arquivo tree.txt o resultado do step
        """

        tab1    = COL * (self.__max_deph-deph)
        tab2    = COL * (deph)

        lines = "\n".join((

    "".join([tab1 , "┆┄{:<2}) N: {:<11}"        .format(deph,strategy.count).ljust(SIZE_COL)   , tab2]),
    "".join([tab1 , "┆P{:<1} Win:{:<2} {:<8}"   .format(player.id,winner,score).ljust(SIZE_COL)        , tab2]),
    self.board_out_simple(board,game.players,deph)
        
        )) + "\n"

        self._file.write(lines)


    def node(self,game,strategy,board,player,deph,pos):

        tab1    = COL * (self.__max_deph-deph)
        tab2    = COL * (deph)

        lines = "\n".join((

    "".join([tab1 , "┆┄{:<2}) N: {:<11}"        .format(deph,strategy.count).ljust(SIZE_COL)           , tab2]),
    "".join([tab1 , "┆P{:<1} {:<15}"            .format(player.id,str(pos)).ljust(SIZE_COL)            , tab2]),
    self.board_out_simple(board,game.players,deph)

        )) + "\n"

        self._file.write(lines)


    def header_tree(self,deph):
 
        self.__max_deph = deph

        lines = "\n".join((

    "".join(["{}".format(self.__max_deph-i).ljust(SIZE_COL) for i in range(self.__max_deph+1)]),
    COL * (self.__max_deph+1)
        
        )) + "\n"

        self._file.write(lines)


class RegisterGame(Register):


    def __init__(self,file_name="trace.txt",verbose = False):

        super().__init__(file_name,verbose)

        self._file = open(file_name,"w") 


    def begin_strategy(self,game,player):
        """
        Registra o inicio da estrategia minimax
        """

        resumo = "\n".join((

    "Player: {} - Start strategy"       .format(player.id) ,
    "Strategy: {}"                      .format(player.strategy.name),
    "Empty cells: {}"                   .format(str(game.empty_cells())) ,
    "Games possibilities: {}"           .format(player.strategy.possibilities_games())
        
        )) + "\n"

        self._board(game.board,game.players,resumo,1)


    def end_strategy(self,game,strategy,player,strategy_result):
        """
        Registra no arquivo trace o board com um resumo das informações referente ao step da estrategia
        """

        (pos,score) = strategy_result

        resumo = "\n".join((

    "Player: {:d}  - End Strategy" .format(player.id),
    "Number of loops: {:<10d}"     .format(strategy.count),
    "Position: {} Score: {:f}"     .format(str(pos),score)
        
        )) + "\n"
        
        self._board(game.board,game.players,resumo,1 )


    def loop_strategy(self,game,strategy,board,player,deph,pos):
        """
        Registra um node do minimax no aruivo trace.txt 
        """

        seq = game.possibilities_cells(board)

        resumo = "\n".join((

    "Player: {:d} - Minimax loop({:d})" .format(player.id,strategy.count),
    "Options({:d}): {}"                 .format(len(seq),str(seq)),
    "Deph: {:d} Position: {}"           .format(deph,str(pos))

        )) + "\n"

        self._board(board, game.players,resumo,2)


    def begin_game(self,game,verbose=False):
        """
        Registra no arquivo trace.txt o inicio de uma partida
        """        

        lines = self.start_game_resume(game)

        if verbose:
            print(lines)
        else:
            self._board(game.board, game.players, lines)

    def end_game(self,game,verbose=False):
        """
        Registra o resumo da de uma partida no arquivo trace
        """

        lines = self.end_game_resume(game)

        if verbose:
            print(lines)
        else:
            self._board(game.board , game.players , lines)


    def turn(self,game,player,pos,score):
        """
        Registra uma jogada
        """

        resumo = "\n".join((

    "Player:   {:d}  - Turn"               .format(player.id),
    "Strategy: {}"                         .format(player.strategy.name) ,
    "Played on Position: {} Score: {:.2f}" .format(str(pos),score)

        )) + "\n"

        self._board(game.board, game.players, resumo)


    def _board(self,board,players,resumo = None,tabs = 0):
        """
        Registra um board no arquivo trace.txt
        """

        lines = self.board_out(board,players,resumo,tabs) + "\n"

        self._file.write(lines)

        if self._verbose:
            print(lines)
