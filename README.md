# 🍫 Toque de Amor — Sistema de Gestão de Confeitaria

Sistema web desenvolvido para auxiliar na gestão de pedidos, produtos e informações comerciais da confeitaria **Toque de Amor**.

O projeto nasceu com o objetivo de facilitar a organização da rotina da confeitaria, centralizando informações e oferecendo ferramentas para tornar o gerenciamento dos pedidos mais simples, prático e eficiente.

Atualmente, o sistema conta com uma interface personalizada, desenvolvida especialmente para a identidade visual da marca.

---

## ✨ Funcionalidades

- **Autenticação:** acesso ao sistema por meio de login administrativo.
- **Painel inicial:** área principal de navegação do sistema.
- **Cadastro de produtos:** gerenciamento de produtos, categorias, preços e unidades.
- **Gestão de pedidos:** registro e acompanhamento de pedidos de clientes.
- **Controle de entregas:** informações sobre retirada, entrega, endereço e frete.
- **Formas de pagamento:** registro da modalidade de pagamento dos pedidos.
- **Relatórios:** geração de relatórios em PDF.
- **Banco de dados:** armazenamento das informações utilizando SQLite.

---

## 🛠️ Tecnologias utilizadas

| Tecnologia | Aplicação |
|---|---|
| Python | Linguagem principal |
| Flask | Framework web |
| SQLite | Banco de dados |
| HTML5 | Estrutura das páginas |
| CSS3 | Estilização e identidade visual |
| Flask-WTF | Proteção CSRF |
| ReportLab | Geração de documentos PDF |
| Gunicorn | Servidor de aplicação |
| Git e GitHub | Controle de versão e hospedagem do código |

---

## 📁 Estrutura do projeto

```text
App/
│
├── app.py
├── requirements.txt
├── .gitignore
│
├── database/
│   ├── banco.py
│   ├── inicializar_banco.py
│   ├── cadastrar_produtos.py
│   └── atualizar_pedidos.py
│
├── templates/
│   ├── index.html
│   ├── produtos.html
│   ├── pedidos.html
│   ├── novo_pedido.html
│   ├── relatorios.html
│   └── login.html
│
├── static/
│   └── Logo.png
│
├── fonts/
│
├── backups/
└── pdfs/
```

---

