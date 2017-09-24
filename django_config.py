import os
import re
import time
import threading
import webbrowser
import argparse
from decouple import config
from github import Github


# Opções de instalação e configuração do ambiente e do Django
parser = argparse.ArgumentParser(description='Opções de instalação do Django')
parser.add_argument('-i', '--ignore', action='store_true',
                    help='Ignora a apresentação das informações no final da instalação.')
parser.add_argument('-g', '--git', action='store_true',
                    help='Cria o repositório no github e envia os arquivos após a instalação por SSH.')
parser.add_argument('-m', '--modify', action='store_true',
                    help='Modifica o arquivo settings.py. '
                         'Cria as pastas "static" e "templates" dentro do "app". '
                         'Cria e configura os arquivos ".env", "Procfile" e "runtime.txt".')
args = parser.parse_args()

os.system('clear')
print("Esse script irá instalar e configurar o Django na última versão dentro do virtualenv.\n")



if args.git:
    username = config('username')
    password = config('password')

    github_api = Github(username, password)
    user_escopo = github_api.get_user()

    lista_repos = [repo.name for repo in user_escopo.get_repos()]

# print(lista_repos)

# Classe que contém o nome e o caminho da pasta, projeto e app
class FoldersStructure:

    def __init__(self, current_folder, new_folder, project, app):
        self.current_folder = current_folder
        self.new_folder = new_folder
        self.project = project
        self.app = app
        self.path_new_folder = '/'.join([current_folder, self.new_folder])
        self.path_project = '/'.join([self.path_new_folder, self.project])
        self.path_app = '/'.join([self.path_project, self.app])


# Solicita nome da pasta, projeto, app e usuário do git (opcional)
while True:
    curr_folder = os.getcwd()
    if args.git:
        print("O nome da pasta será o mesmo nome do repositório no Github!!!\n")
    create_folder = input("Nome da pasta a ser criada: ")
    if args.git:
        if create_folder in lista_repos:
            print("Esse repositório já existe. Escolha outro nome de pasta.")
            cria_repo = False
        else:
            cria_repo = True
    if os.path.exists(create_folder):
        print("Essa pasta já existe. Escolha outro nome.\n")
    else:
        os.makedirs(create_folder)
        if cria_repo:
            user_escopo.create_repo(create_folder)
        os.chdir('./{}'.format(create_folder))
        create_project = input("Digite o nome do projeto: ")
        create_app = input("Digite o nome da app: ")
        folders = FoldersStructure(curr_folder, create_folder, create_project, create_app)
        # if args.git:
        #     user_git = input("Digite seu usuário do github: ")
        # else:
        #     user_git = None
        break

print()

# alias manage='python $VIRTUAL_ENV/../manage.py'
# alias django_config='python3 /home/amauri/python/django/django_config/django_config.py'

# Cria o ambiente virtual e instala as dependências do requirements.txt
os.system('virtualenv -p python3.5 .venv')
print()
os.chdir(folders.current_folder)
# os.chdir('/home/amauri/python/django/django_config')
os.system('cp /home/amauri/python/django/django_config/requirements.txt {}'.format(folders.new_folder))
os.chdir(folders.new_folder)
os.system('.venv/bin/pip install -r requirements.txt')
os.system('.venv/bin/django-admin startproject {} .'.format(folders.project))
os.chdir(folders.path_project)
os.system('../.venv/bin/python ../manage.py startapp {}'.format(folders.app))
os.chdir(folders.path_app)
os.mkdir('static')
os.mkdir('templates')

# Modifica o arquivo settings.py para proteger os dados
if args.modify:
    # Configura e cria os arquivos necessários
    with open("{}/settings.py".format(folders.path_project)) as file:
        readFile = file.read()
        reg_sec_key = re.search("SECRET_KEY = '(.+)'", readFile)
        reg_deb = re.search("DEBUG = (.+)", readFile)

    with open("{}/settings.py".format(folders.path_project), 'w') as file_w:
        reg = re.sub('import os', 'import os\n'
                                  'from decouple import config, Csv\n'
                                  'from dj_database_url import parse as dburl\n',
                                  readFile)
        reg = re.sub("SECRET_KEY = '.+'", "SECRET_KEY = config('SECRET_KEY')", reg)
        reg = re.sub("DEBUG = .+", "DEBUG = config('DEBUG', default=False, cast=bool)", reg)
        reg = re.sub("ALLOWED_HOSTS = \[\]", "ALLOWED_HOSTS = config('ALLOWED_HOSTS', default=[], cast=Csv())", reg)
        reg = re.sub(".staticfiles',", ".staticfiles',\n    '{}.{}',".format(folders.project, folders.app), reg)
        reg = re.sub("DATABASES.+\n.+\n.+\n.+\n.+}\n}",
                     "default_dburl = 'sqlite:///' + os.path.join(BASE_DIR, 'db.sqlite3')\n"
                     "DATABASES = {\n    'default': config('DATABASE_URL', default=default_dburl, cast=dburl),\n}",
                     reg)
        reg = re.sub('en-us', 'pt-br', reg)
        reg = re.sub('UTC', 'America/Sao_Paulo', reg)

        writeFile = file_w.write(reg + "\nSTATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')")

    # Cria o arquivo .env que contém dados secretos/importantes que não são enviados ao git
    with open("{}/.env".format(folders.path_new_folder), "w") as env_file:

        env_file.write("SECRET_KEY=" + reg_sec_key.group(1) + "\n"
                       "DEBUG=" + reg_deb.group(1) + "\n"
                       "ALLOWED_HOSTS=127.0.0.1, .localhost, .herokuapp.com\n")

    # Cria o arquivo Procfile que contém informações para o Heroku
    with open("{}/Procfile".format(folders.path_new_folder), "w") as proc_file:
        proc_file.write("web: gunicorn {}.wsgi --log-file -".format(folders.project))

    # Cria o arquivo runtime.txt contendo a versão do python para o Heroku
    with open("{}/runtime.txt".format(folders.path_new_folder), "w") as run_time:
        run_time.write("python-3.5.2")

# Caso não seja ignorada a opção de mostrar as informações durante a instalação
if not args.ignore:
    os.system('clear')
    print("\nO arquivo settings.py foi modificado.")
    print("Foram criados os seguintes arquivos de configuração:\n.env\nruntime.txt\nProcfile")
    os.chdir(folders.path_new_folder)
    input("\nPressione uma tecla para continuar...")
    os.system('clear')
    print("\nAs seguintes dependências foram instaladas:\n")
    os.system('.venv/bin/pip freeze > {}/requirements.txt'.format(folders.path_new_folder))
    os.system('cat {}/requirements.txt'.format(folders.path_new_folder))
    input("\nPressione uma tecla para continuar...")
    os.system('clear')
    print("\nA estrutura de pastas é a seguinte:\n")
    os.system('tree | more')
    input("\nPressione uma tecla e AGUARDE abrir a página no browser...")

# Informa que o browser é o Google Chrome
b = webbrowser.get('google-chrome')

# Inicializa o git, adiciona, comita e envia os arquivos ao github (opcional)
def git_repo():
    os.chdir(folders.path_new_folder)
    os.system('echo "# {}" >> README.md'.format(folders.new_folder))
    os.system('git init')
    os.system('cp /home/amauri/python/django/django_config/.gitignore .')
    os.system('git add .')
    os.system('git commit -m "first commit"')
    os.system('git remote add origin git@github.com:{}/{}.git'.format(username, folders.new_folder))
    os.system('git push -u origin master')


# Abre o browser com o github (opcional) e abre outra aba com o Django após a inicialização do servidor abaixo
def abre_browser():
    if args.git:
        b.open_new('github.com/{}/{}'.format(username, folders.new_folder))
    time.sleep(3)
    b.open('http:/127.0.0.1:8000')


# Inicia o servidor do Django
def run_server():
    os.chdir(folders.path_new_folder)
    os.system('.venv/bin/python manage.py runserver')


# Se a opção for enviar para o github, chama a função acima
if args.git:
    git_repo()

# Para executar as duas tarefas/funções ao mesmo tempo
threadObj = threading.Thread(target=abre_browser)
threadObj.start()

threadObj2 = threading.Thread(target=run_server)
threadObj2.start()
