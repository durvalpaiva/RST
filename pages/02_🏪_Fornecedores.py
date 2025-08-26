import streamlit as st
import pandas as pd
from datetime import datetime, date
import sys
import os

# Adicionar o diretório raiz ao path para importar config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.firebase_config import init_firebase

# Configuração da página
st.set_page_config(
    page_title="RST - Cadastro de Fornecedores",
    page_icon="🏪",
    layout="wide"
)

# CSS para melhor experiência
st.markdown("""
<style>
    .main > div {
        padding-top: 1rem;
    }
    .fornecedor-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
        margin-bottom: 1rem;
    }
    .inactive-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #6c757d;
        margin-bottom: 1rem;
        opacity: 0.6;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar Firebase
db = init_firebase()

# Título
st.title("🏪 Cadastro de Fornecedores")
st.markdown("Gerencie sua base de fornecedores para facilitar o registro de custos")

if not db:
    st.error("❌ Erro na conexão com Firebase. Verifique as configurações.")
    st.stop()

# Função para buscar fornecedores
@st.cache_data(ttl=60)
def get_fornecedores():
    try:
        docs = db.collection('fornecedores').order_by('nome').stream()
        fornecedores = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            fornecedores.append(data)
        return fornecedores
    except Exception as e:
        st.error(f"Erro ao buscar fornecedores: {e}")
        return []

# Função para buscar custos de um fornecedor
def get_custos_fornecedor(nome_fornecedor):
    try:
        docs = db.collection('custos_contabeis').where(
            'fornecedor', '==', nome_fornecedor
        ).order_by('data', direction='DESCENDING').limit(10).stream()
        
        custos = []
        for doc in docs:
            data = doc.to_dict()
            custos.append(data)
        
        return custos
    except Exception as e:
        return []

# Buscar fornecedores existentes
fornecedores = get_fornecedores()

# Sidebar com estatísticas
st.sidebar.header("📊 Estatísticas")
total_fornecedores = len(fornecedores)
ativos = len([f for f in fornecedores if f.get('ativo', True)])
inativos = total_fornecedores - ativos

st.sidebar.metric("🏪 Total de Fornecedores", total_fornecedores)
st.sidebar.metric("✅ Ativos", ativos)
st.sidebar.metric("⏸️ Inativos", inativos)

# Formulário de cadastro
st.subheader("📝 Novo Fornecedor")

# Toggle para mostrar/ocultar formulário
if 'show_form_fornecedor' not in st.session_state:
    st.session_state.show_form_fornecedor = False

if st.button(
    "📝 Abrir Formulário" if not st.session_state.show_form_fornecedor else "✖️ Fechar Formulário",
    use_container_width=True,
    type="primary" if not st.session_state.show_form_fornecedor else "secondary"
):
    st.session_state.show_form_fornecedor = not st.session_state.show_form_fornecedor

if st.session_state.show_form_fornecedor:
    with st.form("fornecedor_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            nome_fornecedor = st.text_input(
                "🏪 Nome do Fornecedor *",
                placeholder="Ex: Agropecuária São João",
                help="Nome da empresa ou pessoa física"
            )
            
            cnpj_cpf = st.text_input(
                "📄 CNPJ/CPF",
                placeholder="00.000.000/0000-00",
                help="CNPJ para empresas ou CPF para pessoa física"
            )
            
            telefone = st.text_input(
                "📱 Telefone",
                placeholder="(11) 99999-9999",
                help="Telefone principal para contato"
            )
            
            email = st.text_input(
                "📧 E-mail",
                placeholder="contato@fornecedor.com.br",
                help="E-mail para contato"
            )
        
        with col2:
            endereco = st.text_area(
                "📍 Endereço",
                placeholder="Rua, número, bairro, cidade - UF",
                help="Endereço completo do fornecedor"
            )
            
            tipo_fornecedor = st.selectbox(
                "🏷️ Tipo de Fornecedor",
                ["Insumos Agrícolas", "Equipamentos", "Serviços", "Transporte", "Consultoria", "Outros"],
                help="Categoria principal do fornecedor"
            )
            
            observacoes = st.text_area(
                "📝 Observações",
                placeholder="Informações adicionais sobre o fornecedor...",
                help="Observações gerais sobre o fornecedor"
            )
            
            ativo = st.checkbox(
                "✅ Fornecedor Ativo",
                value=True,
                help="Marque se o fornecedor está ativo para novos pedidos"
            )
        
        submitted = st.form_submit_button("💾 Salvar Fornecedor", use_container_width=True)
        
        if submitted:
            if nome_fornecedor.strip():
                try:
                    # Verificar se fornecedor já existe
                    fornecedor_existente = db.collection('fornecedores').where(
                        'nome', '==', nome_fornecedor.strip()
                    ).limit(1).stream()
                    
                    if list(fornecedor_existente):
                        st.warning("⚠️ Fornecedor já cadastrado com este nome!")
                    else:
                        # Preparar dados do fornecedor
                        fornecedor_data = {
                            'nome': nome_fornecedor.strip(),
                            'cnpj_cpf': cnpj_cpf.strip() if cnpj_cpf else '',
                            'telefone': telefone.strip() if telefone else '',
                            'email': email.strip() if email else '',
                            'endereco': endereco.strip() if endereco else '',
                            'tipo_fornecedor': tipo_fornecedor,
                            'observacoes': observacoes.strip() if observacoes else '',
                            'ativo': ativo,
                            'data_cadastro': datetime.now().isoformat(),
                            'ultima_atualizacao': datetime.now().isoformat(),
                            'app_version': 'RST_v2.1'
                        }
                        
                        # Salvar no Firebase
                        doc_ref = db.collection('fornecedores').add(fornecedor_data)
                        
                        st.success(f"✅ Fornecedor '{nome_fornecedor}' cadastrado com sucesso!")
                        
                        # Limpar cache para atualizar lista
                        st.cache_data.clear()
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"❌ Erro ao salvar fornecedor: {e}")
            else:
                st.warning("⚠️ O nome do fornecedor é obrigatório!")

# Lista de fornecedores
st.subheader("📋 Fornecedores Cadastrados")

if fornecedores:
    # Filtros
    col_filtro1, col_filtro2, col_filtro3 = st.columns(3)
    
    with col_filtro1:
        filtro_nome = st.text_input(
            "🔍 Buscar por nome",
            placeholder="Digite parte do nome...",
            help="Busca inteligente por nome do fornecedor"
        )
    
    with col_filtro2:
        tipos_disponíveis = list(set([f.get('tipo_fornecedor', 'Outros') for f in fornecedores]))
        filtro_tipo = st.multiselect(
            "🏷️ Filtrar por tipo",
            options=tipos_disponíveis,
            default=tipos_disponíveis,
            help="Selecione os tipos de fornecedor para exibir"
        )
    
    with col_filtro3:
        filtro_status = st.selectbox(
            "✅ Status",
            ["Todos", "Apenas Ativos", "Apenas Inativos"],
            help="Filtrar por status do fornecedor"
        )
    
    # Aplicar filtros
    fornecedores_filtrados = fornecedores
    
    if filtro_nome:
        fornecedores_filtrados = [f for f in fornecedores_filtrados 
                                if filtro_nome.lower() in f.get('nome', '').lower()]
    
    if filtro_tipo:
        fornecedores_filtrados = [f for f in fornecedores_filtrados 
                                if f.get('tipo_fornecedor', 'Outros') in filtro_tipo]
    
    if filtro_status == "Apenas Ativos":
        fornecedores_filtrados = [f for f in fornecedores_filtrados if f.get('ativo', True)]
    elif filtro_status == "Apenas Inativos":
        fornecedores_filtrados = [f for f in fornecedores_filtrados if not f.get('ativo', True)]
    
    if fornecedores_filtrados:
        st.markdown(f"**Encontrados: {len(fornecedores_filtrados)} fornecedores**")
        
        # Exibir fornecedores em cards
        for fornecedor in fornecedores_filtrados:
            nome = fornecedor.get('nome', 'Nome não informado')
            tipo = fornecedor.get('tipo_fornecedor', 'Não informado')
            telefone = fornecedor.get('telefone', 'Não informado')
            email = fornecedor.get('email', 'Não informado')
            ativo = fornecedor.get('ativo', True)
            data_cadastro = fornecedor.get('data_cadastro', '')
            observacoes = fornecedor.get('observacoes', '')
            
            # Formatar data
            if data_cadastro:
                try:
                    data_formatada = datetime.fromisoformat(data_cadastro).strftime('%d/%m/%Y')
                except:
                    data_formatada = 'Data inválida'
            else:
                data_formatada = 'Não informada'
            
            # Card do fornecedor
            card_class = "fornecedor-card" if ativo else "inactive-card"
            status_icon = "✅" if ativo else "⏸️"
            
            with st.container():
                st.markdown(f"""
                <div class="{card_class}">
                    <h4>{status_icon} {nome}</h4>
                    <p><strong>🏷️ Tipo:</strong> {tipo}</p>
                    <p><strong>📱 Telefone:</strong> {telefone}</p>
                    <p><strong>📧 E-mail:</strong> {email}</p>
                    <p><strong>📅 Cadastrado em:</strong> {data_formatada}</p>
                    {f'<p><strong>📝 Observações:</strong> {observacoes}</p>' if observacoes else ''}
                </div>
                """, unsafe_allow_html=True)
                
                # Botões de ação
                col_btn1, col_btn2, col_btn3 = st.columns(3)
                
                with col_btn1:
                    if st.button(f"📊 Ver Histórico", key=f"hist_{fornecedor['id']}", use_container_width=True):
                        # Buscar custos deste fornecedor
                        custos = get_custos_fornecedor(nome)
                        if custos:
                            st.subheader(f"📊 Histórico de Compras - {nome}")
                            df_custos = pd.DataFrame(custos)
                            df_custos['data_formatada'] = pd.to_datetime(df_custos['data']).dt.strftime('%d/%m/%Y')
                            df_custos['valor_formatado'] = df_custos['valor'].apply(lambda x: f"R$ {x:.2f}")
                            
                            # Mostrar tabela resumida
                            st.dataframe(
                                df_custos[['data_formatada', 'categoria_nome', 'descricao_item', 'valor_formatado']].rename(columns={
                                    'data_formatada': 'Data',
                                    'categoria_nome': 'Categoria',
                                    'descricao_item': 'Produto/Serviço',
                                    'valor_formatado': 'Valor'
                                }),
                                use_container_width=True,
                                hide_index=True
                            )
                            
                            total_compras = df_custos['valor'].sum()
                            st.metric("💰 Total em Compras", f"R$ {total_compras:.2f}")
                        else:
                            st.info(f"Nenhuma compra registrada para {nome}")
                
                with col_btn2:
                    if st.button(f"✏️ Editar", key=f"edit_{fornecedor['id']}", use_container_width=True):
                        st.info("🚧 Funcionalidade de edição em desenvolvimento")
                
                with col_btn3:
                    status_text = "Desativar" if ativo else "Ativar"
                    if st.button(f"🔄 {status_text}", key=f"toggle_{fornecedor['id']}", use_container_width=True):
                        try:
                            # Atualizar status do fornecedor
                            db.collection('fornecedores').document(fornecedor['id']).update({
                                'ativo': not ativo,
                                'ultima_atualizacao': datetime.now().isoformat()
                            })
                            
                            action = "ativado" if not ativo else "desativado"
                            st.success(f"✅ Fornecedor {nome} foi {action}!")
                            
                            # Limpar cache e recarregar
                            st.cache_data.clear()
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"❌ Erro ao alterar status: {e}")
                
                st.markdown("---")
    else:
        st.info("🔍 Nenhum fornecedor encontrado com os filtros aplicados.")
        
    # Tabela resumo
    if len(fornecedores_filtrados) > 0:
        st.subheader("📊 Resumo em Tabela")
        
        # Converter para DataFrame
        df_fornecedores = pd.DataFrame(fornecedores_filtrados)
        
        # Preparar DataFrame para exibição
        df_exibicao = df_fornecedores[['nome', 'tipo_fornecedor', 'telefone', 'email', 'ativo']].copy()
        df_exibicao['ativo'] = df_exibicao['ativo'].apply(lambda x: "✅ Ativo" if x else "⏸️ Inativo")
        
        # Renomear colunas
        df_exibicao = df_exibicao.rename(columns={
            'nome': 'Nome',
            'tipo_fornecedor': 'Tipo',
            'telefone': 'Telefone',
            'email': 'E-mail',
            'ativo': 'Status'
        })
        
        st.dataframe(df_exibicao, use_container_width=True, hide_index=True)
        
        # Download CSV
        csv_data = df_exibicao.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Baixar lista em CSV",
            data=csv_data,
            file_name=f"fornecedores_RST_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )

else:
    st.info("📝 Nenhum fornecedor cadastrado ainda. Use o formulário acima para adicionar o primeiro!")

# Informações úteis
st.markdown("---")
with st.expander("💡 Dicas de Uso"):
    st.markdown("""
    **🏪 Como usar o Cadastro de Fornecedores:**
    
    1. **Cadastrar Fornecedor**: Use o formulário para adicionar novos fornecedores
    2. **Busca Inteligente**: Na aba de custos, o sistema sugerirá fornecedores conforme você digita
    3. **Histórico**: Veja todas as compras realizadas com cada fornecedor
    4. **Status**: Desative fornecedores que não utiliza mais
    5. **Filtros**: Use os filtros para encontrar fornecedores rapidamente
    
    **📊 Benefícios:**
    - Padronização dos nomes de fornecedores
    - Histórico completo de relacionamento
    - Análise de gastos por fornecedor
    - Controle de fornecedores ativos/inativos
    """)

st.markdown("🏪 **Cadastro de Fornecedores RST** - Organize sua base de fornecedores!")