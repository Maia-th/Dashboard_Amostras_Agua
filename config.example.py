"""
Configurações do banco de dados - EXEMPLO
Copie este arquivo para config.py e preencha com suas credenciais
"""

DB_CONFIG = {
    'host': 'localhost',           # ou IP do servidor MySQL
    'user': 'seu_usuario_aqui',    # ALTERE: usuário do MySQL
    'password': 'sua_senha_aqui',  # ALTERE: senha do MySQL
    'database': 'monitoramento_agua',
    'charset': 'utf8mb4',
    'cursorclass': 'DictCursor'
}