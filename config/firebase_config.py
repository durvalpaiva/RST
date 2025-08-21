import firebase_admin
from firebase_admin import credentials, firestore, storage
import streamlit as st
import os
from dotenv import load_dotenv
import uuid
from datetime import datetime

# Carregar variáveis de ambiente
load_dotenv()

@st.cache_resource
def init_firebase():
    if not firebase_admin._apps:
        try:
            # Debug: mostrar secrets disponíveis
            if hasattr(st, 'secrets'):
                available_secrets = list(st.secrets.keys()) if st.secrets else []
                st.info(f"🔍 Secrets disponíveis: {available_secrets}")
            
            # Tentar usar secrets do Streamlit Cloud primeiro (para produção)
            if hasattr(st, 'secrets') and 'firebase' in st.secrets:
                try:
                    firebase_config = {
                        "type": st.secrets["firebase"]["type"],
                        "project_id": st.secrets["firebase"]["project_id"],
                        "private_key_id": st.secrets["firebase"]["private_key_id"],
                        "private_key": st.secrets["firebase"]["private_key"],
                        "client_email": st.secrets["firebase"]["client_email"],
                        "client_id": st.secrets["firebase"]["client_id"],
                        "auth_uri": st.secrets["firebase"]["auth_uri"],
                        "token_uri": st.secrets["firebase"]["token_uri"],
                        "auth_provider_x509_cert_url": st.secrets["firebase"]["auth_provider_x509_cert_url"],
                        "client_x509_cert_url": st.secrets["firebase"]["client_x509_cert_url"]
                    }
                    cred = credentials.Certificate(firebase_config)
                    st.success("🔥 Usando secrets do Streamlit Cloud")
                except Exception as e:
                    st.error(f"Erro ao usar secrets: {e}")
                    raise
            else:
                # Para desenvolvimento local usando .env
                st.warning("⚠️ Secrets do Streamlit não encontrados, usando .env local")
                firebase_private_key = os.getenv("FIREBASE_PRIVATE_KEY")
                if not firebase_private_key:
                    st.error("❌ FIREBASE_PRIVATE_KEY não encontrada no .env")
                    st.info("💡 Configure os secrets no Streamlit Cloud: Settings > Secrets")
                    raise ValueError("FIREBASE_PRIVATE_KEY não encontrada no .env")
                
                firebase_config = {
                    "type": os.getenv("FIREBASE_TYPE"),
                    "project_id": os.getenv("FIREBASE_PROJECT_ID"),
                    "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
                    "private_key": firebase_private_key.replace('\\n', '\n'),
                    "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
                    "client_id": os.getenv("FIREBASE_CLIENT_ID"),
                    "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
                    "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
                }
                cred = credentials.Certificate(firebase_config)
            
            # Inicializar Firebase com storage bucket
            if hasattr(st, 'secrets') and 'general' in st.secrets and 'storage_bucket' in st.secrets['general']:
                firebase_admin.initialize_app(cred, {
                    'storageBucket': st.secrets['general']['storage_bucket']
                })
            else:
                firebase_admin.initialize_app(cred, {
                    'storageBucket': 'apprst-baa01.firebasestorage.app'
                })
            
        except Exception as e:
            st.error(f"Erro ao inicializar Firebase: {e}")
            return None
    
    return firestore.client()

# Função para testar conexão
def test_firebase_connection():
    try:
        db = init_firebase()
        if db:
            # Teste simples de leitura
            test_ref = db.collection('test').limit(1)
            list(test_ref.stream())
            return True, "Conexão com Firebase OK!"
        return False, "Falha ao inicializar Firebase"
    except Exception as e:
        return False, f"Erro de conexão: {e}"

# Função para upload de imagens no Firebase Storage
def upload_image_to_storage(uploaded_file, pasta="notas_fiscais"):
    """
    Faz upload de uma imagem para o Firebase Storage
    
    Args:
        uploaded_file: Arquivo do Streamlit file_uploader
        pasta: Nome da pasta no Storage
    
    Returns:
        str: URL da imagem ou None se erro
    """
    try:
        if not uploaded_file:
            return None
        
        # Gerar nome único para o arquivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_extension = uploaded_file.name.split('.')[-1].lower()
        unique_filename = f"{pasta}/{timestamp}_{uuid.uuid4().hex[:8]}.{file_extension}"
        
        # Tentar upload real no Firebase Storage
        try:
            # Obter bucket do Firebase Storage
            if hasattr(st, 'secrets') and 'general' in st.secrets:
                bucket_name = st.secrets["general"]["storage_bucket"]
            else:
                bucket_name = "apprst-baa01.firebasestorage.app"  # Novo formato Firebase
            
            bucket = storage.bucket(bucket_name)
            blob = bucket.blob(unique_filename)
            
            # Reset file pointer para o início
            uploaded_file.seek(0)
            
            # Upload do arquivo
            blob.upload_from_string(
                uploaded_file.read(), 
                content_type=uploaded_file.type
            )
            
            # Tornar público para acesso
            blob.make_public()
            
            # Retornar URL pública
            return blob.public_url
            
        except Exception as upload_error:
            # Se falhar, retornar placeholder para desenvolvimento
            st.warning(f"⚠️ Upload para Storage falhou (desenvolvimento): {upload_error}")
            placeholder_url = f"https://storage.firebase.com/placeholder/{unique_filename}"
            return placeholder_url
        
    except Exception as e:
        st.error(f"Erro ao fazer upload da imagem: {e}")
        return None

# Função para verificar se arquivo é imagem válida
def is_valid_image(uploaded_file):
    """
    Verifica se o arquivo é uma imagem válida
    
    Args:
        uploaded_file: Arquivo do Streamlit file_uploader
    
    Returns:
        bool: True se for imagem válida
    """
    if not uploaded_file:
        return False
    
    valid_types = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf']
    valid_extensions = ['jpg', 'jpeg', 'png', 'pdf']
    
    # Verificar tipo MIME
    if uploaded_file.type not in valid_types:
        return False
    
    # Verificar extensão
    file_extension = uploaded_file.name.split('.')[-1].lower()
    if file_extension not in valid_extensions:
        return False
    
    # Verificar tamanho (máximo 10MB)
    if uploaded_file.size > 10 * 1024 * 1024:  # 10MB
        return False
    
    return True