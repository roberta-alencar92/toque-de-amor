
import sqlite3

# =====================================================
# CONEXÃO COM O BANCO DE DADOS
# =====================================================

conexao = sqlite3.connect("database/toque_de_amor.db")

try:

    cursor = conexao.cursor()

    # =================================================
    # NOVA LISTA DE PRODUTOS
    # =================================================

    produtos = [
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
    # SUBSTITUIR CADASTRO ANTIGO
    # =====================================================

    cursor.execute("DELETE FROM produtos")

    cursor.executemany("""
        INSERT INTO produtos (nome, categoria, preco, unidade)
        VALUES (?, ?, ?, ?)
    """, produtos)

    conexao.commit()

    print("Cadastro atualizado com sucesso!")
    print(f"Total de produtos cadastrados: {len(produtos)}")

except Exception as erro:

    conexao.rollback()
    print(f"Erro ao atualizar produtos: {erro}")

finally:

    conexao.close()
