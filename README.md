# AutoPrime — Website Institucional para Concessionária

Este projeto consiste no desenvolvimento de um website institucional para a empresa **AutoPrime**, com o objetivo de divulgar informações da empresa, apresentar veículos disponíveis para venda e disponibilizar um canal de contato com os clientes.  

O website foi desenvolvido utilizando tecnologias modernas e responsivas, garantindo boa experiência de navegação em computadores, tablets e smartphones.

---

## Tecnologias Utilizadas  

- Python (Django)
- SQLite  
- HTML5  
- CSS3  
- JavaScript  
- Bootstrap  

---

## Funcionalidades  

- 📄 Página inicial com carrossel de imagens e informações de destaque  
- Página "Sobre a Empresa" com informações institucionais  
- Catálogo de veículos com imagem, descrição e preço  
- Formulário de contato com validação e armazenamento no banco de dados  
- Design responsivo para diferentes dispositivos  
- Área administrativa (Django Admin) para cadastro e gerenciamento de veículos e contatos  

---

## Instalação e Execução  

### Pré-requisitos

- Python 3.x instalado  
- Virtualenv (opcional, mas recomendado)  

### Passos

1. Clone este repositório:
   ```bash
   git clone https://github.com/seuusuario/autoprime-website.git
   cd autoprime-website

2. Crie e ative o ambiente virtual (opcional):

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

4. Execute as migrações do banco de dados:

   ```bash
   python manage.py migrate
   ```

5. Inicie o servidor de desenvolvimento:

   ```bash
   python manage.py runserver
   ```

6. Acesse no navegador:

   ```
   http://127.0.0.1:8000/
   ```

7. Para acessar o painel administrativo:

   ```
   http://127.0.0.1:8000/admin
   ```

   *(crie um superusuário caso ainda não tenha)*

   ```bash
   python manage.py createsuperuser
   ```


---

## Contribuições

Contribuições são bem-vindas!
Sinta-se à vontade para abrir issues ou enviar pull requests com melhorias, correções ou sugestões.

---

## Licença

Este projeto está licenciado sob a licença **MIT**. Consulte o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## Contato

Projeto desenvolvido por **Seu Nome**.
📧 [pauloximana@gmail.com](mailto:pauloximana@gmail.com)


---

