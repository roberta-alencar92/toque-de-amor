
import sqlite3

# Conectar ao banco de dados
conexao = sqlite3.connect("database/toque_de_amor.db")

# Criar um cursor para executar comandos SQL
cursor = conexao.cursor()

# Criar a tabela de produtos
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

# Criar a tabela de pedidos
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

# Criar a tabela de itens dos pedidos
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

# Salvar as alterações
conexao.commit()

# Fechar a conexão
conexao.close()

print("Banco de dados criado com sucesso!")