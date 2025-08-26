import streamlit as st
import pandas as pd
from datetime import datetime, date
import sys
import os
import uuid

# Adicionar o diretório raiz ao path para importar config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.firebase_config import init_firebase

# Configuração da página
st.set_page_config(
    page_title="RST - Gestão de Vendas",
    page_icon="💰",
    layout="wide"
)

# CSS para melhor experiência
st.markdown("""
<style>
    .main > div {
        padding-top: 1rem;
    }
    .venda-card {
        background-color: #1a2e1a; /* Verde escuro */
        color: #ffffff; /* Texto branco */
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745; /* Borda verde mantida */
        margin-bottom: 1rem;
    }
    .pendente-card {
        background-color: #2a2a2a; /* Fundo escuro */
        color: #ffffff; /* Texto branco */
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107; /* Borda amarela mantida */
        margin-bottom: 1rem;
    }
    .produto-item {
        background-color: #1e1e1e; /* Cinza escuro */
        border: 1px solid #2c2c2c;
        color: #ffffff; /* Texto branco para contraste */
        padding: 0.5rem;
        border-radius: 0.3rem;
        margin: 0.2rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar Firebase
db = init_firebase()

# Título
st.title("💰 Gestão de Vendas")
st.markdown("Sistema completo de vendas com múltiplos produtos e controle de recebimentos")

if not db:
    st.error("❌ Erro na conexão com Firebase. Verifique as configurações.")
    st.stop()

# Função para buscar vendas do mês atual
@st.cache_data(ttl=30)
def get_vendas_mes_atual():
    try:
        hoje = datetime.now()
        inicio_mes = f"{hoje.year}-{hoje.month:02d}-01"
        
        docs = db.collection('vendas').where(
            'data_venda', '>=', inicio_mes
        ).order_by('data_venda', direction='DESCENDING').stream()
        
        vendas = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            vendas.append(data)
        
        return vendas
    except Exception as e:
        st.error(f"Erro ao buscar vendas: {e}")
        return []

# Buscar vendas do mês
vendas_mes = get_vendas_mes_atual()

# Calcular totais
total_vendas_mes = sum([float(v.get('valor_total', 0)) for v in vendas_mes])
vendas_pagas = [v for v in vendas_mes if v.get('status_recebimento') == 'Pago']
vendas_pendentes = [v for v in vendas_mes if v.get('status_recebimento') == 'Pendente']
vendas_consignadas = [v for v in vendas_mes if v.get('status_recebimento') == 'Consignado']
total_recebido = sum([float(v.get('valor_total', 0)) for v in vendas_pagas])
total_pendente = sum([float(v.get('valor_total', 0)) for v in vendas_pendentes])
total_consignado = sum([float(v.get('valor_total', 0)) for v in vendas_consignadas])

# Sidebar com resumo
hoje = datetime.now()
mes_atual = hoje.strftime("%m/%y")
st.sidebar.header("💰 Resumo de Vendas")
st.sidebar.markdown(f"**📅 Mês: {mes_atual}**")
st.sidebar.metric("💰 Total Vendas", f"R$ {total_vendas_mes:.2f}")
st.sidebar.metric("✅ Recebido", f"R$ {total_recebido:.2f}")
st.sidebar.metric("⏳ Pendente", f"R$ {total_pendente:.2f}")
st.sidebar.metric("🚚 Consignado", f"R$ {total_consignado:.2f}")
st.sidebar.metric("📄 Total Vendas", len(vendas_mes))

# Toggle para mostrar/ocultar formulário
st.subheader("📝 Nova Venda")

if 'show_form_venda' not in st.session_state:
    st.session_state.show_form_venda = False

if st.button(
    "📝 Abrir Formulário" if not st.session_state.show_form_venda else "✖️ Fechar Formulário",
    use_container_width=True,
    type="primary" if not st.session_state.show_form_venda else "secondary"
):
    st.session_state.show_form_venda = not st.session_state.show_form_venda

# Mostrar formulário apenas se toggle estiver ativo
if st.session_state.show_form_venda:
    with st.form("venda_form"):
        st.markdown("### 👤 Dados do Cliente")
        
        col1, col2 = st.columns(2)
        
        with col1:
            nome_cliente = st.text_input(
                "👤 Nome do Cliente *",
                placeholder="Ex: João Silva",
                help="Nome completo do cliente"
            )
            
            telefone_cliente = st.text_input(
                "📱 Telefone",
                placeholder="(11) 99999-9999",
                help="Telefone para contato"
            )
        
        with col2:
            data_venda = st.date_input(
                "📅 Data da Venda",
                value=date.today(),
                help="Data da venda",
                format="DD/MM/YYYY"
            )
            
            # Modalidade de venda (nova funcionalidade)
            modalidade_venda = st.selectbox(
                "🚚 Modalidade de Venda",
                ["Venda Direta", "Consignação"],
                help="Venda Direta = pagamento imediato | Consignação = acerto posterior"
            )
            
            tipo_pagamento = st.selectbox(
                "💳 Tipo de Pagamento",
                ["Dinheiro", "PIX", "Cartão", "Boleto", "Prazo"],
                help="Forma de pagamento escolhida"
            )
        
        # Data de vencimento para vendas a prazo
        data_vencimento = None
        if tipo_pagamento == "Prazo":
            data_vencimento = st.date_input(
                "📅 Data de Vencimento *",
                value=date.today(),
                help="Data limite para recebimento",
                format="DD/MM/YYYY"
            )
        
        st.markdown("### 🛒 Produtos da Venda")
        
        # Inicializar lista de produtos na sessão
        if 'produtos_venda' not in st.session_state:
            st.session_state.produtos_venda = []
        
        # Formulário para adicionar produto
        st.markdown("**➕ Adicionar Produto:**")
        col_prod1, col_prod2, col_prod3, col_prod4 = st.columns(4)
        
        with col_prod1:
            produto_nome = st.text_input(
                "📦 Produto",
                placeholder="Ex: Alface Crespa",
                key="produto_input"
            )
        
        with col_prod2:
            quantidade = st.number_input(
                "📊 Quantidade",
                min_value=0.01,
                value=1.0,
                step=0.01,
                format="%.2f",
                key="quantidade_input"
            )
            
            unidade = st.selectbox(
                "📏 Unidade",
                ["UN", "KG", "L", "M", "M²", "M³", "T", "SC", "CX", "PC", "DZ"],
                key="unidade_input"
            )
        
        with col_prod3:
            valor_unitario = st.number_input(
                "💰 Valor Unit. (R$)",
                min_value=0.01,
                step=0.01,
                format="%.2f",
                key="valor_unit_input"
            )
        
        with col_prod4:
            valor_produto = quantidade * valor_unitario
            st.metric("💰 Total", f"R$ {valor_produto:.2f}")
            
            # Botão para adicionar produto à lista
            if st.form_submit_button("➕ Adicionar Produto", type="secondary"):
                if produto_nome.strip() and quantidade > 0 and valor_unitario > 0:
                    novo_produto = {
                        'id': str(uuid.uuid4())[:8],
                        'nome': produto_nome.strip(),
                        'quantidade': float(quantidade),
                        'unidade': unidade,
                        'valor_unitario': float(valor_unitario),
                        'valor_total': float(valor_produto)
                    }
                    st.session_state.produtos_venda.append(novo_produto)
                    st.success(f"✅ Produto '{produto_nome}' adicionado!")
                    st.rerun()
                else:
                    st.warning("⚠️ Preencha todos os campos do produto!")
        
        # Mostrar produtos adicionados
        if st.session_state.produtos_venda:
            st.markdown("**🛒 Produtos na Venda:**")
            
            total_venda = 0
            for i, produto in enumerate(st.session_state.produtos_venda):
                qtd_formatada = f"{produto['quantidade']:.2f}".rstrip('0').rstrip('.')
                
                col_prod_info, col_prod_remove = st.columns([4, 1])
                
                with col_prod_info:
                    st.markdown(f"""
                    <div class="produto-item">
                        <strong>📦 {produto['nome']}</strong><br>
                        📊 {qtd_formatada} {produto['unidade']} × R$ {produto['valor_unitario']:.2f} = 
                        <strong>💰 R$ {produto['valor_total']:.2f}</strong>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_prod_remove:
                    if st.form_submit_button(f"🗑️", key=f"remove_{i}", help="Remover produto"):
                        st.session_state.produtos_venda.pop(i)
                        st.rerun()
                
                total_venda += produto['valor_total']
            
            # Total da venda
            st.markdown(f"### 💰 **Total da Venda: R$ {total_venda:.2f}**")
        else:
            st.info("➕ Adicione produtos à venda usando o formulário acima")
            total_venda = 0
        
        # Observações gerais
        observacoes = st.text_area(
            "📝 Observações",
            placeholder="Informações adicionais sobre a venda...",
            help="Observações gerais da venda"
        )
        
        # Status de recebimento baseado na modalidade
        if modalidade_venda == "Consignação":
            status_recebimento = "Consignado"
            st.info("🚚 Venda será marcada como **CONSIGNADA** (aguardando acerto de consumo/perda)")
        elif tipo_pagamento in ["Dinheiro", "PIX", "Cartão"]:
            status_recebimento = "Pago"
            st.success("✅ Venda será marcada como **PAGA** (pagamento à vista)")
        else:
            status_recebimento = "Pendente"
            st.warning("⏳ Venda será marcada como **PENDENTE** (aguardando recebimento)")
        
        # Botão de envio
        submitted = st.form_submit_button("💾 Finalizar Venda", use_container_width=True)
        
        if submitted:
            if nome_cliente.strip() and st.session_state.produtos_venda and total_venda > 0:
                if tipo_pagamento == "Prazo" and not data_vencimento:
                    st.warning("⚠️ Para vendas a prazo, informe a data de vencimento!")
                else:
                    try:
                        # Preparar dados da venda
                        venda_data = {
                            'numero_venda': f"V{datetime.now().strftime('%Y%m%d')}-{len(vendas_mes) + 1:03d}",
                            'data_venda': str(data_venda),
                            'nome_cliente': nome_cliente.strip(),
                            'telefone_cliente': telefone_cliente.strip() if telefone_cliente else '',
                            'modalidade_venda': modalidade_venda,
                            'tipo_pagamento': tipo_pagamento,
                            'data_vencimento': str(data_vencimento) if data_vencimento else '',
                            'status_recebimento': status_recebimento,
                            'produtos': st.session_state.produtos_venda.copy(),
                            'valor_total': float(total_venda),
                            'observacoes': observacoes.strip() if observacoes else '',
                            'timestamp': datetime.now().isoformat(),
                            'app_version': 'RST_v2.4'
                        }
                        
                        # Salvar no Firebase
                        doc_ref = db.collection('vendas').add(venda_data)
                        
                        st.success(f"✅ Venda {venda_data['numero_venda']} registrada com sucesso!")
                        st.success(f"💰 Valor total: R$ {total_venda:.2f}")
                        st.success(f"📊 {len(st.session_state.produtos_venda)} produtos vendidos")
                        
                        # Limpar formulário
                        st.session_state.produtos_venda = []
                        
                        # Limpar cache para atualizar resumo
                        st.cache_data.clear()
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Erro ao salvar venda: {e}")
            else:
                if not nome_cliente.strip():
                    st.warning("⚠️ Informe o nome do cliente!")
                if not st.session_state.produtos_venda:
                    st.warning("⚠️ Adicione pelo menos um produto à venda!")
                if total_venda <= 0:
                    st.warning("⚠️ O valor total deve ser maior que zero!")

# Tabela de vendas
st.subheader("📊 Vendas do Mês - Filtros")

if vendas_mes:
    # Filtros
    col_filtro1, col_filtro2, col_filtro3 = st.columns(3)
    
    with col_filtro1:
        filtro_cliente = st.text_input(
            "🔍 Buscar cliente",
            placeholder="Digite parte do nome...",
            help="Busca por nome do cliente"
        )
    
    with col_filtro2:
        tipos_pagamento = list(set([v.get('tipo_pagamento', 'N/A') for v in vendas_mes]))
        filtro_pagamento = st.multiselect(
            "💳 Tipo de Pagamento",
            options=tipos_pagamento,
            default=tipos_pagamento,
            help="Filtrar por tipo de pagamento"
        )
    
    with col_filtro3:
        filtro_status = st.selectbox(
            "📊 Status",
            ["Todos", "Apenas Pagas", "Apenas Pendentes", "Apenas Consignadas", "Apenas Acertadas"],
            help="Filtrar por status de recebimento"
        )
    
    # Aplicar filtros
    vendas_filtradas = vendas_mes
    
    if filtro_cliente:
        vendas_filtradas = [v for v in vendas_filtradas 
                           if filtro_cliente.lower() in v.get('nome_cliente', '').lower()]
    
    if filtro_pagamento:
        vendas_filtradas = [v for v in vendas_filtradas 
                           if v.get('tipo_pagamento', 'N/A') in filtro_pagamento]
    
    if filtro_status == "Apenas Pagas":
        vendas_filtradas = [v for v in vendas_filtradas if v.get('status_recebimento') == 'Pago']
    elif filtro_status == "Apenas Pendentes":
        vendas_filtradas = [v for v in vendas_filtradas if v.get('status_recebimento') == 'Pendente']
    elif filtro_status == "Apenas Consignadas":
        vendas_filtradas = [v for v in vendas_filtradas if v.get('status_recebimento') == 'Consignado']
    elif filtro_status == "Apenas Acertadas":
        vendas_filtradas = [v for v in vendas_filtradas if v.get('status_recebimento') == 'Acertado']
    
    if vendas_filtradas:
        st.markdown(f"**Encontradas: {len(vendas_filtradas)} vendas**")
        
        # Exibir vendas em cards
        for venda in vendas_filtradas:
            numero = venda.get('numero_venda', 'N/A')
            data_formatada = datetime.fromisoformat(venda['data_venda']).strftime('%d/%m/%Y')
            cliente = venda.get('nome_cliente', 'N/A')
            telefone = venda.get('telefone_cliente', 'N/A')
            valor_total = venda.get('valor_total', 0)
            modalidade = venda.get('modalidade_venda', 'N/A')
            tipo_pagamento = venda.get('tipo_pagamento', 'N/A')
            status = venda.get('status_recebimento', 'N/A')
            produtos = venda.get('produtos', [])
            
            # Card da venda
            if status == "Pago":
                card_class = "venda-card"
                status_icon = "✅"
            elif status == "Consignado":
                card_class = "pendente-card"  # Usar cor amarela para consignação
                status_icon = "🚚"
            elif status == "Acertado":
                card_class = "venda-card"  # Verde para acertados
                status_icon = "📊"
            else:
                card_class = "pendente-card"
                status_icon = "⏳"
            
            with st.container():
                st.markdown(f"""
                <div class="{card_class}">
                    <h4>{status_icon} {numero} - {data_formatada}</h4>
                    <p><strong>👤 Cliente:</strong> {cliente} | <strong>📱 Telefone:</strong> {telefone}</p>
                    <p><strong>🚚 Modalidade:</strong> {modalidade} | <strong>💳 Pagamento:</strong> {tipo_pagamento}</p>
                    <p><strong>📊 Status:</strong> {status} | <strong>💰 Valor Total: R$ {valor_total:.2f}</strong></p>
                </div>
                """, unsafe_allow_html=True)
                
                # Mostrar produtos da venda
                if produtos:
                    with st.expander(f"📦 Ver produtos ({len(produtos)} itens)"):
                        for produto in produtos:
                            qtd = f"{produto['quantidade']:.2f}".rstrip('0').rstrip('.')
                            st.write(f"• **{produto['nome']}** - {qtd} {produto['unidade']} × R$ {produto['valor_unitario']:.2f} = R$ {produto['valor_total']:.2f}")
                
                # Mostrar informações do acerto se foi acertado
                if status == "Acertado" and 'acerto_consumo' in venda:
                    acerto = venda['acerto_consumo']
                    with st.expander(f"📊 Ver acerto de consumo"):
                        col_acerto1, col_acerto2, col_acerto3 = st.columns(3)
                        
                        with col_acerto1:
                            st.metric("💰 Valor Recebido", f"R$ {acerto.get('valor_a_receber', 0):.2f}")
                        
                        with col_acerto2:
                            st.metric("📉 Valor em Perdas", f"R$ {acerto.get('valor_perda', 0):.2f}")
                        
                        with col_acerto3:
                            st.metric("📊 Eficiência", f"{acerto.get('eficiencia_percentual', 0):.1f}%")
                        
                        if acerto.get('observacoes_acerto'):
                            st.write(f"**📝 Observações:** {acerto['observacoes_acerto']}")
                        
                        # Mostrar detalhes por produto
                        if 'produtos_acerto' in acerto:
                            st.markdown("**📦 Detalhes por produto:**")
                            for prod in acerto['produtos_acerto']:
                                st.write(f"• **{prod['nome']}**: Consumido {prod['quantidade_consumida']:.2f}, Perdido {prod['quantidade_perdida']:.2f}, Devolvido {prod['quantidade_devolvida']:.2f}")
                
                # Botões de ação
                col_btn1, col_btn2, col_btn3 = st.columns(3)
                
                with col_btn1:
                    if status == "Pendente":
                        if st.button(f"✅ Marcar como Pago", key=f"pagar_{venda['id']}", use_container_width=True):
                            try:
                                db.collection('vendas').document(venda['id']).update({
                                    'status_recebimento': 'Pago',
                                    'data_recebimento': datetime.now().isoformat()
                                })
                                st.success(f"✅ Venda {numero} marcada como paga!")
                                st.cache_data.clear()
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Erro ao atualizar: {e}")
                    elif status == "Consignado":
                        if st.button(f"📊 Acertar Consumo", key=f"acerto_{venda['id']}", use_container_width=True):
                            st.session_state[f'show_acerto_{venda["id"]}'] = True
                            st.rerun()
                
                with col_btn2:
                    st.write("")  # Espaçamento
                
                with col_btn3:
                    if status == "Consignado":
                        if st.button(f"❌ Cancelar Consignação", key=f"cancel_{venda['id']}", use_container_width=True):
                            try:
                                db.collection('vendas').document(venda['id']).update({
                                    'status_recebimento': 'Cancelado',
                                    'data_cancelamento': datetime.now().isoformat()
                                })
                                st.success(f"❌ Consignação {numero} cancelada!")
                                st.cache_data.clear()
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Erro ao cancelar: {e}")
                
                # Formulário de Acerto de Consumo
                if st.session_state.get(f'show_acerto_{venda["id"]}', False) and status == "Consignado":
                    st.markdown("---")
                    st.markdown(f"### 📊 **Acerto de Consumo - {numero}**")
                    
                    with st.form(f"acerto_form_{venda['id']}"):
                        st.markdown("**📦 Informe o que aconteceu com cada produto:**")
                        
                        produtos_acerto = []
                        total_a_receber = 0
                        total_perda = 0
                        
                        for i, produto in enumerate(produtos):
                            st.markdown(f"**🌱 {produto['nome']}** - Entregue: {produto['quantidade']:.2f} {produto['unidade']}")
                            
                            col_consumo1, col_consumo2, col_consumo3 = st.columns(3)
                            
                            with col_consumo1:
                                qtd_consumida = st.number_input(
                                    "✅ Consumido",
                                    min_value=0.0,
                                    max_value=float(produto['quantidade']),
                                    value=0.0,
                                    step=0.01,
                                    format="%.2f",
                                    key=f"consumido_{venda['id']}_{i}",
                                    help="Quantidade vendida/consumida pelo cliente"
                                )
                            
                            with col_consumo2:
                                qtd_perdida = st.number_input(
                                    "❌ Perdido",
                                    min_value=0.0,
                                    max_value=float(produto['quantidade']),
                                    value=0.0,
                                    step=0.01,
                                    format="%.2f",
                                    key=f"perdido_{venda['id']}_{i}",
                                    help="Quantidade que estragou/deteriorou"
                                )
                            
                            with col_consumo3:
                                qtd_devolvida = produto['quantidade'] - qtd_consumida - qtd_perdida
                                st.metric("🔄 Devolvido", f"{qtd_devolvida:.2f} {produto['unidade']}")
                            
                            # Validações
                            if qtd_consumida + qtd_perdida > produto['quantidade']:
                                st.error(f"⚠️ Total (consumido + perdido) não pode ser maior que {produto['quantidade']:.2f}")
                            
                            # Cálculos financeiros
                            valor_receber = qtd_consumida * produto['valor_unitario']
                            valor_perda = qtd_perdida * produto['valor_unitario']
                            
                            # Mostrar resumo do produto
                            st.info(f"💰 A receber: R$ {valor_receber:.2f} | 📉 Perda: R$ {valor_perda:.2f}")
                            
                            produtos_acerto.append({
                                'nome': produto['nome'],
                                'quantidade_original': produto['quantidade'],
                                'unidade': produto['unidade'],
                                'valor_unitario': produto['valor_unitario'],
                                'quantidade_consumida': qtd_consumida,
                                'quantidade_perdida': qtd_perdida,
                                'quantidade_devolvida': qtd_devolvida,
                                'valor_a_receber': valor_receber,
                                'valor_perda': valor_perda
                            })
                            
                            total_a_receber += valor_receber
                            total_perda += valor_perda
                            
                            st.markdown("---")
                        
                        # Resumo final
                        st.markdown("### 💰 **Resumo do Acerto**")
                        col_resumo1, col_resumo2, col_resumo3 = st.columns(3)
                        
                        with col_resumo1:
                            st.metric("💰 Total a Receber", f"R$ {total_a_receber:.2f}")
                        
                        with col_resumo2:
                            st.metric("📉 Total em Perdas", f"R$ {total_perda:.2f}")
                        
                        with col_resumo3:
                            valor_original = venda.get('valor_total', 0)
                            eficiencia = (total_a_receber / valor_original * 100) if valor_original > 0 else 0
                            st.metric("📊 Eficiência", f"{eficiencia:.1f}%")
                        
                        # Observações do acerto
                        observacoes_acerto = st.text_area(
                            "📝 Observações do Acerto",
                            placeholder="Motivos das perdas, condições dos produtos devolvidos, etc.",
                            help="Registre informações importantes sobre o acerto"
                        )
                        
                        # Botões do formulário
                        col_btn_acerto1, col_btn_acerto2 = st.columns(2)
                        
                        with col_btn_acerto1:
                            finalizar_acerto = st.form_submit_button("✅ Finalizar Acerto", type="primary", use_container_width=True)
                        
                        with col_btn_acerto2:
                            if st.form_submit_button("❌ Cancelar", use_container_width=True):
                                st.session_state[f'show_acerto_{venda["id"]}'] = False
                                st.rerun()
                        
                        if finalizar_acerto:
                            try:
                                # Validar se pelo menos um produto foi consumido
                                if total_a_receber <= 0:
                                    st.warning("⚠️ Informe pelo menos uma quantidade consumida!")
                                else:
                                    # Preparar dados do acerto
                                    acerto_data = {
                                        'data_acerto': datetime.now().isoformat(),
                                        'produtos_acerto': produtos_acerto,
                                        'valor_original': float(valor_original),
                                        'valor_a_receber': float(total_a_receber),
                                        'valor_perda': float(total_perda),
                                        'eficiencia_percentual': float(eficiencia),
                                        'observacoes_acerto': observacoes_acerto.strip(),
                                        'acertado_por': 'Sistema RST'  # Futuro: usuário logado
                                    }
                                    
                                    # Atualizar venda no Firebase
                                    db.collection('vendas').document(venda['id']).update({
                                        'status_recebimento': 'Acertado',
                                        'acerto_consumo': acerto_data,
                                        'valor_final': float(total_a_receber)  # Valor real a receber
                                    })
                                    
                                    st.success(f"✅ Acerto finalizado com sucesso!")
                                    st.success(f"💰 Valor a receber: R$ {total_a_receber:.2f}")
                                    st.success(f"📉 Total em perdas: R$ {total_perda:.2f}")
                                    st.success(f"📊 Eficiência: {eficiencia:.1f}%")
                                    
                                    # Limpar estado e atualizar
                                    st.session_state[f'show_acerto_{venda["id"]}'] = False
                                    st.cache_data.clear()
                                    st.rerun()
                                    
                            except Exception as e:
                                st.error(f"❌ Erro ao finalizar acerto: {e}")
                
                st.markdown("---")
    else:
        st.info("🔍 Nenhuma venda encontrada com os filtros aplicados.")
else:
    st.info("📝 Nenhuma venda registrada ainda. Use o formulário acima para adicionar vendas!")

# Footer com estatísticas
st.markdown("---")
st.subheader("📈 Estatísticas do Mês")

if vendas_mes:
    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
    
    with col_stat1:
        st.metric("🛒 Total de Vendas", len(vendas_mes))
    
    with col_stat2:
        st.metric("💰 Faturamento", f"R$ {total_vendas_mes:.2f}")
    
    with col_stat3:
        if vendas_mes:
            ticket_medio = total_vendas_mes / len(vendas_mes)
            st.metric("🎯 Ticket Médio", f"R$ {ticket_medio:.2f}")
    
    with col_stat4:
        produtos_vendidos = sum([len(v.get('produtos', [])) for v in vendas_mes])
        st.metric("📦 Produtos Vendidos", produtos_vendidos)

# Informações sobre modalidades
st.markdown("---")
with st.expander("📚 Entenda as Modalidades de Venda"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **💰 Venda Direta**
        - Produto vendido e entregue
        - Pagamento imediato ou a prazo
        - Receita confirmada
        - Controle simples
        """)
    
    with col2:
        st.markdown("""
        **🚚 Consignação**
        - Produto entregue, mas não vendido
        - Aguarda acerto de consumo/perda
        - Cliente paga apenas o consumido
        - Ideal para produtos perecíveis
        """)
    
    st.info("""
    **🔧 Próximas funcionalidades:**
    - Sistema de acerto de consignação com consumo e perda
    - Relatórios detalhados por modalidade  
    - Controle de produtos devolvidos
    - Dashboard específico para consignações
    """)

st.markdown("💰 **Sistema de Vendas RST** - Controle completo de vendas, consignações e recebimentos!")