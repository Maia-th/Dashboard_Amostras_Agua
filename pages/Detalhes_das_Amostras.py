"""
Página de Detalhes das Amostras
Análise individual de cada coleta
"""
import streamlit as st
import pandas as pd
import sys
sys.path.append('..')
from database import get_all_data, extrair_local_categoria, converter_url_drive

st.set_page_config(page_title="Detalhes das Amostras", page_icon="📋", layout="wide")

st.markdown("""<style>
/* Forçar altura 100vh e remover scroll */
html, body, [data-testid="stAppViewContainer"], . main {
    height: 100vh;
    overflow: hidden;
}

. main {
    background-color: #f0f2f6; 
    padding: 0. 3rem 0.5rem;
    max-height: 100vh;
    overflow-y: auto;
}

/* Reduzir espaçamentos para caber tudo */
h1 {
    color: #1f77b4; 
    font-weight: 700; 
    font-size: 1.4rem; 
    margin: 0 0 0.2rem 0;
    padding: 0;
}

h2 {
    color: #2c3e50; 
    font-weight: 600; 
    font-size: 1rem; 
    margin: 0. 2rem 0;
}

h3 {
    color: #34495e; 
    font-weight: 500; 
    font-size: 0.9rem; 
    margin: 0.2rem 0;
}

.stMetric {
    background-color: white; 
    padding: 5px; 
    border-radius: 6px; 
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

div[data-testid="stMetricValue"] {
    font-size: 0.95rem;
}

div[data-testid="stMetricLabel"] {
    font-size: 0.75rem;
}

. info-box {
    background-color: white; 
    padding: 8px; 
    border-radius: 6px; 
    box-shadow: 0 1px 3px rgba(0,0,0,0.1); 
    margin-bottom: 6px; 
    font-size: 0.85rem;
}

/* Reduzir espaçamento entre elementos */
.element-container {
    margin-bottom: 0.3rem;
}

/* Compactar colunas */
[data-testid="column"] {
    padding: 0.2rem;
}

/* Remover rodapé extra */
footer {
    display: none;
}

/* Compactar header do streamlit */
header[data-testid="stHeader"] {
    height: 2.5rem;
}
</style>""", unsafe_allow_html=True)

@st.cache_data(ttl=300)
def load_data():
    df = get_all_data()
    df['local_categoria'] = df['descricao_local'].apply(extrair_local_categoria)
    df['url_foto_view'] = df['url_foto'].apply(converter_url_drive)
    return df

try:
    df = load_data()
    if df.empty:
        st. error("⚠️ Nenhum dado encontrado!")
        st.stop()
except Exception as e:
    st. error(f"❌ Erro: {e}")
    st.stop()

# ==================== SIDEBAR ====================
with st.sidebar:
    ordem_locais = ['Prédio 1', 'Prédio 2', 'Anexo I', 'Anexo III', 'Anexo IV', 'Outros']
    df['local_categoria_ordered'] = pd.Categorical(df['local_categoria'], categories=ordem_locais, ordered=True)
    df_ordenado = df.sort_values(['local_categoria_ordered', 'coleta_id'])
    
    opcoes_amostras = []
    for local in ordem_locais:
        amostras_local = df_ordenado[df_ordenado['local_categoria'] == local]
        if not amostras_local.empty:
            opcoes_amostras. append(f"━━━━━━ {local} ━━━━━━")
            for _, row in amostras_local.iterrows():
                opcao = f"  #{row['coleta_id']:02d} | {row['data_hora'].strftime('%d/%m/%Y %H:%M')} | {row['descricao_local'][:40]}"
                opcoes_amostras.append(opcao)
    
    st.header("🔍 Selecione uma amostra:")

    if opcoes_amostras:
        amostra_selecionada = st.selectbox(
            "Amostra",
            opcoes_amostras,
            label_visibility="collapsed"
        )

    st.markdown("---")

    if amostra_selecionada. startswith('━'):
        st.info("👆 Selecione uma amostra específica acima")    

# ==================== CONTEÚDO PRINCIPAL ====================

st.title("📋 Detalhes das Amostras")

if amostra_selecionada. startswith('━'):
    st.markdown("""
    <div style='display: flex; flex-direction: column; align-items: center; justify-content: center; height: 70vh; text-align: center;'>
        <div style='font-size: 5rem; margin-bottom: 1rem;'>🔍</div>
        <div style='font-size: 1.5rem; color: #666; margin-bottom: 0.5rem;'>Escolha uma amostra para exibir os dados</div>
        <div style='font-size: 1rem; color: #999;'>Selecione uma amostra específica na barra lateral</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

if not amostra_selecionada.startswith('━'):
    coleta_id = int(amostra_selecionada.split('#')[1]. split(' ')[0])
    amostra = df[df['coleta_id'] == coleta_id]. iloc[0]
    
    # ========== LAYOUT: DADOS | FOTO ==========
    col_dados, col_foto = st. columns([2.5, 1])
    
    with col_dados:
        # ========== INFORMAÇÕES DA COLETA ==========
        st.markdown("### 📍 Informações da Coleta")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.markdown(f"""<div class='info-box'>
            <strong>🆔 ID:</strong><br>
            #{amostra['coleta_id']}
            </div>""", unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""<div class='info-box'>
            <strong>📅 Data:</strong><br>
            {amostra['data_hora'].strftime('%d/%m/%Y')}
            </div>""", unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""<div class='info-box'>
            <strong>🕐 Hora:</strong><br>
            {amostra['data_hora'].strftime('%H:%M:%S')}
            </div>""", unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""<div class='info-box'>
            <strong>🏢 Categoria:</strong><br>
            {amostra['local_categoria']}
            </div>""", unsafe_allow_html=True)
        
        with col5:
            st.markdown(f"""<div class='info-box'>
            <strong>🌍 Coordenadas:</strong><br>
            {amostra['latitude']}, {amostra['longitude']}
            </div>""", unsafe_allow_html=True)
        
        # Descrição do local e da amostra
        col_desc1, col_desc2 = st.columns(2)
        
        with col_desc1:
            st.markdown(f"""<div class='info-box'>
            <strong>📌 Descrição do Local:</strong><br>
            {amostra['descricao_local']}
            </div>""", unsafe_allow_html=True)
        
        with col_desc2:
            descricao_amostra = amostra['descricao_amostra'] if pd.notna(amostra. get('descricao_amostra')) else "Sem descrição"
            st.markdown(f"""<div class='info-box'>
            <strong>📝 Descrição da Amostra:</strong><br>
            {descricao_amostra}
            </div>""", unsafe_allow_html=True)
        
        st.markdown("")
        
        # ========== DADOS COLETADOS ==========
        st. markdown("### 🧪 Dados Coletados")
        
        col_a, col_b, col_c, col_d = st.columns(4)
        
        ph_val = float(amostra['ph'])
        temp_agua_val = float(amostra['temp_agua_c'])
        temp_ar_val = float(amostra['temp_ar_c'])
        umidade_val = float(amostra['umidade_ar_perc'])
        turbidez_val = int(amostra['turbidez_ntu'])
        
        with col_a:
            st.metric("pH", f"{ph_val:.2f}")
            st.metric("Temp.  Água", f"{temp_agua_val:.1f} °C")
        
        with col_b:
            st.metric("Característica", amostra['carac_ph'])
            st.metric("Temp. Ar", f"{temp_ar_val:.1f} °C")
        
        with col_c:
            st.metric("Turbidez", f"{turbidez_val} NTU")
            st.metric("Umidade Ar", f"{umidade_val:.1f} %")
        
        with col_d:
            classificacao = "Alta" if turbidez_val > 100 else "Baixa"
            st.metric("Classe Turbidez", classificacao)
        
        st.markdown("")
        
        # ========== PROPRIEDADES ABSTRAÍDAS DAS COLETAS ==========
        st.markdown("### 🔬 Propriedades Abstraídas das Coletas")
        
        col_i1, col_i2, col_i3 = st.columns(3)
        
        h_conc = float(amostra['h_ion_conc'])
        oh_conc = float(amostra['oh_ion_conc'])
        orvalho_val = float(amostra['ponto_orvalho_c'])
        
        with col_i1:
            st. markdown(f"""<div class='info-box'>
            <strong>Concentração ácida (H⁺):</strong><br>
            <span style='font-size: 1.05rem; color: #2c3e50;'>{h_conc:.2e} mol/L</span>
            </div>""", unsafe_allow_html=True)
        
        with col_i2:
            st.markdown(f"""<div class='info-box'>
            <strong>Concentração básica (OH⁻):</strong><br>
            <span style='font-size: 1.05rem; color: #2c3e50;'>{oh_conc:.2e} mol/L</span>
            </div>""", unsafe_allow_html=True)
        
        with col_i3:
            st.markdown(f"""<div class='info-box'>
            <strong>Ponto de Orvalho:</strong><br>
            <span style='font-size: 1.05rem; color: #2c3e50;'>{orvalho_val:.1f} °C</span>
            </div>""", unsafe_allow_html=True)
        
        st.markdown("")
        
        # ========== CLASSIFICAÇÕES ==========
        st.markdown("### ⚡ Classificações")
        
        col_c1, col_c2, col_c3 = st. columns(3)
        
        with col_c1:
            if amostra['carac_ph'] == 'Neutro':
                st.success("✅ pH Neutro")
            elif amostra['carac_ph'] == 'Ácido':
                st.error("🔴 pH Ácido")
            else:
                st.info("🔵 pH Básico")
        
        with col_c2:
            if turbidez_val > 100:
                st.warning("⚠️ Turbidez Alta")
            else:
                st.success("✅ Turbidez Normal")
        
        with col_c3:
            if temp_agua_val > 25:
                st.warning("🌡️ Água Aquecida")
            else:
                st.success("❄️ Temperatura Normal")
    
    with col_foto:
        st. markdown("### 📸 Registro Fotográfico")
        
        if pd.notna(amostra['url_foto']):
            url_foto = str(amostra['url_foto'])
            
            # Extrair ID do Google Drive
            file_id = None
            if 'drive.google.com' in url_foto:
                if 'id=' in url_foto:
                    file_id = url_foto.split('id=')[1]. split('&')[0]
                elif '/d/' in url_foto:
                    file_id = url_foto.split('/d/')[1]. split('/')[0]
            
            if file_id:
                # Usar thumbnail do Google Drive
                url_thumbnail = f"https://drive.google.com/thumbnail?id={file_id}&sz=w500"
                
                try:
                    st.image(url_thumbnail, use_container_width=True, caption=f"Amostra #{amostra['coleta_id']}")
                except:
                    st.warning("⚠️ Não foi possível carregar a imagem.")
                
                st.markdown(f"[🔗 Abrir foto no Google Drive](https://drive.google.com/file/d/{file_id}/view)")
            else:
                st.error("❌ URL da foto inválida")
                st.markdown(f"[🔗 Ver link]({url_foto})")
        else:
            st.info("📷 Sem foto disponível para esta amostra")