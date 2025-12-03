"""
Dashboard de Monitoramento da Qualidade da Água
Desenvolvido com Streamlit
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database import get_all_data, extrair_local_categoria, converter_url_drive

# ==================== CONFIGURAÇÃO DA PÁGINA ====================
st.set_page_config(
    page_title="Monitoramento de Água - UNIFEI",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CSS CUSTOMIZADO ====================
st.markdown("""
    <style>
    .main {
        background-color: #f0f2f6;
    }
    .stMetric {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    h1 {
        color: #1f77b4;
        font-weight: 700;
        padding-bottom: 20px;
    }
    h2 {
        color: #2c3e50;
        font-weight: 600;
        padding-top: 20px;
    }
    h3 {
        color: #34495e;
        font-weight: 500;
    }
    .stPlotlyChart {
        background-color: white;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# ==================== CARREGAMENTO DOS DADOS ====================
@st.cache_data(ttl=300)  # Cache por 5 minutos
def load_data():
    """Carrega e processa os dados do banco"""
    df = get_all_data()
    df['local_categoria'] = df['descricao_local'].apply(extrair_local_categoria)
    df['url_foto_view'] = df['url_foto']. apply(converter_url_drive)
    df['data_hora'] = pd.to_datetime(df['data_hora'])
    return df

# ==================== CABEÇALHO ====================
st.title("💧 Dashboard de Monitoramento da Qualidade da Água")
st. markdown("### UNIFEI - Campus Itabira")
st.markdown("---")

# ==================== CARREGAMENTO E VALIDAÇÃO ====================
try:
    with st.spinner("Carregando dados do banco..."):
        df = load_data()
    
    if df.empty:
        st. error("⚠️ Nenhum dado encontrado no banco de dados!")
        st.stop()
    
except Exception as e:
    st. error(f"❌ Erro ao conectar ao banco de dados: {e}")
    st.info("💡 Verifique suas credenciais no arquivo `config.py`")
    st.stop()

# ==================== SIDEBAR - FILTROS ====================
st. sidebar.header("🔍 Filtros")
st.sidebar.markdown("---")

# Filtro por Local
locais_disponiveis = ['Todos'] + sorted(df['local_categoria'].unique(). tolist())
local_selecionado = st. sidebar.selectbox(
    "📍 Selecione o Local:",
    locais_disponiveis
)

# Filtro por Característica do pH
caracteristicas_ph = ['Todas'] + sorted(df['carac_ph'].unique().tolist())
ph_selecionado = st.sidebar.multiselect(
    "🧪 Característica do pH:",
    caracteristicas_ph,
    default=['Todas']
)

# Filtro por Data
st.sidebar.markdown("📅 **Período:**")
data_min = df['data_hora'].min(). date()
data_max = df['data_hora'].max().date()

col1, col2 = st. sidebar.columns(2)
with col1:
    data_inicio = st.date_input("De:", data_min, min_value=data_min, max_value=data_max)
with col2:
    data_fim = st.date_input("Até:", data_max, min_value=data_min, max_value=data_max)

st.sidebar.markdown("---")

# ==================== APLICAÇÃO DOS FILTROS ====================
df_filtrado = df.copy()

# Filtro de local
if local_selecionado != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['local_categoria'] == local_selecionado]

# Filtro de pH
if 'Todas' not in ph_selecionado:
    df_filtrado = df_filtrado[df_filtrado['carac_ph']. isin(ph_selecionado)]

# Filtro de data
df_filtrado = df_filtrado[
    (df_filtrado['data_hora']. dt.date >= data_inicio) &
    (df_filtrado['data_hora'].dt.date <= data_fim)
]

# ==================== MÉTRICAS PRINCIPAIS ====================
st.markdown("## 📊 Visão Geral")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("🧪 Total de Amostras", len(df_filtrado))

with col2:
    ph_medio = df_filtrado['ph'].mean()
    st.metric("pH Médio", f"{ph_medio:.2f}")

with col3:
    temp_media = df_filtrado['temp_agua_c'].mean()
    st.metric("🌡️ Temp. Água (°C)", f"{temp_media:.1f}")

with col4:
    turbidez_media = df_filtrado['turbidez_ntu'].mean()
    st.metric("🌫️ Turbidez Média (NTU)", f"{turbidez_media:.0f}")

with col5:
    umidade_media = df_filtrado['umidade_ar_perc'].mean()
    st.metric("💨 Umidade Média (%)", f"{umidade_media:.1f}")

st.markdown("---")

# ==================== GRÁFICOS ====================
if df_filtrado.empty:
    st.warning("⚠️ Nenhuma amostra encontrada com os filtros selecionados.")
else:
    # ========== LINHA 1: PIZZA E DISPERSÃO ==========
    col1, col2 = st. columns(2)
    
    with col1:
        st. markdown("### 🥧 Distribuição da Característica do pH")
        ph_counts = df_filtrado['carac_ph'].value_counts()
        fig_pizza = px.pie(
            values=ph_counts.values,
            names=ph_counts.index,
            color_discrete_sequence=px.colors.sequential.RdBu,
            hole=0.4
        )
        fig_pizza.update_traces(
            textposition='inside',
            textinfo='percent+label',
            textfont_size=14
        )
        fig_pizza.update_layout(
            showlegend=True,
            height=400,
            margin=dict(t=30, b=30, l=30, r=30)
        )
        st.plotly_chart(fig_pizza, use_container_width=True)
    
    with col2:
        st.markdown("### 📈 Temperatura vs Umidade do Ar")
        fig_dispersao = px.scatter(
            df_filtrado,
            x='temp_ar_c',
            y='umidade_ar_perc',
            color='carac_ph',
            size='ph',
            hover_data=['descricao_local', 'data_hora'],
            color_discrete_sequence=px.colors.qualitative.Set2,
            labels={
                'temp_ar_c': 'Temperatura do Ar (°C)',
                'umidade_ar_perc': 'Umidade do Ar (%)',
                'carac_ph': 'Característica pH'
            }
        )
        fig_dispersao.update_layout(height=400, margin=dict(t=30, b=30, l=30, r=30))
        st.plotly_chart(fig_dispersao, use_container_width=True)
    
    # ========== LINHA 2: BARRA E MAPA ==========
    col1, col2 = st. columns(2)
    
    with col1:
        st. markdown("### 📊 Quantidade de Amostras por Local")
        local_counts = df_filtrado['local_categoria'].value_counts(). reset_index()
        local_counts.columns = ['Local', 'Quantidade']
        
        fig_barra = px. bar(
            local_counts,
            x='Local',
            y='Quantidade',
            color='Quantidade',
            color_continuous_scale='Blues',
            text='Quantidade'
        )
        fig_barra.update_traces(textposition='outside')
        fig_barra.update_layout(
            height=400,
            showlegend=False,
            xaxis_title="Local",
            yaxis_title="Quantidade de Amostras",
            margin=dict(t=30, b=30, l=30, r=30)
        )
        st.plotly_chart(fig_barra, use_container_width=True)
    
    with col2:
        st. markdown("### 🗺️ Mapa de Amostras Coletadas")
        
        # Agrupa por localização e conta amostras
        mapa_data = df_filtrado.groupby(['latitude', 'longitude', 'descricao_local']).size(). reset_index(name='quantidade')
        
        fig_mapa = px.scatter_mapbox(
            mapa_data,
            lat='latitude',
            lon='longitude',
            size='quantidade',
            color='quantidade',
            hover_name='descricao_local',
            hover_data={'quantidade': True, 'latitude': ':.5f', 'longitude': ':. 5f'},
            color_continuous_scale='Viridis',
            size_max=30,
            zoom=15,
            height=400
        )
        fig_mapa.update_layout(
            mapbox_style="open-street-map",
            margin=dict(t=0, b=0, l=0, r=0)
        )
        st.plotly_chart(fig_mapa, use_container_width=True)
    
    # ========== LINHA 3: HISTOGRAMA E BOXPLOT ==========
    col1, col2 = st. columns(2)
    
    with col1:
        st. markdown("### 📉 Distribuição da Turbidez")
        fig_histograma = px.histogram(
            df_filtrado,
            x='turbidez_ntu',
            nbins=20,
            color_discrete_sequence=['#636EFA'],
            labels={'turbidez_ntu': 'Turbidez (NTU)', 'count': 'Frequência'}
        )
        fig_histograma.update_layout(
            height=400,
            showlegend=False,
            xaxis_title="Turbidez (NTU)",
            yaxis_title="Frequência",
            margin=dict(t=30, b=30, l=30, r=30)
        )
        st.plotly_chart(fig_histograma, use_container_width=True)
    
    with col2:
        st.markdown("### 📦 Boxplot de Temperaturas")
        
        # Preparar dados para boxplot
        temp_data = pd.DataFrame({
            'Temperatura': list(df_filtrado['temp_agua_c']) + list(df_filtrado['temp_ar_c']),
            'Tipo': ['Água'] * len(df_filtrado) + ['Ar'] * len(df_filtrado)
        })
        
        fig_boxplot = px.box(
            temp_data,
            x='Tipo',
            y='Temperatura',
            color='Tipo',
            color_discrete_map={'Água': '#3498db', 'Ar': '#e74c3c'},
            labels={'Temperatura': 'Temperatura (°C)'}
        )
        fig_boxplot.update_layout(
            height=400,
            showlegend=False,
            xaxis_title="Tipo de Temperatura",
            yaxis_title="Temperatura (°C)",
            margin=dict(t=30, b=30, l=30, r=30)
        )
        st.plotly_chart(fig_boxplot, use_container_width=True)
    
    st.markdown("---")
    
    # ==================== ANÁLISE TEXTUAL ====================
    st.markdown("## 📝 Análise Detalhada das Amostras")
    
    # Seletor de amostra
    amostras = df_filtrado. sort_values('data_hora', ascending=False)
    opcoes_amostras = [
        f"Amostra #{row['coleta_id']} - {row['data_hora'].strftime('%d/%m/%Y %H:%M')} - {row['descricao_local'][:50]}"
        for _, row in amostras.iterrows()
    ]
    
    if opcoes_amostras:
        amostra_selecionada = st.selectbox("Selecione uma amostra para ver os detalhes:", opcoes_amostras)
        
        # Extrair ID da amostra selecionada
        coleta_id = int(amostra_selecionada.split('#')[1]. split(' ')[0])
        amostra_data = df_filtrado[df_filtrado['coleta_id'] == coleta_id]. iloc[0]
        
        # Exibir detalhes
        col1, col2 = st. columns([2, 1])
        
        with col1:
            st. markdown(f"""
            #### 📍 Local: {amostra_data['descricao_local']}
            **🏢 Categoria:** {amostra_data['local_categoria']}  
            **📅 Data e Hora:** {amostra_data['data_hora'].strftime('%d/%m/%Y às %H:%M:%S')}  
            **📌 Coordenadas:** {amostra_data['latitude']}, {amostra_data['longitude']}
            
            ---
            
            #### 🧪 Dados da Amostra
            
            | Parâmetro | Valor | Classificação |
            |-----------|-------|---------------|
            | **pH** | {amostra_data['ph']} | {amostra_data['carac_ph']} |
            | **Turbidez** | {amostra_data['turbidez_ntu']} NTU | {'Alta' if amostra_data['turbidez_ntu'] > 100 else 'Baixa'} |
            | **Temperatura da Água** | {amostra_data['temp_agua_c']}°C | - |
            | **Temperatura do Ar** | {amostra_data['temp_ar_c']}°C | - |
            | **Umidade do Ar** | {amostra_data['umidade_ar_perc']}% | - |
            | **Ponto de Orvalho** | {amostra_data['ponto_orvalho_c']}°C | - |
            
            ---
            
            #### 🔬 Análise Química
            - **Concentração de H⁺:** {amostra_data['h_ion_conc']:.2e} mol/L
            - **Concentração de OH⁻:** {amostra_data['oh_ion_conc']:.2e} mol/L
            """)
        
        with col2:
            st.markdown("#### 📸 Foto da Amostra")
            if pd.notna(amostra_data['url_foto']):
                try:
                    st.image(amostra_data['url_foto_view'], use_container_width=True)
                    st.markdown(f"[🔗 Abrir imagem no Drive]({amostra_data['url_foto']})")
                except:
                    st.warning("⚠️ Não foi possível carregar a imagem.")
                    st.markdown(f"[🔗 Ver foto no Google Drive]({amostra_data['url_foto']})")
            else:
                st.info("Sem foto disponível para esta amostra.")
    
    st.markdown("---")
    
    # ==================== TABELA DE DADOS ====================
    st.markdown("## 📋 Tabela de Dados Filtrados")
    
    # Preparar colunas para exibição
    colunas_exibir = [
        'coleta_id', 'data_hora', 'local_categoria', 'descricao_local',
        'ph', 'carac_ph', 'turbidez_ntu', 'temp_agua_c', 'temp_ar_c', 'umidade_ar_perc'
    ]
    
    df_exibir = df_filtrado[colunas_exibir]. copy()
    df_exibir. columns = [
        'ID', 'Data/Hora', 'Categoria', 'Local',
        'pH', 'Característica pH', 'Turbidez (NTU)', 
        'Temp. Água (°C)', 'Temp. Ar (°C)', 'Umidade (%)'
    ]
    
    st.dataframe(
        df_exibir.sort_values('Data/Hora', ascending=False),
        use_container_width=True,
        hide_index=True
    )
    
    # Download dos dados
    csv = df_exibir.to_csv(index=False). encode('utf-8')
    st.download_button(
        label="📥 Download dos dados (CSV)",
        data=csv,
        file_name=f"amostras_agua_{data_inicio}_{data_fim}.csv",
        mime="text/csv"
    )

# ==================== RODAPÉ ====================
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #7f8c8d;'>
        <p>💧 Dashboard de Monitoramento da Qualidade da Água | UNIFEI - Campus Itabira</p>
        <p>Desenvolvido com Streamlit, Plotly e Python</p>
    </div>
""", unsafe_allow_html=True)