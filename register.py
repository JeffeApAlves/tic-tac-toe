# Verbose flag
verbose_activate = False

# Quantidade espaços que representa um tab
SIZE_TAB = 6

# Quantidade espaços que representa um tab
SIZE_COL_DEPH = 15

#debug_file,tree_file = None,None
   
debug_file  = open("trace.txt","w") 
tree_file   = open("tree.txt","w")

def open_all():
    """
    Arquivos de trace e arvore de decisão
    """
    pass    
    #global debug_file,tree_file    
    #debug_file  = open("trace.txt","w") 
    #tree_file   = open("tree.txt","w")


def close_all():
    debug_file.close()
    tree_file.close()
