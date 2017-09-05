import os
import re
import time
import threading
import webbrowser
import argparse


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


class FoldersStructure:

    def __init__(self, current_folder, new_folder, project, app):
        self.current_folder = current_folder
        self.new_folder = new_folder
        self.project = project
        self.app = app
        self.path_new_folder = '/'.join([current_folder, self.new_folder])
        self.path_project = '/'.join([self.path_new_folder, self.project])
        self.path_app = '/'.join([self.path_project, self.app])


while True:
    curr_folder = os.getcwd()
    create_folder = input("Nome da pasta a ser criada: ")
    if os.path.exists(create_folder):
        print("Essa pasta já existe. Escolha outro nome.\n")
    else:
        os.makedirs(create_folder)
        os.chdir('./{}'.format(create_folder))
        create_project = input("Digite o nome do projeto: ")
        create_app = input("Digite o nome da app: ")
        folders = FoldersStructure(curr_folder, create_folder, create_project, create_app)
        if args.git:
            user_git = input("Digite seu usuário do github: ")
        else:
            user_git = None
        break

print()

os.system('virtualenv -p python3 .venv')
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

    with open("{}/.env".format(folders.path_new_folder), "w") as env_file:

        env_file.write("SECRET_KEY=" + reg_sec_key.group(1) + "\n"
                       "DEBUG=" + reg_deb.group(1) + "\n"
                       "ALLOWED_HOSTS=127.0.0.1, .localhost, .herokuapp.com\n")

    with open("{}/Procfile".format(folders.path_new_folder), "w") as proc_file:
        proc_file.write("web: gunicorn {}.wsgi --log-file -".format(folders.project))

    with open("{}/runtime.txt".format(folders.path_new_folder), "w") as run_time:
        run_time.write("python-3.5.2")


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

b = webbrowser.get('google-chrome')


def git_repo():
    os.chdir(folders.path_new_folder)
    os.system('echo "# {}" >> README.md'.format(folders.new_folder))
    os.system('git init')
    os.system('cp /home/amauri/python/django/django_config/.gitignore .')#.format(folders.path_new_folder))
    # mudar linha acima para ponto no final
    os.system('git add .')
    os.system('git commit -m "first commit"')
    os.system('git remote add origin git@github.com:{}/{}.git'.format(user_git, folders.new_folder))
    os.system('git push -u origin master')


def abre_browser():
    if args.git:
        b.open_new('github.com/{}/{}'.format(user_git, folders.new_folder))
    time.sleep(5)
    b.open('http:/127.0.0.1:8000')


def run_server():
    os.chdir(folders.path_new_folder)
    os.system('.venv/bin/python manage.py runserver')


if args.git:
    git_repo()

threadObj = threading.Thread(target=abre_browser)
threadObj.start()

threadObj2 = threading.Thread(target=run_server)
threadObj2.start()



"""
…or create a new repository on the command line
echo "# test_django" >> README.md
git init
git add README.md
git commit -m "first commit"
git remote add origin git@github.com:amaurirg/test_django.git
git push -u origin master
"""