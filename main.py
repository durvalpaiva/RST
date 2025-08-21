import streamlit as st
from config.firebase_config import init_firebase, test_firebase_connection

# Configuração da página
st.set_page_config(
    page_title="RST - Fazenda Control",
    page_icon="🚜",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS para melhor experiência mobile
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    .sidebar .sidebar-content {
        width: 100%;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

# Título principal
st.title("🚜 RST - Controle da Fazenda")
st.sidebar.title("🔧 Navegação")

# Teste de conexão Firebase
st.sidebar.subheader("🔌 Status do Sistema")
with st.sidebar:
    if st.button("🧪 Testar Conexão Firebase"):
        with st.spinner("Testando conexão..."):
            success, message = test_firebase_connection()
            if success:
                st.success(message)
            else:
                st.error(message)

# Inicializar Firebase
try:
    db = init_firebase()
    if db:
        st.sidebar.success("✅ Firebase conectado")
    else:
        st.sidebar.error("❌ Erro na conexão Firebase")
except Exception as e:
    st.sidebar.error(f"❌ Erro: {e}")

# Interface principal
st.write("Bem-vindo ao sistema de controle da fazenda RST!")
st.write("Use o menu lateral para navegar entre as funcionalidades.")

# Dashboard rápido
st.subheader("📊 Dashboard Resumo")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="🌱 Lotes Ativos", 
        value="5", 
        delta="↗️ 2",
        help="Número de lotes em produção"
    )

with col2:
    st.metric(
        label="💰 Custos Hoje", 
        value="R$ 127,50", 
        delta="↗️ R$ 23,00",
        help="Gastos registrados hoje"
    )

with col3:
    st.metric(
        label="💵 Vendas Mês", 
        value="R$ 3.450,00", 
        delta="↗️ R$ 890,00",
        help="Vendas acumuladas no mês"
    )

# Seção de testes
st.subheader("🧪 Área de Testes")

# Teste básico de escrita no Firebase
if st.button("🔥 Teste: Adicionar dados ao Firebase"):
    if db:
        try:
            # Adicionar documento de teste
            test_data = {
                'timestamp': st.timestamp,
                'app': 'RST',
                'status': 'teste_funcionando',
                'versao': '1.0.0'
            }
            
            doc_ref = db.collection('testes').add(test_data)
            st.success(f"✅ Dados adicionados com sucesso! ID: {doc_ref[1].id}")
            
        except Exception as e:
            st.error(f"❌ Erro ao adicionar dados: {e}")
    else:
        st.error("❌ Firebase não conectado")

# Teste de leitura do Firebase
if st.button("📖 Teste: Ler dados do Firebase"):
    if db:
        try:
            # Ler últimos 5 documentos de teste
            docs = db.collection('testes').order_by('timestamp', direction='DESCENDING').limit(5).stream()
            
            dados = []
            for doc in docs:
                dados.append({
                    'ID': doc.id,
                    **doc.to_dict()
                })
            
            if dados:
                st.success(f"✅ Encontrados {len(dados)} registros:")
                st.json(dados)
            else:
                st.info("ℹ️ Nenhum dado encontrado. Execute o teste de escrita primeiro.")
                
        except Exception as e:
            st.error(f"❌ Erro ao ler dados: {e}")
    else:
        st.error("❌ Firebase não conectado")

# Instruções para próximos passos
st.subheader("📋 Próximos Passos")
st.info("""
💡 **Funcionalidades básicas funcionando!** 

**Para continuar o desenvolvimento:**
1. ✅ Firebase configurado e conectado
2. ✅ Estrutura básica criada
3. 🔄 Teste as funcionalidades acima
4. 📱 Teste no celular acessando a URL do app
5. 🚀 Pronto para adicionar páginas específicas (custos, produção, vendas)

**Como executar localmente:**
```bash
streamlit run streamlit_app.py
```
""")

# Footer
st.markdown("---")
st.markdown("🚜 **RST Fazenda Control** - Sistema de gestão agrícola v1.0")