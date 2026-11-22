from flask import (
    Flask, render_template, request, redirect, url_for,
    send_file, abort, session, flash
)
from flask_wtf.csrf import CSRFProtect
import sqlite3
import os
from functools import wraps
from getpass import getpass
from werkzeug.security import generate_password_hash, check_password_hash
from decimal import Decimal, ROUND_HALF_UP
from xml.sax.saxutils import escape
from datetime import datetime
from database.inicializar_banco import inicializar_banco
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    Table, TableStyle, Image
)


app = Flask(__name__)

# =====================================================
# CONFIGURAÇÕES DE SEGURANÇA
# =====================================================

app.config["SECRET_KEY"] = os.environ.get(
    "TOQUE_DE_AMOR_SECRET_KEY"
)

if not app.config["SECRET_KEY"]:
    raise RuntimeError(
        "A chave secreta do Toque de Amor não foi configurada."
    )

# Proteção dos cookies da sessão
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# Proteção CSRF
csrf = CSRFProtect(app)

# =====================================================
# PROTEÇÃO DE ACESSO
# =====================================================

def login_obrigatorio(funcao):

    @wraps(funcao)
    def verificar_login(*args, **kwargs):

        if "usuario_logado" not in session:
            return redirect(url_for("login"))

        return funcao(*args, **kwargs)

    return verificar_login


# =====================================================
# REGISTRO DAS FONTES PERSONALIZADAS
# =====================================================

PASTA_FONTES = os.path.join(app.root_path, "fonts")

pdfmetrics.registerFont(TTFont(
    "CormorantMedium",
    os.path.join(PASTA_FONTES, "Cormorant_Garamond",
                 "CormorantGaramond-Medium.ttf")
))

pdfmetrics.registerFont(TTFont(
    "CormorantRegular",
    os.path.join(PASTA_FONTES, "Cormorant_Garamond",
                 "CormorantGaramond-Regular.ttf")
))

pdfmetrics.registerFont(TTFont(
    "CormorantItalic",
    os.path.join(PASTA_FONTES, "Cormorant_Garamond",
                 "CormorantGaramond-Italic.ttf")
))

pdfmetrics.registerFont(TTFont(
    "MontserratRegular",
    os.path.join(PASTA_FONTES, "Montserrat",
                 "Montserrat-Regular.ttf")
))

pdfmetrics.registerFont(TTFont(
    "MontserratSemiBold",
    os.path.join(PASTA_FONTES, "Montserrat",
                 "Montserrat-SemiBold.ttf")
))



# =====================================================
# CONEXÃO COM O BANCO DE DADOS
# =====================================================

PASTA_BANCO = os.path.join(app.root_path, "database")

CAMINHO_BANCO = os.environ.get(
    "DATABASE_PATH",
    os.path.join(PASTA_BANCO, "toque_de_amor.db")
)

PASTA_BACKUPS = os.path.join(app.root_path, "backups")


def conectar_banco():

    pasta = os.path.dirname(os.path.abspath(CAMINHO_BANCO))
    os.makedirs(pasta, exist_ok=True)

    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.row_factory = sqlite3.Row

    return conexao

# =====================================================
# TABELA DE ACESSO ADMINISTRATIVO
# =====================================================

def inicializar_tabela_usuarios():

    conexao = conectar_banco()

    conexao.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT NOT NULL UNIQUE,
            senha_hash TEXT NOT NULL
        )
    """)

    conexao.commit()
    conexao.close()


# =====================================================
# CRIAR PRIMEIRO ADMINISTRADOR
# =====================================================

def criar_administrador_inicial():

    conexao = conectar_banco()

    quantidade = conexao.execute("""
        SELECT COUNT(*) FROM usuarios
    """).fetchone()[0]

    conexao.close()

    if quantidade > 0:
        return

    print("\n================================")
    print(" CONFIGURAÇÃO DO TOQUE DE AMOR")
    print("================================")
    print("Crie o acesso administrativo.\n")

    usuario = input("Nome de usuário: ").strip()

    while not usuario:
        print("O usuário não pode ficar vazio.")
        usuario = input("Nome de usuário: ").strip()

    senha = getpass("Crie sua senha: ")
    confirmacao = getpass("Confirme sua senha: ")

    while len(senha) < 6 or senha != confirmacao:

        if len(senha) < 6:
            print("A senha precisa ter pelo menos 6 caracteres.")
        else:
            print("As senhas não correspondem.")

        senha = getpass("Crie sua senha: ")
        confirmacao = getpass("Confirme sua senha: ")

    senha_hash = generate_password_hash(senha)

    conexao = conectar_banco()

    conexao.execute("""
        INSERT INTO usuarios (usuario, senha_hash)
        VALUES (?, ?)
    """, (usuario, senha_hash))

    conexao.commit()
    conexao.close()

    print("\nAdministrador criado com sucesso!")


def criar_administrador_por_variaveis():

    conexao = conectar_banco()

    quantidade = conexao.execute("""
        SELECT COUNT(*) FROM usuarios
    """).fetchone()[0]

    conexao.close()

    if quantidade > 0:
        return

    usuario = os.environ.get("TOQUE_DE_AMOR_ADMIN_USER")
    senha = os.environ.get("TOQUE_DE_AMOR_ADMIN_PASSWORD")

    if not usuario or not senha:
        raise RuntimeError(
            "Configure TOQUE_DE_AMOR_ADMIN_USER e "
            "TOQUE_DE_AMOR_ADMIN_PASSWORD nas variáveis "
            "de ambiente do servidor."
        )

    if len(senha) < 6:
        raise RuntimeError(
            "A senha administrativa precisa ter pelo menos "
            "6 caracteres."
        )

    conexao = conectar_banco()

    conexao.execute("""
        INSERT INTO usuarios (usuario, senha_hash)
        VALUES (?, ?)
    """, (
        usuario.strip(),
        generate_password_hash(senha)
    ))

    conexao.commit()
    conexao.close()

# =====================================================
# BACKUP AUTOMÁTICO DO BANCO DE DADOS
# =====================================================

def criar_backup_automatico():

    os.makedirs(PASTA_BACKUPS, exist_ok=True)

    if not os.path.exists(CAMINHO_BANCO):
        raise FileNotFoundError("Banco de dados não encontrado.")

    data_hora = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    nome_backup = f"backup_toque_de_amor_{data_hora}.db"

    caminho_backup = os.path.join(PASTA_BACKUPS, nome_backup)

    banco_original = sqlite3.connect(CAMINHO_BANCO)
    banco_backup = sqlite3.connect(caminho_backup)

    try:
        banco_original.backup(banco_backup)
    finally:
        banco_backup.close()
        banco_original.close()

    print(f"Backup criado com sucesso: {nome_backup}")


# =====================================================
# CONVERSÃO DE VALORES
# =====================================================

def decimal_para_centavos(valor):

    valor_decimal = Decimal(str(valor))

    return int(
        (valor_decimal * 100).quantize(
            Decimal("1"),
            rounding=ROUND_HALF_UP
        )
    )


def formatar_moeda(centavos):

    valor = centavos / 100

    return f"R$ {valor:,.2f}".replace(
        ",", "X"
    ).replace(".", ",").replace("X", ".")


def formatar_data(data):

    if not data:
        return "Não informada"

    try:
        partes = data.split("-")
        return f"{partes[2]}/{partes[1]}/{partes[0]}"
    except (IndexError, AttributeError):
        return data


# =====================================================
# LOGIN
# =====================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        usuario = request.form.get("usuario", "").strip()
        senha = request.form.get("senha", "")

        conexao = conectar_banco()

        administrador = conexao.execute("""
            SELECT *
            FROM usuarios
            WHERE usuario = ?
        """, (usuario,)).fetchone()

        conexao.close()

        if administrador and check_password_hash(
            administrador["senha_hash"], senha
        ):

            session.clear()
            session["usuario_logado"] = administrador["usuario"]

            return redirect(url_for("inicio"))

        flash("Usuário ou senha incorretos.", "erro")

    return render_template("login.html")


# =====================================================
# SAIR DO SISTEMA
# =====================================================

@app.route("/sair")
def sair():

    session.clear()

    return redirect(url_for("login"))


# =====================================================
# PÁGINA INICIAL
# =====================================================

@app.route("/")
@login_obrigatorio
def inicio():

    return render_template("index.html")


# =====================================================
# PRODUTOS
# =====================================================

@app.route("/produtos")
@login_obrigatorio
def produtos():

    conexao = conectar_banco()

    lista_produtos = conexao.execute("""
        SELECT *
        FROM produtos
        WHERE ativo = 1
        ORDER BY categoria, nome
    """).fetchall()

    conexao.close()

    return render_template(
        "produtos.html",
        produtos=lista_produtos
    )


# =====================================================
# CADASTRAR PRODUTO
# =====================================================

@app.route("/cadastrar_produto", methods=["POST"])
@login_obrigatorio
def cadastrar_produto():

    nome = request.form["nome"]
    categoria = request.form["categoria"]
    preco = request.form["preco"]
    unidade = request.form["unidade"]

    conexao = conectar_banco()

    conexao.execute("""
        INSERT INTO produtos (nome, categoria, preco, unidade)
        VALUES (?, ?, ?, ?)
    """, (nome, categoria, preco, unidade))

    conexao.commit()
    conexao.close()

    return redirect(url_for("produtos"))


# =====================================================
# EXCLUIR PRODUTO
# =====================================================

@app.route("/excluir_produto/<int:id>", methods=["POST"])
@login_obrigatorio
def excluir_produto(id):

    conexao = conectar_banco()

    conexao.execute("""
        UPDATE produtos
        SET ativo = 0
        WHERE id = ?
    """, (id,))

    conexao.commit()
    conexao.close()

    return redirect(url_for("produtos"))


# =====================================================
# HISTÓRICO DE PEDIDOS
# =====================================================

@app.route("/pedidos")
@login_obrigatorio
def pedidos():

    conexao = conectar_banco()

    lista_pedidos = conexao.execute("""
        SELECT *
        FROM pedidos
        ORDER BY id DESC
    """).fetchall()

    pedidos_com_itens = []

    for pedido in lista_pedidos:

        itens = conexao.execute("""
            SELECT
                nome_produto,
                preco_unitario_centavos,
                quantidade,
                subtotal_centavos
            FROM itens_pedido
            WHERE pedido_id = ?
            ORDER BY id
        """, (pedido["id"],)).fetchall()

        pedidos_com_itens.append({
            "dados": dict(pedido),
            "itens": [dict(item) for item in itens]
        })

    conexao.close()

    return render_template(
        "pedidos.html",
        pedidos=pedidos_com_itens
    )


# =====================================================
# GERAR PDF DO PEDIDO
# =====================================================

@app.route("/pedido/<int:id>/pdf")
@login_obrigatorio
def gerar_pdf_pedido(id):

    conexao = conectar_banco()

    pedido = conexao.execute("""
        SELECT *
        FROM pedidos
        WHERE id = ?
    """, (id,)).fetchone()

    if pedido is None:
        conexao.close()
        abort(404)

    itens = conexao.execute("""
        SELECT
            nome_produto,
            preco_unitario_centavos,
            quantidade,
            subtotal_centavos
        FROM itens_pedido
        WHERE pedido_id = ?
        ORDER BY id
    """, (id,)).fetchall()

    conexao.close()

    pasta_pdfs = os.path.join(app.root_path, "pdfs")
    os.makedirs(pasta_pdfs, exist_ok=True)

    caminho_pdf = os.path.join(pasta_pdfs, f"pedido_{id}.pdf")

    # PALETA DE CORES ORIGINAL

    bordo = colors.HexColor("#873e59")
    rosa = colors.HexColor("#f8e9ed")
    rosa_claro = colors.HexColor("#fff7f8")
    cinza = colors.HexColor("#666666")
    texto = colors.HexColor("#44343a")
    branco = colors.white

    # CONFIGURAÇÃO DO DOCUMENTO

    documento = SimpleDocTemplate(
        caminho_pdf,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=1.6 * cm,
        bottomMargin=2 * cm
    )

    largura_tabela = 17 * cm

    # MOLDURA E RODAPÉ

    def desenhar_pagina(canvas, doc):

        canvas.saveState()

        largura_pagina, altura_pagina = A4

        canvas.setStrokeColor(rosa)
        canvas.setLineWidth(0.7)

        canvas.roundRect(
            1.1 * cm, 1.1 * cm,
            largura_pagina - 2.2 * cm,
            altura_pagina - 2.2 * cm,
            8, stroke=1, fill=0
        )

        canvas.setStrokeColor(rosa)
        canvas.setLineWidth(0.5)

        canvas.line(
            2 * cm, 1.65 * cm,
            largura_pagina - 2 * cm, 1.65 * cm
        )

        canvas.setFont("MontserratRegular", 7)
        canvas.setFillColor(cinza)

        canvas.drawCentredString(
            largura_pagina / 2,
            1.3 * cm,
            "Toque de Amor - Variedades em Doces Gourmet"
        )

        canvas.restoreState()

    # ESTILOS DO PDF

    estilos = getSampleStyleSheet()

    estilo_titulo = ParagraphStyle(
        "TituloToque",
        parent=estilos["Title"],
        fontName="CormorantMedium",
        fontSize=24,
        leading=28,
        textColor=bordo,
        alignment=TA_CENTER,
        spaceBefore=5,
        spaceAfter=5
    )

    estilo_subtitulo = ParagraphStyle(
        "SubtituloToque",
        parent=estilos["Normal"],
        fontName="CormorantItalic",
        fontSize=12,
        leading=16,
        textColor=bordo,
        alignment=TA_CENTER,
        spaceAfter=13
    )

    estilo_secao = ParagraphStyle(
        "SecaoToque",
        parent=estilos["Heading2"],
        fontName="CormorantMedium",
        fontSize=15,
        leading=19,
        textColor=bordo,
        spaceBefore=13,
        spaceAfter=7
    )

    estilo_normal = ParagraphStyle(
        "NormalToque",
        parent=estilos["Normal"],
        fontName="MontserratRegular",
        fontSize=8,
        leading=12,
        textColor=texto
    )

    estilo_label = ParagraphStyle(
        "LabelToque",
        parent=estilos["Normal"],
        fontName="MontserratSemiBold",
        fontSize=7.5,
        leading=11,
        textColor=bordo
    )

    estilo_centro = ParagraphStyle(
        "CentroToque",
        parent=estilo_normal,
        alignment=TA_CENTER
    )

    estilo_total_label = ParagraphStyle(
        "TotalLabelToque",
        parent=estilos["Normal"],
        fontName="MontserratSemiBold",
        fontSize=10,
        textColor=bordo,
        alignment=TA_RIGHT
    )

    estilo_total_valor = ParagraphStyle(
        "TotalValorToque",
        parent=estilos["Normal"],
        fontName="MontserratSemiBold",
        fontSize=15,
        textColor=bordo,
        alignment=TA_RIGHT
    )

    estilo_agradecimento = ParagraphStyle(
        "AgradecimentoToque",
        parent=estilos["Normal"],
        fontName="CormorantItalic",
        fontSize=15,
        leading=19,
        textColor=bordo,
        alignment=TA_CENTER
    )

    conteudo = []

    # CABEÇALHO E LOGO

    caminho_logo = os.path.join(
        app.root_path, "static", "Logo.png"
    )

    if os.path.exists(caminho_logo):

        logo = Image(
            caminho_logo,
            width=5 * cm,
            height=3 * cm,
            kind="proportional"
        )

        logo.hAlign = "CENTER"
        conteudo.append(logo)

    conteudo.append(Spacer(1, 5))

    conteudo.append(Paragraph(
        "CONFIRMAÇÃO DE PEDIDO",
        estilo_titulo
    ))

    conteudo.append(Paragraph(
        "Toque de Amor - Variedades em Doces Gourmet",
        estilo_subtitulo
    ))

    linha_decorativa = Table(
        [[""]],
        colWidths=[largura_tabela],
        rowHeights=[1.2]
    )

    linha_decorativa.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), rosa),
        ("LINEBELOW", (0, 0), (-1, -1), 0.5, bordo)
    ]))

    conteudo.append(linha_decorativa)
    conteudo.append(Spacer(1, 10))

    tabela_numero = Table(
        [[Paragraph(
            f"<b>PEDIDO Nº {pedido['id']}</b>",
            ParagraphStyle(
                "NumeroPedido",
                parent=estilo_normal,
                fontName="MontserratSemiBold",
                fontSize=10,
                textColor=bordo,
                alignment=TA_CENTER
            )
        )]],
        colWidths=[largura_tabela]
    )

    tabela_numero.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), rosa_claro),
        ("BOX", (0, 0), (-1, -1), 0.7, rosa),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9)
    ]))

    conteudo.append(tabela_numero)

    # DADOS DO CLIENTE

    conteudo.append(Paragraph(
        "DADOS DO CLIENTE",
        estilo_secao
    ))

    dados_cliente = []

    def adicionar_dado(rotulo, valor):

        dados_cliente.append([
            Paragraph(escape(rotulo.upper()), estilo_label),
            Paragraph(escape(str(valor)), estilo_normal)
        ])

    adicionar_dado("Cliente", pedido["cliente_nome"] or "Não informado")
    adicionar_dado("Telefone", pedido["cliente_telefone"] or "Não informado")
    adicionar_dado("Data do pedido", formatar_data(pedido["data_pedido"]))
    adicionar_dado("Data de entrega", formatar_data(pedido["data_entrega"]))
    adicionar_dado("Tipo de entrega", pedido["tipo_entrega"] or "Não informado")

    if pedido["tipo_entrega"] == "Delivery":
        adicionar_dado("Endereço", pedido["endereco"] or "Não informado")
        adicionar_dado("Município", pedido["municipio"] or "Não informado")

    adicionar_dado(
        "Forma de pagamento",
        pedido["forma_pagamento"] or "Não informada"
    )

    tabela_cliente = Table(
        dados_cliente,
        colWidths=[3.5 * cm, 13.5 * cm]
    )

    tabela_cliente.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), rosa_claro),
        ("BOX", (0, 0), (-1, -1), 0.6, rosa),
        ("LINEBELOW", (0, 0), (-1, -2), 0.35, rosa),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7)
    ]))

    conteudo.append(tabela_cliente)

    # PRODUTOS DO PEDIDO

    conteudo.append(Paragraph(
        "DETALHAMENTO DO PEDIDO",
        estilo_secao
    ))

    estilo_cabecalho_tabela = ParagraphStyle(
        "CabecalhoTabela",
        parent=estilo_normal,
        fontName="MontserratSemiBold",
        fontSize=8,
        textColor=branco,
        alignment=TA_CENTER
    )

    dados_itens = [[
        Paragraph("PRODUTO", estilo_cabecalho_tabela),
        Paragraph("QTD.", estilo_cabecalho_tabela),
        Paragraph("VALOR UNIT.", estilo_cabecalho_tabela),
        Paragraph("SUBTOTAL", estilo_cabecalho_tabela)
    ]]

    for item in itens:

        dados_itens.append([
            Paragraph(escape(item["nome_produto"]), estilo_normal),
            str(item["quantidade"]),
            formatar_moeda(item["preco_unitario_centavos"]),
            formatar_moeda(item["subtotal_centavos"])
        ])

    tabela_itens = Table(
        dados_itens,
        colWidths=[7.2 * cm, 1.5 * cm, 4.0 * cm, 4.3 * cm],
        repeatRows=1
    )

    tabela_itens.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), bordo),
        ("GRID", (0, 0), (-1, -1), 0.4, rosa),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [branco, rosa_claro]),
        ("FONTNAME", (0, 1), (-1, -1), "MontserratRegular"),
        ("FONTSIZE", (0, 1), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (1, 1), (1, -1), "CENTER"),
        ("ALIGN", (2, 1), (-1, -1), "RIGHT"),
        ("ALIGN", (1, 0), (-1, 0), "CENTER"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9)
    ]))

    conteudo.append(tabela_itens)
    conteudo.append(Spacer(1, 13))

    # FRETE E TOTAL

    frete = pedido["valor_frete_centavos"] or 0

    estilo_valor_frete = ParagraphStyle(
        "ValorFrete",
        parent=estilo_normal,
        alignment=TA_RIGHT
    )

    tabela_valores = Table(
        [
            [
                Paragraph("Frete", estilo_normal),
                Paragraph(formatar_moeda(frete), estilo_valor_frete)
            ],
            [
                Paragraph("TOTAL DO PEDIDO", estilo_total_label),
                Paragraph(
                    formatar_moeda(pedido["valor_total_centavos"]),
                    estilo_total_valor
                )
            ]
        ],
        colWidths=[10 * cm, 7 * cm]
    )

    tabela_valores.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), rosa_claro),
        ("BACKGROUND", (0, 1), (-1, 1), rosa),
        ("BOX", (0, 0), (-1, -1), 0.6, rosa),
        ("LINEABOVE", (0, 1), (-1, 1), 0.8, bordo),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10)
    ]))

    conteudo.append(tabela_valores)
    conteudo.append(Spacer(1, 25))

    # MENSAGEM FINAL

    conteudo.append(Paragraph(
        "Agradecemos pela preferência!",
        estilo_agradecimento
    ))

    conteudo.append(Spacer(1, 5))

    conteudo.append(Paragraph(
        "Seu pedido foi registrado com carinho pela Toque de Amor.",
        estilo_centro
    ))

    # GERAÇÃO DO PDF

    documento.build(
        conteudo,
        onFirstPage=desenhar_pagina,
        onLaterPages=desenhar_pagina
    )

    return send_file(
        caminho_pdf,
        as_attachment=True,
        download_name=f"Toque_de_Amor_Pedido_{id}.pdf",
        mimetype="application/pdf"
    )


# =====================================================
# EXCLUIR PEDIDO
# =====================================================

@app.route("/excluir_pedido/<int:id>", methods=["POST"])
@login_obrigatorio
def excluir_pedido(id):

    conexao = conectar_banco()

    try:

        conexao.execute("""
            DELETE FROM itens_pedido
            WHERE pedido_id = ?
        """, (id,))

        conexao.execute("""
            DELETE FROM pedidos
            WHERE id = ?
        """, (id,))

        quantidade_pedidos = conexao.execute("""
            SELECT COUNT(*) FROM pedidos
        """).fetchone()[0]

        if quantidade_pedidos == 0:
            conexao.execute("""
                DELETE FROM sqlite_sequence
                WHERE name = 'pedidos'
            """)

        conexao.commit()

    except Exception:
        conexao.rollback()
        conexao.close()
        raise

    conexao.close()

    return redirect(url_for("pedidos"))


# =====================================================
# NOVO PEDIDO
# =====================================================

@app.route("/novo_pedido", methods=["GET", "POST"])
@login_obrigatorio
def novo_pedido():

    if request.method == "POST":

        cliente_nome = request.form["cliente_nome"]
        cliente_telefone = request.form["cliente_telefone"]
        data_pedido = request.form["data_pedido"]
        data_entrega = request.form["data_entrega"]
        tipo_entrega = request.form["tipo_entrega"]
        endereco = request.form.get("endereco", "")
        municipio = request.form.get("municipio", "")
        forma_pagamento = request.form["forma_pagamento"]

        valor_frete = request.form.get("valor_frete", "0")

        if tipo_entrega == "Delivery":
            valor_frete_centavos = decimal_para_centavos(valor_frete)
        else:
            valor_frete_centavos = 0

        produto_ids = request.form.getlist("produto_id[]")
        quantidades = request.form.getlist("quantidade[]")

        conexao = conectar_banco()

        try:

            itens = []
            subtotal_geral = 0

            for produto_id, quantidade in zip(produto_ids, quantidades):

                if not produto_id:
                    continue

                quantidade = int(quantidade)

                if quantidade <= 0:
                    raise ValueError(
                        "A quantidade deve ser maior que zero."
                    )

                produto = conexao.execute("""
                    SELECT id, nome, preco
                    FROM produtos
                    WHERE id = ? AND ativo = 1
                """, (produto_id,)).fetchone()

                if produto is None:
                    raise ValueError(
                        "Um dos produtos selecionados não está disponível."
                    )

                preco_centavos = decimal_para_centavos(produto["preco"])
                subtotal_item = preco_centavos * quantidade

                itens.append({
                    "produto_id": produto["id"],
                    "nome": produto["nome"],
                    "preco": preco_centavos,
                    "quantidade": quantidade,
                    "subtotal": subtotal_item
                })

                subtotal_geral += subtotal_item

            if not itens:
                raise ValueError("Selecione pelo menos um produto.")

            valor_total = subtotal_geral + valor_frete_centavos

            cursor = conexao.execute("""
                INSERT INTO pedidos (
                    cliente_nome,
                    cliente_telefone,
                    data_pedido,
                    data_entrega,
                    tipo_entrega,
                    valor_frete_centavos,
                    endereco,
                    municipio,
                    forma_pagamento,
                    valor_total_centavos
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cliente_nome,
                cliente_telefone,
                data_pedido,
                data_entrega,
                tipo_entrega,
                valor_frete_centavos,
                endereco,
                municipio,
                forma_pagamento,
                valor_total
            ))

            pedido_id = cursor.lastrowid

            for item in itens:

                conexao.execute("""
                    INSERT INTO itens_pedido (
                        pedido_id,
                        produto_id,
                        nome_produto,
                        preco_unitario_centavos,
                        quantidade,
                        subtotal_centavos
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    pedido_id,
                    item["produto_id"],
                    item["nome"],
                    item["preco"],
                    item["quantidade"],
                    item["subtotal"]
                ))

            conexao.commit()
            conexao.close()

            return redirect(url_for("pedidos"))

        except Exception as erro:

            conexao.rollback()
            conexao.close()

            return f"Erro ao salvar pedido: {erro}"

    conexao = conectar_banco()

    lista_produtos = conexao.execute("""
        SELECT *
        FROM produtos
        WHERE ativo = 1
        ORDER BY categoria, nome
    """).fetchall()

    conexao.close()

    return render_template(
        "novo_pedido.html",
        produtos=lista_produtos
    )


# =====================================================
# RELATÓRIOS
# =====================================================

@app.route("/relatorios")
@login_obrigatorio
def relatorios():

    data_inicio = request.args.get("data_inicio", "")
    data_fim = request.args.get("data_fim", "")

    conexao = conectar_banco()

    condicoes = []
    parametros = []

    if data_inicio:
        condicoes.append("DATE(data_pedido) >= DATE(?)")
        parametros.append(data_inicio)

    if data_fim:
        condicoes.append("DATE(data_pedido) <= DATE(?)")
        parametros.append(data_fim)

    filtro = ""

    if condicoes:
        filtro = "WHERE " + " AND ".join(condicoes)

    # INDICADORES GERAIS

    indicadores = conexao.execute(f"""
        SELECT
            COUNT(*) AS total_pedidos,
            COALESCE(SUM(valor_total_centavos), 0) AS faturamento,
            COALESCE(AVG(valor_total_centavos), 0) AS ticket_medio
        FROM pedidos
        {filtro}
    """, parametros).fetchone()

    # PRODUTOS MAIS VENDIDOS

    produtos_mais_vendidos = conexao.execute(f"""
        SELECT
            ip.nome_produto,
            SUM(ip.quantidade) AS quantidade_vendida,
            SUM(ip.subtotal_centavos) AS faturamento_produto
        FROM itens_pedido ip
        INNER JOIN pedidos p
            ON p.id = ip.pedido_id
        {filtro.replace("data_pedido", "p.data_pedido") if filtro else ""}
        GROUP BY ip.nome_produto
        ORDER BY quantidade_vendida DESC
        LIMIT 5
    """, parametros).fetchall()

    # EVOLUÇÃO MENSAL

    faturamento_mensal = conexao.execute(f"""
        SELECT
            strftime('%Y-%m', p.data_pedido) AS mes,
            COALESCE(SUM(p.valor_total_centavos), 0) AS faturamento,
            COUNT(*) AS total_pedidos
        FROM pedidos p
        {filtro.replace("data_pedido", "p.data_pedido") if filtro else ""}
        GROUP BY strftime('%Y-%m', p.data_pedido)
        ORDER BY mes ASC
    """, parametros).fetchall()

    conexao.close()

    return render_template(
        "relatorios.html",
        indicadores=indicadores,
        produtos_mais_vendidos=produtos_mais_vendidos,
        faturamento_mensal=faturamento_mensal,
        data_inicio=data_inicio,
        data_fim=data_fim
    )


# =====================================================
# INICIALIZAÇÃO DO SISTEMA
# =====================================================

# Cria as tabelas e atualiza os campos necessários.
inicializar_banco()

# Cria a tabela de usuários, caso ainda não exista.
inicializar_tabela_usuarios()


# =====================================================
# EXECUTAR LOCALMENTE
# =====================================================

if __name__ == "__main__":

    criar_backup_automatico()

    criar_administrador_inicial()

    app.run(debug=True, use_reloader=False)


# =====================================================
# EXECUTAR NO SERVIDOR (RENDER)
# =====================================================

else:

    criar_administrador_por_variaveis()