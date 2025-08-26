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

# Status atual - Atualizado
st.success("✅ **Status Atual:** Sistema completo de vendas e custos funcionando!")

# Resumo das funcionalidades já implementadas
st.info("""
**🎉 FUNCIONALIDADES JÁ IMPLEMENTADAS:**
- ✅ **Sistema de Custos**: Categorização contábil, fornecedores integrados, campos quantidade/valor unitário
- ✅ **Cadastro de Fornecedores**: Busca inteligente, histórico de compras, controle ativo/inativo
- ✅ **Sistema de Vendas**: Múltiplos produtos, consignação, controle de recebimentos
- ✅ **Acerto de Consumo**: Sistema completo para produtos perecíveis com cálculo de perdas
- ✅ **Interface Dark Mode**: Otimizada para todos os dispositivos
- ✅ **Firebase Cloud**: Dados seguros na nuvem com cache inteligente
""")

# Abas para organizar informações
tab1, tab2, tab3 = st.tabs(["📋 Próximos Passos", "🎯 Funcionalidades Planejadas", "💡 Ideias Futuras"])

with tab1:
    st.markdown("""
    ### 🚀 Próximas Implementações (Prioridade Alta)
    
    **📊 Dashboard/Relatórios**
    - [ ] Gráficos de pizza: Distribuição custos vs vendas
    - [ ] Timeline de fluxo de caixa: Entradas e saídas por dia/mês
    - [ ] Análise de rentabilidade: Por produto, cliente, fornecedor
    - [ ] Meta vs Realizado: Estabelecer metas mensais
    
    **👥 Cadastro de Clientes**
    - [ ] Sistema similar aos fornecedores com busca inteligente
    - [ ] Histórico completo de compras por cliente
    - [ ] Preferências e produtos mais comprados
    - [ ] Controle de crédito/limite para vendas a prazo
    
    **🔔 Notificações/Alertas**
    - [ ] Vendas a vencer: Cobranças automáticas
    - [ ] Consignações antigas: Que precisam ser acertadas
    - [ ] Produtos em baixa: Análise de vendas
    - [ ] Metas atingidas: Comemorações automáticas
    """)

with tab2:
    st.markdown("""
    ### 🎯 Funcionalidades Planejadas
    
    **🏪 Melhorias em Fornecedores**
    - Histórico completo de compras por fornecedor
    - Avaliação de fornecedores (qualidade, pontualidade, preços)
    - Alertas para fornecedores inativos há muito tempo
    - Ranking dos melhores fornecedores por categoria
    
    **📱 Experiência Mobile**
    - Botões maiores para dispositivos touch
    - Campos otimizados para teclado mobile
    - Scanner QR/Barcode para produtos
    - Camera integrada para captura de notas fiscais
    
    **📈 Analytics Avançado**
    - Produtos mais rentáveis e análise de margens
    - Clientes mais lucrativos e padrões de compra
    - Sazonalidade: Padrões de venda por mês/trimestre
    - Previsões com IA para estimar vendas futuras
    
    **🌾 Gestão Agrícola**
    - Calendário agrícola e cronograma de atividades
    - Controle de estoque (sementes, defensivos, fertilizantes)
    - Controle de lotes/talhões de produção
    - Acompanhamento plantio → colheita
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