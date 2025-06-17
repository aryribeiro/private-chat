import streamlit as st
import json
import os
from datetime import datetime
import emoji
from PIL import Image
import base64
import io
import time
import hashlib
from streamlit_autorefresh import st_autorefresh

# Configuração da página
st.set_page_config(
    page_title="Private Chat",
    page_icon="💬",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# CSS personalizado para visual moderno estilo UOL Chat
def load_css():
    st.markdown("""
    <style>
    /* Estilo global */
    .main > div {
        padding-top: 2rem;
    }
    
    /* Cabeçalho */
    .chat-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .chat-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    /* Container do chat */
    .chat-container {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 15px;
        padding: 20px;
        max-height: 500px;
        overflow-y: auto;
        margin-bottom: 20px;
        box-shadow: inset 0 2px 10px rgba(0,0,0,0.1);
    }
    
    /* Mensagens */
    .message-bubble {
        background: white;
        padding: 12px 16px;
        border-radius: 20px;
        margin: 8px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        position: relative;
        word-wrap: break-word;
        animation: fadeIn 0.3s ease-in;
    }
    
    .message-bubble.own {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-left: 20%;
    }
    
    .message-bubble.other {
        background: white;
        margin-right: 20%;
    }
    
    .message-header {
        font-size: 0.8rem;
        opacity: 0.7;
        margin-bottom: 5px;
        font-weight: bold;
    }
    
    .message-time {
        font-size: 0.7rem;
        opacity: 0.5;
        margin-top: 5px;
    }
    
    /* Animação */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Formulário de entrada */
    .input-container {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Botões personalizados */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 10px 25px;
        font-weight: bold;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Status indicators */
    .status-online {
        color: #4CAF50;
        font-weight: bold;
    }
    
    .status-private {
        color: #FF9800;
        font-weight: bold;
    }
    
    /* Image container */
    .image-message {
        text-align: center;
        margin: 10px 0;
    }
    
    .image-message img {
        max-width: 300px;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }
    
    /* Ocultar elementos vazios do Streamlit */
    .element-container:has(.stEmpty) {
        display: none !important;
    }
    
    .block-container .element-container:empty {
        display: none !important;
    }
    
    /* Ocultar divs vazias */
    div:empty {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Classe principal do Chat
class PrivateChat:
    def __init__(self):
        self.data_file = "chat_data.json"
        self.init_session_state()
        self.load_data()
    
    def init_session_state(self):
        """Inicializa o estado da sessão"""
        if 'chat_data' not in st.session_state:
            st.session_state.chat_data = {
                'public_messages': [],
                'private_messages': {},
                'users': set(),
                'banned_users': set(),
                'private_pins': {},
                'private_banned_users': {}
            }
        
        if 'current_user' not in st.session_state:
            st.session_state.current_user = None
        
        if 'current_room' not in st.session_state:
            st.session_state.current_room = None
        
        if 'current_pin' not in st.session_state:
            st.session_state.current_pin = None
        
        if 'auto_refresh' not in st.session_state:
            st.session_state.auto_refresh = True
    
    def load_data(self):
        """Carrega dados do arquivo JSON"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        data = json.loads(content)
                        st.session_state.chat_data.update(data)
                        # Converter sets que foram salvos como listas
                        st.session_state.chat_data['users'] = set(st.session_state.chat_data.get('users', []))
                        st.session_state.chat_data['banned_users'] = set(st.session_state.chat_data.get('banned_users', []))
                        # Inicializar campos que podem não existir
                        if 'private_banned_users' not in st.session_state.chat_data:
                            st.session_state.chat_data['private_banned_users'] = {}
        except (json.JSONDecodeError, Exception) as e:
            st.session_state.chat_data = {
                'public_messages': [],
                'private_messages': {},
                'users': set(),
                'banned_users': set(),
                'private_pins': {},
                'private_banned_users': {}
            }
    
    def save_data(self):
        """Salva dados no arquivo JSON"""
        try:
            data_to_save = st.session_state.chat_data.copy()
            # Converter sets para listas para JSON
            data_to_save['users'] = list(data_to_save['users'])
            data_to_save['banned_users'] = list(data_to_save['banned_users'])
            
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=2)
        except Exception as e:
            st.error(f"Erro ao salvar dados: {e}")
    
    def generate_user_id(self, username):
        """Gera um ID único para o usuário"""
        return hashlib.md5(f"{username}_{datetime.now().isoformat()}".encode()).hexdigest()[:8]
    
    def add_message(self, room_type, message, user, message_type="text", pin=None):
        """Adiciona uma mensagem ao chat"""
        timestamp = datetime.now()
        message_data = {
            'user': user,
            'message': message,
            'timestamp': timestamp.isoformat(),
            'type': message_type,
            'id': self.generate_user_id(f"{user}_{timestamp}")
        }
        
        if room_type == "public":
            st.session_state.chat_data['public_messages'].append(message_data)
        elif room_type == "private" and pin:
            if pin not in st.session_state.chat_data['private_messages']:
                st.session_state.chat_data['private_messages'][pin] = []
            st.session_state.chat_data['private_messages'][pin].append(message_data)
        
        self.save_data()
    
    def get_messages(self, room_type, pin=None):
        """Obtém mensagens do chat"""
        if room_type == "public":
            return st.session_state.chat_data['public_messages']
        elif room_type == "private" and pin:
            return st.session_state.chat_data['private_messages'].get(pin, [])
        return []
    
    def clear_chat(self, room_type, pin=None):
        """Limpa mensagens do chat"""
        if room_type == "public":
            st.session_state.chat_data['public_messages'] = []
        elif room_type == "private" and pin:
            if pin in st.session_state.chat_data['private_messages']:
                st.session_state.chat_data['private_messages'][pin] = []
        self.save_data()
    
    def ban_user(self, username, pin=None):
        """Bane um usuário"""
        if pin:
            # Ban específico para sala privada
            if pin not in st.session_state.chat_data['private_banned_users']:
                st.session_state.chat_data['private_banned_users'][pin] = set()
            st.session_state.chat_data['private_banned_users'][pin].add(username)
        else:
            # Ban global
            st.session_state.chat_data['banned_users'].add(username)
        self.save_data()
    
    def is_banned(self, username, pin=None):
        """Verifica se usuário está banido"""
        # Verificar ban global
        if username in st.session_state.chat_data['banned_users']:
            return True
        
        # Verificar ban específico da sala privada
        if pin and pin in st.session_state.chat_data['private_banned_users']:
            return username in st.session_state.chat_data['private_banned_users'][pin]
        
        return False
    
    def pin_exists(self, pin):
        """Verifica se PIN existe"""
        return pin in st.session_state.chat_data['private_pins']
    
    def image_to_base64(self, image):
        """Converte imagem para base64"""
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"
    
    def display_messages(self, messages, current_user):
        """Exibe mensagens do chat"""
        if not messages:
            st.markdown("**💬 Nenhuma mensagem ainda. Seja o primeiro a conversar!**")
            return
        
        # Container para mensagens
        for msg in messages[-50:]:  # Mostra apenas as últimas 50 mensagens
            try:
                timestamp = datetime.fromisoformat(msg['timestamp'])
                time_str = timestamp.strftime("%H:%M")
                
                # Determinar estilo da mensagem
                is_own = msg['user'] == current_user
                
                if msg['type'] == "image":
                    if is_own:
                        col1, col2 = st.columns([1, 4])
                        with col2:
                            st.markdown(f"**{msg['user']}** • {time_str}")
                            st.image(msg['message'], width=300)
                    else:
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            st.markdown(f"**{msg['user']}** • {time_str}")
                            st.image(msg['message'], width=300)
                else:
                    # Processar emojis
                    try:
                        message_text = emoji.emojize(msg['message'], language='alias')
                    except:
                        message_text = msg['message']
                    
                    if is_own:
                        col1, col2 = st.columns([1, 4])
                        with col2:
                            st.markdown(f"""
                            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                       color: white; padding: 12px; border-radius: 20px; margin: 5px 0;">
                                <div style="font-size: 0.8rem; opacity: 0.8; margin-bottom: 5px;">
                                    <strong>{msg['user']}</strong>
                                </div>
                                <div>{message_text}</div>
                                <div style="font-size: 0.7rem; opacity: 0.6; margin-top: 5px; text-align: right;">
                                    {time_str}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            st.markdown(f"""
                            <div style="background: white; color: #333; padding: 12px; border-radius: 20px; 
                                       margin: 5px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                                <div style="font-size: 0.8rem; opacity: 0.7; margin-bottom: 5px;">
                                    <strong>{msg['user']}</strong>
                                </div>
                                <div>{message_text}</div>
                                <div style="font-size: 0.7rem; opacity: 0.5; margin-top: 5px;">
                                    {time_str}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
            except Exception as e:
                continue
    
    def login_page(self):
        """Página de login"""
        st.markdown('''
        <div class="chat-header">
            <h1>💬 Private Chat</h1>
            <p>Sistema de Chat Moderno • Público & Privado</p>
        </div>
        ''', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("<h4 style='text-align: center;'>👤 Digite seu nickname</h4>", unsafe_allow_html=True)
            username = st.text_input(
                "Nome de usuário", 
                placeholder="nome ou apelido...", 
                key="username_input",
                label_visibility="collapsed"
            )
            
            if st.button("🚀 Entrar no Chat", type="primary", use_container_width=True):
                if username.strip():
                    if self.is_banned(username):
                        st.error("❌ Usuário banido do chat!")
                    elif len(username) < 3:
                        st.error("❌ Nome deve ter pelo menos 3 caracteres!")
                    else:
                        st.session_state.current_user = username.strip()
                        st.session_state.chat_data['users'].add(username.strip())
                        self.save_data()
                        st.rerun()
                else:
                    st.error("❌ Por favor, digite um nome válido!")
    
    def room_selection(self):
        """Seleção de sala"""
        st.markdown(f'''
        <div class="chat-header">
            <h1>💬 Private Chat</h1>
            <p>Bem-vindo, <strong>{st.session_state.current_user}</strong>!</p>
        </div>
        ''', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🌍 Chat Público")
            st.markdown("Converse com todos os usuários online")
            st.markdown(f"**👥 {len(st.session_state.chat_data['users'])} usuários conectados**")
            
            if st.button("🚀 Entrar no Chat Público", type="primary", use_container_width=True):
                st.session_state.current_room = "public"
                st.rerun()
        
        with col2:
            st.markdown("### 🔒 Chat Privado")
            st.markdown("Acesso restrito com PIN")
            
            pin = st.text_input(
                "PIN da sala privada", 
                type="password", 
                key="pin_input",
                placeholder="Digite o PIN...",
                label_visibility="collapsed"
            )
            
            col2a, col2b = st.columns(2)
            with col2a:
                if st.button("🔓 Entrar", use_container_width=True):
                    if pin.strip():
                        if not self.pin_exists(pin.strip()):
                            st.error("❌ PIN não existe! Solicite a criação da sala.")
                        elif self.is_banned(st.session_state.current_user, pin.strip()):
                            st.error("❌ Você foi banido desta sala privada!")
                        else:
                            st.session_state.current_room = "private"
                            st.session_state.current_pin = pin.strip()
                            st.rerun()
                    else:
                        st.error("❌ Digite um PIN válido!")
            
            with col2b:
                if st.button("🆕 Criar Sala", use_container_width=True):
                    if pin.strip() and len(pin.strip()) >= 4:
                        if self.pin_exists(pin.strip()):
                            st.error("❌ PIN já existe! Use outro PIN ou entre na sala existente.")
                        else:
                            st.session_state.current_room = "private"
                            st.session_state.current_pin = pin.strip()
                            st.session_state.chat_data['private_pins'][pin.strip()] = st.session_state.current_user
                            self.save_data()
                            st.success(f"✅ Sala criada com PIN: {pin.strip()}")
                            time.sleep(1)
                            st.rerun()
                    else:
                        st.error("❌ PIN deve ter pelo menos 4 caracteres!")
        
        # Botão de logout
        if st.button("🚪 Sair", type="secondary"):
            st.session_state.current_user = None
            st.session_state.current_room = None
            st.session_state.current_pin = None
            st.rerun()
    
    def chat_interface(self):
        """Interface principal do chat"""
        # Auto-refresh: atualiza a cada 3 segundos quando habilitado
        if st.session_state.auto_refresh:
            st_autorefresh(interval=3000, key="chat_refresh")
        
        room_name = "🌍 Chat Público" if st.session_state.current_room == "public" else f"🔒 Chat Privado (PIN: {st.session_state.current_pin})"
        
        # Header  
        st.markdown(f'''
        <div class="chat-header">
            <h1>{room_name}</h1>
            <p>👤 {st.session_state.current_user} • <span class="status-online">🟢 Online</span></p>
        </div>
        ''', unsafe_allow_html=True)
        
        # Área de mensagens
        messages = self.get_messages(st.session_state.current_room, st.session_state.current_pin)
        self.display_messages(messages, st.session_state.current_user)
        
        # Formulário de entrada
        st.markdown('<div class="input-container">', unsafe_allow_html=True)
        
        # Upload de imagem
        uploaded_file = st.file_uploader(
            "Selecionar imagem", 
            type=['png', 'jpg', 'jpeg'], 
            key="image_upload",
            label_visibility="collapsed",
            help="📎 Enviar imagem PNG ou JPG"
        )
        
        # Área de texto e botões
        col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
        
        with col1:
            message = st.text_input(
                "Mensagem de chat", 
                key="message_input", 
                placeholder="Digite sua mensagem... (use :smile:)",
                label_visibility="collapsed"
            )
        
        with col2:
            send_text = st.button("Envia", type="primary")

        with col3:
            if st.button("🔄"):
                st.rerun()
        
        with col4:
            if st.button("Volta"):
                st.session_state.current_room = None
                st.session_state.current_pin = None
                st.rerun()
        
        with col5:
            send_image = st.button("📤") if uploaded_file else None
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Processar envio de mensagem
        if send_text and message.strip():
            self.add_message(
                st.session_state.current_room,
                message.strip(),
                st.session_state.current_user,
                "text",
                st.session_state.current_pin
            )
            st.rerun()
        
        # Processar envio de imagem
        if uploaded_file and (send_image or st.session_state.get('auto_send_image')):
            try:
                image = Image.open(uploaded_file)
                # Redimensionar se muito grande
                if image.width > 800 or image.height > 600:
                    image.thumbnail((800, 600), Image.Resampling.LANCZOS)
                
                base64_image = self.image_to_base64(image)
                self.add_message(
                    st.session_state.current_room,
                    base64_image,
                    st.session_state.current_user,
                    "image",
                    st.session_state.current_pin
                )
                st.success("✅ Imagem enviada!")
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error(f"❌ Erro ao enviar imagem: {e}")
        
        # Painel de administração (sidebar) - APENAS para salas privadas
        if st.session_state.current_room == "private":
            is_room_owner = (
                st.session_state.current_pin in st.session_state.chat_data['private_pins'] and
                st.session_state.chat_data['private_pins'][st.session_state.current_pin] == st.session_state.current_user
            )
            
            if is_room_owner:
                with st.sidebar:
                    st.markdown("### ⚙️ Painel de Controle")
                    
                    if st.button("🗑️ Limpar Chat", type="secondary"):
                        self.clear_chat(st.session_state.current_room, st.session_state.current_pin)
                        st.success("✅ Chat limpo!")
                        time.sleep(1)
                        st.rerun()
                    
                    st.markdown("#### 🚫 Moderar Usuários")
                    
                    # Obter usuários que já enviaram mensagens nesta sala
                    users_in_room = set()
                    for msg in messages:
                        if msg['user'] != st.session_state.current_user:
                            users_in_room.add(msg['user'])
                    
                    # Remover usuários já banidos desta sala
                    banned_in_room = st.session_state.chat_data['private_banned_users'].get(st.session_state.current_pin, set())
                    users_in_room = users_in_room - banned_in_room
                    
                    if users_in_room:
                        user_to_ban = st.selectbox(
                            "Selecionar usuário para banir:",
                            options=list(users_in_room),
                            index=None,
                            placeholder="Escolha um usuário..."
                        )
                        if st.button("🔨 Banir", type="secondary"):
                            if user_to_ban:
                                self.ban_user(user_to_ban, st.session_state.current_pin)
                                st.error(f"❌ {user_to_ban} foi banido desta sala!")
                                time.sleep(1)
                                st.rerun()
                    else:
                        st.info("Nenhum usuário para moderar nesta sala")
                    
                    # Auto-refresh control
                    st.markdown("#### 🔄 Configurações")
                    auto_refresh = st.checkbox(
                        "Ativar atualização automática (3s)", 
                        value=st.session_state.auto_refresh,
                        help="O chat será atualizado automaticamente a cada 3 segundos"
                    )
                    st.session_state.auto_refresh = auto_refresh
                    
                    # Estatísticas do chat
                    st.markdown("#### 📊 Estatísticas")
                    st.metric("👥 Usuários conectados", len(st.session_state.chat_data['users']))
                    st.metric("💬 Mensagens no chat", len(messages))
                    total_private_rooms = len(st.session_state.chat_data['private_messages'])
                    st.metric("🔒 Salas privadas", total_private_rooms)
        
        # Para usuários não-proprietários em salas privadas, mostrar apenas configurações básicas
        elif st.session_state.current_room == "private":
            with st.sidebar:
                st.markdown("### ⚙️ Configurações")
                auto_refresh = st.checkbox(
                    "Ativar atualização automática (3s)", 
                    value=st.session_state.auto_refresh,
                    help="O chat será atualizado automaticamente a cada 3 segundos"
                )
                st.session_state.auto_refresh = auto_refresh
                
                st.markdown("#### 📊 Estatísticas")
                st.metric("💬 Mensagens no chat", len(messages))
    
    def run(self):
        """Executa a aplicação"""
        load_css()
        
        # Lógica de navegação
        if not st.session_state.current_user:
            self.login_page()
        elif not st.session_state.current_room:
            self.room_selection()
        else:
            self.chat_interface()

# Execução principal
if __name__ == "__main__":
    app = PrivateChat()
    app.run()

st.markdown("""
---
<div style="text-align: center;">
    <h4>Private Chat: privacidade de verdade, só c/ seu próprio web app</h4>
    Código Python (Open Source) disponível no GitHub | por <strong>Ary Ribeiro</strong>: <a href="mailto:aryribeiro@gmail.com">aryribeiro@gmail.com</a><br>
    <strong>100% gratuito.</strong> Aqui você não verá propagandas, não será rastreado e não terá seus dados vendidos.
</div>
""", unsafe_allow_html=True)

st.markdown("""
<style>
    .main {
        background-color: #ffffff;
        color: #333333;
    }
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
    }

    /* Esconde a barra padrão do Streamlit */
    header {display: none !important;}
    footer {display: none !important;}
    #MainMenu {display: none !important;}

    /* Reduz, mas não zera, o espaço vertical */
    div[data-testid="stAppViewBlockContainer"] {
        padding-top: 0.5rem !important;
        padding-bottom: 0.5rem !important;
    }
    div[data-testid="stVerticalBlock"] {
        gap: 0.5rem !important; /* Espaçamento vertical mínimo */
        padding-top: 0.5rem !important;
        padding-bottom: 0.5rem !important;
    }

    /* Mantém margens mínimas para evitar "embolamento" */
    .element-container {
        margin-top: 0.3rem !important;
        margin-bottom: 0.3rem !important;
    }

    /* Espaçamento horizontal entre elementos lado a lado */
    div[data-testid="column"] {
        padding-left: 0.5rem;
        padding-right: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)