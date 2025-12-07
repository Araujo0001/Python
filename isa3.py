import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd
import calendar

st.set_page_config(page_title="Studio de Sobrancelhas - Agendamentos", layout="wide")

st.title('💅 Studio de Design de Sobrancelhas')

# Inicializar variáveis de sessão
if 'agendamentos' not in st.session_state:
    st.session_state.agendamentos = []
if 'editar_index' not in st.session_state:
    st.session_state.editar_index = None
if 'modo_edicao' not in st.session_state:
    st.session_state.modo_edicao = False

# Horários disponíveis (9h às 18h, de hora em hora)
HORARIOS_DISPONIVEIS = [f"{h:02d}:00" for h in range(9, 18)]

# Serviços oferecidos com preços padrão
SERVICOS = {
    "Cílios comun": 25.00,
    "Design com Henna": 40.00,
    "Combo": 110.00,
    #"Aplicação de Cílios": 150.00,
    "Buço": 15.00,
    "Cílios Italiano": 70.00,
    "Maquiagem": 100.00,
    "Retoque Henna": 20.00
}

# Taxas de deslocamento
TAXAS_DESLOCAMENTO = {
    "ZN - Zona Norte": 5.00,
    "ZL - Zona Leste": 10.00,
    "ZS - Zona Sul": 15.00,
    "Sem taxas": 0.00
}

# Funções auxiliares
def carregar_agendamentos():
    """Carrega os agendamentos do arquivo JSON"""
    arquivo_json = 'agendamentos_sobracelhas.json'
    if os.path.exists(arquivo_json):
        try:
            with open(arquivo_json, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def salvar_agendamentos(agendamentos):
    """Salva os agendamentos no arquivo JSON"""
    arquivo_json = 'agendamentos_sobracelhas.json'
    try:
        with open(arquivo_json, 'w', encoding='utf-8') as f:
            json.dump(agendamentos, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        st.error(f'Erro ao salvar: {e}')
        return False

def formatar_data(data_str):
    """Formata data para exibição"""
    try:
        data_obj = datetime.strptime(data_str, '%Y-%m-%d')
        return data_obj.strftime('%d/%m/%Y')
    except:
        return data_str

def verificar_horario_disponivel(data, hora):
    """Verifica se o horário já está agendado"""
    for agendamento in st.session_state.agendamentos:
        if agendamento['data'] == data and agendamento['hora'] == hora:
            return False
    return True

def calcular_duracao_servico(servico):
    """Calcula a duração estimada do serviço em minutos"""
    duracao_map = {
        "Design de Sobrancelhas": 30,
        "Design com Henna": 45,
        "Design + Henna + Tintura": 60,
        "Aplicação de Cílios": 90,
        "Remoção de Cílios": 30,
        "Limpeza de Pele": 60,
        "Maquiagem": 60,
        "Pacote Completo": 180
    }
    return duracao_map.get(servico, 60)

def obter_valor_agendamento(agendamento):
    """Obtém o valor do agendamento (usando valor cadastrado ou padrão)"""
    valor_servico = 0
    if agendamento.get('valor') and float(agendamento['valor']) > 0:
        valor_servico = float(agendamento['valor'])
    else:
        valor_servico = SERVICOS.get(agendamento['servico'], 0)
    
    # Adicionar taxa de deslocamento se existir
    if agendamento.get('taxa_deslocamento'):
        valor_servico += float(agendamento['taxa_deslocamento'])
    
    return valor_servico

def calcular_saldo_dia(data_str=None):
    """Calcula o faturamento total de um dia específico"""
    if data_str is None:
        data_str = datetime.now().strftime('%Y-%m-%d')
    
    saldo_total = 0
    agendamentos_dia = []
    
    for agendamento in st.session_state.agendamentos:
        if agendamento['data'] == data_str:
            agendamentos_dia.append(agendamento)
            saldo_total += obter_valor_agendamento(agendamento)
    
    return {
        'saldo_total': saldo_total,
        'quantidade': len(agendamentos_dia),
        'agendamentos': agendamentos_dia,
        'data': data_str
    }

def calcular_saldo_mes(ano=None, mes=None):
    """Calcula o faturamento total de um mês específico"""
    if ano is None or mes is None:
        hoje = datetime.now()
        ano = hoje.year
        mes = hoje.month
    
    saldo_total = 0
    agendamentos_mes = []
    
    for agendamento in st.session_state.agendamentos:
        try:
            data_agendamento = datetime.strptime(agendamento['data'], '%Y-%m-%d')
            if data_agendamento.year == ano and data_agendamento.month == mes:
                agendamentos_mes.append(agendamento)
                saldo_total += obter_valor_agendamento(agendamento)
        except:
            continue
    
    return {
        'saldo_total': saldo_total,
        'quantidade': len(agendamentos_mes),
        'agendamentos': agendamentos_mes,
        'mes': mes,
        'ano': ano,
        'nome_mes': calendar.month_name[mes]
    }

def calcular_estatisticas_mes(ano=None, mes=None):
    """Calcula estatísticas detalhadas do mês"""
    if ano is None or mes is None:
        hoje = datetime.now()
        ano = hoje.year
        mes = hoje.month
    
    dados = calcular_saldo_mes(ano, mes)
    agendamentos = dados['agendamentos']
    
    if not agendamentos:
        return {
            'servicos_mais_vendidos': [],
            'clientes_frequentes': [],
            'dias_mais_lotados': [],
            'faturamento_diario': {}
        }
    
    # Serviços mais vendidos
    servicos_count = {}
    for ag in agendamentos:
        servico = ag['servico']
        servicos_count[servico] = servicos_count.get(servico, 0) + 1
    
    servicos_mais_vendidos = sorted(servicos_count.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # Clientes mais frequentes
    clientes_count = {}
    for ag in agendamentos:
        cliente = ag['cliente']
        clientes_count[cliente] = clientes_count.get(cliente, 0) + 1
    
    clientes_frequentes = sorted(clientes_count.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # Dias mais lotados
    dias_count = {}
    for ag in agendamentos:
        dia = ag['data'][8:10]  # Extrai o dia
        dias_count[dia] = dias_count.get(dia, 0) + 1
    
    dias_mais_lotados = sorted(dias_count.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # Faturamento por dia
    faturamento_diario = {}
    for ag in agendamentos:
        dia = ag['data']
        valor = obter_valor_agendamento(ag)
        faturamento_diario[dia] = faturamento_diario.get(dia, 0) + valor
    
    return {
        'servicos_mais_vendidos': servicos_mais_vendidos,
        'clientes_frequentes': clientes_frequentes,
        'dias_mais_lotados': dias_mais_lotados,
        'faturamento_diario': faturamento_diario
    }

# Carregar agendamentos do arquivo
st.session_state.agendamentos = carregar_agendamentos()

# Sidebar para navegação
st.sidebar.title("💅 Studio Isa Beauty")
opcao = st.sidebar.radio(
    "Selecione uma opção:",
    ["📋 Listar Todos", "📅 Agenda do Dia", "💰 Saldo do Dia", "📊 Saldo do Mês", "🔍 Pesquisar", 
     "➕ Novo Agendamento", "✏️ Editar", "🗑️ Excluir", "🏷️ Preços"]
)

# FUNÇÃO: LISTAR TODOS OS AGENDAMENTOS
if opcao == "📋 Listar Todos":
    st.header("📋 Todos os Agendamentos")
    
    if st.session_state.agendamentos:
        # Converter para DataFrame para melhor visualização
        df = pd.DataFrame(st.session_state.agendamentos)
        
        # Formatar data para exibição
        if 'data' in df.columns:
            df['data_formatada'] = df['data'].apply(formatar_data)
        
        # Mostrar estatísticas
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total de Agendamentos", len(st.session_state.agendamentos))
        with col2:
            st.metric("Clientes Únicos", df['cliente'].nunique() if 'cliente' in df.columns else 0)
        with col3:
            hoje = datetime.now().strftime('%Y-%m-%d')
            saldo_hoje = calcular_saldo_dia(hoje)
            st.metric("Saldo Hoje", f"R$ {saldo_hoje['saldo_total']:.2f}")
        with col4:
            hoje_obj = datetime.now()
            saldo_mes = calcular_saldo_mes(hoje_obj.year, hoje_obj.month)
            st.metric("Saldo Mês", f"R$ {saldo_mes['saldo_total']:.2f}")
        
        # Ordenar por data e hora
        if 'data' in df.columns and 'hora' in df.columns:
            df['data_hora'] = pd.to_datetime(df['data'] + ' ' + df['hora'])
            df = df.sort_values('data_hora', ascending=False)
        
        # Mostrar tabela
        colunas_mostrar = ['cliente', 'telefone', 'servico', 'data_formatada', 'hora', 'valor']
        if all(col in df.columns for col in ['cliente', 'telefone', 'servico', 'data_formatada', 'hora']):
            # Adicionar coluna de valor formatada
            df['valor_formatado'] = df.apply(
                lambda row: f"R$ {obter_valor_agendamento(row):.2f}" if row.get('valor') or row.get('servico') else "-",
                axis=1
            )
            
            st.dataframe(
                df[['cliente', 'telefone', 'servico', 'data_formatada', 'hora', 'valor_formatado']],
                use_container_width=True,
                column_config={
                    "cliente": "Cliente",
                    "telefone": "Telefone",
                    "servico": "Serviço",
                    "data_formatada": "Data",
                    "hora": "Hora",
                    "valor_formatado": "Valor Total"
                }
            )
    else:
        st.info("📭 Nenhum agendamento cadastrado ainda.")

# FUNÇÃO: AGENDA DO DIA
elif opcao == "📅 Agenda do Dia":
    st.header("📅 Agenda do Dia")
    
    hoje = datetime.now().strftime('%Y-%m-%d')
    saldo_hoje = calcular_saldo_dia(hoje)
    agendamentos_hoje = saldo_hoje['agendamentos']
    
    if agendamentos_hoje:
        col1, col2 = st.columns(2)
        with col1:
            st.success(f"✅ {len(agendamentos_hoje)} agendamento(s) para hoje!")
        with col2:
            st.info(f"💰 **Saldo do dia: R$ {saldo_hoje['saldo_total']:.2f}**")
        
        # Ordenar por hora
        agendamentos_hoje.sort(key=lambda x: x['hora'])
        
        for i, agendamento in enumerate(agendamentos_hoje, 1):
            duracao = calcular_duracao_servico(agendamento['servico'])
            valor_total = obter_valor_agendamento(agendamento)
            valor_servico = float(agendamento.get('valor', 0)) if agendamento.get('valor') else SERVICOS.get(agendamento['servico'], 0)
            taxa_deslocamento = float(agendamento.get('taxa_deslocamento', 0)) if agendamento.get('taxa_deslocamento') else 0
            
            with st.container(border=True):
                col1, col2, col3 = st.columns([1, 2, 1])
                with col1:
                    st.markdown(f"**{agendamento['hora']}**")
                    st.caption(f"{duracao} min")
                with col2:
                    st.markdown(f"**{agendamento['cliente']}**")
                    st.caption(f"{agendamento['servico']}")
                    if agendamento.get('observacoes'):
                        st.caption(f"📝 {agendamento['observacoes']}")
                    if agendamento.get('taxa_deslocamento') and float(agendamento['taxa_deslocamento']) > 0:
                        st.caption(f"📍 Taxa deslocamento: R$ {taxa_deslocamento:.2f}")
                with col3:
                    st.caption(f"📞 {agendamento['telefone']}")
                    st.markdown(f"**R$ {valor_total:.2f}**")
                    if taxa_deslocamento > 0:
                        st.caption(f"(serviço: R$ {valor_servico:.2f})")
    else:
        st.info("🎉 Nenhum agendamento para hoje!")

# FUNÇÃO: SALDO DO DIA
elif opcao == "💰 Saldo do Dia":
    st.header("💰 Saldo do Dia")
    
    # Seletor de data
    col1, col2 = st.columns(2)
    with col1:
        data_selecionada = st.date_input(
            "Selecione a data:",
            value=datetime.now(),
            key="saldo_dia_data"
        )
    
    # Calcular saldo do dia selecionado
    data_str = data_selecionada.strftime('%Y-%m-%d')
    saldo_dia = calcular_saldo_dia(data_str)
    
    # Exibir métricas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "Total Agendamentos",
            saldo_dia['quantidade'],
            delta=None
        )
    with col2:
        st.metric(
            "Faturamento Bruto",
            f"R$ {saldo_dia['saldo_total']:.2f}"
        )
    with col3:
        # Calcular média por cliente
        media_cliente = saldo_dia['saldo_total'] / saldo_dia['quantidade'] if saldo_dia['quantidade'] > 0 else 0
        st.metric(
            "Ticket Médio",
            f"R$ {media_cliente:.2f}"
        )
    
    # Listar detalhes dos agendamentos
    if saldo_dia['agendamentos']:
        st.subheader(f"📋 Detalhes dos Agendamentos - {formatar_data(data_str)}")
        
        # Criar DataFrame para exibição
        detalhes_data = []
        for ag in saldo_dia['agendamentos']:
            valor_total = obter_valor_agendamento(ag)
            valor_servico = float(ag.get('valor', 0)) if ag.get('valor') else SERVICOS.get(ag['servico'], 0)
            taxa = float(ag.get('taxa_deslocamento', 0)) if ag.get('taxa_deslocamento') else 0
            
            detalhes_data.append({
                'Cliente': ag['cliente'],
                'Serviço': ag['servico'],
                'Hora': ag['hora'],
                'Telefone': ag['telefone'],
                'Serviço (R$)': f"R$ {valor_servico:.2f}",
                'Taxa (R$)': f"R$ {taxa:.2f}" if taxa > 0 else "-",
                'Total (R$)': f"R$ {valor_total:.2f}"
            })
        
        df_detalhes = pd.DataFrame(detalhes_data)
        st.dataframe(df_detalhes, use_container_width=True, hide_index=True)
        
        # Gráfico de serviços do dia (se houver dados)
        if saldo_dia['quantidade'] > 0:
            st.subheader("📊 Distribuição por Serviço")
            
            # Contar serviços
            servicos_count = {}
            for ag in saldo_dia['agendamentos']:
                servico = ag['servico']
                servicos_count[servico] = servicos_count.get(servico, 0) + 1
            
            # Criar DataFrame para gráfico
            df_servicos = pd.DataFrame({
                'Serviço': list(servicos_count.keys()),
                'Quantidade': list(servicos_count.values())
            })
            
            # Exibir gráfico de barras
            st.bar_chart(df_servicos.set_index('Serviço'))
    else:
        st.info(f"📭 Nenhum agendamento para {formatar_data(data_str)}")

# FUNÇÃO: SALDO DO MÊS
elif opcao == "📊 Saldo do Mês":
    st.header("📊 Saldo do Mês")
    
    # Seletor de mês e ano
    hoje = datetime.now()
    col1, col2 = st.columns(2)
    with col1:
        ano_selecionado = st.selectbox(
            "Ano:",
            range(2023, hoje.year + 2),
            index=hoje.year - 2023,
            key="saldo_mes_ano"
        )
    with col2:
        mes_selecionado = st.selectbox(
            "Mês:",
            range(1, 13),
            format_func=lambda x: calendar.month_name[x],
            index=hoje.month - 1,
            key="saldo_mes_mes"
        )
    
    # Calcular saldo do mês selecionado
    saldo_mes = calcular_saldo_mes(ano_selecionado, mes_selecionado)
    
    # Exibir métricas principais
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            "Total Agendamentos",
            saldo_mes['quantidade']
        )
    with col2:
        st.metric(
            "Faturamento Total",
            f"R$ {saldo_mes['saldo_total']:.2f}"
        )
    with col3:
        # Calcular média por dia útil (considerando 22 dias úteis)
        media_dia_util = saldo_mes['saldo_total'] / 22 if saldo_mes['saldo_total'] > 0 else 0
        st.metric(
            "Média/Dia Útil",
            f"R$ {media_dia_util:.2f}"
        )
    with col4:
        # Calcular média por cliente
        media_cliente = saldo_mes['saldo_total'] / saldo_mes['quantidade'] if saldo_mes['quantidade'] > 0 else 0
        st.metric(
            "Ticket Médio",
            f"R$ {media_cliente:.2f}"
        )
    
    # Calcular estatísticas detalhadas
    estatisticas = calcular_estatisticas_mes(ano_selecionado, mes_selecionado)
    
    if saldo_mes['quantidade'] > 0:
        # Layout com tabs para diferentes visualizações
        tab1, tab2, tab3, tab4 = st.tabs(["📈 Faturamento Diário", "🏆 Serviços Mais Vendidos", "👑 Clientes Frequentes", "📋 Todos os Agendamentos"])
        
        with tab1:
            st.subheader("📈 Faturamento Diário")
            
            if estatisticas['faturamento_diario']:
                # Criar DataFrame para gráfico
                dias = list(estatisticas['faturamento_diario'].keys())
                valores = list(estatisticas['faturamento_diario'].values())
                
                # Formatar datas para exibição
                dias_formatados = [formatar_data(dia) for dia in dias]
                
                df_faturamento = pd.DataFrame({
                    'Dia': dias_formatados,
                    'Data Original': dias,
                    'Faturamento': valores
                })
                
                # Ordenar por data
                df_faturamento = df_faturamento.sort_values('Data Original')
                
                # Exibir gráfico
                st.bar_chart(df_faturamento.set_index('Dia')['Faturamento'])
                
                # Exibir tabela
                st.dataframe(
                    df_faturamento[['Dia', 'Faturamento']],
                    column_config={
                        "Dia": "Data",
                        "Faturamento": st.column_config.NumberColumn(
                            "Faturamento (R$)",
                            format="R$ %.2f"
                        )
                    },
                    hide_index=True,
                    use_container_width=True
                )
        
        with tab2:
            st.subheader("🏆 Serviços Mais Vendidos")
            
            if estatisticas['servicos_mais_vendidos']:
                df_servicos = pd.DataFrame(
                    estatisticas['servicos_mais_vendidos'],
                    columns=['Serviço', 'Quantidade']
                )
                
                # Calcular faturamento por serviço
                faturamento_servicos = []
                for servico, quantidade in estatisticas['servicos_mais_vendidos']:
                    valor_servico = SERVICOS.get(servico, 0)
                    faturamento_servicos.append(valor_servico * quantidade)
                
                df_servicos['Faturamento'] = faturamento_servicos
                
                col1, col2 = st.columns(2)
                with col1:
                    st.dataframe(
                        df_servicos,
                        column_config={
                            "Serviço": "Serviço",
                            "Quantidade": "Qtd",
                            "Faturamento": st.column_config.NumberColumn(
                                "Faturamento (R$)",
                                format="R$ %.2f"
                            )
                        },
                        hide_index=True,
                        use_container_width=True
                    )
                with col2:
                    st.bar_chart(df_servicos.set_index('Serviço')['Faturamento'])
        
        with tab3:
            st.subheader("👑 Clientes Frequentes")
            
            if estatisticas['clientes_frequentes']:
                df_clientes = pd.DataFrame(
                    estatisticas['clientes_frequentes'],
                    columns=['Cliente', 'Visitas']
                )
                
                st.dataframe(
                    df_clientes,
                    column_config={
                        "Cliente": "Cliente",
                        "Visitas": "Nº de Visitas"
                    },
                    hide_index=True,
                    use_container_width=True
                )
                
                # Exibir como gráfico
                st.bar_chart(df_clientes.set_index('Cliente')['Visitas'])
        
        with tab4:
            st.subheader(f"📋 Todos os Agendamentos - {calendar.month_name[mes_selecionado]}/{ano_selecionado}")
            
            # Criar DataFrame com todos os agendamentos do mês
            detalhes_mes = []
            for ag in saldo_mes['agendamentos']:
                valor_total = obter_valor_agendamento(ag)
                valor_servico = float(ag.get('valor', 0)) if ag.get('valor') else SERVICOS.get(ag['servico'], 0)
                taxa = float(ag.get('taxa_deslocamento', 0)) if ag.get('taxa_deslocamento') else 0
                
                detalhes_mes.append({
                    'Data': formatar_data(ag['data']),
                    'Dia': ag['data'],
                    'Cliente': ag['cliente'],
                    'Serviço': ag['servico'],
                    'Hora': ag['hora'],
                    'Serviço (R$)': valor_servico,
                    'Taxa (R$)': taxa,
                    'Total (R$)': valor_total
                })
            
            if detalhes_mes:
                df_detalhes_mes = pd.DataFrame(detalhes_mes)
                df_detalhes_mes = df_detalhes_mes.sort_values('Dia')
                
                st.dataframe(
                    df_detalhes_mes[['Data', 'Cliente', 'Serviço', 'Hora', 'Serviço (R$)', 'Taxa (R$)', 'Total (R$)']],
                    column_config={
                        "Data": "Data",
                        "Cliente": "Cliente",
                        "Serviço": "Serviço",
                        "Hora": "Hora",
                        "Serviço (R$)": st.column_config.NumberColumn(
                            "Serviço (R$)",
                            format="R$ %.2f"
                        ),
                        "Taxa (R$)": st.column_config.NumberColumn(
                            "Taxa (R$)",
                            format="R$ %.2f"
                        ),
                        "Total (R$)": st.column_config.NumberColumn(
                            "Total (R$)",
                            format="R$ %.2f"
                        )
                    },
                    hide_index=True,
                    use_container_width=True
                )
    else:
        nome_mes = calendar.month_name[mes_selecionado]
        st.info(f"📭 Nenhum agendamento para {nome_mes}/{ano_selecionado}")

# FUNÇÃO: PESQUISAR
elif opcao == "🔍 Pesquisar":
    st.header("🔍 Pesquisar Agendamentos")
    
    col1, col2 = st.columns(2)
    with col1:
        tipo_pesquisa = st.radio(
            "Pesquisar por:",
            ["Cliente", "Telefone", "Data"]
        )
    
    with col2:
        if tipo_pesquisa == "Data":
            data_pesquisa = st.date_input("Selecione a data:")
            termo_pesquisa = data_pesquisa.strftime('%Y-%m-%d') if data_pesquisa else ""
        else:
            termo_pesquisa = st.text_input(f"Digite o {tipo_pesquisa.lower()}:")
    
    if termo_pesquisa:
        resultados = []
        for agendamento in st.session_state.agendamentos:
            if tipo_pesquisa == "Cliente":
                if termo_pesquisa.lower() in agendamento['cliente'].lower():
                    resultados.append(agendamento)
            elif tipo_pesquisa == "Telefone":
                if termo_pesquisa in agendamento['telefone']:
                    resultados.append(agendamento)
            elif tipo_pesquisa == "Data":
                if termo_pesquisa == agendamento['data']:
                    resultados.append(agendamento)
        
        if resultados:
            st.success(f"✅ Encontrados {len(resultados)} resultado(s)")
            
            for i, agendamento in enumerate(resultados, 1):
                with st.expander(f"{agendamento['cliente']} - {formatar_data(agendamento['data'])} {agendamento['hora']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Cliente:** {agendamento['cliente']}")
                        st.write(f"**Telefone:** {agendamento['telefone']}")
                        st.write(f"**Data:** {formatar_data(agendamento['data'])}")
                        st.write(f"**Serviço:** {agendamento['servico']}")
                    with col2:
                        st.write(f"**Hora:** {agendamento['hora']}")
                        valor_total = obter_valor_agendamento(agendamento)
                        valor_servico = float(agendamento.get('valor', 0)) if agendamento.get('valor') else SERVICOS.get(agendamento['servico'], 0)
                        taxa = float(agendamento.get('taxa_deslocamento', 0)) if agendamento.get('taxa_deslocamento') else 0
                        
                        st.write(f"**Valor Serviço:** R$ {valor_servico:.2f}")
                        if taxa > 0:
                            st.write(f"**Taxa Deslocamento:** R$ {taxa:.2f}")
                        st.write(f"**Valor Total:** R$ {valor_total:.2f}")
                        
                        if agendamento.get('observacoes'):
                            st.write(f"**Observações:** {agendamento['observacoes']}")
        else:
            st.warning(f"⚠️ Nenhum agendamento encontrado")

# FUNÇÃO: NOVO AGENDAMENTO - CORRIGIDA (SEM CALLBACKS NO FORM)
elif opcao == "➕ Novo Agendamento":
    st.header("➕ Novo Agendamento")
    
    # Usar formulário normal sem callbacks
    with st.form("form_novo_agendamento"):
        col1, col2 = st.columns(2)
        
        with col1:
            cliente = st.text_input("Nome do Cliente:*")
            telefone = st.text_input("Telefone:*")
            servico = st.selectbox("Serviço:*", list(SERVICOS.keys()))
        
        with col2:
            data = st.date_input("Data do Agendamento:*")
            
            # Mostrar apenas horários disponíveis
            horarios_disponiveis = []
            for hora in HORARIOS_DISPONIVEIS:
                if verificar_horario_disponivel(data.strftime('%Y-%m-%d'), hora):
                    horarios_disponiveis.append(hora)
            
            if horarios_disponiveis:
                hora = st.selectbox("Hora do Agendamento:*", horarios_disponiveis)
            else:
                st.warning("⚠️ Não há horários disponíveis nesta data!")
                hora = None
        
        # Segunda linha de campos
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📍 Taxa de Deslocamento")
            
            # Taxa de deslocamento
            taxa_deslocamento = st.selectbox(
                "Selecione a taxa de deslocamento:",
                list(TAXAS_DESLOCAMENTO.keys()),
                index=3  # Começa com "Sem taxa"
            )
            
            # Obter valor da taxa
            taxa_valor = TAXAS_DESLOCAMENTO[taxa_deslocamento]
            
            if taxa_valor > 0:
                st.info(f"**Taxa de deslocamento: R$ {taxa_valor:.2f}**")
            else:
                st.info("**Sem taxa de deslocamento**")
        
        with col2:
            # Sugerir valor padrão baseado no serviço
            valor_padrao = SERVICOS.get(servico, 0)
            
            # Campo de valor do serviço
            valor = st.number_input(
                "Valor do Serviço (R$):", 
                min_value=0.0, 
                step=10.0, 
                value=valor_padrao
            )
            
            # Calcular e mostrar valor total
            valor_total = valor + taxa_valor
            
            # Exibir resumo dos valores
            st.subheader("💰 Resumo do Valor")
            
            # Container para os valores
            with st.container(border=True):
                col_val1, col_val2 = st.columns(2)
                with col_val1:
                    st.metric("Serviço", f"R$ {valor:.2f}")
                with col_val2:
                    st.metric("Taxa", f"R$ {taxa_valor:.2f}")
                
                # Linha separadora
                st.markdown("---")
                
                # Valor total em destaque
                st.markdown(f"<h3 style='text-align: center; color: #4CAF50;'>TOTAL: R$ {valor_total:.2f}</h3>", 
                           unsafe_allow_html=True)
        
        # Terceira linha para observações
        observacoes = st.text_area("Observações:", height=100)
        
        st.caption("* Campos obrigatórios")
        
        # Botões dentro do formulário
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            submitted = st.form_submit_button("💾 Salvar Agendamento", type="primary")
        
        if submitted:
            if not cliente or not telefone or not servico or not data or not hora:
                st.error("⚠️ Por favor, preencha todos os campos obrigatórios!")
            else:
                novo_agendamento = {
                    'id': len(st.session_state.agendamentos) + 1,
                    'cliente': cliente,
                    'telefone': telefone,
                    'servico': servico,
                    'data': data.strftime('%Y-%m-%d'),
                    'hora': hora,
                    'valor': valor,
                    'taxa_deslocamento': taxa_valor,
                    'tipo_taxa': taxa_deslocamento,
                    'valor_total': valor_total,
                    'observacoes': observacoes if observacoes else None,
                    'data_cadastro': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                st.session_state.agendamentos.append(novo_agendamento)
                if salvar_agendamentos(st.session_state.agendamentos):
                    st.balloons()
                    st.success(f"✅ Agendamento para {cliente} salvo com sucesso!")
                    
                    # Mostrar resumo detalhado
                    with st.expander("📋 Detalhes do Agendamento", expanded=True):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Cliente:** {cliente}")
                            st.write(f"**Telefone:** {telefone}")
                            st.write(f"**Serviço:** {servico}")
                            st.write(f"**Data:** {formatar_data(data.strftime('%Y-%m-%d'))}")
                        with col2:
                            st.write(f"**Hora:** {hora}")
                            st.write(f"**Valor Serviço:** R$ {valor:.2f}")
                            if taxa_valor > 0:
                                st.write(f"**Taxa Deslocamento:** R$ {taxa_valor:.2f} ({taxa_deslocamento})")
                            else:
                                st.write("**Taxa Deslocamento:** Sem taxa")
                            st.write(f"**Valor Total:** R$ {valor_total:.2f}")
                    
                    # Limpar formulário usando rerun
                    st.rerun()
                else:
                    st.error("❌ Erro ao salvar agendamento!")

# FUNÇÃO: EDITAR AGENDAMENTO - CORRIGIDA (SEM CALLBACKS NO FORM)
elif opcao == "✏️ Editar":
    st.header("✏️ Editar Agendamento")
    
    if not st.session_state.agendamentos:
        st.info("📭 Nenhum agendamento para editar.")
    else:
        # Listar agendamentos para seleção
        opcoes = [f"{ag['cliente']} - {formatar_data(ag['data'])} {ag['hora']} ({ag['servico']})" 
                 for ag in st.session_state.agendamentos]
        
        selecionado = st.selectbox(
            "Selecione o agendamento para editar:",
            opcoes,
            index=None,
            placeholder="Escolha um agendamento..."
        )
        
        if selecionado:
            index_selecionado = opcoes.index(selecionado)
            agendamento_editar = st.session_state.agendamentos[index_selecionado]
            
            with st.form("form_editar_agendamento"):
                col1, col2 = st.columns(2)
                
                with col1:
                    cliente_edit = st.text_input(
                        "Nome do Cliente:", 
                        value=agendamento_editar['cliente']
                    )
                    telefone_edit = st.text_input(
                        "Telefone:", 
                        value=agendamento_editar['telefone']
                    )
                    servico_edit = st.selectbox(
                        "Serviço:", 
                        list(SERVICOS.keys()),
                        index=list(SERVICOS.keys()).index(agendamento_editar['servico']) if agendamento_editar['servico'] in SERVICOS else 0
                    )
                
                with col2:
                    # Converter string para datetime
                    data_original = datetime.strptime(agendamento_editar['data'], '%Y-%m-%d')
                    
                    data_edit = st.date_input(
                        "Data do Agendamento:", 
                        value=data_original
                    )
                    
                    # Horário atual do agendamento
                    hora_atual = agendamento_editar['hora']
                    
                    # Verificar horários disponíveis (incluindo o atual)
                    horarios_disponiveis = []
                    for hora in HORARIOS_DISPONIVEIS:
                        if hora == hora_atual or verificar_horario_disponivel(data_edit.strftime('%Y-%m-%d'), hora):
                            horarios_disponiveis.append(hora)
                    
                    hora_edit = st.selectbox(
                        "Hora do Agendamento:", 
                        horarios_disponiveis,
                        index=horarios_disponiveis.index(hora_atual) if hora_atual in horarios_disponiveis else 0
                    )
                
                # Segunda linha de campos
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("📍 Taxa de Deslocamento")
                    
                    # Obter tipo de taxa atual ou usar padrão
                    tipo_taxa_atual = agendamento_editar.get('tipo_taxa', 'Sem taxa')
                    if tipo_taxa_atual not in TAXAS_DESLOCAMENTO:
                        tipo_taxa_atual = 'Sem taxa'
                    
                    taxa_deslocamento_edit = st.selectbox(
                        "Selecione a taxa de deslocamento:",
                        list(TAXAS_DESLOCAMENTO.keys()),
                        index=list(TAXAS_DESLOCAMENTO.keys()).index(tipo_taxa_atual) if tipo_taxa_atual in TAXAS_DESLOCAMENTO else 3
                    )
                    
                    # Atualizar o valor da taxa
                    taxa_valor_edit = TAXAS_DESLOCAMENTO[taxa_deslocamento_edit]
                    
                    if taxa_valor_edit > 0:
                        st.info(f"**Taxa de deslocamento: R$ {taxa_valor_edit:.2f}**")
                    else:
                        st.info("**Sem taxa de deslocamento**")
                
                with col2:
                    # Campo de valor do serviço
                    valor_default = float(agendamento_editar.get('valor', 0)) if agendamento_editar.get('valor') else SERVICOS.get(agendamento_editar['servico'], 0)
                    
                    valor_edit = st.number_input(
                        "Valor do Serviço (R$):", 
                        value=valor_default,
                        min_value=0.0,
                        step=10.0
                    )
                    
                    # Calcular e mostrar valor total
                    valor_total_edit = valor_edit + taxa_valor_edit
                    
                    # Exibir resumo dos valores
                    st.subheader("💰 Resumo do Valor")
                    
                    # Container para os valores
                    with st.container(border=True):
                        col_val1, col_val2 = st.columns(2)
                        with col_val1:
                            st.metric("Serviço", f"R$ {valor_edit:.2f}")
                        with col_val2:
                            st.metric("Taxa", f"R$ {taxa_valor_edit:.2f}")
                        
                        # Linha separadora
                        st.markdown("---")
                        
                        # Valor total em destaque
                        st.markdown(f"<h3 style='text-align: center; color: #4CAF50;'>TOTAL: R$ {valor_total_edit:.2f}</h3>", 
                                   unsafe_allow_html=True)
                
                # Terceira linha para observações
                observacoes_edit = st.text_area(
                    "Observações:", 
                    value=agendamento_editar.get('observacoes', ''),
                    height=100
                )
                
                col1, col2, col3 = st.columns([1, 1, 2])
                with col1:
                    submitted_edit = st.form_submit_button("💾 Salvar Alterações", type="primary")
                with col2:
                    cancelar = st.form_submit_button("❌ Cancelar")
                
                if submitted_edit:
                    if not cliente_edit or not telefone_edit or not servico_edit:
                        st.error("⚠️ Por favor, preencha todos os campos obrigatórios!")
                    else:
                        # Atualizar agendamento
                        st.session_state.agendamentos[index_selecionado] = {
                            'id': agendamento_editar.get('id', index_selecionado + 1),
                            'cliente': cliente_edit,
                            'telefone': telefone_edit,
                            'servico': servico_edit,
                            'data': data_edit.strftime('%Y-%m-%d'),
                            'hora': hora_edit,
                            'valor': valor_edit,
                            'taxa_deslocamento': taxa_valor_edit,
                            'tipo_taxa': taxa_deslocamento_edit,
                            'valor_total': valor_total_edit,
                            'observacoes': observacoes_edit if observacoes_edit else None,
                            'data_cadastro': agendamento_editar.get('data_cadastro', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                            'data_edicao': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }
                        
                        if salvar_agendamentos(st.session_state.agendamentos):
                            st.success("✅ Agendamento atualizado com sucesso!")
                            
                            # Mostrar resumo detalhado
                            with st.expander("📋 Detalhes Atualizados", expanded=True):
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.write(f"**Cliente:** {cliente_edit}")
                                    st.write(f"**Telefone:** {telefone_edit}")
                                    st.write(f"**Serviço:** {servico_edit}")
                                    st.write(f"**Data:** {formatar_data(data_edit.strftime('%Y-%m-%d'))}")
                                with col2:
                                    st.write(f"**Hora:** {hora_edit}")
                                    st.write(f"**Valor Serviço:** R$ {valor_edit:.2f}")
                                    st.write(f"**Taxa Deslocamento:** R$ {taxa_valor_edit:.2f} ({taxa_deslocamento_edit})")
                                    st.write(f"**Valor Total:** R$ {valor_total_edit:.2f}")
                            
                            st.rerun()
                        else:
                            st.error("❌ Erro ao atualizar agendamento!")

# FUNÇÃO: EXCLUIR AGENDAMENTO
elif opcao == "🗑️ Excluir":
    st.header("🗑️ Excluir Agendamento")
    
    if not st.session_state.agendamentos:
        st.info("📭 Nenhum agendamento para excluir.")
    else:
        # Listar agendamentos para seleção
        opcoes = [f"{ag['cliente']} - {formatar_data(ag['data'])} {ag['hora']} ({ag['servico']})" 
                 for ag in st.session_state.agendamentos]
        
        selecionado = st.selectbox(
            "Selecione o agendamento para excluir:",
            opcoes,
            index=None,
            placeholder="Escolha um agendamento..."
        )
        
        if selecionado:
            index_selecionado = opcoes.index(selecionado)
            agendamento_excluir = st.session_state.agendamentos[index_selecionado]
            
            # Mostrar detalhes do agendamento selecionado
            st.warning("⚠️ Você está prestes a excluir o seguinte agendamento:")
            
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"*Cliente:* {agendamento_excluir['cliente']}")
                st.info(f"*Telefone:* {agendamento_excluir['telefone']}")
                st.info(f"*Data:* {formatar_data(agendamento_excluir['data'])}")
                st.info(f"*Serviço:* {agendamento_excluir['servico']}")
            with col2:
                st.info(f"*Hora:* {agendamento_excluir['hora']}")
                
                valor_servico = float(agendamento_excluir.get('valor', 0)) if agendamento_excluir.get('valor') else SERVICOS.get(agendamento_excluir['servico'], 0)
                st.info(f"*Valor Serviço:* R$ {valor_servico:.2f}")
                
                if agendamento_excluir.get('taxa_deslocamento') and float(agendamento_excluir['taxa_deslocamento']) > 0:
                    taxa_valor = float(agendamento_excluir['taxa_deslocamento'])
                    tipo_taxa = agendamento_excluir.get('tipo_taxa', 'Taxa de deslocamento')
                    st.info(f"*Taxa Deslocamento:* R$ {taxa_valor:.2f} ({tipo_taxa})")
                
                valor_total = obter_valor_agendamento(agendamento_excluir)
                st.info(f"*Valor Total:* R$ {valor_total:.2f}")
            
            # Confirmação de exclusão
            col1, col2, col3 = st.columns(3)
            with col1:
                confirmar = st.button("✅ Confirmar Exclusão", type="primary")
            with col2:
                cancelar = st.button("❌ Cancelar")
            
            if confirmar:
                # Remover agendamento
                agendamento_removido = st.session_state.agendamentos.pop(index_selecionado)
                
                if salvar_agendamentos(st.session_state.agendamentos):
                    st.error(f"🗑️ Agendamento de {agendamento_removido['cliente']} excluído com sucesso!")
                    st.rerun()
                else:
                    st.error("❌ Erro ao excluir agendamento!")
            elif cancelar:
                st.info("❌ Operação cancelada!")
                st.rerun()

# FUNÇÃO: PREÇOS
elif opcao == "🏷️ Preços":
    st.header("🏷️ Tabela de Preços e Taxas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💰 Serviços")
        tabela_precos = {
            "Serviço": list(SERVICOS.keys()),
            "Preço (R$)": [f"{preco:.2f}" for preco in SERVICOS.values()],
            "Duração": [
                "30 min",
                "45 min",
                "60 min",
                "90 min",
                "30 min",
                "60 min",
                "60 min",
                "3 horas"
            ]
        }
        
        df_precos = pd.DataFrame(tabela_precos)
        st.dataframe(df_precos, use_container_width=True, hide_index=True)
    
    with col2:
        st.subheader("📍 Taxas de Deslocamento")
        tabela_taxas = {
            "Zona": list(TAXAS_DESLOCAMENTO.keys()),
            "Taxa (R$)": [f"{taxa:.2f}" for taxa in TAXAS_DESLOCAMENTO.values()]
        }
        
        df_taxas = pd.DataFrame(tabela_taxas)
        st.dataframe(df_taxas, use_container_width=True, hide_index=True)
    
    # Calcular faturamento mensal estimado
    st.subheader("📊 Projeção de Faturamento")
    col1, col2, col3 = st.columns(3)
    with col1:
        dias_trabalhados = st.number_input("Dias trabalhados no mês:", min_value=1, max_value=31, value=22)
    with col2:
        clientes_dia = st.number_input("Média de clientes por dia:", min_value=1, value=5)
    with col3:
        taxa_media = st.number_input("Média taxa deslocamento (R$):", min_value=0.0, value=5.0, step=1.0)
    
    # Calcular projeção
    valor_medio_servico = sum(SERVICOS.values()) / len(SERVICOS)
    valor_total_medio = valor_medio_servico + taxa_media
    faturamento_estimado = valor_total_medio * clientes_dia * dias_trabalhados
    
    st.info(f"""
    **Projeção mensal:**
    - Valor médio por serviço: **R$ {valor_medio_servico:.2f}**
    - Média taxa deslocamento: **R$ {taxa_media:.2f}**
    - Ticket médio total: **R$ {valor_total_medio:.2f}**
    - Faturamento estimado: **R$ {faturamento_estimado:.2f}**
    - Meta diária: **R$ {(faturamento_estimado/dias_trabalhados):.2f}**
    """)

# Rodapé com informações
st.sidebar.markdown("---")
st.sidebar.info("""
**💅 Studio Isa Beauty**
*Sistema de Agendamento*

**📍 Taxas de Deslocamento:**
• ZN - Zona Norte: R$ 5,00
• ZL - Zona Leste: R$ 10,00
• ZS - Zona Sul: R$ 15,00
• Sem taxa: R$ 0,00

**Controle Financeiro:**
• Saldo do dia atual
• Histórico mensal
• Estatísticas de vendas
• Inclui taxas de deslocamento

Dados salvos em: *agendamentos_sobracelhas.json*
""")

# Mostrar estatísticas na sidebar
st.sidebar.markdown("### 📊 Estatísticas Rápidas")

if st.session_state.agendamentos:
    total = len(st.session_state.agendamentos)
    
    # Agendamentos de hoje
    hoje = datetime.now().strftime('%Y-%m-%d')
    saldo_hoje = calcular_saldo_dia(hoje)
    
    # Saldo do mês atual
    hoje_obj = datetime.now()
    saldo_mes = calcular_saldo_mes(hoje_obj.year, hoje_obj.month)
    
    # Clientes únicos
    df = pd.DataFrame(st.session_state.agendamentos)
    clientes_unicos = df['cliente'].nunique() if 'cliente' in df.columns else 0
    
    # Calcular total de taxas de deslocamento
    total_taxas = 0
    for ag in st.session_state.agendamentos:
        if ag.get('taxa_deslocamento'):
            total_taxas += float(ag['taxa_deslocamento'])
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.metric("Total", total, delta=None)
    with col2:
        st.metric("Clientes", clientes_unicos, delta=None)
    
    st.sidebar.metric("Saldo Hoje", f"R$ {saldo_hoje['saldo_total']:.2f}")
    st.sidebar.metric("Saldo Mês", f"R$ {saldo_mes['saldo_total']:.2f}")
    st.sidebar.metric("Total Taxas", f"R$ {total_taxas:.2f}")
else:
    st.sidebar.info("Nenhum agendamento cadastrado.")