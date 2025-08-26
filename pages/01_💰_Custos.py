import streamlit as st
import pandas as pd
from datetime import datetime, date
import sys
import os

# Adicionar o diretório raiz ao path para importar config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.firebase_config import init_firebase, upload_image_to_storage, is_valid_image

# Configuração da página
st.set_page_config(
    page_title="RST - Gestão de Custos",
    page_icon="💰",
    layout="wide"
)

# CSS para melhor experiência mobile
st.markdown("""
<style>
    .main > div {
        padding-top: 1rem;
    }
    .custo-card {
        background-color: #1a2e1a; /* Verde escuro */
        color: #ffffff; /* Texto branco */
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #dc3545;
        margin-bottom: 1rem;
    }
    .success-card {
        background-color: #1a2e1a; /* Verde escuro */
        color: #ffffff; /* Texto branco */
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Definir categorias contábeis
CUSTOS_FIXOS = {
    'salarios': 'Salários',
    'internet': 'Internet',
    'telefone': 'Telefone',
    'manutencao_geral': 'Manutenção em Geral',
    'sistema': 'Sistema',
    'imposto': 'Imposto',
    'consultoria': 'Consultoria',
    'marketing': 'Marketing'
}

CUSTOS_VARIAVEIS = {
    'sementes': 'Sementes',
    'fertilizantes': 'Fertilizantes',
    'espuma_fenolica': 'Espuma Fenólica',
    'produtos_limpeza': 'Produtos de Limpeza',
    'equipamentos_descartaveis': 'Equipamentos Descartáveis',
    'frete': 'Frete',
    'nutrientes': 'Nutrientes',
    'embalagens': 'Embalagens',
    'defensivos': 'Defensivos',
    'aluguel_maquina': 'Aluguel de Máquina',
    'diesel_trator': 'Diesel para Trator',
    'mao_obra_temporaria': 'Mão de Obra Temporária',
    'outros_variaveis': 'Outros Variáveis'
}

INVESTIMENTOS = {
    'equipamentos': 'Equipamentos',
    'tecnologia': 'Tecnologia',
    'veiculos': 'Veículos',
    'bens_moveis': 'Bens Móveis',
    'irrigacao': 'Sistema de Irrigação',
    'construcao': 'Construção',
    'melhorias_terreno': 'Melhorias no Terreno',
    'expansao_area': 'Expansão de Área',
    'infraestrutura': 'Infraestrutura',
    'outros_investimentos': 'Outros Investimentos'
}

# Inicializar Firebase
db = init_firebase()

# Título
st.title("💰 Gestão de Custos - Classificação Contábil")
st.markdown("Controle financeiro com classificação contábil: **Fixos**, **Variáveis** e **Investimentos**")

if not db:
    st.error("❌ Erro na conexão com Firebase. Verifique as configurações.")
    st.stop()

# Função para buscar custos do mês atual
@st.cache_data(ttl=60)
def get_custos_mes_atual():
    try:
        hoje = datetime.now()
        inicio_mes = f"{hoje.year}-{hoje.month:02d}-01"
        
        docs = db.collection('custos_contabeis').where(
            'data', '>=', inicio_mes
        ).order_by('data', direction='DESCENDING').stream()
        
        custos = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            custos.append(data)
        
        return custos
    except Exception as e:
        st.error(f"Erro ao buscar custos: {e}")
        return []

# Função para buscar fornecedores ativos
@st.cache_data(ttl=30)  # Cache menor para atualizar mais rápido
def get_fornecedores_ativos():
    try:
        # Buscar todos os fornecedores primeiro
        docs = db.collection('fornecedores').stream()
        
        fornecedores = []
        for doc in docs:
            data = doc.to_dict()
            # Considerar ativo se o campo não existir ou for True
            ativo = data.get('ativo', True)  
            
            if ativo:  # Só adicionar se ativo
                fornecedores.append({
                    'nome': data.get('nome', ''),
                    'tipo': data.get('tipo_fornecedor', ''),
                    'telefone': data.get('telefone', ''),
                    'id': doc.id
                })
        
        # Ordenar por nome
        fornecedores.sort(key=lambda x: x['nome'].lower())
        return fornecedores
        
    except Exception as e:
        st.error(f"Erro ao buscar fornecedores: {e}")
        return []

# Função para buscar fornecedor por nome (busca inteligente)
def buscar_fornecedores(termo_busca):
    fornecedores = get_fornecedores_ativos()
    
    # Debug: mostrar quantos fornecedores foram encontrados
    if not fornecedores:
        st.warning("⚠️ Nenhum fornecedor encontrado no banco de dados")
        return []
    
    if not termo_busca or termo_busca.strip() == "":
        return fornecedores[:10]  # Limitar a 10 para não sobrecarregar
    
    termo = termo_busca.lower().strip()
    # Busca mais flexível: busca por qualquer parte do nome
    resultados = [f for f in fornecedores if termo in f['nome'].lower()]
    
    return resultados

# Buscar custos do mês
custos_mes = get_custos_mes_atual()

# Calcular totais por tipo
custos_fixos_mes = sum([float(c.get('valor', 0)) for c in custos_mes if c.get('tipo_custo') == 'Custos Fixos'])
custos_variaveis_mes = sum([float(c.get('valor', 0)) for c in custos_mes if c.get('tipo_custo') == 'Custos Variáveis'])
investimentos_mes = sum([float(c.get('valor', 0)) for c in custos_mes if c.get('tipo_custo') == 'Investimentos'])
depreciacao_mes = sum([float(c.get('depreciacao_mensal', 0)) for c in custos_mes if c.get('tipo_custo') == 'Investimentos'])

total_mes = custos_fixos_mes + custos_variaveis_mes + investimentos_mes

# Sidebar com resumo contábil
hoje = datetime.now()
mes_atual = hoje.strftime("%m/%y")
st.sidebar.header("💰 Resumo Contábil")
st.sidebar.markdown(f"**📅 Mês: {mes_atual}**")
st.sidebar.metric("🔒 Custos Fixos", f"R$ {custos_fixos_mes:.2f}")
st.sidebar.metric("📈 Custos Variáveis", f"R$ {custos_variaveis_mes:.2f}")
st.sidebar.metric("💎 Investimentos", f"R$ {investimentos_mes:.2f}")
if depreciacao_mes > 0:
    st.sidebar.metric("📉 Depreciação/Mês", f"R$ {depreciacao_mes:.2f}")
st.sidebar.metric("💰 Total Mês", f"R$ {total_mes:.2f}")
st.sidebar.metric("📅 Registros", len(custos_mes))

# Toggle para mostrar/ocultar formulário
st.subheader("📝 Novo Registro de Custo")

# Inicializar estado do toggle
if 'show_form' not in st.session_state:
    st.session_state.show_form = False

# Botão toggle estilizado
if st.button(
    "📝 Abrir Formulário" if not st.session_state.show_form else "✖️ Fechar Formulário",
    use_container_width=True,
    type="primary" if not st.session_state.show_form else "secondary"
):
    st.session_state.show_form = not st.session_state.show_form

# Debug: Botões para troubleshooting da busca de fornecedores (fora do formulário)
if st.session_state.get('show_form', False):
    st.markdown("**🔧 Ferramentas de Debug:**")
    col_debug1, col_debug2 = st.columns(2)
    
    with col_debug1:
        if st.button("🔍 Debug: Listar fornecedores", help="Ver fornecedores cadastrados"):
            todos_fornecedores = get_fornecedores_ativos()
            if todos_fornecedores:
                st.success(f"✅ {len(todos_fornecedores)} fornecedores encontrados:")
                for f in todos_fornecedores:
                    st.write(f"• **{f['nome']}** - {f['tipo']} - {f['telefone']}")
            else:
                st.error("❌ Nenhum fornecedor encontrado no banco")
    
    with col_debug2:
        if st.button("🔄 Limpar Cache", help="Atualizar lista de fornecedores"):
            st.cache_data.clear()
            st.success("✅ Cache limpo! Tente buscar novamente.")
            st.rerun()
    
    st.markdown("---")

# Mostrar formulário apenas se toggle estiver ativo
if st.session_state.show_form:
    tipo_custo = st.selectbox(
        "🏷️ Classificação Contábil",
        ["Custos Fixos", "Custos Variáveis", "Investimentos"],
        help="Selecione a classificação contábil do custo"
    )

    with st.form("custos_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            data_custo = st.date_input(
                "📅 Data (dd/mm/aaaa)",
                value=date.today(),
                help="Data do custo registrado - formato brasileiro",
                format="DD/MM/YYYY"
            )
            
            # Definir categorias baseadas no tipo selecionado
            if tipo_custo == "Custos Fixos":
                categorias = CUSTOS_FIXOS
                icon = "🔒"
            elif tipo_custo == "Custos Variáveis":
                categorias = CUSTOS_VARIAVEIS
                icon = "📈"
            else:  # Investimentos
                categorias = INVESTIMENTOS
                icon = "💎"
            
            categoria = st.selectbox(
                f"{icon} Categoria",
                list(categorias.keys()),
                format_func=lambda x: categorias[x],
                help=f"Categoria específica de {tipo_custo.lower()}"
            )
            
            # Campo obrigatório para descrição do produto/serviço
            descricao_item = st.text_input(
                "📦 Descrição do Produto/Serviço *",
                placeholder="Ex: Adubo NPK 10-10-10, Consultoria agronômica...",
                help="Nome específico do produto ou serviço adquirido"
            )
            
            # Campos para quantidade e valor unitário
            col_qtd, col_unit = st.columns(2)
            
            with col_qtd:
                quantidade = st.number_input(
                    "📊 Quantidade",
                    min_value=0.01,
                    value=1.0,
                    step=0.01,
                    format="%.2f",
                    help="Quantidade do produto/serviço"
                )
                
                unidade_medida = st.selectbox(
                    "📏 Unidade",
                    ["UN", "KG", "L", "M", "M²", "M³", "T", "SC", "CX", "PC", "HR", "DIA"],
                    help="Unidade de medida"
                )
            
            with col_unit:
                valor_unitario = st.number_input(
                    "💰 Valor Unitário (R$)",
                    min_value=0.01,
                    step=0.01,
                    format="%.2f",
                    help="Valor por unidade do produto/serviço"
                )
                
                # Calcular valor total automaticamente
                valor_total = quantidade * valor_unitario
                st.metric(
                    "💰 Valor Total",
                    f"R$ {valor_total:.2f}",
                    help="Quantidade × Valor Unitário"
                )
            
            # Usar valor_total ao invés de valor
            valor = valor_total
        
        with col2:
            # Campos específicos para investimentos
            if tipo_custo == "Investimentos":
                vida_util = st.number_input(
                    "⏳ Vida Útil (meses)",
                    min_value=1,
                    value=12,
                    help="Vida útil estimada do investimento em meses"
                )
                
                depreciacao_mensal = valor / vida_util if vida_util > 0 else 0
                st.metric("📉 Depreciação Mensal", f"R$ {depreciacao_mensal:.2f}")
            
            observacoes = st.text_area(
                "📝 Observações",
                placeholder="Descrição detalhada do custo...",
                help="Descrição das atividades ou detalhes do custo"
            )
            
            # Para custos variáveis, permitir associar à produção
            if tipo_custo == "Custos Variáveis":
                lote_producao = st.text_input(
                    "🌱 Lote de Produção (opcional)",
                    placeholder="Ex: ALFACE_001",
                    help="Associar este custo a um lote específico"
                )
        
        # SEÇÃO DE UPLOAD DE NOTA FISCAL
        st.subheader("📄 Nota Fiscal / Cupom")
        
        # Instruções para câmera mobile
        st.info("""
        📱 **Para usuários móveis**: 
        • Clique em "Browse files" abaixo
        • Escolha "Câmera" ou "Tirar foto"
        • A foto será anexada automaticamente
        """)
        
        # Campos de fornecedor e número da NF
        col_nf1, col_nf2 = st.columns(2)
        
        with col_nf1:
            st.markdown("**🏪 Fornecedor (Obrigatório) ***")
            
            # Buscar todos os fornecedores ativos
            todos_fornecedores = get_fornecedores_ativos()
            
            if not todos_fornecedores:
                st.error("❌ Nenhum fornecedor cadastrado!")
                st.info("**📝 Para cadastrar fornecedores:** Vá na aba '🏪 Fornecedores'")
                fornecedor_selecionado_id = None
                fornecedor_nome = ""
            else:
                # Criar lista de opções para selectbox
                opcoes_fornecedores = ["Selecione um fornecedor..."] + [f"{f['nome']} - {f['tipo']}" for f in todos_fornecedores]
                
                # Selectbox para escolher fornecedor
                escolha = st.selectbox(
                    "Escolha o fornecedor:",
                    options=range(len(opcoes_fornecedores)),
                    format_func=lambda x: opcoes_fornecedores[x],
                    help="Selecione um fornecedor cadastrado no sistema",
                    label_visibility="collapsed"
                )
                
                if escolha == 0:  # "Selecione um fornecedor..."
                    fornecedor_selecionado_id = None
                    fornecedor_nome = ""
                    st.warning("⚠️ Selecione um fornecedor para continuar")
                else:
                    # Fornecedor selecionado
                    fornecedor_selecionado = todos_fornecedores[escolha - 1]
                    fornecedor_selecionado_id = fornecedor_selecionado['id']
                    fornecedor_nome = fornecedor_selecionado['nome']
                    
                    # Mostrar detalhes do fornecedor selecionado
                    st.success(f"✅ **{fornecedor_nome}**")
                    st.caption(f"📞 {fornecedor_selecionado['telefone']} | 🏷️ {fornecedor_selecionado['tipo']}")
                
                # Campo de busca rápida (opcional)
                st.markdown("**🔍 Busca Rápida (opcional):**")
                termo_busca = st.text_input(
                    "Digite para filtrar fornecedores:",
                    placeholder="Digite parte do nome para filtrar...",
                    help="Filtra a lista de fornecedores",
                    label_visibility="collapsed"
                )
                
                # Filtrar fornecedores se houver termo de busca
                if termo_busca:
                    fornecedores_filtrados = [f for f in todos_fornecedores if termo_busca.lower() in f['nome'].lower()]
                    if fornecedores_filtrados:
                        st.markdown("**📋 Fornecedores encontrados:**")
                        for i, forn in enumerate(fornecedores_filtrados[:5]):
                            col_info, col_btn = st.columns([3, 1])
                            with col_info:
                                st.markdown(f"**{forn['nome']}**")
                                st.caption(f"{forn['tipo']} | {forn['telefone']}")
                            with col_btn:
                                if st.button("Usar", key=f"usar_forn_{i}", type="primary"):
                                    # Encontrar o índice no selectbox
                                    for idx, f in enumerate(todos_fornecedores):
                                        if f['id'] == forn['id']:
                                            st.session_state['fornecedor_escolhido'] = idx + 1
                                            st.rerun()
                    else:
                        st.warning("❌ Nenhum fornecedor encontrado com este termo")
            
            # Definir variável final para o formulário
            fornecedor = fornecedor_nome
        
        with col_nf2:
            numero_nf = st.text_input(
                "🧾 Número da NF/Cupom",
                placeholder="123456",
                help="Número da nota fiscal ou cupom"
            )
        
        # Upload da imagem
        uploaded_file = st.file_uploader(
            "📷 Anexar Foto da Nota Fiscal",
            type=['png', 'jpg', 'jpeg', 'pdf'],
            help="Formatos aceitos: PNG, JPG, JPEG, PDF (máx. 10MB)"
        )
        
        # Validação da imagem
        imagem_url = None
        if uploaded_file:
            if is_valid_image(uploaded_file):
                st.success(f"✅ Arquivo válido: {uploaded_file.name} ({uploaded_file.size/1024:.1f} KB)")
                # Preview da imagem (somente para imagens)
                if uploaded_file.type.startswith('image/'):
                    st.image(uploaded_file, caption="Preview da nota fiscal", width=200)
            else:
                st.error("❌ Arquivo inválido! Use PNG, JPG, JPEG ou PDF (máx. 10MB)")
                uploaded_file = None
    
        # Mostrar resumo do custo
        st.markdown(f"**💰 {tipo_custo}: R$ {valor:.2f}**")
        if tipo_custo == "Investimentos" and valor > 0:
            st.markdown(f"**📉 Impacto mensal: R$ {depreciacao_mensal:.2f}**")
        
        # Botão de envio
        submitted = st.form_submit_button(f"💾 Salvar {tipo_custo}", use_container_width=True)
    
        if submitted:
            if valor > 0 and descricao_item.strip() and quantidade > 0 and valor_unitario > 0 and fornecedor.strip():
                try:
                    # Upload da imagem se fornecida
                    if uploaded_file:
                        with st.spinner("📤 Fazendo upload da imagem..."):
                            imagem_url = upload_image_to_storage(uploaded_file)
                        
                        if imagem_url:
                            st.success("✅ Imagem salva com sucesso!")
                        else:
                            st.warning("⚠️ Falha no upload da imagem, mas o custo será salvo mesmo assim.")
                    
                    # Preparar dados
                    custo_data = {
                        'data': str(data_custo),
                        'tipo_custo': tipo_custo,
                        'categoria': categoria,
                        'categoria_nome': categorias[categoria],
                        'descricao_item': descricao_item.strip(),
                        'quantidade': float(quantidade),
                        'unidade_medida': unidade_medida,
                        'valor_unitario': float(valor_unitario),
                        'valor': float(valor),
                        'fornecedor': fornecedor.strip(),
                        'fornecedor_id': fornecedor_selecionado_id if 'fornecedor_selecionado_id' in locals() else '',
                        'numero_nf': numero_nf.strip() if numero_nf else '',
                        'imagem_nf_url': imagem_url or '',
                        'tem_nota_fiscal': bool(uploaded_file),
                        'observacoes': observacoes.strip(),
                        'timestamp': datetime.now().isoformat(),
                        'app_version': 'RST_v2.3'
                    }
                    
                    # Campos específicos para investimentos
                    if tipo_custo == "Investimentos":
                        custo_data.update({
                            'vida_util_meses': int(vida_util),
                            'depreciacao_mensal': float(depreciacao_mensal),
                            'roi_calculado': False  # Será calculado quando houver receitas
                        })
                    
                    # Para custos variáveis
                    if tipo_custo == "Custos Variáveis" and lote_producao.strip():
                        custo_data['lote_producao'] = lote_producao.strip()
                    
                    # Salvar no Firebase
                    doc_ref = db.collection('custos_contabeis').add(custo_data)
                    
                    # Mensagem de sucesso com detalhes
                    success_msg = f"✅ {tipo_custo} de {data_custo.strftime('%d/%m/%Y')} salvo com sucesso!"
                    if fornecedor:
                        success_msg += f" | Fornecedor: {fornecedor}"
                    if numero_nf:
                        success_msg += f" | NF: {numero_nf}"
                    if uploaded_file:
                        success_msg += f" | 📷 Com anexo"
                    
                    st.success(success_msg)
                    
                    # Limpar cache para atualizar resumo
                    st.cache_data.clear()
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Erro ao salvar: {e}")
            else:
                if valor <= 0:
                    st.warning("⚠️ Informe um valor maior que zero!")
                if not descricao_item.strip():
                    st.warning("⚠️ A descrição do produto/serviço é obrigatória!")
                if quantidade <= 0:
                    st.warning("⚠️ A quantidade deve ser maior que zero!")
                if valor_unitario <= 0:
                    st.warning("⚠️ O valor unitário deve ser maior que zero!")
                if not fornecedor.strip():
                    st.warning("⚠️ Selecione um fornecedor cadastrado no sistema!")

# Tabela filtrada com dados dos custos
st.subheader("📊 Dados dos Custos - Tabela Filtrável")

if custos_mes:
    # Converter lista para DataFrame
    df_custos = pd.DataFrame(custos_mes)
    
    # Adicionar coluna de data formatada
    df_custos['data_formatada'] = pd.to_datetime(df_custos['data']).dt.strftime('%d/%m/%Y')
    
    # Garantir que colunas novas existam (para compatibilidade com dados antigos)
    if 'quantidade' not in df_custos.columns:
        df_custos['quantidade'] = 1.0
    if 'unidade_medida' not in df_custos.columns:
        df_custos['unidade_medida'] = 'UN'
    if 'valor_unitario' not in df_custos.columns:
        df_custos['valor_unitario'] = df_custos['valor']
    
    # Selector de colunas para exibir
    colunas_disponiveis = {
        'data_formatada': 'Data',
        'tipo_custo': 'Tipo',
        'categoria_nome': 'Categoria',
        'descricao_item': 'Produto/Serviço',
        'quantidade': 'Qtd',
        'unidade_medida': 'Un.',
        'valor_unitario': 'Valor Unit. (R$)',
        'valor': 'Valor Total (R$)',
        'fornecedor': 'Fornecedor',
        'numero_nf': 'Nº NF',
        'tem_nota_fiscal': 'Com NF',
        'observacoes': 'Observações'
    }
    
    # Filtros
    col_filtro1, col_filtro2, col_filtro3 = st.columns(3)
    
    with col_filtro1:
        tipos_selecionados = st.multiselect(
            "🏷️ Filtrar por Tipo",
            options=df_custos['tipo_custo'].unique(),
            default=df_custos['tipo_custo'].unique(),
            help="Selecione os tipos de custo para exibir"
        )
    
    with col_filtro2:
        colunas_selecionadas = st.multiselect(
            "📋 Colunas para Exibir",
            options=list(colunas_disponiveis.keys()),
            default=['data_formatada', 'tipo_custo', 'categoria_nome', 'descricao_item', 'quantidade', 'unidade_medida', 'valor_unitario', 'valor', 'fornecedor'],
            format_func=lambda x: colunas_disponiveis[x],
            help="Escolha quais colunas mostrar na tabela"
        )
    
    with col_filtro3:
        valor_minimo = st.number_input(
            "💰 Valor Mínimo (R$)",
            min_value=0.0,
            value=0.0,
            step=1.0,
            help="Filtrar custos com valor mínimo"
        )
    
    # Aplicar filtros
    df_filtrado = df_custos[
        (df_custos['tipo_custo'].isin(tipos_selecionados)) &
        (df_custos['valor'] >= valor_minimo)
    ]
    
    if not df_filtrado.empty and colunas_selecionadas:
        # Preparar DataFrame para exibição
        df_exibicao = df_filtrado[colunas_selecionadas].copy()
        
        # Renomear colunas para nomes mais amigáveis
        df_exibicao = df_exibicao.rename(columns=colunas_disponiveis)
        
        # Formatar valores monetários e quantidade
        if 'Valor Total (R$)' in df_exibicao.columns:
            df_exibicao['Valor Total (R$)'] = df_exibicao['Valor Total (R$)'].apply(lambda x: f"R$ {x:.2f}")
        if 'Valor Unit. (R$)' in df_exibicao.columns:
            df_exibicao['Valor Unit. (R$)'] = df_exibicao['Valor Unit. (R$)'].apply(lambda x: f"R$ {x:.2f}")
        if 'Qtd' in df_exibicao.columns:
            df_exibicao['Qtd'] = df_exibicao['Qtd'].apply(lambda x: f"{x:.2f}".rstrip('0').rstrip('.'))
        
        # Exibir tabela
        st.dataframe(
            df_exibicao,
            use_container_width=True,
            hide_index=True
        )
        
        # Estatísticas rápidas
        total_filtrado = df_filtrado['valor'].sum()
        count_filtrado = len(df_filtrado)
        
        col_stats1, col_stats2, col_stats3 = st.columns(3)
        with col_stats1:
            st.metric("📊 Total Filtrado", f"R$ {total_filtrado:.2f}")
        with col_stats2:
            st.metric("📈 Registros", count_filtrado)
        with col_stats3:
            if count_filtrado > 0:
                media = total_filtrado / count_filtrado
                st.metric("📊 Média", f"R$ {media:.2f}")
        
        # Botão de download CSV
        csv_data = df_exibicao.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Baixar dados em CSV",
            data=csv_data,
            file_name=f"custos_RST_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.info("📋 Nenhum dado encontrado com os filtros aplicados.")
else:
    st.info("📝 Nenhum custo registrado ainda. Use o formulário acima para adicionar registros!")

# Histórico de custos em cards
st.subheader("📆 Histórico de Custos por Classificação")

if custos_mes:
    # Criar abas por tipo de custo
    tab1, tab2, tab3 = st.tabs(["🔒 Custos Fixos", "📈 Custos Variáveis", "💎 Investimentos"])
    
    # Função para mostrar custos por tipo
    def mostrar_custos_por_tipo(custos_filtrados, tipo):
        if custos_filtrados:
            for custo in custos_filtrados[:10]:  # Últimos 10
                data_formatada = datetime.fromisoformat(custo['data']).strftime('%d/%m')
                valor = custo.get('valor', 0)
                categoria = custo.get('categoria_nome', 'N/A')
                descricao = custo.get('descricao_item', 'Sem descrição')
                quantidade = custo.get('quantidade', 1.0)
                unidade = custo.get('unidade_medida', 'UN')
                valor_unit = custo.get('valor_unitario', valor)
                
                # Ícone baseado no tipo
                if tipo == 'Custos Fixos':
                    icon = "🔒"
                    cor = "#dc3545"  # Vermelho
                elif tipo == 'Custos Variáveis':
                    icon = "📈"
                    cor = "#ffc107"  # Amarelo
                else:
                    icon = "💎"
                    cor = "#17a2b8"  # Azul
                
                with st.container():
                    # Formatear quantidade para exibição
                    qtd_formatada = f"{quantidade:.2f}".rstrip('0').rstrip('.')
                    
                    # Mostrar detalhes apenas se tiver dados de quantidade/valor unitário
                    if 'quantidade' in custo and 'valor_unitario' in custo:
                        valor_detalhes = f"📊 {qtd_formatada} {unidade} × R$ {valor_unit:.2f} = 💰 R$ {valor:.2f}"
                    else:
                        valor_detalhes = f"💰 R$ {valor:.2f}"
                    
                    st.markdown(f"""
                    <div style="background-color: #1a2e1a; color: #ffffff; padding: 1rem; border-radius: 0.5rem; 
                                border-left: 4px solid {cor}; margin-bottom: 0.5rem;">
                        <h4>{icon} {data_formatada} - {categoria}</h4>
                        <p><strong>📦 {descricao}</strong></p>
                        <p><strong>{valor_detalhes}</strong></p>
                        <p><em>{custo.get('observacoes', 'Sem observações')}</em></p>
                        {f'<p><small>📉 Depreciação mensal: R$ {custo.get("depreciacao_mensal", 0):.2f}</small></p>' if tipo == 'Investimentos' and custo.get('depreciacao_mensal') else ''}
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info(f"Nenhum registro de {tipo.lower()} ainda.")
    
    with tab1:
        custos_fixos = [c for c in custos_mes if c.get('tipo_custo') == 'Custos Fixos']
        mostrar_custos_por_tipo(custos_fixos, 'Custos Fixos')
    
    with tab2:
        custos_vars = [c for c in custos_mes if c.get('tipo_custo') == 'Custos Variáveis']
        mostrar_custos_por_tipo(custos_vars, 'Custos Variáveis')
    
    with tab3:
        investimentos = [c for c in custos_mes if c.get('tipo_custo') == 'Investimentos']
        mostrar_custos_por_tipo(investimentos, 'Investimentos')
        
        # Mostrar resumo de ROI (placeholder para implementação futura)
        if investimentos:
            st.subheader("📉 Análise de ROI")
            total_investido = sum([float(i.get('valor', 0)) for i in investimentos])
            deprec_total = sum([float(i.get('depreciacao_mensal', 0)) for i in investimentos])
            st.info(f"💰 Total investido: R$ {total_investido:.2f} | 📉 Depreciação mensal: R$ {deprec_total:.2f}")
            st.markdown("*Cálculo de ROI será implementado quando houver dados de receita.*")
    
    # Gráfico comparativo
    if len(custos_mes) > 1:
        st.subheader("📈 Evolução por Tipo de Custo")
        df_grafico = pd.DataFrame(custos_mes)
        df_grafico['data'] = pd.to_datetime(df_grafico['data'])
        
        # Agrupar por data e tipo
        pivot_data = df_grafico.groupby(['data', 'tipo_custo'])['valor'].sum().unstack(fill_value=0)
        
        # Formatá índice do gráfico para formato brasileiro compacto
        pivot_data.index = pivot_data.index.strftime('%d/%m')
        st.area_chart(pivot_data)

else:
    st.info("📝 Nenhum custo registrado ainda. Adicione o primeiro registro acima!")

# Footer com explicação das categorias
st.markdown("---")
with st.expander("📊 Entenda as Classificações Contábeis"):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **🔒 Custos Fixos**
        Não variam com a produção:
        - Salários administrativos
        - Diárias
        - Licenças e taxas
        - Energia
        - Transporte
        """)
    
    with col2:
        st.markdown("""
        **📈 Custos Variáveis**
        Flutuam com o volume:
        - Sementes e fertilizantes
        - Embalagens
        - Mão de obra temporária
        - Matéria-prima
        """)
    
    with col3:
        st.markdown("""
        **💎 Investimentos**
        Bens de capital:
        - Equipamentos
        - Sistema de irrigação
        - Infraestrutura
        - Cálculo de ROI
        """)

st.markdown("💰 **Gestão Contábil RST** - Controle financeiro profissional!")