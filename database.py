"""
Módulo para gerenciar conexão e consultas ao banco de dados
"""
import pymysql
import pandas as pd
from config import DB_CONFIG

def get_connection():
    """Cria e retorna uma conexão com o banco de dados"""
    try:
        connection = pymysql.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database'],
            charset=DB_CONFIG['charset']
        )
        return connection
    except Exception as e:
        raise Exception(f"Erro ao conectar ao banco de dados: {e}")

def get_all_data():
    """Busca todos os dados necessários do banco"""
    query = """
    SELECT 
        c.coleta_id,
        c.data_hora,
        c.descricao_amostra,
        c.ph,
        c.carac_ph,
        c. turbidez_ntu,
        c.temp_agua_c,
        c.temp_ar_c,
        c.umidade_ar_perc,
        c.h_ion_conc,
        c.oh_ion_conc,
        c.ponto_orvalho_c,
        l.latitude,
        l.longitude,
        l.descricao_local,
        f.url_foto
    FROM COLETAS c
    INNER JOIN LOCAIS l ON c.local_id = l.local_id
    LEFT JOIN FOTOS f ON c.coleta_id = f.coleta_id
    ORDER BY c.data_hora DESC
    """
    
    connection = get_connection()
    try:
        df = pd.read_sql(query, connection)
        df['data_hora'] = pd.to_datetime(df['data_hora'])
        return df
    except Exception as e:
        raise Exception(f"Erro ao buscar dados: {e}")
    finally:
        connection.close()

def extrair_local_categoria(descricao):
    """Extrai a categoria do local baseado na descrição - com correspondência exata"""
    if pd.isna(descricao):
        return 'Outros'
    
    descricao_lower = str(descricao).lower()
    
    if 'anexo iii' in descricao_lower or 'anexo 3' in descricao_lower:
        return 'Anexo III'
    elif 'anexo iv' in descricao_lower or 'anexo 4' in descricao_lower:
        return 'Anexo IV'
    elif 'anexo ii' in descricao_lower or 'anexo 2' in descricao_lower:
        return 'Anexo II'
    elif 'anexo i' in descricao_lower or 'anexo 1' in descricao_lower:
        return 'Anexo I'
    elif 'predio 2' in descricao_lower or 'prédio 2' in descricao_lower or 'torre 2' in descricao_lower:
        return 'Prédio 2'
    elif 'predio 1' in descricao_lower or 'prédio 1' in descricao_lower:
        return 'Prédio 1'
    else:
        return 'Outros'

def converter_url_drive(url):
    """Converte URL do Google Drive para formato de visualização direta"""
    if pd.isna(url):
        return None
    
    url_str = str(url)
    if 'drive.google.com' in url_str and 'id=' in url_str:
        file_id = url_str.split('id=')[1].split('&')[0]
        return f"https://drive.google.com/uc? export=view&id={file_id}"
    return url_str