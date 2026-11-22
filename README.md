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

## 💻 Como executar o projeto localmente

### 1. Clone o repositório

```bash
git clone https://github.com/roberta-alencar92/toque-de-amor.git
```

### 2. Entre na pasta do projeto

```bash
cd toque-de-amor
```

### 3. Crie um ambiente virtual

```bash
python -m venv venv
```

### 4. Ative o ambiente virtual

No Windows:

```bash
venv\Scripts\activate
```

### 5. Instale as dependências

```bash
pip install -r requirements.txt
```

### 6. Configure as variáveis de ambiente

Antes de executar, configure uma chave secreta para a aplicação e as credenciais administrativas.

Não compartilhe senhas ou chaves secretas no repositório.

### 7. Execute a aplicação

```bash
python app.py
```

Acesse pelo navegador:

```text
http://127.0.0.1:5000
```

---

## 🌐 Hospedagem

O sistema possui uma versão publicada na plataforma Render:

**https://toque-de-amor.onrender.com**

A disponibilidade e a persistência dos dados dependem das configurações do serviço de hospedagem.

---

## 🔒 Segurança e armazenamento

- Senhas administrativas armazenadas utilizando hash.
- Proteção CSRF nos formulários.
- Credenciais e chaves secretas configuradas por variáveis de ambiente.
- Arquivos de banco de dados e backups locais excluídos do controle de versão.

**Importante:** a versão gratuita de hospedagem utiliza armazenamento efêmero. Antes de utilizar o sistema com dados reais da confeitaria, é necessário configurar uma solução de banco de dados persistente e validar a estratégia de backups.

---

## ❤️ Sobre o projeto

O **Toque de Amor** é um projeto desenvolvido com dedicação, aprendizado e o propósito de transformar uma necessidade real em uma solução tecnológica.

Mais do que um sistema de gestão, representa a aplicação prática de conhecimentos em desenvolvimento web, organização de dados e automação de processos.

**Desenvolvimento:** Roberta Alencar  
**Projeto:** Toque de Amor — Sistema de Gestão de Confeitaria

---

*Feito com dedicação, tecnologia e um toque de amor. 🍫❤️*
