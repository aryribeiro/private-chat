Obs.: caso o app esteja no modo "sleeping" (dormindo) ao entrar, basta clicar no botão que estará disponível e aguardar, para ativar o mesmo. 
![print](https://github.com/user-attachments/assets/9820f420-0cca-4171-9dad-cca1e3f66430)
# 💬 Private Chat: Web App em Python e Streamlit

Um web app de **chat moderno em tempo real**, inspirado no clássico UOL Chat, criado com Python e Streamlit. Suporta **conversas públicas e privadas (com PIN)**, **emojis**, **envio de imagens**, **painel de administração**, e visual estilizado com HTML/CSS/JS injetados.

## ✨ Funcionalidades

- 🌍 Chat público com atualização automática
- 🔒 Chat privado com PIN personalizado
- 👤 Login via nickname (sem senha)
- 🖼️ Upload e envio de imagens PNG/JPG
- 😄 Suporte a emojis (ex.: Olá pessoal! :smile: :rocket:)
- 🧹 Limpeza de chat (apenas para administradores)
- 🔨 Banimento de usuários
- 📊 Métricas de usuários e salas
- 💅 Visual moderno com CSS personalizado
- 🔁 Atualização automática a cada 3s (opcional)
- 💾 Salvamento persistente via `chat_data.json`


## 🚀 Tecnologias Utilizadas

- [Streamlit](https://streamlit.io/)
- [Python 3.8+](https://www.python.org/)
- [Pillow](https://pillow.readthedocs.io/)
- [emoji](https://pypi.org/project/emoji/)
- [streamlit-autorefresh](https://pypi.org/project/streamlit-autorefresh/)


## 🖥️ Como Executar Localmente

### 1. Clone o repositório

git clone https://github.com/aryribeiro/private-chat.git
cd private-chat

2. Crie um ambiente virtual (opcional)

python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate no Windows

3. Instale as dependências

pip install -r requirements.txt

4. Execute o app

streamlit run app.py

📁 Estrutura do Projeto

private-chat/
│
├── app.py                # Código principal do aplicativo
├── chat_data.json        # Armazena mensagens e usuários (gerado dinamicamente)
├── requirements.txt      # Lista de dependências
└── README.md             # Documentação do projeto

⚠️ Limitações Atuais

    Sem autenticação real (nickname apenas)

    Armazenamento em arquivo local (JSON), não recomendado para produção com muitos usuários simultâneos

    Streamlit não usa WebSocket, então não é "tempo real verdadeiro" — apenas simulado com atualizações automáticas

🧠 Melhorias Futuras

    Integração com PostgreSQL, Firebase ou Redis

    Suporte a autenticação real (OAuth, email/senha)

    Backend com WebSocket usando FastAPI

    Deploy com Docker ou Streamlit Cloud

📸 Screenshot

    Adicione aqui um screenshot do app rodando com st.image(...)

📄 Licença

Este projeto está licenciado sob a MIT License. Sinta-se livre para usar, modificar e distribuir.
🙌 Agradecimentos

Desenvolvido com ❤️ por Ary Ribeiro
