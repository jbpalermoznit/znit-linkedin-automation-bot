# LinkedIn Bot com Cadencia

Sistema de automacao para LinkedIn com cadencia programada de mensagens.

## Funcionalidades

- **Duas cadencias separadas**: uma para novos contatos (convites) e outra para conexoes existentes (mensagens)
- **Deteccao automatica**: identifica se o perfil ja e uma conexao ou nao
- **Agendamento por horarios**: define janelas de envio (ex: 09:00-12:00 e 14:00-17:00)
- **Limites de seguranca**: maximo por dia, por hora e intervalos entre envios
- **Sequencia multi-etapas**: follow-ups automaticos com dias de espera configuráveis
- **Modo de teste**: valida mensagens antes de enviar
- **Persistencia de estado**: retoma de onde parou

## Estrutura

```
znit-linkedin-bot/
├── linkedin_bot_cadencia.py    # Bot principal
├── requirements.txt            # Dependencias
├── .env                        # Credenciais (nao commitar)
├── config/
│   ├── cadencia.json           # Configuracao da cadencia
│   └── urls.csv                # Lista de URLs para processar
├── data/
│   ├── estado_cadencia.json    # Estado persistido (gerado)
│   └── log_envios.csv          # Log de envios (gerado)
├── examples/
│   ├── template_convite.txt         # Msg convite (novos)
│   ├── template_followup1.txt       # Follow-up 1 (novos)
│   ├── template_followup2.txt       # Follow-up 2 (novos)
│   ├── template_conexao_msg1.txt    # Msg inicial (conexoes)
│   ├── template_conexao_msg2.txt    # Follow-up 1 (conexoes)
│   └── template_conexao_msg3.txt    # Follow-up 2 (conexoes)
└── logs/
```

## Instalacao

```bash
# Clone o repositorio
git clone https://github.com/joaobrunopalermo/znit-linkedin-bot.git
cd znit-linkedin-bot

# Crie ambiente virtual
python3 -m venv .venv
source .venv/bin/activate

# Instale dependencias
pip install -r requirements.txt
```

## Configuracao

### 1. Credenciais (.env)

```env
LINKEDIN_EMAIL=seu-email@example.com
LINKEDIN_SENHA=sua-senha
```

### 2. URLs (config/urls.csv)

```csv
url,nome,area
https://linkedin.com/in/pessoa1,Maria,consultoria em tecnologia
https://linkedin.com/in/pessoa2,Joao,transformacao digital
```

### 3. Cadencia (config/cadencia.json)

```json
{
  "ativo": true,
  "horarios": {
    "janelas": [
      {"inicio": "09:00", "fim": "12:00"},
      {"inicio": "14:00", "fim": "17:00"}
    ],
    "dias_semana": [0, 1, 2, 3, 4],
    "fuso_horario": "America/Sao_Paulo"
  },
  "limites": {
    "max_por_dia": 25,
    "max_por_hora": 10,
    "intervalo_min_segundos": 60,
    "intervalo_max_segundos": 180
  },
  "sequencia_novos_contatos": {
    "ativo": true,
    "etapas": [
      {"id": 1, "tipo": "convite_com_mensagem", "template": "examples/template_convite.txt", "dias_espera": 0},
      {"id": 2, "tipo": "mensagem", "template": "examples/template_followup1.txt", "dias_espera": 3},
      {"id": 3, "tipo": "mensagem", "template": "examples/template_followup2.txt", "dias_espera": 7}
    ]
  },
  "sequencia_conexoes_existentes": {
    "ativo": true,
    "etapas": [
      {"id": 1, "tipo": "mensagem", "template": "examples/template_conexao_msg1.txt", "dias_espera": 0},
      {"id": 2, "tipo": "mensagem", "template": "examples/template_conexao_msg2.txt", "dias_espera": 4},
      {"id": 3, "tipo": "mensagem", "template": "examples/template_conexao_msg3.txt", "dias_espera": 10}
    ]
  }
}
```

### 4. Templates

Edite os arquivos em `examples/` com suas mensagens. Use variaveis:
- `{nome}` - Primeiro nome da pessoa
- `{nome_completo}` - Nome completo
- `{area}` - Coluna do CSV (ou qualquer outra coluna)

**Limite de convites**: 300 caracteres

## Uso

```bash
python linkedin_bot_cadencia.py
```

### Menu de Opcoes

```
1. Executar uma sessao (com cadencia)
2. Modo continuo (fica rodando)
3. Ver status da cadencia
4. Resetar estado da cadencia
─────────────────────────────────
5. MODO TESTE - Testar URLs da lista
6. MODO TESTE - Testar URL especifica
7. Validar templates
```

### Opcao 1 - Sessao Unica
Executa uma sessao de envios respeitando os limites configurados.

### Opcao 2 - Modo Continuo
Fica rodando continuamente, enviando nas janelas de horario permitidas.

### Opcao 3 - Ver Status
Mostra quantos envios foram feitos hoje, contatos pendentes, etc.

### Opcao 5/6 - Modo Teste
Permite testar URLs sem enviar de verdade:
- **Opcao 1**: Apenas detecta tipo (conexao ou novo)
- **Opcao 2**: Simula envio (mostra mensagem)
- **Opcao 3**: Envia de verdade (com confirmacao manual)

### Opcao 7 - Validar Templates
Verifica se todos os arquivos de template existem e mostra preview.

## Como Funciona

1. **Carrega URLs** do arquivo `config/urls.csv`
2. **Detecta tipo**: verifica se cada perfil ja e conexao ou nao
3. **Seleciona cadencia**: usa a sequencia apropriada
4. **Verifica etapa**: ve em qual etapa o contato esta
5. **Envia mensagem**: se passou os dias de espera necessarios
6. **Registra estado**: salva progresso em `data/estado_cadencia.json`

## Seguranca

- Use delays aleatorios (ja configurado)
- Nao envie mais de 25-50 mensagens por dia
- Monitore os logs em `data/log_envios.csv`
- Nunca commite o arquivo `.env`

## Desenvolvido por

Joao Bruno Palermo
GitHub: https://github.com/joaobrunopalermo
