# 🤖 LinkedIn Automation Bot

> **Sistema completo de automação para networking no LinkedIn com 2 versões: Simples e com IA**

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Selenium](https://img.shields.io/badge/selenium-4.0+-green.svg)](https://www.selenium.dev/)
[![Made with ❤️](https://img.shields.io/badge/Made%20with-❤️-red.svg)](https://github.com/joaobrunopalermo)

**Desenvolvido por [João Bruno Palermo](https://github.com/joaobrunopalermo)**

⚠️ **AVISO:** Este projeto é apenas para fins educacionais. O uso de automação pode violar os Termos de Serviço do LinkedIn. Use por sua conta e risco.

---

## 📋 Índice

- [Características](#-características)
- [Versões Disponíveis](#-versões-disponíveis)
- [Instalação](#-instalação)
- [Configuração](#️-configuração)
- [Uso](#-uso)
- [Comparação de Versões](#-comparação-de-versões)
- [Segurança](#-segurança)
- [Contribuindo](#-contribuindo)
- [License](#-license)

---

## ✨ Características

### Versão Simples
- ✅ Automação de envio de convites
- ✅ Mensagens personalizadas com templates
- ✅ Delays aleatórios para segurança
- ✅ Logging completo de ações
- ✅ Suporte a CSV e TXT
- ✅ **Totalmente gratuito**

### Versão IA (Avançada) 🤖
- ✨ **Extração automática de dados do perfil**
- ✨ **Geração de mensagens únicas usando IA (Claude)**
- ✨ Personalização profunda baseada em contexto
- ✨ **Salva dados dos perfis em JSON**
- ✨ Taxa de aceitação 2x maior
- ✨ Ideal para networking estratégico

---

## 🎯 Versões Disponíveis

| Característica | Bot Simples | Bot IA |
|---------------|-------------|--------|
| Velocidade | ⚡⚡⚡ Rápido (5-8s) | ⚡⚡ Médio (15-20s) |
| Personalização | ⭐⭐ Básica | ⭐⭐⭐⭐⭐ Avançada |
| Taxa de aceitação | 20-30% | 40-60% |
| Custo | 🆓 Grátis | 💰 ~$0.01/mensagem |
| Extração de dados | ❌ | ✅ |
| Volume recomendado | 100+ por dia | 30-50 por dia |
| Uso ideal | Volume | Qualidade |

---

## 🚀 Instalação

### Pré-requisitos

- Python 3.8 ou superior
- Google Chrome instalado
- Conta no LinkedIn

### Passos

1. **Clone o repositório:**
```bash
git clone https://github.com/seu-usuario/linkedin-automation-bot.git
cd linkedin-automation-bot
```

2. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

3. **Verifique a instalação:**
```bash
python verificar_instalacao.py
```

---

## ⚙️ Configuração

### 1. Configure suas credenciais

**IMPORTANTE:** Nunca commite suas credenciais no Git!

Crie um arquivo `credentials.py`:

```python
# credentials.py (não será commitado)
LINKEDIN_EMAIL = "seu_email@example.com"
LINKEDIN_PASSWORD = "sua_senha_segura"
```

Ou edite diretamente no script (menos seguro):

```python
# No arquivo linkedin_bot.py ou linkedin_bot_ia.py
EMAIL = "seu_email@example.com"
SENHA = "sua_senha_segura"
```

### 2. Prepare sua lista de URLs

Crie um arquivo `urls.csv`:

```csv
nome,url,empresa,cargo
João Silva,https://www.linkedin.com/in/joaosilva/,Tech Corp,Desenvolvedor
Maria Santos,https://www.linkedin.com/in/mariasousa/,StartupX,Designer
```

Ou use formato simples `urls.txt`:
```
https://www.linkedin.com/in/joaosilva/
https://www.linkedin.com/in/mariasousa/
```

### 3. Escolha o modo

**Bot Simples:**
```python
MODO = "convites_com_mensagem"
```

**Bot IA:**
```python
MODO = "convites_com_mensagem_ia"
USE_IA = True
```

---

## 🎮 Uso

### Bot Simples (Volume)

```bash
python linkedin_bot.py
```

**Ideal para:**
- Grandes volumes (100+ convites/dia)
- Primeira fase de prospecção
- Perfis similares
- Budget zero

### Bot IA (Qualidade)

```bash
python linkedin_bot_ia.py
```

**Ideal para:**
- Networking estratégico
- Recrutamento especializado
- Vendas B2B
- Leads prioritários

### Ferramentas Auxiliares

```bash
# Ver comparação das versões
python demo_comparacao.py

# Menu interativo
python configurador.py

# Referência rápida de comandos
./comandos.sh
```

---

## 📊 Comparação de Versões

Execute para ver comparação detalhada:

```bash
python demo_comparacao.py
```

### Exemplo de Mensagens Geradas

**Perfil:** João Silva - Desenvolvedor Full Stack na Tech Corp

**Bot Simples:**
> "Olá João! Vi seu perfil na Tech Corp. Gostaria de conectar e trocar ideias!"

**Bot IA:**
> "Olá João! Impressionante seus 8 anos em desenvolvimento web, especialmente sua especialização em React e Node.js. Trabalho com stack similar e adoraria trocar experiências sobre arquitetura de microserviços."

---

## 🛡️ Segurança

### ⚠️ Limites Recomendados

- **Iniciantes:** 10-20 convites/dia
- **Experientes:** 30-50 convites/dia
- **Máximo:** 100 convites/semana

### ✅ Boas Práticas

1. **Delays adequados:** Mantenha 3-7 segundos entre ações
2. **Começe devagar:** Teste com 5-10 perfis primeiro
3. **Monitore sua conta:** Fique atento a warnings do LinkedIn
4. **Personalize mensagens:** Evite spam genérico
5. **Use em horários normais:** 9h-18h em dias úteis

### 🔐 Segurança de Credenciais

**NUNCA commite credenciais no Git!**

```bash
# Verifique antes de commit
git status

# Certifique-se que .gitignore está funcionando
git check-ignore credentials.py  # Deve retornar o arquivo
```

---

## 📁 Estrutura do Projeto

```
linkedin-automation-bot/
├── linkedin_bot.py              # Bot simples
├── linkedin_bot_ia.py           # Bot com IA
├── verificar_instalacao.py      # Testa instalação
├── configurador.py              # Menu interativo
├── demo_comparacao.py           # Comparação
├── urls.csv                     # Lista de URLs (exemplo)
├── template.txt                 # Template de mensagem
├── requirements.txt             # Dependências
├── .gitignore                   # Arquivos ignorados
├── README.md                    # Este arquivo
├── GUIA_TERMINAL.md            # Guia completo
├── GUIA_IA.md                  # Guia versão IA
└── LICENSE                      # Licença MIT
```

---

## 📝 Arquivos Gerados

### Bot Simples
- `log_envios.csv` - Log de todas as ações

### Bot IA
- `log_envios_ia.csv` - Log detalhado
- `perfis_extraidos.json` - **Dados completos dos perfis!** 💎

---

## 🎓 Documentação Completa

- **[GUIA_TERMINAL.md](GUIA_TERMINAL.md)** - Guia completo de uso no terminal
- **[GUIA_IA.md](GUIA_IA.md)** - Guia da versão com IA
- **[INICIO_RAPIDO.md](INICIO_RAPIDO.md)** - Setup em 5 minutos
- **[linkedin_automation_guide.md](linkedin_automation_guide.md)** - Guia detalhado

---

## 💡 Casos de Uso

### 1. Recrutamento
```python
# Use versão IA para candidatos qualificados
MODO = "convites_com_mensagem_ia"
MAX_CONVITES = 30
```

### 2. Vendas B2B
```python
# Segmente lista: VIPs com IA, volume com Simples
leads_vip.csv → linkedin_bot_ia.py
leads_volume.csv → linkedin_bot.py
```

### 3. Networking Massivo
```python
# Use bot simples para mapear mercado
MODO = "convites"
MAX_CONVITES = 100
```

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/NovaFuncionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/NovaFuncionalidade`)
5. Abra um Pull Request

---

## ⚖️ Aviso Legal

Este projeto é fornecido apenas para fins **educacionais e de pesquisa**.

- ⚠️ O uso de bots pode violar os Termos de Serviço do LinkedIn
- ⚠️ Use por sua conta e risco
- ⚠️ O LinkedIn pode restringir ou banir sua conta
- ⚠️ Os autores não se responsabilizam pelo uso inadequado

**Recomendação:** Use com moderação, ética e responsabilidade.

---

## 📄 License

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

## 🙏 Agradecimentos

- [Selenium](https://www.selenium.dev/) - Automação web
- [Anthropic Claude](https://www.anthropic.com/) - IA para geração de mensagens
- Comunidade open source

---

## 📞 Suporte

- 📖 Leia a [documentação completa](GUIA_TERMINAL.md)
- 🐛 Reporte bugs nas [Issues](https://github.com/seu-usuario/linkedin-automation-bot/issues)
- 💬 Discussões na aba [Discussions](https://github.com/seu-usuario/linkedin-automation-bot/discussions)

---

## 🌟 Star o projeto!

Se este projeto te ajudou, considere dar uma ⭐ no GitHub!

---

## 👨‍💻 Autor

**João Bruno Palermo**

- GitHub: [@joaobrunopalermo](https://github.com/joaobrunopalermo)
- LinkedIn: [João Bruno Palermo](https://linkedin.com/in/joaobrunopalermo)
- Email: contato@joaobrunopalermo.com

---

**Desenvolvido com ❤️ para a comunidade de networking**

**Última atualização:** Janeiro 2025 | **Versão:** 2.0
