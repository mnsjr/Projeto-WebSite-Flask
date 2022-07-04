from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager


app = Flask(__name__, static_url_path='/static')

app.config['SECRET_KEY'] = '8395f56ef02988e047b7f6a9bf462f77'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///python_tech_dev.db'

app.secret_key = "sk51un4f65slk7ln"

# atribuindo o banco de dados ao app
database = SQLAlchemy(app)

# atribuindo a criptografia da senha do usuário ao app
bcrypt = Bcrypt(app)

# tratando as permissões de acesso somente para usuários logados
login_manager = LoginManager(app)
login_manager.login_view = 'entrar'
login_manager.login_message = 'Faça Login para Prosseguir.'
login_manager.login_message_category = 'alert-info'


from pythontechdev import routs
