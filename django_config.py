import os
import sys
import string
import re
import time
import threading
import webbrowser
import argparse
import platform
import shutil
from decouple import config
from github import Github


# Opções de instalação e configuração do ambiente e do Django
# Para acessar essas opções digite django_config -h ou django_config --help
parser = argparse.ArgumentParser(description='Opções de instalação do Django')
parser.add_argument('-i', '--ignore', action='store_true',
                    help='Ignora a apresentação das informações no final da instalação.')
parser.add_argument('-g', '--git', action='store_true',
                    help='Cria o repositório no github e envia os arquivos após a instalação por SSH.'
                    'Para isto você tem que ter uma conta no Github e suas credenciais configuradas neste computador.'
                    'Cria o arquivo .gitignore para não enviar suas credenciais e configurações para o Github.')
parser.add_argument('-m', '--modify', action='store_true',
                    help='Modifica os arquivos settings.py. e wsgi.py'
                         'Cria as pastas "static" e "templates" dentro do "app".'
                         'Cria e configura os arquivos ".env", "Procfile" e "runtime.txt".')
parser.add_argument('-d', '--deploy', action='store_true',
                    help='Faz o deploy no Heroku enviando as configurações do arquivo ".env" com segurança.'
                    'Para isto você tem que ter uma conta no Heroku e o Toolbelt instalado.')
args = parser.parse_args()

os.system('clear')

print("Esse script irá instalar e configurar o Django na última versão dentro do virtualenv.\n")

if args.ignore:
    print("Você escolheu ignorar as informações no final da instalação.\n"
          "Não será mostrado quais arquivos foram criados e a estrutura de pastas.\n")
if args.modify:
    print("Você escolheu modificar os arquivos settings.py. e wsgi.py.\n"
          "Esses arquivos serão preparados para sua segurança e agilidade no projeto.\n")

if args.git:
    username = config('username')
    password = config('password')

    user_escopo = Github(username, password).get_user()

    print("Obtendo lista de repositórios do Github...")
    lista_repos = [repo.name for repo in user_escopo.get_repos()]

    print("Você escolheu enviar para o Github. Será criado o arquivo .gitignore para não enviar\n"
          "suas credenciais e configurações para o Github.\n")
else:
    lista_repos = []
    user_escopo = None

apps = []
create_app_heroku = ''
if args.deploy:
    print("Obtendo lista de apps do Heroku...")
    apps = os.popen('heroku apps').read().strip().split('\n')
    if len(apps[1:]) >= 5:
        print("Você já tem 5 apps no Heroku. Se sua conta for gratuita não será permitido a criação de novos apps.\n")
        while True:
            resp = input("Deseja continuar? (s/n): ")
            if resp == 's':
                break
            elif resp == 'n':
                sys.exit()
            else:
                pass
    print("Você escolheu fazer o deploy no Heroku. Será enviado o arquivo .env para enviar\n"
          "suas credenciais e configurações para o Heroku com segurança\n")
print("Caso queira alterar o modo de instalação, pressione CTRL+C para cancelar essa instalação\n"
      "e digite 'django_config -h' para ver as opções.\n\n")


# Classe que contém o nome e o caminho da pasta, projeto e app
class FoldersStructure:

    def __init__(self, current_folder, new_folder, project, app, app_heroku):
        self.current_folder = current_folder
        self.new_folder = new_folder
        self.project = project
        self.app = app
        self.app_heroku = app_heroku
        self.path_new_folder = '/'.join([current_folder, self.new_folder])
        self.path_project = '/'.join([self.path_new_folder, self.project])
        self.path_app = '/'.join([self.path_project, self.app])

curr_folder = os.getcwd()

aceita_g = list(list(string.ascii_letters) + list(string.digits) + ['_', '-'])
aceita_d = aceita_g[:-1]
# aceita_h = aceita_g[:-1] + ['_']
aceita_h = list(list(string.ascii_lowercase) + list(string.digits) + ['-'])

def verifica(proj, repo):
    palavra = ''
    invalidos = ''
    for caractere in proj:
        if caractere not in repo:
            invalidos += caractere
        else:
            palavra += caractere
    if palavra != proj:
        print("\nCaractere(s) inválido(s): {}\n".format(invalidos))
        width = os.get_terminal_size()[0]
        print("=" * width + "\n")
        return False
    else:
        print("OK")
    return True


while True:
    if args.git:
        print("Você escolheu criar o repositório no Gihub. O nome da pasta e repositório serão os mesmos!!!")
    print("\nO nome da pasta e repositório só aceita letras minúsculas, números, underline(_) e hífen(-).")
    create_folder = input("Nome da pasta a ser criada: ")

    if not verifica(create_folder, aceita_g):
        pass
    else:
        if os.path.exists(create_folder) or create_folder in lista_repos:
            print("Essa pasta (e|ou) repositório já existe(m). Escolha outro nome.\n")
            # width = rows, columns = os.popen('stty size', 'r').read().split()
            width = os.get_terminal_size()[0]
            print("=" * width + "\n")
        else:
            os.makedirs(create_folder)
            if args.git:
                user_escopo.create_repo(create_folder)
                descricao = input("Você pode inserir uma descrição para o repositório no Github (opcional = ENTER): ")
                user_escopo.get_repo(create_folder).edit(description=descricao)
            os.chdir('./{}'.format(create_folder))

            while True:
                print("\nO Django só aceita letras minúsculas, números e underline(_) para o nome do projeto.")
                create_project = input("Digite o nome do projeto Django: ")
                if not verifica(create_project, aceita_d):
                    continue
                else:
                    break

            while True:
                print("\nO nome do app aceita letras minúsculas, números e underline(_).")
                create_app = input("Digite o nome da app do projeto Django: ")
                if not verifica(create_app, aceita_d):
                    continue
                else:
                    break

            if args.deploy:
                while True:
                    print("\nO Heroku só aceita letras minúsculas, números e hífen(-) para a criação do app.")
                    create_app_heroku = input("Nome do app que será criado no Heroku: ")
                    if not verifica(create_app_heroku, aceita_h):
                        continue
                    if create_app_heroku in apps:
                        print("Esse app já existe no Heroku. Escolha outro nome.\n")
                        continue
                    else:
                        break

            folders = FoldersStructure(curr_folder, create_folder, create_project, create_app, create_app_heroku)
            break

print()

# Lê a variável de ambiente criada no arquivo .bashrc através do arquivo cria_aliases.py
path_djc = os.getenv('PATH_DJC')

# Cria o ambiente virtual e instala as dependências do requirements.txt
os.system('virtualenv -p python3 .venv')    # ************* mudar para venv ********************
print()
os.chdir(folders.current_folder)
os.system('cp {}/requirements.txt {}'.format(path_djc, folders.new_folder))
os.chdir(folders.new_folder)
os.system('.venv/bin/pip install -r requirements.txt')
os.system('.venv/bin/django-admin startproject {} .'.format(folders.project))
os.chdir(folders.path_project)
os.system('../.venv/bin/python ../manage.py startapp {}'.format(folders.app))
os.chdir(folders.path_app)
os.mkdir('static')
os.mkdir('templates')
os.mkdir('html_to_django')
os.system('cp {}/regex_html.py html_to_django'.format(path_djc))

# Modifica o arquivo settings.py para proteger os dados
if args.modify:
    # Configura e cria os arquivos necessários
    with open("{}/settings.py".format(folders.path_project)) as file_r:
        readFile = file_r.read()
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

    with open("{}/wsgi.py".format(folders.path_project)) as file_r:
        readFile = file_r.read()

    with open("{}/wsgi.py".format(folders.path_project), "w") as file_w:
        reg = re.sub("import os", "import os\nfrom dj_static import Cling", readFile)
        reg = re.sub("application = get_wsgi_application\(\)", "application = Cling(get_wsgi_application())", reg)
        writeFile = file_w.write(reg)

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
        run_time.write("python-{}".format(platform.python_version()))

# Caso não seja ignorada a opção de mostrar as informações durante a instalação
if not args.ignore:
    os.system('clear')
    if args.modify:
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
    # os.system('cp {}/.gitignore .'.format(path_djc))
    with open(".gitignore", "w") as file_i:
        file_i.write(".env\n.idea\n.venv\ndb.sqlite3\n*pyc\n__pycache__")
    os.system('git add .')
    os.system('git commit -m "first commit"')
    os.system('git remote add origin git@github.com:{}/{}.git'.format(username, folders.new_folder))
    os.system('git push -u origin master')


# Faz o deploy no Heroku e abre o browser na página da aplicação
def deploy_heroku():
    os.system('heroku apps:create {}'.format(create_app_heroku))
    os.system('heroku config:push')
    os.system('git push heroku master --force')
    os.system('heroku config:set ALLOWED_HOSTS=.herokuapp.com')
    os.system('heroku config:set DEBUG=False')
    # b.open('https://{}.herokuapp.com/'.format(folders.app_heroku))


# Abre o browser com o github (opcional) e abre outra aba com o Django após a inicialização do servidor abaixo
def abre_browser():
    time.sleep(5)
    b.open('http:/127.0.0.1:8000')
    time.sleep(5)
    if args.git:
        b.open('github.com/{}/{}'.format(username, folders.new_folder))
    time.sleep(5)
    if args.deploy:
        b.open('https://{}.herokuapp.com/'.format(folders.app_heroku))


# Inicia o servidor do Django
def run_server():
    os.chdir(folders.path_new_folder)
    os.system('.venv/bin/python manage.py runserver')

if args.deploy:
    with open("{}/urls.py".format(folders.path_project), "r+") as arq_urls:
        busca = re.search(r'from django.contrib import admin', arq_urls.read())
        fim = busca.end() + 1
        arq_urls.seek(fim)
        arq_urls.write("from {}.{}.views import home\nfrom django.urls import path\n\n\n"
                       "urlpatterns = [\n"
                       "    path('', home),\n"
                       "    path('admin/', admin.site.urls),\n"
                       "]\n".format(folders.project, folders.app))

    with open("{}/views.py".format(folders.path_app), "a") as arq_view:
        arq_view.write('\ndef home(request):\n    return render(request, "index.html")\n')
    os.chdir(folders.path_app)
    os.system('cp -R {}/img static'.format(path_djc))
    os.system('cp {}/index.html templates'.format(path_djc))

# Se a opção for enviar para o github, chama a função acima
if args.git:
    git_repo()

if args.deploy:
    deploy_heroku()
    # threadObj2 = threading.Thread(target=deploy_heroku)
    # threadObj2.start()

# Para executar as tarefas/funções ao mesmo tempo
threadObj = threading.Thread(target=abre_browser)
threadObj.start()

threadObj2 = threading.Thread(target=run_server)
threadObj2.start()
