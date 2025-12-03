"""
Dashboard de Monitoramento da Qualidade da Água
Desenvolvido com Streamlit - Página Principal
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
st. markdown("""
    <style>
    .main {
        background-color: #f0f2f6;
    }
    . stMetric {
        background-color: white;
        padding: 10px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    h1 {
        color: #1f77b4;
        font-weight: 700;
        padding-bottom: 10px;
        font-size: 2rem;
    }
    h2 {
        color: #2c3e50;
        font-weight: 600;
        padding-top: 10px;
        font-size: 1.5rem;
    }
    h3 {
        color: #34495e;
        font-weight: 500;
        font-size: 1.2rem;
    }
    . stPlotlyChart {
        background-color: white;
        border-radius: 10px;
        padding: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# ==================== CARREGAMENTO DOS DADOS ====================
@st.cache_data(ttl=300)
def load_data():
    """Carrega e processa os dados do banco"""
    df = get_all_data()
    df['local_categoria'] = df['descricao_local'].apply(extrair_local_categoria)
    df['url_foto_view'] = df['url_foto'].apply(converter_url_drive)
    return df

# ==================== CABEÇALHO ====================
st.title("💧 Dashboard de Monitoramento da Qualidade da Água")

# ==================== CARREGAMENTO E VALIDAÇÃO ====================
try:
    with st.spinner("Carregando dados do banco..."):
        df = load_data()
    
    if df.empty:
        st.error("⚠️ Nenhum dado encontrado no banco de dados!")
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
    "📍 Local:",
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
st.sidebar.info("💡 Acesse **Detalhes das Amostras** no menu lateral para análises individuais")

# ==================== APLICAÇÃO DOS FILTROS ====================
df_filtrado = df. copy()

if local_selecionado != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['local_categoria'] == local_selecionado]

if 'Todas' not in ph_selecionado:
    df_filtrado = df_filtrado[df_filtrado['carac_ph']. isin(ph_selecionado)]

df_filtrado = df_filtrado[
    (df_filtrado['data_hora']. dt.date >= data_inicio) &
    (df_filtrado['data_hora'].dt.date <= data_fim)
]

# ==================== MÉTRICAS PRINCIPAIS ====================
st.markdown("## 📊 Visão Geral")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("🧪 Total", len(df_filtrado))

with col2:
    ph_medio = df_filtrado['ph']. mean()
    st.metric("pH Médio", f"{ph_medio:.2f}")

with col3:
    temp_media = df_filtrado['temp_agua_c'].mean()
    st.metric("Temp. Água", f"{temp_media:.1f}°C")

with col4:
    turbidez_media = df_filtrado['turbidez_ntu'].mean()
    st.metric("Turbidez", f"{turbidez_media:.0f} NTU")

with col5:
    umidade_media = df_filtrado['umidade_ar_perc'].mean()
    st. metric("Umidade", f"{umidade_media:.1f}%")

st.markdown("---")

# ==================== GRÁFICOS ====================
if df_filtrado.empty:
    st.warning("⚠️ Nenhuma amostra encontrada com os filtros selecionados.")
else:
    # ========== LINHA 1: PIZZA E DISPERSÃO ==========
    col1, col2 = st. columns(2)
    
    with col1:
        st.markdown("### 🥧 Característica do pH")
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
            textfont_size=12
        )
        fig_pizza.update_layout(
            showlegend=True,
            height=300,
            margin=dict(t=10, b=10, l=10, r=10)
        )
        st.plotly_chart(fig_pizza, use_container_width=True)
    
    with col2:
        st.markdown("### 📈 Temperatura vs Umidade")
        fig_dispersao = px.scatter(
            df_filtrado,
            x='temp_ar_c',
            y='umidade_ar_perc',
            color='carac_ph',
            size='ph',
            hover_data=['descricao_local'],
            color_discrete_sequence=px.colors.qualitative.Set2,
            labels={
                'temp_ar_c': 'Temperatura (°C)',
                'umidade_ar_perc': 'Umidade (%)',
                'carac_ph': 'pH'
            }
        )
        fig_dispersao.update_layout(
            height=300,
            margin=dict(t=10, b=10, l=10, r=10),
            legend=dict(orientation="h", yanchor="bottom", y=-0.3)
        )
        st.plotly_chart(fig_dispersao, use_container_width=True)
    
    # ========== LINHA 2: BARRA E MAPA ==========
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Amostras por Local")
        local_counts = df_filtrado['local_categoria'].value_counts(). reset_index()
        local_counts.columns = ['Local', 'Quantidade']
        
        fig_barra = px.bar(
            local_counts,
            x='Local',
            y='Quantidade',
            color='Quantidade',
            color_continuous_scale='Blues',
            text='Quantidade'
        )
        fig_barra.update_traces(textposition='outside')
        fig_barra.update_layout(
            height=300,
            showlegend=False,
            xaxis_title="",
            yaxis_title="Quantidade",
            margin=dict(t=10, b=10, l=10, r=10)
        )
        st.plotly_chart(fig_barra, use_container_width=True)
    
    with col2:
        st.markdown("### 🗺️ Mapa de Coletas")
        mapa_data = df_filtrado.groupby(['latitude', 'longitude', 'descricao_local']).size().reset_index(name='quantidade')
        
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
            height=300
        )
        fig_mapa.update_layout(
            mapbox_style="open-street-map",
            margin=dict(t=0, b=0, l=0, r=0)
        )
        st.plotly_chart(fig_mapa, use_container_width=True)
    
    # ========== LINHA 3: HISTOGRAMA E BOXPLOT ==========
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📉 Distribuição da Turbidez")
        fig_histograma = px.histogram(
            df_filtrado,
            x='turbidez_ntu',
            nbins=20,
            color_discrete_sequence=['#636EFA'],
            labels={'turbidez_ntu': 'Turbidez (NTU)', 'count': 'Frequência'}
        )
        fig_histograma.update_layout(
            height=300,
            showlegend=False,
            xaxis_title="Turbidez (NTU)",
            yaxis_title="Frequência",
            margin=dict(t=10, b=10, l=10, r=10)
        )
        st.plotly_chart(fig_histograma, use_container_width=True)
    
    with col2:
        st.markdown("### 📦 Boxplot de Temperaturas")
        temp_data = pd.DataFrame({
            'Temperatura': list(df_filtrado['temp_agua_c']) + list(df_filtrado['temp_ar_c']),
            'Tipo': ['Água'] * len(df_filtrado) + ['Ar'] * len(df_filtrado)
        })
        
        fig_boxplot = px. box(
            temp_data,
            x='Tipo',
            y='Temperatura',
            color='Tipo',
            color_discrete_map={'Água': '#3498db', 'Ar': '#e74c3c'},
            labels={'Temperatura': 'Temperatura (°C)'}
        )
        fig_boxplot.update_layout(
            height=300,
            showlegend=False,
            xaxis_title="",
            yaxis_title="Temperatura (°C)",
            margin=dict(t=10, b=10, l=10, r=10)
        )
        st.plotly_chart(fig_boxplot, use_container_width=True)

# ==================== RODAPÉ ====================
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #7f8c8d; font-size: 0. 9rem;'>
        <p>💧 Dashboard de Monitoramento da Qualidade da Água | UNIFEI - Campus Itabira</p>
    </div>
""", unsafe_allow_html=True)