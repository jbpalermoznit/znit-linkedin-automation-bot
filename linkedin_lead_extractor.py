"""
LinkedIn Lead Extractor & AI Message Generator
Extrai dados dos perfis e usa Claude AI para criar mensagens personalizadas

Fluxo:
1. python linkedin_lead_extractor.py extrair    -> Extrai dados e gera arquivos .md
2. Revise os dados e marque [x] **DADOS APROVADOS**
3. python linkedin_lead_extractor.py gerar      -> Claude cria mensagens únicas
4. Revise as mensagens e marque [x] **MENSAGENS APROVADAS**
5. python linkedin_lead_extractor.py aprovar    -> Dispara envios
"""

import time
import random
import json
import os
import re
from datetime import datetime
from pathlib import Path
import pytz
import pandas as pd
from dotenv import load_dotenv
import anthropic

load_dotenv()

# API do Claude para geração de mensagens
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# Selenium para extração de dados e envio
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# ============================================
# CONFIGURAÇÕES
# ============================================

EMAIL = os.getenv("LINKEDIN_EMAIL", "")
SENHA = os.getenv("LINKEDIN_SENHA", "")

ARQUIVO_URLS = "config/urls.csv"
ARQUIVO_CADENCIA = "config/cadencia.json"
PASTA_LEADS = "leads"
ARQUIVO_LEADS_JSON = "leads/leads_data.json"

TIMEOUT = 15

# ============================================
# EXTRATOR DE DADOS DO PERFIL (usando Selenium)
# ============================================

class LinkedInExtractor:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.leads_data = {}

    def inicializar(self):
        """Inicializa o navegador Chrome"""
        print("🚀 Iniciando navegador...")

        try:
            chrome_options = Options()

            # Usa um perfil dedicado para o bot (não conflita com Chrome aberto)
            perfil_bot = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chrome_profile")
            os.makedirs(perfil_bot, exist_ok=True)
            chrome_options.add_argument(f"--user-data-dir={perfil_bot}")

            chrome_options.add_argument("--start-maximized")
            chrome_options.add_argument("--disable-notifications")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)

            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.wait = WebDriverWait(self.driver, TIMEOUT)

            print("✅ Navegador iniciado!")

            # Verifica se está logado
            self.driver.get("https://www.linkedin.com/feed/")
            time.sleep(3)

            if "login" in self.driver.current_url or "checkpoint" in self.driver.current_url:
                print("⚠️ Não está logado. Fazendo login...")
                return self._fazer_login()

            print("✅ Sessão do LinkedIn ativa!")
            return True

        except Exception as e:
            print(f"❌ Erro ao iniciar navegador: {str(e)}")
            return False

    def _fazer_login(self):
        """Faz login no LinkedIn"""
        try:
            self.driver.get("https://www.linkedin.com/login")
            time.sleep(2)

            # Preenche email
            email_field = self.wait.until(EC.presence_of_element_located((By.ID, "username")))
            email_field.clear()
            email_field.send_keys(EMAIL)

            # Preenche senha
            senha_field = self.driver.find_element(By.ID, "password")
            senha_field.clear()
            senha_field.send_keys(SENHA)

            # Clica em entrar
            login_btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_btn.click()

            time.sleep(5)

            # Verifica se login foi bem sucedido
            if "feed" in self.driver.current_url:
                print("✅ Login realizado com sucesso!")
                return True
            elif "checkpoint" in self.driver.current_url:
                print("⚠️ LinkedIn pediu verificação de segurança.")
                print("   Complete a verificação manualmente no navegador...")
                input("   Pressione ENTER quando terminar...")
                return "feed" in self.driver.current_url
            else:
                print(f"❌ Login falhou. URL atual: {self.driver.current_url}")
                return False

        except Exception as e:
            print(f"❌ Erro no login: {str(e)}")
            return False

    def extrair_dados_perfil(self, url):
        """Extrai nome, cargo e empresa do perfil via Selenium"""
        dados = {
            "url": url,
            "nome": "",
            "cargo": "",
            "empresa": "",
            "area": "",
            "tipo": None,
            "localizacao": "",
            "sobre": "",
            "publicacoes": [],
            "extraido_em": datetime.now().isoformat()
        }

        try:
            print(f"\n🔍 Extraindo: {url}")

            # Navega para o perfil
            self.driver.get(url)
            time.sleep(random.uniform(3, 5))

            # Extrai nome
            dados["nome"] = self._extrair_nome()

            # Extrai cargo e empresa da headline ou experiência
            dados["cargo"], dados["empresa"] = self._extrair_cargo_empresa()

            # Infere área de atuação
            dados["area"] = self._inferir_area(dados["cargo"])

            # Detecta tipo (conexão existente vs novo contato)
            dados["tipo"] = self._detectar_tipo()

            # Extrai localização
            dados["localizacao"] = self._extrair_localizacao()

            # Extrai seção "Sobre"
            dados["sobre"] = self._extrair_sobre()

            # Extrai últimas publicações
            dados["publicacoes"] = self._extrair_publicacoes()

            # Mostra resultados
            print(f"   👤 Nome: {dados['nome'] or '(não encontrado)'}")
            print(f"   💼 Cargo: {dados['cargo'] or '(não encontrado)'}")
            print(f"   🏢 Empresa: {dados['empresa'] or '(não encontrada)'}")
            print(f"   📋 Área: {dados['area'] or '(não identificada)'}")
            print(f"   📍 Local: {dados['localizacao'] or '(não encontrado)'}")
            print(f"   🏷️  Tipo: {'Conexão existente' if dados['tipo'] == 'conexao_existente' else 'Novo contato'}")
            print(f"   📝 Publicações: {len(dados['publicacoes'])} encontradas")

            return dados

        except Exception as e:
            print(f"   ❌ Erro na extração: {str(e)}")
            return dados

    def _extrair_nome(self):
        """Extrai o nome do perfil com múltiplos seletores"""
        seletores_nome = [
            # Seletores mais específicos primeiro
            "h1.text-heading-xlarge",
            "h1.inline.t-24.v-align-middle.break-words",
            "h1[class*='text-heading']",
            "div.pv-text-details__left-panel h1",
            "div.ph5 h1",
            ".pv-top-card--list h1",
            # Seletores genéricos
            "h1",
        ]

        for seletor in seletores_nome:
            try:
                elemento = self.driver.find_element(By.CSS_SELECTOR, seletor)
                nome = elemento.text.strip()
                if nome and len(nome) > 1 and not nome.startswith("LinkedIn"):
                    return nome
            except:
                continue

        # Fallback: extrai do título da página
        try:
            titulo = self.driver.title
            # Título geralmente é: "Nome Sobrenome | LinkedIn"
            if "|" in titulo:
                nome = titulo.split("|")[0].strip()
                if nome and "LinkedIn" not in nome:
                    return nome
        except:
            pass

        # Último fallback: extrai da URL
        try:
            url_parts = self.driver.current_url.split("/in/")
            if len(url_parts) > 1:
                slug = url_parts[1].split("/")[0].split("?")[0]
                nome = slug.replace("-", " ").title()
                return nome
        except:
            pass

        return ""

    def _extrair_cargo_empresa(self):
        """Extrai cargo e empresa do perfil"""
        cargo = ""
        empresa = ""

        # =====================================================
        # PRIMEIRO: Busca EMPRESA (mais confiável via links)
        # =====================================================

        # 1. Busca pelo link direto da empresa no card superior
        try:
            link_empresa = self.driver.find_element(By.CSS_SELECTOR,
                "div.pv-text-details__right-panel a[href*='/company/']")
            spans = link_empresa.find_elements(By.TAG_NAME, "span")
            if spans:
                empresa = spans[0].text.strip()
            else:
                empresa = link_empresa.text.strip()
            empresa = self._limpar_empresa(empresa)
        except:
            pass

        # 2. Busca botão de empresa atual
        if not empresa:
            try:
                btn_empresa = self.driver.find_element(By.CSS_SELECTOR,
                    "button[aria-label*='empresa atual'], button[aria-label*='Current company']")
                aria_label = btn_empresa.get_attribute("aria-label")
                if ":" in aria_label:
                    empresa = aria_label.split(":")[-1].strip()
                empresa = self._limpar_empresa(empresa)
            except:
                pass

        # 3. Busca na seção de experiências
        if not empresa:
            try:
                exp_section = self.driver.find_elements(By.CSS_SELECTOR, "#experience")
                if exp_section:
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", exp_section[0])
                    time.sleep(1)

                primeira_exp = self.driver.find_elements(By.CSS_SELECTOR,
                    "#experience ~ div li.artdeco-list__item:first-child")
                if primeira_exp:
                    link_emp = primeira_exp[0].find_elements(By.CSS_SELECTOR, "a[href*='/company/']")
                    if link_emp:
                        empresa = link_emp[0].text.strip()
                        empresa = self._limpar_empresa(empresa)
            except:
                pass

        # 4. Fallback - qualquer link de empresa
        if not empresa:
            try:
                links_empresa = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/company/']")
                for link in links_empresa[:5]:
                    try:
                        texto = link.text.strip()
                        if texto:
                            empresa = self._limpar_empresa(texto)
                            if empresa and len(empresa) > 2:
                                break
                    except:
                        continue
            except:
                pass

        # =====================================================
        # SEGUNDO: Busca CARGO da headline
        # =====================================================

        seletores_headline = [
            "div.text-body-medium.break-words",
            "div[class*='text-body-medium']",
            ".pv-top-card--list .text-body-medium",
            "div.ph5 div.text-body-medium",
        ]

        headline = ""
        for seletor in seletores_headline:
            try:
                elemento = self.driver.find_element(By.CSS_SELECTOR, seletor)
                headline = elemento.text.strip()
                if headline:
                    break
            except:
                continue

        if headline:
            # Se headline tem muitos "|" (lista de skills), pega só o primeiro
            if headline.count("|") >= 2:
                cargo = headline.split("|")[0].strip()
            # Se empresa encontrada e está na headline, extrai só o cargo
            elif empresa:
                separadores = [" na ", " at ", " @ "]
                encontrou = False
                for sep in separadores:
                    if sep in headline.lower():
                        idx = headline.lower().find(sep.lower())
                        cargo = headline[:idx].strip()
                        encontrou = True
                        break
                if not encontrou:
                    cargo = headline
            else:
                # Tenta separar cargo/empresa apenas com " na " ou " at "
                separadores = [" na ", " at "]
                encontrou = False
                for sep in separadores:
                    if sep in headline.lower():
                        idx = headline.lower().find(sep.lower())
                        cargo = headline[:idx].strip()
                        if not empresa:
                            empresa = headline[idx + len(sep):].strip()
                        encontrou = True
                        break
                if not encontrou:
                    cargo = headline

        # Se cargo ainda é muito longo (parece lista de skills), simplifica
        if cargo and cargo.count("|") >= 1:
            cargo = cargo.split("|")[0].strip()

        return cargo, empresa

    def _limpar_empresa(self, texto):
        """Limpa o texto da empresa removendo lixo"""
        if not texto:
            return ""

        # Pega só a primeira linha
        primeira_linha = texto.split('\n')[0].strip()

        # Remove padrões de seguidores/followers
        padroes_remover = [
            r'\d+\.?\d*\s*(seguidores|followers)',
            r'\d+\s*(seguidores|followers)',
            r'seguidores',
            r'followers',
        ]

        resultado = primeira_linha
        for padrao in padroes_remover:
            resultado = re.sub(padrao, '', resultado, flags=re.IGNORECASE)

        return resultado.strip()

    def _detectar_tipo(self):
        """Detecta se é conexão existente (1º grau) ou novo contato"""
        try:
            page_source = self.driver.page_source.lower()

            # Indicadores de conexão de 1º grau
            indicadores_conexao = [
                "1st degree connection",
                "1º grau",
                "1st",
                "degree connection",
                "message" in page_source and "connect" not in page_source,
            ]

            # Verifica texto na página
            for indicador in indicadores_conexao[:-1]:
                if indicador in page_source:
                    return "conexao_existente"

            # Verifica botões disponíveis
            try:
                # Se tem botão "Mensagem" proeminente, provavelmente é conexão
                botao_msg = self.driver.find_elements(By.CSS_SELECTOR,
                    "button[aria-label*='Mensagem'], button[aria-label*='Message']")
                if botao_msg:
                    # Verifica se é o botão principal (não dentro de dropdown)
                    for btn in botao_msg:
                        if btn.is_displayed() and "more" not in btn.get_attribute("aria-label").lower():
                            return "conexao_existente"
            except:
                pass

            # Verifica badge de grau de conexão
            try:
                grau_elements = self.driver.find_elements(By.CSS_SELECTOR,
                    ".dist-value, span[class*='distance'], .pvs-header__subtitle")
                for elem in grau_elements:
                    texto = elem.text.lower()
                    if "1st" in texto or "1º" in texto:
                        return "conexao_existente"
            except:
                pass

            # Verifica se tem botão "Conectar" visível (indica que NÃO é conexão)
            try:
                botao_conectar = self.driver.find_elements(By.CSS_SELECTOR,
                    "button[aria-label*='Conectar'], button[aria-label*='Connect']")
                for btn in botao_conectar:
                    if btn.is_displayed():
                        return "novo"
            except:
                pass

            return "novo"

        except Exception as e:
            print(f"   ⚠️ Erro ao detectar tipo: {str(e)}")
            return "novo"

    def _inferir_area(self, cargo):
        """Infere a área de atuação baseado no cargo"""
        if not cargo:
            return ""

        cargo_lower = cargo.lower()

        # Mapeamento de palavras-chave para áreas
        areas_map = {
            "sustentabilidade": ["sustentabilidade", "esg", "ambiental", "meio ambiente", "green", "carbono", "sustainability"],
            "engenharia": ["engenheiro", "engenharia", "engineer", "engineering", "técnico"],
            "construção": ["construção", "obra", "construction", "building", "incorporação", "incorporador"],
            "inovação": ["inovação", "innovation", "p&d", "r&d", "pesquisa", "research"],
            "tecnologia": ["tecnologia", "tech", "ti", "it", "software", "developer", "dados", "data"],
            "comercial": ["comercial", "vendas", "sales", "business development", "negócios"],
            "marketing": ["marketing", "comunicação", "branding", "digital"],
            "operações": ["operações", "operations", "supply chain", "logística"],
            "financeiro": ["financeiro", "finance", "controller", "contábil", "cfo"],
            "gestão": ["diretor", "gerente", "coordenador", "manager", "head", "líder", "ceo", "coo", "cto"]
        }

        for area, palavras in areas_map.items():
            for palavra in palavras:
                if palavra in cargo_lower:
                    return area

        return ""

    def _extrair_localizacao(self):
        """Extrai a localização do perfil"""
        seletores = [
            "span.text-body-small.inline.t-black--light.break-words",
            ".pv-text-details__left-panel span.text-body-small",
            "div.ph5 span.text-body-small",
        ]

        for seletor in seletores:
            try:
                elementos = self.driver.find_elements(By.CSS_SELECTOR, seletor)
                for elem in elementos:
                    texto = elem.text.strip()
                    # Localização geralmente tem vírgula (Cidade, Estado) ou é curta
                    if texto and len(texto) > 2 and len(texto) < 100:
                        # Ignora textos que são claramente não-localização
                        if not any(x in texto.lower() for x in ['seguidores', 'conexões', 'followers', 'connections']):
                            return texto
            except:
                continue
        return ""

    def _extrair_sobre(self):
        """Extrai a seção 'Sobre' do perfil"""
        try:
            # Rola até a seção Sobre
            sobre_section = self.driver.find_elements(By.CSS_SELECTOR, "#about")
            if sobre_section:
                self.driver.execute_script("arguments[0].scrollIntoView(true);", sobre_section[0])
                time.sleep(1)

            # Tenta diferentes seletores para o texto do Sobre
            seletores = [
                "#about + div + div span[aria-hidden='true']",
                "#about ~ div .inline-show-more-text span",
                "#about ~ div .pv-shared-text-with-see-more span",
                "section.pv-about-section div.pv-shared-text-with-see-more span",
            ]

            for seletor in seletores:
                try:
                    elementos = self.driver.find_elements(By.CSS_SELECTOR, seletor)
                    for elem in elementos:
                        texto = elem.text.strip()
                        if texto and len(texto) > 50:  # Sobre geralmente é mais longo
                            return texto[:1000]  # Limita a 1000 caracteres
                except:
                    continue

        except:
            pass
        return ""

    def _extrair_publicacoes(self):
        """Extrai as últimas publicações do perfil"""
        publicacoes = []

        try:
            # Navega para a página de atividades/posts do perfil
            url_atual = self.driver.current_url.rstrip('/')
            url_posts = f"{url_atual}/recent-activity/all/"

            self.driver.get(url_posts)
            time.sleep(random.uniform(2, 4))

            # Rola um pouco para carregar posts
            self.driver.execute_script("window.scrollTo(0, 800);")
            time.sleep(2)

            # Busca os posts
            seletores_post = [
                "div.feed-shared-update-v2",
                "div[data-urn*='activity']",
                ".occludable-update",
            ]

            posts_elements = []
            for seletor in seletores_post:
                posts_elements = self.driver.find_elements(By.CSS_SELECTOR, seletor)
                if posts_elements:
                    break

            # Extrai até 3 publicações
            for i, post in enumerate(posts_elements[:3]):
                try:
                    pub = {"texto": "", "data": "", "tipo": "post"}

                    # Extrai texto do post
                    texto_elements = post.find_elements(By.CSS_SELECTOR,
                        "span.break-words, .feed-shared-text span, .update-components-text span")
                    for elem in texto_elements:
                        texto = elem.text.strip()
                        if texto and len(texto) > 20:
                            pub["texto"] = texto[:500]  # Limita a 500 chars
                            break

                    # Extrai data aproximada
                    data_elements = post.find_elements(By.CSS_SELECTOR,
                        "span.update-components-actor__sub-description span, time, .feed-shared-actor__sub-description span")
                    for elem in data_elements:
                        data_texto = elem.text.strip()
                        if data_texto and any(x in data_texto.lower() for x in ['h', 'd', 'sem', 'mês', 'ano', 'week', 'month', 'year', 'hour', 'day']):
                            pub["data"] = data_texto
                            break

                    # Verifica se é repost
                    if post.find_elements(By.CSS_SELECTOR, "[data-urn*='share']"):
                        pub["tipo"] = "repost"

                    if pub["texto"]:
                        publicacoes.append(pub)

                except Exception as e:
                    continue

            # Volta para o perfil principal
            self.driver.get(url_atual)
            time.sleep(1)

        except Exception as e:
            print(f"   ⚠️ Erro ao extrair publicações: {str(e)}")

        return publicacoes

    def fechar(self):
        """Fecha o navegador"""
        if self.driver:
            self.driver.quit()
        print("\n👋 Navegador fechado")


# ============================================
# GERADOR DE ARQUIVOS MARKDOWN (Dados Brutos)
# ============================================

class LeadMarkdownGenerator:
    def __init__(self):
        self.config = self._carregar_config()

    def _carregar_config(self):
        """Carrega configuração de cadência"""
        try:
            with open(ARQUIVO_CADENCIA, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Arquivo de cadência não encontrado: {ARQUIVO_CADENCIA}")
            return {}

    def gerar_arquivo_lead(self, dados):
        """Gera arquivo .md com dados brutos do lead (sem mensagens ainda)"""

        # Cria pasta leads se não existir
        os.makedirs(PASTA_LEADS, exist_ok=True)

        # Nome do arquivo: slug do nome ou da URL
        nome = dados.get('nome', '')
        if not nome or nome == 'Desconhecido':
            url = dados.get('url', '')
            nome = url.split("/in/")[-1].split("/")[0].split("?")[0].replace("-", " ").title()

        nome_slug = self._criar_slug(nome) if nome else 'lead-sem-nome'

        if not nome_slug:
            nome_slug = f"lead-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        arquivo_md = os.path.join(PASTA_LEADS, f"{nome_slug}.md")

        # Define tipo
        if dados.get('tipo') == 'conexao_existente':
            tipo_label = "CONEXÃO EXISTENTE"
        else:
            tipo_label = "NOVO CONTATO"

        # Monta conteúdo do markdown com DADOS BRUTOS
        conteudo = f"""# {dados.get('nome', 'Nome não encontrado')}

## Dados do Perfil
- **URL:** {dados.get('url', '')}
- **Cargo:** {dados.get('cargo', 'Não identificado')}
- **Empresa:** {dados.get('empresa', 'Não identificada')}
- **Área:** {dados.get('area', 'Não identificada')}
- **Localização:** {dados.get('localizacao', 'Não identificada')}
- **Tipo:** {tipo_label}
- **Extraído em:** {dados.get('extraido_em', '')}

---

## Sobre

{dados.get('sobre', '(Seção "Sobre" não disponível ou vazia)')}

---

## Últimas Publicações

"""
        # Adiciona publicações
        publicacoes = dados.get('publicacoes', [])
        if publicacoes:
            for i, pub in enumerate(publicacoes, 1):
                conteudo += f"""### Publicação {i}
- **Data:** {pub.get('data', 'Não identificada')}
- **Tipo:** {pub.get('tipo', 'post')}

> {pub.get('texto', '(Sem texto)')}

---

"""
        else:
            conteudo += "(Nenhuma publicação encontrada)\n\n---\n\n"

        # Seção de status
        conteudo += """## Status

- [ ] **DADOS APROVADOS** - Marque para gerar mensagens personalizadas

> Após aprovar os dados, execute: `python linkedin_lead_extractor.py gerar`
> Isso usará a IA para criar mensagens únicas baseadas neste perfil.
"""

        # Salva arquivo
        with open(arquivo_md, 'w', encoding='utf-8') as f:
            f.write(conteudo)

        print(f"   📄 Arquivo gerado: {arquivo_md}")
        return arquivo_md

    def _criar_slug(self, texto):
        """Cria slug a partir do texto"""
        texto = texto.lower().strip()
        texto = re.sub(r'[àáâãäå]', 'a', texto)
        texto = re.sub(r'[èéêë]', 'e', texto)
        texto = re.sub(r'[ìíîï]', 'i', texto)
        texto = re.sub(r'[òóôõö]', 'o', texto)
        texto = re.sub(r'[ùúûü]', 'u', texto)
        texto = re.sub(r'[ç]', 'c', texto)
        texto = re.sub(r'[^a-z0-9\s-]', '', texto)
        texto = re.sub(r'[\s_]+', '-', texto)
        texto = re.sub(r'-+', '-', texto)
        return texto.strip('-')


# ============================================
# PROCESSADOR DE APROVAÇÃO
# ============================================

class ApprovalProcessor:
    def __init__(self):
        self.config = self._carregar_config()

    def _carregar_config(self):
        """Carrega configuração de cadência"""
        try:
            with open(ARQUIVO_CADENCIA, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def verificar_aprovados(self):
        """Verifica quais leads têm mensagens aprovadas"""
        aprovados = []

        if not os.path.exists(PASTA_LEADS):
            print(f"❌ Pasta {PASTA_LEADS} não encontrada")
            return aprovados

        for arquivo in os.listdir(PASTA_LEADS):
            if arquivo.endswith('.md') and not arquivo.startswith('_'):
                caminho = os.path.join(PASTA_LEADS, arquivo)
                with open(caminho, 'r', encoding='utf-8') as f:
                    conteudo = f.read()

                # Verifica se MENSAGENS foram aprovadas (novo fluxo)
                if '[x] **MENSAGENS APROVADAS**' in conteudo.lower() or '[X] **MENSAGENS APROVADAS**' in conteudo:
                    dados = self._extrair_dados_md(conteudo, arquivo)
                    if dados and dados.get('mensagens'):
                        aprovados.append(dados)

        return aprovados

    def _extrair_dados_md(self, conteudo, arquivo):
        """Extrai dados do arquivo markdown"""
        dados = {
            "arquivo": arquivo,
            "nome": "",
            "url": "",
            "tipo": "",
            "mensagens": []
        }

        # Extrai URL
        match = re.search(r'\*\*URL:\*\*\s*(.+)', conteudo)
        if match:
            dados["url"] = match.group(1).strip()

        # Extrai nome (título H1)
        match = re.search(r'^# (.+)$', conteudo, re.MULTILINE)
        if match:
            dados["nome"] = match.group(1).strip()

        # Extrai tipo
        if 'CONEXÃO EXISTENTE' in conteudo:
            dados["tipo"] = "conexao_existente"
        else:
            dados["tipo"] = "novo"

        # Extrai mensagens da seção "Mensagens Geradas"
        # Formato: ### MENSAGEM 1: Convite\n[texto]\n\n### MENSAGEM 2:...
        secao_msgs = re.search(r'## Mensagens Geradas\n\n.*?\n\n(### MENSAGEM.*?)(?=\n---\n|$)', conteudo, re.DOTALL)
        if secao_msgs:
            texto_mensagens = secao_msgs.group(1)
            # Extrai cada mensagem
            msgs = re.findall(r'### MENSAGEM (\d+):[^\n]*\n(.*?)(?=### MENSAGEM|\Z)', texto_mensagens, re.DOTALL)
            for num, msg in msgs:
                texto_limpo = msg.strip()
                if texto_limpo:
                    dados["mensagens"].append({
                        "numero": int(num),
                        "texto": texto_limpo
                    })

        return dados


# ============================================
# FUNÇÕES PRINCIPAIS
# ============================================

def carregar_urls(arquivo):
    """Carrega URLs do arquivo"""
    try:
        if arquivo.endswith('.csv'):
            df = pd.read_csv(arquivo)
            return df.to_dict('records')
        else:
            with open(arquivo, 'r', encoding='utf-8') as f:
                return [{"url": line.strip()} for line in f if line.strip()]
    except FileNotFoundError:
        print(f"❌ Arquivo não encontrado: {arquivo}")
        return []

def salvar_leads_json(leads_data):
    """Salva dados dos leads em JSON"""
    os.makedirs(PASTA_LEADS, exist_ok=True)
    with open(ARQUIVO_LEADS_JSON, 'w', encoding='utf-8') as f:
        json.dump(leads_data, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Dados salvos em: {ARQUIVO_LEADS_JSON}")

def comando_extrair():
    """Comando para extrair dados dos perfis"""
    print("""
    ╔════════════════════════════════════════════╗
    ║   LinkedIn Lead Extractor                  ║
    ║   Passo 1: Extração de Dados (Selenium)    ║
    ╚════════════════════════════════════════════╝
    """)

    if not EMAIL or not SENHA:
        print("❌ Configure LINKEDIN_EMAIL e LINKEDIN_SENHA no arquivo .env")
        return

    urls = carregar_urls(ARQUIVO_URLS)
    if not urls:
        print("❌ Nenhuma URL para processar!")
        return

    print(f"📋 {len(urls)} URLs para extrair")

    extractor = LinkedInExtractor()
    generator = LeadMarkdownGenerator()

    try:
        if not extractor.inicializar():
            print("❌ Falha ao conectar à API")
            return

        leads_data = []

        for i, item in enumerate(urls, 1):
            url = item.get('url', item) if isinstance(item, dict) else item

            print(f"\n[{i}/{len(urls)}] Processando...")

            # Extrai dados via API
            dados = extractor.extrair_dados_perfil(url)
            leads_data.append(dados)

            # Gera arquivo markdown
            generator.gerar_arquivo_lead(dados)

            # Delay entre extrações (evita rate limiting)
            if i < len(urls):
                delay = random.uniform(2, 4)
                print(f"   ⏱️ Aguardando {delay:.1f}s...")
                time.sleep(delay)

        # Salva JSON com todos os dados
        salvar_leads_json(leads_data)

        print("\n" + "="*50)
        print("✅ EXTRAÇÃO CONCLUÍDA!")
        print("="*50)
        print(f"\n📁 Arquivos gerados em: {PASTA_LEADS}/")
        print("\n📝 Próximos passos:")
        print("   1. Revise os arquivos .md na pasta leads/")
        print("   2. Verifique se os dados estão corretos")
        print("   3. Marque [x] **DADOS APROVADOS** nos leads")
        print("   4. Execute: python linkedin_lead_extractor.py gerar")

    except KeyboardInterrupt:
        print("\n\n⚠️ Interrompido pelo usuário")

    finally:
        extractor.fechar()

def comando_aprovar():
    """Comando para processar leads com mensagens aprovadas"""
    print("""
    ╔════════════════════════════════════════════╗
    ║   LinkedIn Lead Extractor                  ║
    ║   Passo 3: Envio das Mensagens Aprovadas   ║
    ╚════════════════════════════════════════════╝
    """)

    processor = ApprovalProcessor()
    aprovados = processor.verificar_aprovados()

    if not aprovados:
        print("❌ Nenhum lead com mensagens aprovadas encontrado!")
        print("\n💡 Fluxo completo:")
        print("   1. Execute 'extrair' para gerar os .md com dados")
        print("   2. Marque [x] **DADOS APROVADOS** nos arquivos")
        print("   3. Execute 'gerar' para criar mensagens com IA")
        print("   4. Revise as mensagens geradas")
        print("   5. Marque [x] **MENSAGENS APROVADAS**")
        print("   6. Execute este comando novamente")
        return

    print(f"\n✅ {len(aprovados)} lead(s) aprovado(s):")
    for lead in aprovados:
        print(f"   - {lead['nome']} ({lead['tipo']})")

    print("\n" + "="*50)
    confirma = input("\n🚀 Deseja iniciar o envio? (s/n): ").strip().lower()

    if confirma != 's':
        print("❌ Envio cancelado")
        return

    # Importa o bot original para fazer os envios
    from linkedin_bot_cadencia import LinkedInBotCadencia

    bot = LinkedInBotCadencia()

    try:
        bot.inicializar_driver()

        if not bot.fazer_login():
            print("❌ Falha no login")
            return

        for i, lead in enumerate(aprovados, 1):
            print(f"\n[{i}/{len(aprovados)}] Enviando para: {lead['nome']}")

            url = lead['url']
            tipo = lead['tipo']
            mensagens = lead['mensagens']

            if not mensagens:
                print("   ⚠️ Nenhuma mensagem encontrada, pulando...")
                continue

            # Envia primeira mensagem da cadência
            primeira_msg = mensagens[0]['texto']

            if tipo == 'novo':
                # Envia convite com mensagem
                sucesso, status = bot.enviar_convite(url, primeira_msg)
            else:
                # Envia mensagem direta
                sucesso, status = bot.enviar_mensagem(url, primeira_msg)

            if sucesso:
                print(f"   ✅ Enviado com sucesso!")
                # Move arquivo para pasta 'enviados'
                _mover_para_enviados(lead['arquivo'])
            else:
                print(f"   ❌ Falha: {status}")

            # Delay entre envios
            if i < len(aprovados):
                delay = random.uniform(60, 120)
                print(f"   ⏱️ Aguardando {delay:.0f}s...")
                time.sleep(delay)

        bot.salvar_log()

        print("\n" + "="*50)
        print("✅ ENVIOS CONCLUÍDOS!")
        print("="*50)

    except KeyboardInterrupt:
        print("\n\n⚠️ Interrompido pelo usuário")
        bot.salvar_log()

    finally:
        bot.fechar()

def _mover_para_enviados(arquivo):
    """Move arquivo para pasta de enviados"""
    pasta_enviados = os.path.join(PASTA_LEADS, "enviados")
    os.makedirs(pasta_enviados, exist_ok=True)

    origem = os.path.join(PASTA_LEADS, arquivo)
    destino = os.path.join(pasta_enviados, arquivo)

    if os.path.exists(origem):
        os.rename(origem, destino)
        print(f"   📁 Movido para: {destino}")

def comando_gerar():
    """Comando para gerar mensagens personalizadas com Claude"""
    print("""
    ╔════════════════════════════════════════════╗
    ║   LinkedIn Lead Extractor                  ║
    ║   Passo 2: Gerar Mensagens (Claude AI)     ║
    ╚════════════════════════════════════════════╝
    """)

    if not ANTHROPIC_API_KEY:
        print("❌ Configure ANTHROPIC_API_KEY no arquivo .env")
        return

    if not os.path.exists(PASTA_LEADS):
        print(f"❌ Pasta {PASTA_LEADS} não existe. Execute 'extrair' primeiro.")
        return

    # Carrega templates de exemplo
    templates = _carregar_templates_exemplo()

    # Busca leads com dados aprovados
    leads_para_gerar = []
    for arquivo in os.listdir(PASTA_LEADS):
        if arquivo.endswith('.md') and not arquivo.startswith('_'):
            caminho = os.path.join(PASTA_LEADS, arquivo)
            with open(caminho, 'r', encoding='utf-8') as f:
                conteudo = f.read()

            # Verifica se dados foram aprovados
            if '[x] **DADOS APROVADOS**' in conteudo.lower() or '[X] **DADOS APROVADOS**' in conteudo:
                # Verifica se já tem mensagens geradas
                if '## Mensagens Geradas' not in conteudo:
                    leads_para_gerar.append((arquivo, caminho, conteudo))

    if not leads_para_gerar:
        print("❌ Nenhum lead com dados aprovados para gerar mensagens!")
        print("\n💡 Para aprovar os dados de um lead:")
        print("   1. Abra o arquivo .md do lead em leads/")
        print("   2. Marque o checkbox: [x] **DADOS APROVADOS**")
        print("   3. Execute este comando novamente")
        return

    print(f"\n📋 {len(leads_para_gerar)} lead(s) para gerar mensagens:")
    for arquivo, _, _ in leads_para_gerar:
        print(f"   - {arquivo}")

    # Inicializa cliente Claude
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    for arquivo, caminho, conteudo in leads_para_gerar:
        print(f"\n🤖 Gerando mensagens para: {arquivo}")

        try:
            # Extrai dados do markdown
            dados = _extrair_dados_do_md(conteudo)

            # Gera mensagens com Claude
            mensagens = _gerar_mensagens_claude(client, dados, templates)

            # Atualiza o arquivo .md com as mensagens
            _atualizar_md_com_mensagens(caminho, conteudo, mensagens, dados)

            print(f"   ✅ Mensagens geradas!")

        except Exception as e:
            print(f"   ❌ Erro: {str(e)}")

    print("\n" + "="*50)
    print("✅ GERAÇÃO CONCLUÍDA!")
    print("="*50)
    print("\n📝 Próximos passos:")
    print("   1. Revise as mensagens geradas nos arquivos .md")
    print("   2. Edite se necessário")
    print("   3. Marque [x] **MENSAGENS APROVADAS**")
    print("   4. Execute: python linkedin_lead_extractor.py aprovar")


def _carregar_templates_exemplo():
    """Carrega templates de exemplo para referência"""
    templates = {}
    pasta_examples = "examples"

    arquivos = [
        ("convite", "template_convite.txt"),
        ("conexao_msg1", "template_conexao_msg1.txt"),
        ("followup1", "template_followup1.txt"),
        ("followup2", "template_followup2.txt"),
    ]

    for nome, arquivo in arquivos:
        caminho = os.path.join(pasta_examples, arquivo)
        try:
            with open(caminho, 'r', encoding='utf-8') as f:
                templates[nome] = f.read().strip()
        except:
            templates[nome] = ""

    return templates


def _extrair_dados_do_md(conteudo):
    """Extrai dados estruturados do arquivo markdown"""
    dados = {}

    # Extrai nome (título H1)
    match = re.search(r'^# (.+)$', conteudo, re.MULTILINE)
    if match:
        dados['nome'] = match.group(1).strip()

    # Extrai campos do perfil
    campos = ['URL', 'Cargo', 'Empresa', 'Área', 'Localização', 'Tipo']
    for campo in campos:
        match = re.search(rf'\*\*{campo}:\*\*\s*(.+)', conteudo)
        if match:
            dados[campo.lower()] = match.group(1).strip()

    # Extrai seção Sobre
    match = re.search(r'## Sobre\n\n(.+?)\n\n---', conteudo, re.DOTALL)
    if match:
        dados['sobre'] = match.group(1).strip()

    # Extrai publicações
    publicacoes = []
    pub_matches = re.findall(r'### Publicação \d+\n.*?\n> (.+?)\n\n---', conteudo, re.DOTALL)
    for pub in pub_matches:
        publicacoes.append(pub.strip())
    dados['publicacoes'] = publicacoes

    return dados


def _gerar_mensagens_claude(client, dados, templates):
    """Usa Claude para gerar mensagens personalizadas"""

    primeiro_nome = dados.get('nome', '').split()[0] if dados.get('nome') else 'você'
    tipo = dados.get('tipo', 'NOVO CONTATO')

    # Monta contexto do lead
    contexto_lead = f"""
DADOS DO LEAD:
- Nome: {dados.get('nome', 'Não informado')}
- Cargo: {dados.get('cargo', 'Não informado')}
- Empresa: {dados.get('empresa', 'Não informada')}
- Área: {dados.get('area', 'Não informada')}
- Localização: {dados.get('localizacao', 'Não informada')}
- Tipo de conexão: {tipo}

SOBRE O LEAD:
{dados.get('sobre', '(Não disponível)')}

ÚLTIMAS PUBLICAÇÕES:
"""
    for i, pub in enumerate(dados.get('publicacoes', []), 1):
        contexto_lead += f"\n{i}. {pub[:300]}..."

    # Define quantas mensagens baseado no tipo
    if 'CONEXÃO EXISTENTE' in tipo:
        num_msgs = 3
        tipo_primeira = "mensagem direta"
    else:
        num_msgs = 3
        tipo_primeira = "convite de conexão (máximo 300 caracteres!)"

    # Prompt para o Claude
    prompt = f"""Você é um especialista em outreach B2B para a ZNIT, uma empresa de tecnologia que ajuda construtoras e incorporadoras a gerenciar ESG/sustentabilidade de forma automatizada, substituindo controles manuais em planilhas.

{contexto_lead}

EXEMPLOS DE MENSAGENS (use como referência de tom e estilo, mas NÃO copie):

Exemplo de convite:
{templates.get('convite', '')}

Exemplo de primeira mensagem para conexão existente:
{templates.get('conexao_msg1', '')}

Exemplo de follow-up 1:
{templates.get('followup1', '')}

Exemplo de follow-up 2:
{templates.get('followup2', '')}

---

TAREFA: Crie {num_msgs} mensagens personalizadas para este lead específico.

REGRAS IMPORTANTES:
1. A primeira mensagem é um {tipo_primeira}
2. Use informações ESPECÍFICAS do perfil (publicações, cargo, empresa, sobre)
3. Mencione algo relevante que a pessoa publicou ou faz
4. Mantenha tom profissional mas humanizado
5. Foque em construção civil, ESG, sustentabilidade, Green Capex
6. {"CONVITES devem ter NO MÁXIMO 300 caracteres!" if 'NOVO' in tipo else ""}
7. NÃO use emojis
8. Seja específico, não genérico

FORMATO DE RESPOSTA (use exatamente este formato):

### MENSAGEM 1: {"Convite" if 'NOVO' in tipo else "Primeira mensagem"}
[texto da mensagem aqui]

### MENSAGEM 2: Follow-up 1
[texto da mensagem aqui]

### MENSAGEM 3: Follow-up 2
[texto da mensagem aqui]
"""

    # Chama Claude API
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response.content[0].text


def _atualizar_md_com_mensagens(caminho, conteudo_original, mensagens_geradas, dados):
    """Atualiza o arquivo .md com as mensagens geradas"""

    tipo = dados.get('tipo', 'NOVO CONTATO')

    # Remove a seção de status antiga
    conteudo = re.sub(r'## Status\n\n.*$', '', conteudo_original, flags=re.DOTALL)

    # Adiciona seção de mensagens geradas
    conteudo += f"""## Mensagens Geradas

> Mensagens criadas pela IA baseadas no perfil do lead.
> Revise e edite conforme necessário antes de aprovar.

{mensagens_geradas}

---

## Aprovação Final

- [ ] **MENSAGENS APROVADAS** - Marque para liberar o envio

> Após aprovar, execute: `python linkedin_lead_extractor.py aprovar`
"""

    # Salva arquivo atualizado
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(conteudo)


def comando_status():
    """Mostra status dos leads"""
    print("""
    ╔════════════════════════════════════════════╗
    ║   LinkedIn Lead Extractor                  ║
    ║   Status dos Leads                         ║
    ╚════════════════════════════════════════════╝
    """)

    if not os.path.exists(PASTA_LEADS):
        print(f"❌ Pasta {PASTA_LEADS} não existe. Execute 'extrair' primeiro.")
        return

    # Conta arquivos por status
    pendentes_dados = []
    dados_aprovados = []
    mensagens_geradas = []
    mensagens_aprovadas = []
    enviados = []

    for arquivo in os.listdir(PASTA_LEADS):
        if arquivo.endswith('.md') and not arquivo.startswith('_'):
            caminho = os.path.join(PASTA_LEADS, arquivo)
            with open(caminho, 'r', encoding='utf-8') as f:
                conteudo = f.read()

            if '[x] **MENSAGENS APROVADAS**' in conteudo.lower() or '[X] **MENSAGENS APROVADAS**' in conteudo:
                mensagens_aprovadas.append(arquivo)
            elif '## Mensagens Geradas' in conteudo:
                mensagens_geradas.append(arquivo)
            elif '[x] **DADOS APROVADOS**' in conteudo.lower() or '[X] **DADOS APROVADOS**' in conteudo:
                dados_aprovados.append(arquivo)
            else:
                pendentes_dados.append(arquivo)

    pasta_enviados = os.path.join(PASTA_LEADS, "enviados")
    if os.path.exists(pasta_enviados):
        enviados = [f for f in os.listdir(pasta_enviados) if f.endswith('.md')]

    print(f"\n📊 Status dos Leads:")
    print(f"   1️⃣  Pendentes revisão de dados: {len(pendentes_dados)}")
    print(f"   2️⃣  Dados aprovados (aguardando gerar): {len(dados_aprovados)}")
    print(f"   3️⃣  Mensagens geradas (aguardando revisão): {len(mensagens_geradas)}")
    print(f"   4️⃣  Mensagens aprovadas (prontos p/ envio): {len(mensagens_aprovadas)}")
    print(f"   ✅ Já enviados: {len(enviados)}")

    if dados_aprovados:
        print(f"\n📋 Prontos para gerar mensagens:")
        for a in dados_aprovados:
            print(f"   - {a}")
        print(f"\n   Execute: python linkedin_lead_extractor.py gerar")

    if mensagens_aprovadas:
        print(f"\n📋 Prontos para envio:")
        for a in mensagens_aprovadas:
            print(f"   - {a}")
        print(f"\n   Execute: python linkedin_lead_extractor.py aprovar")

def main():
    import sys

    if len(sys.argv) < 2:
        print("""
    ╔════════════════════════════════════════════╗
    ║   LinkedIn Lead Extractor                  ║
    ║   Mensagens personalizadas com IA          ║
    ╚════════════════════════════════════════════╝

    Uso:
        python linkedin_lead_extractor.py <comando>

    Comandos:
        extrair   - Extrai dados dos perfis e gera arquivos .md
        gerar     - Usa Claude AI para criar mensagens personalizadas
        aprovar   - Envia mensagens dos leads aprovados
        status    - Mostra status dos leads

    Fluxo:
        1. extrair  -> Extrai dados e gera arquivos .md
        2. Revise os dados e marque [x] **DADOS APROVADOS**
        3. gerar    -> Claude cria mensagens únicas para cada lead
        4. Revise as mensagens e marque [x] **MENSAGENS APROVADAS**
        5. aprovar  -> Dispara envio dos aprovados
        """)
        return

    comando = sys.argv[1].lower()

    if comando == "extrair":
        comando_extrair()
    elif comando == "gerar":
        comando_gerar()
    elif comando == "aprovar":
        comando_aprovar()
    elif comando == "status":
        comando_status()
    else:
        print(f"❌ Comando desconhecido: {comando}")
        print("   Use: extrair, gerar, aprovar ou status")


if __name__ == "__main__":
    main()
