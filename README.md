# 💧 Dashboard de Monitoramento da Qualidade da Água

Dashboard interativo desenvolvido com Streamlit para visualização e análise de dados de amostras de água coletadas na UNIFEI - Campus Itabira.

## 📋 Funcionalidades

✅ **6 Tipos de Gráficos Interativos:**
- 🥧 Gráfico de Pizza: Distribuição da característica do pH
- 📈 Gráfico de Dispersão: Temperatura vs Umidade
- 📊 Gráfico de Barras: Quantidade de amostras por local
- 🗺️ Mapa Interativo: Visualização geográfica das coletas
- 📉 Histograma: Distribuição da turbidez
- 📦 Boxplot: Análise de temperaturas (água e ar)

✅ **Filtros Avançados:**
- Filtro por local (Anexo I, III, IV, Prédio 1, Prédio 2)
- Filtro por característica do pH (Ácido, Neutro, Básico)
- Filtro por período (data início e fim)

✅ **Análise Detalhada:**
- Visualização individual de cada amostra
- Dados químicos e físicos completos
- Fotos das amostras (integração com Google Drive)
- Tabela de dados com opção de download em CSV

## 🚀 Como subir o ambiente

### Configuração Inicial (primeira vez)

```bash
# 1. Entre no diretório do projeto
cd dashboard_amostras

# 2.  Ative o ambiente virtual
source bin/activate

# 3.  Instale as dependências
pip install -r requirements.txt

# 4. Configure o banco de dados
# Edite o arquivo config.py com suas credenciais:
nano config.py
```

### Configuração do Banco de Dados

1. Copie o arquivo de exemplo:
```bash
cp config.example.py config.py


2. Edite o arquivo `config.py` e altere as seguintes linhas:

```python
DB_CONFIG = {
    'host': 'localhost',        # ou IP do servidor
    'user': 'seu_usuario',      # ALTERE AQUI
    'password': 'sua_senha',    # ALTERE AQUI
    'database': 'monitoramento_agua',
    'charset': 'utf8mb4',
    'cursorclass': 'DictCursor'
}
```

### Executar o Dashboard

```bash
# 1. Ative o ambiente virtual (se não estiver ativo)
source bin/activate

# 2. Execute o dashboard
streamlit run app.py
```

O dashboard abrirá automaticamente em: `http://localhost:8501`

### Ao terminar

```bash
# Desative o ambiente virtual
deactivate
```

## 📁 Estrutura do Projeto

```
dashboard_amostras/
├── bin/                    # Executáveis do ambiente virtual
├── lib/                    # Bibliotecas do ambiente virtual
├── include/                # Headers do Python
├── config.py              # ⚙️ Configurações do banco de dados
├── database. py            # 🗄️ Módulo de conexão e queries
├── app.py                 # 🎯 Dashboard principal
├── requirements.txt       # 📦 Dependências do projeto
└── README.md             # 📖 Este arquivo
```

## 🗄️ Estrutura do Banco de Dados

O dashboard se conecta a um banco MySQL com as seguintes tabelas:

- **LOCAIS**: Dados dos pontos de coleta (latitude, longitude, descrição)
- **COLETAS**: Medições e dados das amostras
- **FOTOS**: Links para fotos no Google Drive

## 📊 Visualizações Disponíveis

### Métricas Principais
- Total de amostras coletadas
- pH médio
- Temperatura média da água
- Turbidez média
- Umidade média do ar

### Gráficos Interativos
Todos os gráficos são interativos e respondem aos filtros aplicados na sidebar.

### Análise Detalhada
Selecione qualquer amostra para ver:
- Localização e coordenadas
- Todos os parâmetros medidos
- Concentrações iônicas
- Foto da coleta

## 🔧 Troubleshooting

### Erro de Conexão com Banco de Dados

Se você receber erro de conexão:
1. Verifique se o MySQL está rodando
2. Confirme as credenciais no `config.py`
3.  Teste a conexão manualmente:

```bash
mysql -u seu_usuario -p -h localhost monitoramento_agua
```

### Imagens não carregam

As imagens do Google Drive podem ter problemas de permissão. Certifique-se que:
- Os arquivos estão com permissão de visualização pública
- Os links estão no formato correto

### Reinstalar dependências

```bash
pip install --force-reinstall -r requirements. txt
```

## 📦 Dependências

- **streamlit**: Framework para dashboards interativos
- **pandas**: Manipulação e análise de dados
- **plotly**: Visualizações interativas e gráficos
- **pymysql**: Conexão com banco de dados MySQL

