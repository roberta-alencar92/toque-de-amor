
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
# CATÁLOGO ATUAL DA TOQUE DE AMOR
# =====================================================

PRODUTOS_INICIAIS = [

    ("Forminhas Acetato (50 un)", "Forminhas", 6.00, "Pacote"),
    ("Forminhas Acetato (1 un)", "Forminhas", 0.15, "Unidade"),

    ("Tradicional - Ninho", "Tradicional", 1.30, "Unidade"),
    ("Tradicional - Brigadeiro", "Tradicional", 1.30, "Unidade"),
    ("Tradicional - Beijinho", "Tradicional", 1.30, "Unidade"),
    ("Tradicional - Nesquik", "Tradicional", 1.30, "Unidade"),
    ("Tradicional - Paçoca", "Tradicional", 1.30, "Unidade"),

    ("Especiais - Casadinho", "Especiais", 1.40, "Unidade"),
    ("Especiais - Churros", "Especiais", 1.40, "Unidade"),
    ("Especiais - Cappuccino", "Especiais", 1.40, "Unidade"),
    ("Especiais - Cajuzinho", "Especiais", 1.40, "Unidade"),
    ("Especiais - Coco Queimado", "Especiais", 1.40, "Unidade"),
    ("Especiais - Ninho Colorido", "Especiais", 1.40, "Unidade"),

    ("Premium - Maracujá", "Premium", 1.80, "Unidade"),
    ("Premium - Limão", "Premium", 1.80, "Unidade"),
    ("Premium - Creme Brulée", "Premium", 1.80, "Unidade"),
    ("Premium - Prestígio", "Premium", 1.80, "Unidade"),
    ("Premium - Olho de Sogra", "Premium", 1.80, "Unidade"),
    ("Premium - Paçoca Especial", "Premium", 1.80, "Unidade"),

    ("Gourmet - Ferrero Rocher", "Gourmet", 2.15, "Unidade"),
    ("Gourmet - Ninho com Nutella", "Gourmet", 2.15, "Unidade"),
    ("Gourmet - Brigadeiro Branco", "Gourmet", 2.15, "Unidade"),
    ("Gourmet - Romeu & Julieta", "Gourmet", 2.15, "Unidade"),
    ("Gourmet - Surpresa de Uva", "Gourmet", 2.15, "Unidade"),
    ("Gourmet - Caramelo Salgado", "Gourmet", 2.15, "Unidade"),
    ("Gourmet - Sensação", "Gourmet", 2.15, "Unidade"),

    ("Gourmet Especial - Confetti", "Gourmet Especial", 2.50, "Unidade"),
    ("Gourmet Especial - Kinder Bueno", "Gourmet Especial", 2.50, "Unidade"),
    ("Gourmet Especial - Mini Brownie", "Gourmet Especial", 2.50, "Unidade"),
    ("Gourmet Especial - Surpresa de Uva", "Gourmet Especial", 2.50, "Unidade"),

    ("Finos - Camafeu de Nozes", "Finos", 3.00, "Unidade"),
    ("Finos - Copinho Recheado", "Finos", 3.00, "Unidade"),
    ("Finos - Concha", "Finos", 3.00, "Unidade")
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
        # CONTROLE DE ATUALIZAÇÃO DO CATÁLOGO
        # -------------------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS controle_migracoes (
                chave TEXT PRIMARY KEY,
                executada_em TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        chave_migracao = "catalogo_toque_de_amor_v2"

        cursor.execute("""
            SELECT chave
            FROM controle_migracoes
            WHERE chave = ?
        """, (chave_migracao,))

        migracao_realizada = cursor.fetchone()

        if not migracao_realizada:

            # Verificar se existem pedidos ou itens vinculados

            cursor.execute("SELECT COUNT(*) FROM pedidos")
            quantidade_pedidos = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM itens_pedido")
            quantidade_itens = cursor.fetchone()[0]

            if quantidade_pedidos > 0 or quantidade_itens > 0:

                raise RuntimeError(
                    "Atualização do catálogo interrompida: "
                    "existem pedidos cadastrados no banco."
                )

            # Substituir o catálogo antigo

            cursor.execute("DELETE FROM produtos")

            cursor.executemany("""
                INSERT INTO produtos (
                    nome,
                    categoria,
                    preco,
                    unidade
                )
                VALUES (?, ?, ?, ?)
            """, PRODUTOS_INICIAIS)

            # Registrar que a atualização já foi realizada

            cursor.execute("""
                INSERT INTO controle_migracoes (chave)
                VALUES (?)
            """, (chave_migracao,))

            print("Catálogo atualizado com sucesso!")
            print(
                f"Total de produtos: {len(PRODUTOS_INICIAIS)}"
            )

        else:

            # Caso seja a primeira inicialização de um banco
            # com essa migração já registrada, não alterar nada.

            print("Catálogo já está atualizado.")

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
