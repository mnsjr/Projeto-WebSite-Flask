from flask import render_template, redirect, request, url_for, flash, abort
from pythontechdev import app, database, bcrypt
from pythontechdev.forms import FormEntrar, FormCriarConta, FormEditarPerfil, FormCriarPost, FormEditarPost
from pythontechdev.models import Usuario, Post
from flask_login import login_user, logout_user, current_user, login_required
import os
from PIL import Image


@app.route('/')
def home():
    posts = Post.query.order_by(Post.id.desc())
    return render_template('home.html', posts=posts)


@app.route('/Posts')
def posts():
    posts = Post.query.order_by(Post.id.desc())
    return render_template('posts.html', posts=posts)


@app.route('/usuarios')
@login_required
def usuarios():
    lista_usuarios = Usuario.query.all()
    return render_template('usuarios.html', lista_usuarios=lista_usuarios)


@app.route('/entrar', methods=['GET', 'POST'])
def entrar():
    form_entrar = FormEntrar()
    if form_entrar.validate_on_submit() and 'botao_submit_entrar' in request.form:
        usuario = Usuario.query.filter_by(email=form_entrar.email.data).first()
        if usuario and bcrypt.check_password_hash(usuario.senha.decode('utf-8'), form_entrar.senha.data):
            login_user(usuario, remember=form_entrar.lembrar_dados.data)
            flash(f'Login realizado com sucesso na conta {form_entrar.email.data}.', 'alert-success')
            par_next = request.args.get('next')
            if par_next:
                return redirect(par_next)
            else:
                return redirect(url_for('home'))
        else:
            flash(f'Falha no login, e-mail ou senha incorretos.', 'alert-danger')
    return render_template('entrar.html', form_entrar=form_entrar)


@app.route('/criar_conta', methods=['GET', 'POST'])
def criar_conta():
    form_criarconta = FormCriarConta()
    if form_criarconta.validate_on_submit() and 'botao_submit_criarconta' in request.form:
        '''
        Criar usuário, add na session e commit no db
        '''
        senha_cript = bcrypt.generate_password_hash(form_criarconta.senha.data)  # .encode('utf-8')
        usuario = Usuario(username=form_criarconta.username.data,
                          email=form_criarconta.email.data,
                          senha=senha_cript)
        database.session.add(usuario)
        database.session.commit()
        flash(f'Conta criada com sucesso para o usuário {form_criarconta.email.data}.', 'alert-success')
        return redirect(url_for('home'))
    return render_template('criar_conta.html', form_criarconta=form_criarconta)


@app.route('/sair')
@login_required
def sair():
    logout_user()
    flash(f'Logout feito com sucesso.', 'alert-success')
    return redirect(url_for('home'))


@app.route('/perfil')
@login_required
def perfil():
    foto_perfil = url_for('static', filename='fotos_perfil/{}'.format(current_user.foto_perfil))
    return render_template('perfil.html', foto_perfil=foto_perfil)


@app.route('/post/criar', methods=['GET', 'POST'])
@login_required
def criar_post():
    form = FormCriarPost()
    if form.validate_on_submit():
        post = Post(titulo=form.titulo.data, corpo=form.corpo.data, autor=current_user)
        database.session.add(post)
        database.session.commit()
        flash('Post criado com sucesso.', 'alert-success')
        return redirect(url_for('posts'))
    return render_template('criarpost.html', form=form)


@app.route('/post/<post_id>', methods=['GET', 'POST'])
@login_required
def exibir_post(post_id):
    """
    Devolve uma nova url com o id do post em uma nova página somente com o post em questão.
    :param post_id: id do post no db
    :return: retorna uma página com o post selecionado
    """
    post = Post.query.get(post_id)
    if current_user == post.autor:
        form = FormEditarPost()
        if request.method == 'GET':
            """
            Este método exibe os campos já preenchidos.
            """
            form.titulo.data = post.titulo
            form.corpo.data = post.corpo
        elif form.validate_on_submit():
            post.titulo = form.titulo.data
            post.corpo = form.corpo.data
            database.session.commit()
            flash('Post Atualizado com Sucesso', 'alert-success')
            return redirect(url_for('posts'))
    else:
        form = None
    return render_template('post.html', post=post, form=form)


@app.route('/post/<post_id>/excluir', methods=['GET', 'POST'])
@login_required
def excluir_post(post_id):
    post = Post.query.get(post_id)
    if current_user == post.autor:
        database.session.delete(post)
        database.session.commit()
        flash('Post Excluído com Sucesso.', 'alert-success')
        return redirect(url_for('posts'))
    else:
        abort(403)


def salvar_imagem(imagem):
    """
    Função auxiliar de 'editar_perfil():'
    1 add código ao nome da imagem, para que não haja conflito no banco de dados
    2 excluir foto antiga do db
    3 reduzir tamanho da imagem
    4 salvar a imagem no db
    """
    novo_nome = current_user.email
    novo_nome = novo_nome.replace('@', '_')
    nome, extensao = os.path.splitext(imagem.filename)
    nome_arquivo = novo_nome + extensao
    caminho = os.path.join(app.root_path, 'static/fotos_perfil', nome_arquivo)

    foto_antiga = current_user.foto_perfil
    if foto_antiga != 'default.jpg':
        arquivo = os.path.join(app.root_path, 'static/fotos_perfil', foto_antiga)
        if os.path.isfile(arquivo):
            os.remove(arquivo)

    tamanho = (400, 400)
    imagem_reduzida = Image.open(imagem)
    imagem_reduzida.thumbnail(tamanho)
    imagem_reduzida.save(caminho)
    return nome_arquivo


def atualizar_cursos(form):
    """
    Função auxiliar de 'editar_perfil():'
    :param form: recebe os atributos de 'form'
    :return: nomes das habilidades
    """
    lista_habilidades = []
    for campo in form:
        if 'hab_' in campo.name:
            if campo.data:
                lista_habilidades.append(campo.label.text)
    return ';'.join(lista_habilidades)


@app.route('/perfil/editar', methods=['GET', 'POST'])
@login_required
def editar_perfil():
    form = FormEditarPerfil()
    if form.validate_on_submit():
        '''
        Sempre que for adicionar algo ao formulário:
        1 - add o campo no formulário, forms.py
        2 - add o campo no html
        3 - criar a logica para salva a info no banco de dados em routs.py
        Se formulário for válido:
        '''
        current_user.email = form.email.data
        current_user.username = form.username.data
        if form.foto_perfil.data:
            '''
            Irá receber o retorno da função salvar imagem acima.
            '''
            nome_imagem = salvar_imagem(form.foto_perfil.data)
            current_user.foto_perfil = nome_imagem
        current_user.habilidades = atualizar_cursos(form)
        database.session.commit()
        flash('Perfil atualizado com sucesso.', 'alert-success')
        return redirect(url_for('perfil'))
    elif request.method == "GET":
        '''
        Para que o formulário já apareça preenchido:
        Se a pagina for carregada:
        '''
        form.email.data = current_user.email
        form.username.data = current_user.username
    foto_perfil = url_for('static', filename='fotos_perfil/{}'.format(current_user.foto_perfil))
    return render_template('editarperfil.html', foto_perfil=foto_perfil, form=form)
