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
            from datetime import datetime
            test_data = {
                'timestamp': datetime.now().isoformat(),
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

# Roadmap e próximos passos
st.subheader("🗺️ Roadmap de Desenvolvimento")

# Status atual
st.success("✅ **Status Atual:** Sistema base funcionando - Firebase conectado!")

# Abas para organizar informações
tab1, tab2, tab3 = st.tabs(["📋 Próximos Passos", "🎯 Funcionalidades Planejadas", "💡 Ideias Futuras"])

with tab1:
    st.markdown("""
    ### 🚀 Próximas Implementações (Prioridade Alta)
    
    **📊 Sistema de Custos (Expandir)**
    - [ ] Categorização avançada (Fixos, Variáveis, Semi-variáveis)
    - [ ] Análise de tendências e gráficos temporais
    - [ ] Comparativo mensal/anual
    - [ ] Alertas de gastos excessivos
    
    **📱 Produção e Lotes**
    - [ ] Cadastro e controle de lotes/talhões
    - [ ] Acompanhamento de plantio → colheita
    - [ ] Controle de aplicações (defensivos, fertilizantes)
    - [ ] Histórico produtivo por área
    
    **💰 Sistema de Vendas**
    - [ ] Registro de vendas e recebimentos
    - [ ] Controle de clientes e contratos
    - [ ] Relatórios de rentabilidade por cultura
    - [ ] Fluxo de caixa projetado
    """)

with tab2:
    st.markdown("""
    ### 🎯 Módulos Planejados
    
    **🌾 Gestão Agrícola**
    - Calendário agrícola e cronograma de atividades
    - Controle de estoque (sementes, defensivos, fertilizantes)
    - Monitoramento climático integrado
    - Controle de máquinas e implementos
    
    **👥 Gestão de Pessoas**
    - Controle de funcionários e prestadores
    - Registro de horas trabalhadas
    - Controle de EPIs e treinamentos
    
    **📈 Business Intelligence**
    - Dashboard executivo com KPIs principais
    - Análise de rentabilidade por hectare
    - Comparativo com índices do setor
    - Projeções e simulações de cenários
    
    **🔄 Integrações**
    - API de cotações (CEPEA, CME)
    - Dados meteorológicos (INMET)
    - Bancos para conciliação financeira
    """)

with tab3:
    st.markdown("""
    ### 💡 Ideias para o Futuro
    
    **🤖 Automação e IA**
    - Reconhecimento de notas fiscais por OCR
    - Previsões de produtividade com ML
    - Chatbot para consultas rápidas
    - Recomendações automáticas de manejo
    
    **📊 Analytics Avançado**
    - Mapas de produtividade georeferenciados
    - Análise de imagens de satélite
    - Correlação clima x produtividade
    - Benchmarking com outras propriedades
    
    **💼 Expansão do Negócio**
    - Módulo para consultoria agronômica
    - Marketplace de insumos
    - Sistema multi-fazenda
    - App mobile nativo
    """)

# Informações técnicas
st.subheader("🔧 Informações Técnicas")
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **📚 Stack Tecnológica:**
    - Frontend: Streamlit
    - Backend: Firebase Firestore
    - Storage: Firebase Storage
    - Deploy: Streamlit Cloud
    - Language: Python 3.9+
    """)

with col2:
    st.markdown("""
    **🚀 Como Contribuir:**
    ```bash
    # Executar localmente
    streamlit run main.py
    
    # Testar Firebase
    python test_firebase.py
    ```
    """)

# Call to action
st.info("💬 **Feedback e Sugestões:** Sua opinião é fundamental para priorizar as próximas funcionalidades!")

# Footer
st.markdown("---")
st.markdown("🚜 **RST Fazenda Control** - Sistema de gestão agrícola v1.0")