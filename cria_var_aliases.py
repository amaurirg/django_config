from getpass import getuser
import os
import shutil
import re
from subprocess import call


"""
'ESSE ARQUIVO CRIARÁ UM ALIAS PARA O MANAGE.PY DO DJANGO E PARA O DJANGO_CONFIG CASO NÃO EXISTAM.'

Assim, DE QUALQUER PASTA DENTRO DO VIRTUALENV, você poderá usar o manage.py digitando apenas manage.
Exemplo: manage runserver ou manage startapp <nome_do_projeto>.
O outro alias serve para criar um projeto DE QUALQUER PASTA digitando apenas django_config.
Exemplo: usuario@computador:$ django_config

OBS: SE NO FINAL DO SCRIPT NÃO ABRIR UM NOVO TERMINAL, EXECUTE OS PASSOS ABAIXO PARA FUNCIONAR:
    1 - EXECUTE ESTE ARQUIVO
    2 - FECHE O TERMINAL
    3 - ABRA NOVAMENTE O TERMINAL.
"""

# Caminhos das pasta home e django_config e do arquivo .bashrc
path_home = "/home/{}".format(getuser())
path_bashrc = "/home/{}/.bashrc".format(getuser())
path_djc = os.getcwd()

# Verifica se existe uma cópis do arquivo .bashrc. Caso não exista, faz uma cópia como garantia.
if not os.path.exists("{}/copia_bashrc".format(path_home)):
    shutil.copy(path_bashrc, "{}/copia_bashrc".format(path_home))
    print("Foi criada uma cópia de segurança do arquivo .bashrc no diretório {} chamado 'copia_bashrc'.".format(path_home))

# Declara as variáveis para posteriormente verificar se existem aliases com esses nomes.
cria_alias_manage = True
cria_alias_djc = True
cria_path_djc = True

# Verifica se existem aliases com esses nomes.
with open(path_bashrc) as alias_bashrc:
    texto = alias_bashrc.read()
    if re.search(r'alias manage=', texto):
        cria_alias_manage = False
    if re.search(r'alias django_config=', texto):
        cria_alias_djc = False
    if re.search(r'PATH_DJC', texto):
        cria_path_djc = False

# Se não existir algum desses aliases, será criado. Caso não exista, não será recriado.
with open(path_bashrc, "a") as alias_bashrc:
    if cria_alias_manage:
        alias_bashrc.write("\nalias manage='python $VIRTUAL_ENV/../manage.py'")
        print("Foi criado o alias para o manage.")
    else:
        print("O alias para o manage já existe e não foi recriado!")
    if cria_alias_djc:
        alias_bashrc.write("\nalias django_config='python3 {}/django_config.py'".format(path_djc))
        print("Foi criado o alias para o django_config.")
    else:
        print("O alias para o django_config já existe e não foi recriado!")
    if cria_path_djc:
        alias_bashrc.write("\nexport PATH_DJC='{}'".format(path_djc))
        print("Foi criado a variável de ambiente path_djc com o path do django_config")
    else:
        print("A variável de ambiente path_djc já existe e não foi recriada!")

# Informações. Aguarda o susário teclar ENTER para continuar.
if not cria_alias_manage and not cria_alias_djc and not cria_path_djc == False:
    input("\nEsse terminal será fechado e aberto um outro para que os aliases funcionem."
          "\nAgora é só digitar django_config EM QUALQUER PASTA para criar um projeto Django"
          "\ne dentro do Virtualenv digitar manage para usar os recursos do manage.py."
          "\nPressione ENTER para continuar ...")

    # Abre um novo terminal para reiniciar o processo do bash tendo acesso aos aliases.
    call(['gnome-terminal'])

    # Fecha o terminal anterior.
    os.system("kill -9 %d"%(os.getppid()))
