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
    html, body, [data-testid="stAppViewContainer"], . main {
        height: 100vh;
        overflow: hidden;
    }
    
    .  main {
        background-color: #f0f2f6;
        padding: 0.3rem 0.5rem;
        max-height: 100vh;
        overflow-y: auto;
    }
    
    . stMetric {
        background-color: white;
        padding: 6px;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    h1 {
        color: #1f77b4;
        font-weight: 700;
        padding-bottom: 5px;
        font-size: 1.5rem;
        margin: 0 0 0.3rem 0;
    }
    
    h2 {
        color: #2c3e50;
        font-weight: 600;
        padding-top: 5px;
        font-size: 1.1rem;
        margin: 0.2rem 0;
    }
    
    h3 {
        color: #34495e;
        font-weight: 500;
        font-size: 0.85rem;
        margin: 0.2rem 0;
    }
    
    .stPlotlyChart {
        background-color: white;
        border-radius: 8px;
        padding: 5px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    div[data-testid="stMetricValue"] {
        font-size: 1.1rem;
    }
    
    div[data-testid="stMetricLabel"] {
        font-size: 0.75rem;
    }
    
    . element-container {
        margin-bottom: 0.2rem;
    }
    
    [data-testid="column"] {
        padding: 0.15rem;
    }
    
    footer {
        display: none;
    }
    
    header[data-testid="stHeader"] {
        height: 2.5rem;
    }
    
    hr {
        margin: 0.5rem 0;
    }
    
    .stMarkdown {
        margin-bottom: 0.2rem;
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
    st.error(f"❌ Erro ao conectar ao banco de dados: {e}")
    st.info("💡 Verifique suas credenciais no arquivo `config.py`")
    st.stop()

# ==================== SIDEBAR - FILTROS ====================
st. sidebar.header("🔍 Filtros")
st.sidebar.markdown("---")

# Filtro por Local
locais_disponiveis = ['Todos'] + sorted(df['local_categoria'].unique().tolist())
local_selecionado = st. sidebar.selectbox(
    "📍 Local:",
    locais_disponiveis
)

# Filtro por Característica do pH
caracteristicas_ph = ['Todas'] + sorted(df['carac_ph'].unique().tolist())
ph_selecionado = st.sidebar. multiselect(
    "🧪 Característica do pH:",
    caracteristicas_ph,
    default=['Todas']
)

# Filtro por Data
st.sidebar.markdown("📅 **Período:**")
data_min = df['data_hora'].min().date()
data_max = df['data_hora'].max().date()

col1, col2 = st. sidebar.columns(2)
with col1:
    data_inicio = st.date_input("De:", data_min, min_value=data_min, max_value=data_max)
with col2:
    data_fim = st.date_input("Até:", data_max, min_value=data_min, max_value=data_max)

st. sidebar.markdown("---")
st.sidebar.info("💡 Clique nos gráficos para filtrar dados interativamente")

# ==================== APLICAÇÃO DOS FILTROS ====================
df_filtrado = df. copy()

if local_selecionado != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['local_categoria'] == local_selecionado]

if 'Todas' not in ph_selecionado:
    df_filtrado = df_filtrado[df_filtrado['carac_ph']. isin(ph_selecionado)]

df_filtrado = df_filtrado[
    (df_filtrado['data_hora'].dt.date >= data_inicio) &
    (df_filtrado['data_hora'].dt. date <= data_fim)
]

# ==================== MÉTRICAS PRINCIPAIS ====================
st. markdown("## Visão Geral")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("🧪 Total", len(df_filtrado))

with col2:
    ph_medio = df_filtrado['ph'].mean()
    st.metric("pH Médio", f"{ph_medio:.2f}")

with col3:
    temp_agua_media = df_filtrado['temp_agua_c'].mean()
    st.metric("Temp.  Água", f"{temp_agua_media:.1f}°C")

with col4:
    temp_ar_media = df_filtrado['temp_ar_c']. mean()
    st.metric("Temp. Ar", f"{temp_ar_media:.1f}°C")

with col5:
    umidade_media = df_filtrado['umidade_ar_perc'].mean()
    st.metric("Umidade", f"{umidade_media:.1f}%")

# ==================== GRÁFICOS ====================
if df_filtrado. empty:
    st.warning("⚠️ Nenhuma amostra encontrada com os filtros selecionados.")
else:
    # ========== LINHA 1: 3 GRÁFICOS ==========
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### pH")
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
            textfont_size=9
        )
        fig_pizza.update_layout(
            showlegend=True,
            height=220,
            margin=dict(t=5, b=5, l=5, r=5),
            legend=dict(font=dict(size=8))
        )
        st. plotly_chart(fig_pizza, use_container_width=True, key="pizza")
    
    with col2:
        st.markdown("### Locais")
        local_counts = df_filtrado['local_categoria']. value_counts(). reset_index()
        local_counts.columns = ['Local', 'Quantidade']
        
        fig_barra = px.bar(
            local_counts,
            x='Local',
            y='Quantidade',
            color='Quantidade',
            color_continuous_scale='Blues',
            text='Quantidade'
        )
        fig_barra.update_traces(textposition='outside', textfont_size=9)
        fig_barra.update_layout(
            height=220,
            showlegend=False,
            xaxis_title="",
            yaxis_title="Qtd",
            margin=dict(t=5, b=5, l=5, r=5),
            font=dict(size=9),
            xaxis=dict(tickangle=-45)
        )
        st.plotly_chart(fig_barra, use_container_width=True, key="barra")
    
    with col3:
        st.markdown("### Temp x Umidade")
        fig_dispersao = px.scatter(
            df_filtrado,
            x='temp_ar_c',
            y='umidade_ar_perc',
            color='carac_ph',
            size='ph',
            hover_data=['descricao_local'],
            color_discrete_sequence=px.colors.qualitative.Set2,
            labels={
                'temp_ar_c': 'Temp (°C)',
                'umidade_ar_perc': 'Umidade (%)',
                'carac_ph': 'pH'
            }
        )
        fig_dispersao.update_layout(
            height=220,
            margin=dict(t=5, b=5, l=5, r=5),
            legend=dict(orientation="h", yanchor="bottom", y=-0.6, font=dict(size=8)),
            font=dict(size=9)
        )
        st.plotly_chart(fig_dispersao, use_container_width=True, key="dispersao")
    
    # ========== LINHA 2: 3 GRÁFICOS ==========
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### Mapa")
        mapa_data = df_filtrado.groupby(['latitude', 'longitude', 'descricao_local', 'local_categoria']).size().reset_index(name='quantidade')
        
        fig_mapa = px.scatter_mapbox(
            mapa_data,
            lat='latitude',
            lon='longitude',
            size='quantidade',
            color='local_categoria',
            hover_name='descricao_local',
            hover_data={'quantidade': True, 'latitude': ':.5f', 'longitude': ':.5f'},
            color_discrete_sequence=px.colors.qualitative. Set3,
            size_max=25,
            zoom=15,
            height=220
        )
        fig_mapa.update_layout(
            mapbox_style="open-street-map",
            margin=dict(t=0, b=0, l=0, r=0),
            legend=dict(font=dict(size=7))
        )
        st. plotly_chart(fig_mapa, use_container_width=True, key="mapa")
    
    with col2:
        st.markdown("### Turbidez")
        fig_histograma = px.histogram(
            df_filtrado,
            x='turbidez_ntu',
            nbins=15,
            color_discrete_sequence=['#636EFA'],
            labels={'turbidez_ntu': 'Turbidez (NTU)', 'count': 'Freq'}
        )
        fig_histograma.update_layout(
            height=220,
            showlegend=False,
            xaxis_title="Turbidez (NTU)",
            yaxis_title="Freq",
            margin=dict(t=5, b=5, l=5, r=5),
            font=dict(size=9)
        )
        st.plotly_chart(fig_histograma, use_container_width=True, key="histograma")
    
    with col3:
        st.markdown("### Temperaturas")
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
            labels={'Temperatura': 'Temp (°C)'}
        )
        fig_boxplot.update_layout(
            height=220,
            showlegend=False,
            xaxis_title="",
            yaxis_title="Temp (°C)",
            margin=dict(t=5, b=5, l=5, r=5),
            font=dict(size=9)
        )
        st.plotly_chart(fig_boxplot, use_container_width=True, key="boxplot")