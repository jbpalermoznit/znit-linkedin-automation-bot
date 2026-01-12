"""
Arquivo de Configuração - EXEMPLO
Copie este arquivo para config.py e preencha com suas informações

IMPORTANTE: 
- O arquivo config.py está no .gitignore e NÃO será commitado
- NUNCA commite suas credenciais reais no Git
"""

# ============================================
# CREDENCIAIS DO LINKEDIN
# ============================================

# Suas credenciais do LinkedIn
LINKEDIN_EMAIL = "seu_email@example.com"
LINKEDIN_PASSWORD = "sua_senha_segura_aqui"

# ⚠️ DICA DE SEGURANÇA:
# 1. Copie este arquivo: cp config.example.py config.py
# 2. Edite config.py com suas credenciais reais
# 3. config.py está no .gitignore e não será commitado


# ============================================
# CONFIGURAÇÕES DO BOT SIMPLES
# ============================================

# Modo de operação
# Opções: "convites", "convites_com_mensagem", "mensagens"
BOT_MODO = "convites_com_mensagem"

# Arquivos
BOT_ARQUIVO_URLS = "urls.csv"
BOT_ARQUIVO_TEMPLATE = "template.txt"
BOT_ARQUIVO_LOG = "log_envios.csv"

# Limites de segurança
BOT_DELAY_MIN = 3  # segundos mínimos entre ações
BOT_DELAY_MAX = 7  # segundos máximos entre ações
BOT_MAX_CONVITES = 50  # máximo de ações por execução
BOT_TIMEOUT = 15  # timeout para elementos da página


# ============================================
# CONFIGURAÇÕES DO BOT IA
# ============================================

# Modo de operação IA
# Opções: "convites", "convites_com_mensagem_ia", "mensagens_ia"
BOT_IA_MODO = "convites_com_mensagem_ia"

# Usar IA para gerar mensagens
BOT_IA_USE_IA = True  # True = usa IA | False = usa template simples

# API da Anthropic (Claude)
# Obtenha sua chave em: https://console.anthropic.com/
ANTHROPIC_API_KEY = "sk-ant-..."  # Sua API key aqui

# Arquivos
BOT_IA_ARQUIVO_URLS = "urls.csv"
BOT_IA_ARQUIVO_LOG = "log_envios_ia.csv"
BOT_IA_ARQUIVO_PERFIS = "perfis_extraidos.json"

# Limites de segurança (mais lento por causa da extração)
BOT_IA_DELAY_MIN = 4
BOT_IA_DELAY_MAX = 8
BOT_IA_MAX_CONVITES = 50
BOT_IA_TIMEOUT = 15

# Template base para IA (personalizável)
BOT_IA_TEMPLATE_BASE = """
Contexto: Você é um profissional fazendo networking no LinkedIn.
Escreva uma mensagem curta e personalizada para conectar com {nome}.

Informações do perfil:
- Nome: {nome}
- Título/Cargo atual: {titulo}
- Empresa atual: {empresa}
- Localização: {localizacao}
- Sobre: {sobre}
- Experiências recentes: {experiencias}

Diretrizes:
1. Seja genuíno e específico
2. Mencione algo do perfil da pessoa
3. Explique brevemente por que quer conectar
4. Mantenha tom profissional mas amigável
5. Máximo 250 caracteres (convite) ou 500 caracteres (mensagem)
6. Não use emojis
7. Escreva em português do Brasil

Responda APENAS com a mensagem, sem explicações adicionais.
"""


# ============================================
# CONFIGURAÇÕES AVANÇADAS
# ============================================

# Navegador
BROWSER_HEADLESS = False  # True = sem interface gráfica
BROWSER_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Logging
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_CONSOLE = True  # Mostrar logs no console
LOG_FILE = True  # Salvar logs em arquivo

# Retry
RETRY_MAX_ATTEMPTS = 3  # Tentativas em caso de erro
RETRY_DELAY = 5  # Segundos entre tentativas


# ============================================
# SEGMENTAÇÃO (OPCIONAL)
# ============================================

# Filtros para perfis (todos opcionais)
FILTERS = {
    "min_connections": 100,  # Mínimo de conexões
    "locations": ["Brazil", "Portugal"],  # Localizações permitidas
    "companies": [],  # Lista de empresas (vazio = todas)
    "job_titles": [],  # Lista de cargos (vazio = todos)
}


# ============================================
# NOTIFICAÇÕES (FUTURO)
# ============================================

# Email (para receber notificações)
NOTIFICATION_EMAIL_ENABLED = False
NOTIFICATION_EMAIL_FROM = "bot@example.com"
NOTIFICATION_EMAIL_TO = "seu_email@example.com"
NOTIFICATION_EMAIL_SMTP = "smtp.gmail.com"
NOTIFICATION_EMAIL_PORT = 587

# Webhook
NOTIFICATION_WEBHOOK_ENABLED = False
NOTIFICATION_WEBHOOK_URL = "https://hooks.slack.com/services/..."


# ============================================
# NOTAS
# ============================================

"""
COMO USAR ESTE ARQUIVO:

1. Copie para config.py:
   cp config.example.py config.py

2. Edite config.py com suas configurações:
   nano config.py

3. Importe no bot:
   from config import *

4. NUNCA commite config.py (já está no .gitignore)

EXEMPLO DE USO:

# No seu script
try:
    from config import LINKEDIN_EMAIL, LINKEDIN_PASSWORD
    EMAIL = LINKEDIN_EMAIL
    SENHA = LINKEDIN_PASSWORD
except ImportError:
    # Fallback para valores padrão
    EMAIL = "seu_email@example.com"
    SENHA = "sua_senha_aqui"
    print("⚠️ Arquivo config.py não encontrado. Usando valores padrão.")
    print("💡 Dica: Copie config.example.py para config.py e configure.")
"""
