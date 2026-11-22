
import os
import sqlite3


# =====================================================
# CAMINHO DO BANCO DE DADOS
# =====================================================

PASTA_ATUAL = os.path.dirname(os.path.abspath(__file__))

CAMINHO_BANCO = os.environ.get(
    "DATABASE_PATH",
    os.path.join(PASTA_ATUAL, "toque_de_amor.db")
)

os.makedirs(
    os.path.dirname(os.path.abspath(CAMINHO_BANCO)),
    exist_ok=True
)


# =====================================================
# PRODUTOS INICIAIS
# =====================================================

PRODUTOS_INICIAIS = [

    ("Forminhas Acetato (50 un)", "Forminhas", 5.80, "Pacote"),
    ("Forminhas Acetato (1 un)", "Forminhas", 0.12, "Unidade"),

    ("Tradicional - Ninho", "Tradicional", 1.30, "Unidade"),
    ("Tradicional - Brigadeiro", "Tradicional", 1.30, "Unidade"),
    ("Tradicional - Beijinho", "Tradicional", 1.30, "Unidade"),
    ("Tradicional - Coco Queimado", "Tradicional", 1.30, "Unidade"),
    ("Tradicional - Nesquik", "Tradicional", 1.30, "Unidade"),
    ("Tradicional - Paçoca", "Tradicional", 1.30, "Unidade"),

    ("Especiais - Casadinho", "Especiais", 1.40, "Unidade"),
    ("Especiais - Churros", "Especiais", 1.40, "Unidade"),
    ("Especiais - Cappuccino", "Especiais", 1.40, "Unidade"),
    ("Especiais - Cajuzinho", "Especiais", 1.40, "Unidade"),

    ("Gourmet - Maracujá", "Gourmet", 1.80, "Unidade"),
    ("Gourmet - Limão", "Gourmet", 1.80, "Unidade"),
    ("Gourmet - Creme Brulée", "Gourmet", 1.80, "Unidade"),
    ("Gourmet - Prestígio", "Gourmet", 1.80, "Unidade"),
    ("Gourmet - Olho de Sogra", "Gourmet", 1.80, "Unidade"),
    ("Gourmet - Paçoca Especial", "Gourmet", 1.80, "Unidade"),

    ("Queridinhos - Ferrero Rocher", "Queridinhos", 2.15, "Unidade"),
    ("Queridinhos - Ninho com Nutella", "Queridinhos", 2.15, "Unidade"),
    ("Queridinhos - Chocolate Branco", "Queridinhos", 2.15, "Unidade"),
    ("Queridinhos - Romeu & Julieta", "Queridinhos", 2.15, "Unidade"),
    ("Queridinhos - Surpresa de Uva", "Queridinhos", 2.15, "Unidade"),
    ("Queridinhos - Caramelo Salgado", "Queridinhos", 2.15, "Unidade"),

    ("Especialidades - Confetti", "Especialidades", 2.50, "Unidade"),
    ("Especialidades - Kinder Bueno", "Especialidades", 2.50, "Unidade"),
    ("Especialidades - Mini Brownie", "Especialidades", 2.50, "Unidade"),
    ("Especialidades - Surpresa de Uva", "Especialidades", 2.50, "Unidade")
]


# =====================================================
# INICIALIZAÇÃO DO BANCO
# =====================================================

def inicializar_banco():

    conexao = sqlite3.connect(CAMINHO_BANCO)

    try:

        cursor = conexao.cursor()

        # -------------------------------------------------
        # TABELA DE PRODUTOS
        # -------------------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                categoria TEXT NOT NULL,
                preco REAL NOT NULL,
                unidade TEXT NOT NULL,
                ativo INTEGER DEFAULT 1
            )
        """)

        # -------------------------------------------------
        # TABELA DE PEDIDOS
        # -------------------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pedidos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_nome TEXT NOT NULL,
                cliente_telefone TEXT,
                data_entrega TEXT,
                observacoes TEXT,
                status TEXT DEFAULT 'Pendente',
                valor_total_centavos INTEGER DEFAULT 0,
                criado_em TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # -------------------------------------------------
        # TABELA DE ITENS DOS PEDIDOS
        # -------------------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS itens_pedido (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pedido_id INTEGER NOT NULL,
                produto_id INTEGER NOT NULL,
                nome_produto TEXT NOT NULL,
                preco_unitario_centavos INTEGER NOT NULL,
                quantidade INTEGER NOT NULL,
                subtotal_centavos INTEGER NOT NULL,
                FOREIGN KEY (pedido_id) REFERENCES pedidos(id),
                FOREIGN KEY (produto_id) REFERENCES produtos(id)
            )
        """)

        # -------------------------------------------------
        # CAMPOS ADICIONAIS DOS PEDIDOS
        # -------------------------------------------------

        cursor.execute("PRAGMA table_info(pedidos)")

        colunas_existentes = [
            coluna[1] for coluna in cursor.fetchall()
        ]

        novas_colunas = {
            "data_pedido": "TEXT",
            "tipo_entrega": "TEXT DEFAULT 'Retirada'",
            "valor_frete_centavos": "INTEGER DEFAULT 0",
            "endereco": "TEXT",
            "municipio": "TEXT",
            "forma_pagamento": "TEXT"
        }

        for nome, tipo in novas_colunas.items():

            if nome not in colunas_existentes:

                cursor.execute(
                    f"ALTER TABLE pedidos ADD COLUMN {nome} {tipo}"
                )

        # -------------------------------------------------
        # CADASTRO AUTOMÁTICO DOS PRODUTOS INICIAIS
        # -------------------------------------------------

        cursor.execute("""
            SELECT COUNT(*) FROM produtos
        """)

        quantidade_produtos = cursor.fetchone()[0]

        if quantidade_produtos == 0:

            cursor.executemany("""
                INSERT INTO produtos (
                    nome,
                    categoria,
                    preco,
                    unidade
                )
                VALUES (?, ?, ?, ?)
            """, PRODUTOS_INICIAIS)

            print("Produtos iniciais cadastrados com sucesso!")

        conexao.commit()

    except Exception:

        conexao.rollback()
        raise

    finally:

        conexao.close()


# =====================================================
# EXECUÇÃO DIRETA
# =====================================================

if __name__ == "__main__":

    inicializar_banco()

    print("Banco de dados inicializado com sucesso!")
