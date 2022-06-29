from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from pythontechdev.models import Usuario
from flask_login import current_user


class FormCriarConta(FlaskForm):
    username = StringField('nome de usuário',
                           validators=[DataRequired(), Length(2, 20, message="Todo usuário precisa ""de um nome")])
    email = StringField('e-mail', validators=[DataRequired(), Email(message="Digite um endereço de email válido")])
    senha = PasswordField('senha', validators=[DataRequired(), Length(6, 8, message="A senha deve conter entre 6 e 8 "
                                                                                    "caracteres")])
    confirmacao_senha = PasswordField('confirmação de senha',
                                      validators=[DataRequired(),
                                                  EqualTo('senha',
                                                          message="Senha diferente da preenchida anteriormente")])
    botao_submit_criarconta = SubmitField('Criar Conta')

    def validate_email(self, email):
        """
        Toda função com nome iniciado com 'validate_',
        automaticamente se tornará um método de validação wtforms.validators
        utilizará as regras de formatação e de mensagens de erro exibidas para o usuário na aplicação
        e será invocada automaticamente pelo método submite ao tentar validar os dados.
        :param email: é necessário passar como parâmetro o atributo a ser validado na classe.
        """
        usuario = Usuario.query.filter_by(email=email.data).first()
        if usuario:
            raise ValidationError('e-mail já cadastrado, cadastre-se com outro e-mail ou faça login para continuar')


class FormEntrar(FlaskForm):
    email = StringField('e-mail', validators=[DataRequired(), Email(message="Digite um email válido")])
    senha = PasswordField('senha', validators=[DataRequired(message="A senha deve conter entre 6 e 8 "
                                                                    "caracteres"), Length(6, 8)])
    lembrar_dados = BooleanField('Lembrar Dados de Acesso')
    botao_submit_entrar = SubmitField('Entrar')


class FormEditarPerfil(FlaskForm):
    username = StringField('Nome de usuário',
                           validators=[DataRequired(), Length(2, 20, message="Todo usuário precisa de um nome")])
    email = StringField('E-mail', validators=[DataRequired(), Email(message="Digite um endereço de email válido")])
    foto_perfil = FileField('Atualizar foto de perfil.',
                            validators=[FileAllowed(['jpg', 'png', 'jpeg'],
                                                    message='Escolha um arquivo de extensão jpg ou png')])

    hab_python = BooleanField('Python')
    hab_frontend = BooleanField('Frontend')
    hab_backend = BooleanField('Backend')
    hab_ciencia_dados = BooleanField('Ciência de Dados')
    hab_automacao = BooleanField('Automação de Processos')
    hab_web_scraping = BooleanField('Web Scraping')
    hab_agil = BooleanField('Metodologias Ágeis')
    hab_banco_dados = BooleanField('Bando de Dados')

    botao_submit_editarperfil = SubmitField('Confirmar Edição')

    def validate_email(self, email):
        """
        Toda função com nome iniciado com 'validate_',
        automaticamente se tornará um método de validação wtforms.validators
        utilizará as regras de formatação e de mensagens de erro exibidas para o usuário na aplicação
        e será invocada automaticamente pelo método submite ao tentar validar os dados.
        :param email: é necessário passar como parâmetro o atributo a ser validado na classe.
        """
        # verificar se o e-mail mudou
        if current_user.email != email.data:
            usuario = Usuario.query.filter_by(email=email.data).first()
            if usuario:
                raise ValidationError('Já existe um usuário com este e-mail. Cadastre outro e-mail.')


class FormContato(FlaskForm):
    name = StringField(label='Nome', validators=[DataRequired()])
    email = StringField(label='E-mail', validators=[DataRequired(), Email(granular_message=True)])
    message = TextAreaField(label='Mensagem')
    submit = SubmitField(label="Enviar")


class FormCriarPost(FlaskForm):
    titulo = StringField('Titulo do Post', validators=[DataRequired(), Length(2, 120)])
    corpo = TextAreaField('Escreva seu Post aqui', validators=[DataRequired()])
    botao_submit = SubmitField('Criar Post')

