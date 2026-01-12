# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

---

## [2.0.0] - 2025-01-12

### 🎉 Lançamento Inicial

**Desenvolvido por:** João Bruno Palermo ([@joaobrunopalermo](https://github.com/joaobrunopalermo))

### ✨ Adicionado

#### Bot Simples (v1.0)
- ✅ Automação de envio de convites no LinkedIn
- ✅ Mensagens personalizadas com templates
- ✅ Suporte a CSV e TXT para listas de URLs
- ✅ Delays aleatórios para segurança (3-7s)
- ✅ Sistema de logging completo
- ✅ Limite configurável de convites/dia
- ✅ 3 modos: convites simples, com mensagem, mensagens diretas
- ✅ Taxa de aceitação: 20-30%

#### Bot IA (v2.0) 🤖
- ✨ **Extração automática de dados do perfil LinkedIn:**
  - Nome completo
  - Cargo/título atual
  - Empresa
  - Localização
  - Seção "Sobre"
  - Experiências profissionais
  - Formação acadêmica
- ✨ **Integração com IA (Claude da Anthropic)**
- ✨ **Geração de mensagens únicas e personalizadas**
- ✨ **Análise de contexto do perfil**
- ✨ **Salvamento de dados em JSON** (`perfis_extraidos.json`)
- ✨ Taxa de aceitação: 40-60%
- ✨ Personalização profunda baseada em contexto

#### Documentação
- 📚 README.md completo com badges
- 📚 GUIA_TERMINAL.md - Guia de uso no terminal
- 📚 GUIA_IA.md - Documentação da versão IA
- 📚 INICIO_RAPIDO.md - Setup rápido
- 📚 GITHUB_SETUP.md - Como publicar no GitHub
- 📚 CONTRIBUTING.md - Guia para contribuidores
- 📚 LICENSE - MIT License

#### Ferramentas Auxiliares
- 🛠️ `verificar_instalacao.py` - Testa instalação
- 🛠️ `configurador.py` - Menu interativo
- 🛠️ `demo_comparacao.py` - Compara as 2 versões
- 🛠️ `comandos.sh` - Referência rápida

#### Arquivos de Exemplo
- 📋 `urls.csv` - Lista com dados adicionais
- 📋 `urls.txt` - Lista simples
- 📋 `template.txt` - Template de mensagem

#### Configuração
- ⚙️ `.gitignore` - Proteção de credenciais
- ⚙️ `requirements.txt` - Dependências Python
- ⚙️ `AUTHORS.md` - Lista de autores

### 🛡️ Segurança

- ✅ `.gitignore` configurado para proteger:
  - Credenciais (`credentials.py`, `.env`)
  - Logs (`log_envios*.csv`)
  - Dados sensíveis (`perfis_extraidos.json`)
  - URLs reais dos usuários
- ✅ Avisos legais em toda documentação
- ✅ Validação de configurações antes de executar
- ✅ Sistema de delays aleatórios anti-detecção
- ✅ Tratamento robusto de erros

### 📊 Recursos de Análise

- 📈 Logs em CSV com timestamp
- 📈 Status de cada ação (sucesso/erro/timeout)
- 📈 Mensagens enviadas registradas
- 📈 Dados de perfis salvos em JSON (versão IA)
- 📈 Estatísticas de processamento

### 🎯 Casos de Uso Suportados

- Recrutamento especializado
- Vendas B2B
- Networking estratégico
- Pesquisa de mercado
- Prospecção em massa
- Follow-up automatizado

---

## [Unreleased]

### 🔮 Planejado para Próximas Versões

#### v2.1.0 - Melhorias de Análise
- [ ] Dashboard de resultados
- [ ] Gráficos de taxa de aceitação
- [ ] Análise de melhores horários
- [ ] Exportação de relatórios

#### v2.2.0 - Integrações
- [ ] Integração com CRM (HubSpot, Salesforce)
- [ ] Webhook para notificações
- [ ] API REST para controle remoto
- [ ] Sincronização com Google Sheets

#### v2.3.0 - Recursos Avançados
- [ ] A/B testing de mensagens
- [ ] Sistema de agendamento
- [ ] Suporte a múltiplas contas
- [ ] Interface gráfica (GUI)

#### v3.0.0 - Expansão
- [ ] Suporte a outros idiomas
- [ ] Automação para outras redes (Twitter, etc)
- [ ] Machine Learning para otimização
- [ ] Modo headless melhorado

---

## Tipos de Mudanças

- `Added` - Novas funcionalidades
- `Changed` - Mudanças em funcionalidades existentes
- `Deprecated` - Funcionalidades que serão removidas
- `Removed` - Funcionalidades removidas
- `Fixed` - Correções de bugs
- `Security` - Correções de segurança

---

## Como Contribuir

Quer sugerir uma funcionalidade ou reportar um bug?

1. Abra uma [Issue](https://github.com/joaobrunopalermo/linkedin-automation-bot/issues)
2. Veja o [CONTRIBUTING.md](CONTRIBUTING.md)
3. Envie um Pull Request

---

**Mantido por:** [João Bruno Palermo](https://github.com/joaobrunopalermo)

**Links:**
- [GitHub](https://github.com/joaobrunopalermo/linkedin-automation-bot)
- [Issues](https://github.com/joaobrunopalermo/linkedin-automation-bot/issues)
- [Discussions](https://github.com/joaobrunopalermo/linkedin-automation-bot/discussions)
