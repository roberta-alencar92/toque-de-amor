import sqlite3

# Conectar ao banco de dados
conexao = sqlite3.connect("database/toque_de_amor.db")

cursor = conexao.cursor()

# Lista inicial de produtos
produtos = [
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

# Inserir produtos no banco
cursor.executemany("""
    INSERT INTO produtos (nome, categoria, preco, unidade)
    VALUES (?, ?, ?, ?)
""", produtos)

conexao.commit()
conexao.close()

print("Produtos cadastrados com sucesso!")