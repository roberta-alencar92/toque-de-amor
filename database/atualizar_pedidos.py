
import sqlite3

conexao = sqlite3.connect("database/toque_de_amor.db")
cursor = conexao.cursor()

# Verifica quais colunas já existem na tabela pedidos
cursor.execute("PRAGMA table_info(pedidos)")
colunas_existentes = [coluna[1] for coluna in cursor.fetchall()]

# Novos campos que precisamos adicionar
novas_colunas = {
    "data_pedido": "TEXT",
    "tipo_entrega": "TEXT DEFAULT 'Retirada'",
    "valor_frete_centavos": "INTEGER DEFAULT 0",
    "endereco": "TEXT",
    "municipio": "TEXT",
    "forma_pagamento": "TEXT"
}

# Adiciona somente as colunas que ainda não existem
for nome, tipo in novas_colunas.items():
    if nome not in colunas_existentes:
        cursor.execute(
            f"ALTER TABLE pedidos ADD COLUMN {nome} {tipo}"
        )

conexao.commit()
conexao.close()

print("Tabela de pedidos atualizada com sucesso!")