"""
LinkedIn Automation Bot com Cadência
Envia convites e mensagens em sequência programada

Desenvolvido por: João Bruno Palermo
GitHub: https://github.com/joaobrunopalermo
Versão: 3.1 - Com cadências separadas para novos contatos e conexões existentes

AVISO: Use com moderação para evitar restrições do LinkedIn
"""

import time
import random
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import pytz
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# ============================================
# CONFIGURAÇÕES BÁSICAS
# ============================================

EMAIL = os.getenv("LINKEDIN_EMAIL", "")
SENHA = os.getenv("LINKEDIN_PASSWORD", "")

# Arquivos
ARQUIVO_URLS = "config/urls.csv"
ARQUIVO_CADENCIA = "config/cadencia.json"
ARQUIVO_ESTADO = "data/estado_cadencia.json"
ARQUIVO_LOG = "data/log_envios.csv"

TIMEOUT = 15

# ============================================
# GERENCIADOR DE CADÊNCIA
# ============================================

class CadenciaManager:
    def __init__(self):
        self.config = self.carregar_config()
        self.estado = self.carregar_estado()
        self.fuso = pytz.timezone(self.config['horarios']['fuso_horario'])

    def carregar_config(self):
        """Carrega configuração de cadência"""
        try:
            with open(ARQUIVO_CADENCIA, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Arquivo de cadência não encontrado: {ARQUIVO_CADENCIA}")
            return self._config_padrao()

    def _config_padrao(self):
        """Retorna configuração padrão"""
        return {
            "ativo": True,
            "horarios": {
                "janelas": [{"inicio": "09:00", "fim": "18:00"}],
                "dias_semana": [0, 1, 2, 3, 4],
                "fuso_horario": "America/Sao_Paulo"
            },
            "limites": {
                "max_por_dia": 25,
                "max_por_hora": 10,
                "intervalo_min_segundos": 60,
                "intervalo_max_segundos": 180
            },
            "sequencia": {"ativo": False, "etapas": []},
            "execucao": {"modo": "continuo", "verificar_intervalo_minutos": 5}
        }

    def carregar_estado(self):
        """Carrega estado da execução"""
        try:
            with open(ARQUIVO_ESTADO, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return self._estado_inicial()

    def _estado_inicial(self):
        """Retorna estado inicial"""
        return {
            "ultima_execucao": None,
            "envios_hoje": 0,
            "envios_hora_atual": 0,
            "hora_atual": None,
            "data_atual": None,
            "contatos": {}  # Armazena info de cada contato incluindo tipo (novo/conexao)
        }

    def salvar_estado(self):
        """Salva estado atual"""
        os.makedirs(os.path.dirname(ARQUIVO_ESTADO), exist_ok=True)
        with open(ARQUIVO_ESTADO, 'w', encoding='utf-8') as f:
            json.dump(self.estado, f, indent=2, ensure_ascii=False)

    def agora(self):
        """Retorna datetime atual no fuso configurado"""
        return datetime.now(self.fuso)

    def resetar_contadores_se_necessario(self):
        """Reseta contadores diários/horários"""
        agora = self.agora()
        data_atual = agora.strftime("%Y-%m-%d")
        hora_atual = agora.hour

        # Reset diário
        if self.estado['data_atual'] != data_atual:
            self.estado['data_atual'] = data_atual
            self.estado['envios_hoje'] = 0
            self.estado['envios_hora_atual'] = 0
            self.estado['hora_atual'] = hora_atual
            print(f"📅 Novo dia: {data_atual} - Contadores resetados")

        # Reset horário
        if self.estado['hora_atual'] != hora_atual:
            self.estado['hora_atual'] = hora_atual
            self.estado['envios_hora_atual'] = 0
            print(f"⏰ Nova hora: {hora_atual}h - Contador horário resetado")

        self.salvar_estado()

    def dentro_janela_horario(self):
        """Verifica se está dentro da janela de horário permitida"""
        agora = self.agora()
        dia_semana = agora.weekday()

        # Verifica dia da semana
        if dia_semana not in self.config['horarios']['dias_semana']:
            return False, f"Dia {dia_semana} não está na lista de dias permitidos"

        # Verifica janelas de horário
        hora_atual = agora.strftime("%H:%M")
        for janela in self.config['horarios']['janelas']:
            if janela['inicio'] <= hora_atual <= janela['fim']:
                return True, f"Dentro da janela {janela['inicio']}-{janela['fim']}"

        return False, f"Fora das janelas de horário ({hora_atual})"

    def pode_enviar(self):
        """Verifica se pode enviar mais mensagens"""
        self.resetar_contadores_se_necessario()

        limites = self.config['limites']

        # Verifica limite diário
        if self.estado['envios_hoje'] >= limites['max_por_dia']:
            return False, f"Limite diário atingido ({limites['max_por_dia']})"

        # Verifica limite por hora
        if self.estado['envios_hora_atual'] >= limites['max_por_hora']:
            return False, f"Limite por hora atingido ({limites['max_por_hora']})"

        # Verifica janela de horário
        dentro, motivo = self.dentro_janela_horario()
        if not dentro:
            return False, motivo

        return True, "OK"

    def registrar_envio(self, url, sucesso=True):
        """Registra um envio realizado"""
        if sucesso:
            self.estado['envios_hoje'] += 1
            self.estado['envios_hora_atual'] += 1
        self.estado['ultima_execucao'] = self.agora().isoformat()
        self.salvar_estado()

    def get_intervalo(self):
        """Retorna intervalo aleatório entre ações"""
        limites = self.config['limites']
        return random.uniform(
            limites['intervalo_min_segundos'],
            limites['intervalo_max_segundos']
        )

    def proxima_janela(self):
        """Calcula quando será a próxima janela de envio"""
        agora = self.agora()

        # Verifica próximas janelas hoje
        for janela in self.config['horarios']['janelas']:
            inicio = datetime.strptime(janela['inicio'], "%H:%M").time()
            if agora.time() < inicio:
                proxima = agora.replace(
                    hour=inicio.hour,
                    minute=inicio.minute,
                    second=0
                )
                return proxima

        # Se não há mais janelas hoje, pega primeira de amanhã
        amanha = agora + timedelta(days=1)
        primeira_janela = self.config['horarios']['janelas'][0]
        inicio = datetime.strptime(primeira_janela['inicio'], "%H:%M").time()
        proxima = amanha.replace(
            hour=inicio.hour,
            minute=inicio.minute,
            second=0
        )

        # Pula para próximo dia permitido
        while proxima.weekday() not in self.config['horarios']['dias_semana']:
            proxima += timedelta(days=1)

        return proxima

    # ============================================
    # SISTEMA DE SEQUÊNCIA (MULTI-STEP) COM DUAS CADÊNCIAS
    # ============================================

    def get_etapa_contato(self, url):
        """Retorna a etapa atual de um contato"""
        if url not in self.estado['contatos']:
            self.estado['contatos'][url] = {
                "tipo": None,  # 'novo' ou 'conexao_existente'
                "etapa_atual": 0,
                "ultima_acao": None,
                "historico": []
            }
        return self.estado['contatos'][url]

    def definir_tipo_contato(self, url, tipo):
        """Define o tipo do contato (novo ou conexao_existente)"""
        contato = self.get_etapa_contato(url)
        if contato['tipo'] is None:  # Só define se ainda não foi definido
            contato['tipo'] = tipo
            self.estado['contatos'][url] = contato
            self.salvar_estado()
        return contato['tipo']

    def get_sequencia_para_tipo(self, tipo):
        """Retorna a sequência correta baseada no tipo de contato"""
        if tipo == 'conexao_existente':
            return self.config.get('sequencia_conexoes_existentes', {'ativo': False, 'etapas': []})
        else:
            return self.config.get('sequencia_novos_contatos', {'ativo': False, 'etapas': []})

    def get_proxima_etapa(self, url, tipo_contato=None):
        """Retorna a próxima etapa a ser executada para um contato"""
        contato = self.get_etapa_contato(url)

        # Usa o tipo já definido ou o novo tipo passado
        tipo = contato['tipo'] or tipo_contato

        if not tipo:
            # Tipo ainda não definido - será detectado pelo bot
            return None, None

        sequencia = self.get_sequencia_para_tipo(tipo)

        if not sequencia.get('ativo', False):
            # Se sequência não está ativa, retorna etapa 1 sempre
            etapas = sequencia.get('etapas', [])
            return (etapas[0], tipo) if etapas else (None, tipo)

        etapa_atual = contato['etapa_atual']
        etapas = sequencia.get('etapas', [])

        if etapa_atual >= len(etapas):
            return None, tipo  # Sequência completa

        proxima_etapa = etapas[etapa_atual]

        # Verifica dias de espera
        if contato['ultima_acao']:
            ultima = datetime.fromisoformat(contato['ultima_acao'])
            dias_passados = (self.agora() - ultima.replace(tzinfo=self.fuso)).days

            if dias_passados < proxima_etapa.get('dias_espera', 0):
                return None, tipo  # Ainda não é hora

        return proxima_etapa, tipo

    def registrar_etapa_concluida(self, url, etapa_id, tipo_contato, sucesso=True):
        """Registra conclusão de uma etapa"""
        contato = self.get_etapa_contato(url)

        # Garante que o tipo está definido
        if contato['tipo'] is None:
            contato['tipo'] = tipo_contato

        contato['historico'].append({
            "etapa_id": etapa_id,
            "tipo": tipo_contato,
            "data": self.agora().isoformat(),
            "sucesso": sucesso
        })

        if sucesso:
            contato['etapa_atual'] += 1
            contato['ultima_acao'] = self.agora().isoformat()

        self.estado['contatos'][url] = contato
        self.salvar_estado()

    def get_contatos_pendentes(self, urls):
        """Retorna contatos que têm ações pendentes (para contatos já tipados)"""
        pendentes = []

        for item in urls:
            url = item.get('url', item) if isinstance(item, dict) else item
            contato = self.get_etapa_contato(url)

            # Se tipo já foi definido, verifica próxima etapa
            if contato['tipo']:
                etapa, tipo = self.get_proxima_etapa(url)
                if etapa:
                    pendentes.append({
                        "url": url,
                        "dados": item if isinstance(item, dict) else {"url": url},
                        "etapa": etapa,
                        "tipo": tipo
                    })
            else:
                # Contato novo - precisa detectar tipo
                pendentes.append({
                    "url": url,
                    "dados": item if isinstance(item, dict) else {"url": url},
                    "etapa": None,  # Será definida após detectar tipo
                    "tipo": None    # Será detectado pelo bot
                })

        return pendentes

    def status(self):
        """Retorna status atual da cadência"""
        pode, motivo = self.pode_enviar()
        dentro_janela, janela_motivo = self.dentro_janela_horario()

        return {
            "pode_enviar": pode,
            "motivo": motivo,
            "dentro_janela": dentro_janela,
            "janela_motivo": janela_motivo,
            "envios_hoje": self.estado['envios_hoje'],
            "limite_diario": self.config['limites']['max_por_dia'],
            "envios_hora": self.estado['envios_hora_atual'],
            "limite_hora": self.config['limites']['max_por_hora'],
            "proxima_janela": self.proxima_janela().isoformat() if not dentro_janela else None
        }


# ============================================
# BOT LINKEDIN COM CADÊNCIA
# ============================================

class LinkedInBotCadencia:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.cadencia = CadenciaManager()
        self.log_data = []

    def inicializar_driver(self):
        """Inicializa o navegador Chrome"""
        print("🚀 Iniciando navegador...")

        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        self.wait = WebDriverWait(self.driver, TIMEOUT)
        print("✅ Navegador iniciado!")

    def fazer_login(self):
        """Faz login no LinkedIn"""
        print("\n🔐 Fazendo login...")

        try:
            self.driver.get("https://www.linkedin.com/login")
            time.sleep(random.uniform(2, 4))

            email_field = self.wait.until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            email_field.send_keys(EMAIL)
            time.sleep(random.uniform(0.5, 1.5))

            password_field = self.driver.find_element(By.ID, "password")
            password_field.send_keys(SENHA)
            time.sleep(random.uniform(0.5, 1.5))

            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()

            time.sleep(5)

            if "feed" in self.driver.current_url or "check" not in self.driver.current_url:
                print("✅ Login realizado!")
                return True
            else:
                print("⚠️ Verificação adicional necessária")
                print("Complete manualmente e pressione ENTER")
                input()
                return True

        except Exception as e:
            print(f"❌ Erro no login: {str(e)}")
            return False

    def carregar_template(self, arquivo):
        """Carrega template de mensagem"""
        try:
            with open(arquivo, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except FileNotFoundError:
            print(f"⚠️ Template não encontrado: {arquivo}")
            return ""

    def personalizar_mensagem(self, template, nome, dados_perfil):
        """Personaliza mensagem com dados do perfil"""
        mensagem = template
        primeiro_nome = nome.split()[0] if nome != "Desconhecido" else nome

        mensagem = mensagem.replace("{nome}", primeiro_nome)
        mensagem = mensagem.replace("{nome_completo}", nome)

        if dados_perfil:
            for chave, valor in dados_perfil.items():
                mensagem = mensagem.replace(f"{{{chave}}}", str(valor))

        return mensagem

    def detectar_tipo_contato(self, url):
        """
        Detecta se o perfil é uma conexão existente ou novo contato.
        Retorna: 'conexao_existente' ou 'novo'
        """
        try:
            print(f"\n🔍 Detectando tipo de contato: {url}")
            self.driver.get(url)
            time.sleep(random.uniform(2, 4))

            # Fecha popups que podem atrapalhar
            try:
                dismiss_buttons = self.driver.find_elements(By.CSS_SELECTOR,
                    "button[aria-label*='Dismiss'], button[data-test-modal-close-btn]")
                for btn in dismiss_buttons:
                    try:
                        btn.click()
                        time.sleep(0.5)
                    except:
                        pass
            except:
                pass

            # Verifica se tem botão "Mensagem" visível (indica conexão existente)
            botoes = self.driver.find_elements(By.TAG_NAME, "button")

            tem_botao_mensagem = False
            tem_botao_conectar = False

            for botao in botoes:
                try:
                    texto = botao.text.lower()
                    aria_label = (botao.get_attribute("aria-label") or "").lower()

                    # Verifica botão de mensagem
                    if "mensagem" in texto or "message" in texto or "mensagem" in aria_label or "message" in aria_label:
                        tem_botao_mensagem = True

                    # Verifica botão de conectar
                    if "conectar" in texto or "connect" in texto:
                        tem_botao_conectar = True
                except:
                    pass

            # Também verifica pelo grau de conexão exibido na página
            try:
                # LinkedIn mostra "1º" ou "1st" para conexões de primeiro grau
                page_source = self.driver.page_source.lower()
                if "1º grau" in page_source or "1st degree" in page_source or "1º" in page_source:
                    tem_botao_mensagem = True
            except:
                pass

            if tem_botao_mensagem and not tem_botao_conectar:
                print("✅ Tipo detectado: CONEXÃO EXISTENTE")
                return "conexao_existente"
            else:
                print("✅ Tipo detectado: NOVO CONTATO")
                return "novo"

        except Exception as e:
            print(f"⚠️ Erro ao detectar tipo: {str(e)} - Assumindo novo contato")
            return "novo"

    def enviar_convite(self, url, mensagem=None, dados_perfil=None):
        """Envia convite de conexão"""
        try:
            print(f"\n📨 Acessando: {url}")
            self.driver.get(url)
            time.sleep(random.uniform(2, 4))

            nome = "Desconhecido"

            try:
                nome_element = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "h1.text-heading-xlarge"))
                )
                nome = nome_element.text
                print(f"👤 Perfil: {nome}")
            except:
                pass

            # Fecha popups
            try:
                dismiss_buttons = self.driver.find_elements(By.CSS_SELECTOR,
                    "button[aria-label*='Dismiss'], button[data-test-modal-close-btn]")
                for btn in dismiss_buttons:
                    try:
                        btn.click()
                        time.sleep(0.5)
                    except:
                        pass
            except:
                pass

            # Procura botão Conectar
            botoes = self.driver.find_elements(By.TAG_NAME, "button")
            botao_conectar = None

            for botao in botoes:
                texto = botao.text.lower()
                if "conectar" in texto or "connect" in texto:
                    botao_conectar = botao
                    break

            if not botao_conectar:
                print("⚠️ Botão 'Conectar' não encontrado")
                self.registrar_log(url, nome, "já_conectado", "convite", "")
                return False, "já_conectado"

            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", botao_conectar)
            time.sleep(1)

            try:
                botao_conectar.click()
            except:
                self.driver.execute_script("arguments[0].click();", botao_conectar)
            time.sleep(random.uniform(1, 2))

            # Adiciona nota se houver mensagem
            if mensagem:
                try:
                    botao_nota = self.wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "button[aria-label*='nota'], button[aria-label*='note']"))
                    )
                    botao_nota.click()
                    time.sleep(1)

                    msg_personalizada = self.personalizar_mensagem(mensagem, nome, dados_perfil)

                    if len(msg_personalizada) > 300:
                        msg_personalizada = msg_personalizada[:297] + "..."

                    campo_mensagem = self.wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "textarea[name='message']"))
                    )
                    campo_mensagem.send_keys(msg_personalizada)
                    time.sleep(1)

                    print(f"📝 Mensagem: {msg_personalizada[:50]}...")
                except Exception as e:
                    print(f"⚠️ Não foi possível adicionar nota: {str(e)}")

            # Confirma envio
            botao_enviar = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label*='Enviar'], button[aria-label*='Send']"))
            )
            botao_enviar.click()

            print("✅ Convite enviado!")
            self.registrar_log(url, nome, "sucesso", "convite", mensagem if mensagem else "")
            return True, "sucesso"

        except Exception as e:
            print(f"❌ Erro: {str(e)}")
            self.registrar_log(url, "Erro", "erro", "convite", str(e))
            return False, "erro"

    def enviar_mensagem(self, url, mensagem, dados_perfil=None):
        """Envia mensagem para conexão existente"""
        try:
            print(f"\n📨 Acessando: {url}")
            self.driver.get(url)
            time.sleep(random.uniform(2, 4))

            nome = "Desconhecido"

            try:
                nome_element = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "h1.text-heading-xlarge"))
                )
                nome = nome_element.text
                print(f"👤 Perfil: {nome}")
            except:
                pass

            try:
                botao_mensagem = self.wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label*='Mensagem'], button[aria-label*='Message']"))
                )
                botao_mensagem.click()
                time.sleep(2)

                msg_personalizada = self.personalizar_mensagem(mensagem, nome, dados_perfil)

                campo_mensagem = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.msg-form__contenteditable"))
                )
                campo_mensagem.send_keys(msg_personalizada)
                time.sleep(1)

                print(f"📝 Mensagem: {msg_personalizada[:50]}...")

                botao_enviar = self.wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.msg-form__send-button"))
                )
                botao_enviar.click()

                print("✅ Mensagem enviada!")
                self.registrar_log(url, nome, "sucesso", "mensagem", msg_personalizada)
                return True, "sucesso"

            except Exception as e:
                print(f"❌ Erro: {str(e)}")
                self.registrar_log(url, nome, "erro", "mensagem", str(e))
                return False, "erro"

        except Exception as e:
            print(f"❌ Erro geral: {str(e)}")
            self.registrar_log(url, "Erro", "erro_geral", "mensagem", str(e))
            return False, "erro"

    def registrar_log(self, url, nome, status, tipo, mensagem):
        """Registra ação no log"""
        self.log_data.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "url": url,
            "nome": nome,
            "status": status,
            "tipo": tipo,
            "mensagem_enviada": mensagem[:100] if mensagem else ""
        })

    def salvar_log(self):
        """Salva log em CSV"""
        try:
            os.makedirs(os.path.dirname(ARQUIVO_LOG), exist_ok=True)
            df = pd.DataFrame(self.log_data)

            try:
                df_existente = pd.read_csv(ARQUIVO_LOG)
                df = pd.concat([df_existente, df], ignore_index=True)
            except FileNotFoundError:
                pass

            df.to_csv(ARQUIVO_LOG, index=False, encoding='utf-8-sig')
            print(f"\n📊 Log salvo: {ARQUIVO_LOG}")
        except Exception as e:
            print(f"⚠️ Erro ao salvar log: {str(e)}")

    def executar_etapa(self, contato_info):
        """Executa uma etapa da sequência para um contato"""
        url = contato_info['url']
        dados = contato_info['dados']
        etapa = contato_info.get('etapa')
        tipo_contato = contato_info.get('tipo')

        print(f"\n{'='*50}")

        # Se o tipo ainda não foi detectado, detecta agora
        if not tipo_contato:
            tipo_contato = self.detectar_tipo_contato(url)
            self.cadencia.definir_tipo_contato(url, tipo_contato)

            # Agora busca a etapa correta para esse tipo
            etapa, _ = self.cadencia.get_proxima_etapa(url, tipo_contato)

            if not etapa:
                print(f"⚠️ Sem etapa disponível para {url}")
                return False

        print(f"👤 Tipo: {'Conexão existente' if tipo_contato == 'conexao_existente' else 'Novo contato'}")
        print(f"📌 Etapa: {etapa['nome']} (ID: {etapa['id']})")

        # Carrega template
        template = self.carregar_template(etapa['template'])
        if not template:
            print(f"⚠️ Template vazio, pulando...")
            return False

        # Executa ação baseada no tipo da etapa
        if etapa['tipo'] in ['convite', 'convite_com_mensagem']:
            usar_msg = etapa['tipo'] == 'convite_com_mensagem'
            sucesso, status = self.enviar_convite(
                url,
                template if usar_msg else None,
                dados if isinstance(dados, dict) else None
            )
        else:  # mensagem
            sucesso, status = self.enviar_mensagem(
                url,
                template,
                dados if isinstance(dados, dict) else None
            )

        # Registra conclusão
        self.cadencia.registrar_etapa_concluida(url, etapa['id'], tipo_contato, sucesso)
        self.cadencia.registrar_envio(url, sucesso)

        return sucesso

    def processar_cadencia(self, urls):
        """Processa lista com sistema de cadência"""
        print("\n" + "="*50)
        print("🔄 MODO CADÊNCIA ATIVADO")
        print("="*50)

        # Mostra status inicial
        status = self.cadencia.status()
        print(f"\n📊 Status:")
        print(f"   Envios hoje: {status['envios_hoje']}/{status['limite_diario']}")
        print(f"   Envios esta hora: {status['envios_hora']}/{status['limite_hora']}")
        print(f"   Dentro da janela: {'✅' if status['dentro_janela'] else '❌'} {status['janela_motivo']}")

        if not status['pode_enviar']:
            print(f"\n⏸️ Não é possível enviar agora: {status['motivo']}")
            if status['proxima_janela']:
                print(f"   Próxima janela: {status['proxima_janela']}")
            return

        # Obtém contatos pendentes
        pendentes = self.cadencia.get_contatos_pendentes(urls)
        print(f"\n📋 Contatos com ações pendentes: {len(pendentes)}")

        if not pendentes:
            print("✅ Todos os contatos já foram processados!")
            return

        contador = 0

        for contato in pendentes:
            # Verifica se ainda pode enviar
            pode, motivo = self.cadencia.pode_enviar()
            if not pode:
                print(f"\n⏸️ Parando: {motivo}")
                break

            # Executa etapa
            sucesso = self.executar_etapa(contato)

            if sucesso:
                contador += 1

            # Delay entre ações
            if pode:
                intervalo = self.cadencia.get_intervalo()
                print(f"\n⏱️ Aguardando {intervalo:.0f}s até próxima ação...")
                time.sleep(intervalo)

        print("\n" + "="*50)
        print(f"✅ Sessão concluída! Enviados: {contador}")

        # Mostra status final
        status = self.cadencia.status()
        print(f"\n📊 Status final:")
        print(f"   Envios hoje: {status['envios_hoje']}/{status['limite_diario']}")
        if not status['dentro_janela'] and status['proxima_janela']:
            print(f"   Próxima janela: {status['proxima_janela']}")

    def modo_continuo(self, urls):
        """Executa em modo contínuo (fica rodando)"""
        print("\n🔄 MODO CONTÍNUO - Ctrl+C para parar")

        intervalo_verificacao = self.cadencia.config['execucao']['verificar_intervalo_minutos']

        while True:
            try:
                status = self.cadencia.status()

                if status['pode_enviar']:
                    self.processar_cadencia(urls)
                else:
                    print(f"\n⏸️ Aguardando: {status['motivo']}")
                    if status['proxima_janela']:
                        print(f"   Próxima janela: {status['proxima_janela']}")

                # Aguarda próxima verificação
                print(f"\n💤 Próxima verificação em {intervalo_verificacao} minutos...")
                time.sleep(intervalo_verificacao * 60)

            except KeyboardInterrupt:
                print("\n\n⚠️ Interrompido pelo usuário")
                break

    def fechar(self):
        """Fecha o navegador"""
        if self.driver:
            self.driver.quit()
            print("\n👋 Navegador fechado")

    def modo_teste(self, urls, url_especifica=None):
        """
        Modo de teste manual com confirmação a cada envio.
        Permite testar uma URL específica ou as primeiras N URLs da lista.
        """
        print("\n" + "="*50)
        print("🧪 MODO TESTE - Confirmação manual a cada envio")
        print("="*50)

        # Se URL específica foi fornecida, usa ela
        if url_especifica:
            urls_teste = [{"url": url_especifica}]
            print(f"\n🎯 Testando URL específica: {url_especifica}")
        else:
            # Pergunta quantas URLs testar
            try:
                qtd = input("\nQuantas URLs deseja testar? (padrão: 1): ").strip()
                qtd = int(qtd) if qtd else 1
                qtd = min(qtd, len(urls))  # Não exceder total
            except ValueError:
                qtd = 1

            urls_teste = urls[:qtd]
            print(f"\n📋 Testando {len(urls_teste)} URL(s)")

        # Pergunta se quer simular ou enviar de verdade
        print("\n📌 Opções de teste:")
        print("1. Apenas detectar tipo (não envia nada)")
        print("2. Simular envio (mostra o que seria enviado)")
        print("3. Enviar de verdade (com confirmação)")

        modo_teste = input("\nEscolha (1-3): ").strip()

        for i, item in enumerate(urls_teste, 1):
            url = item.get('url', item) if isinstance(item, dict) else item
            dados = item if isinstance(item, dict) else {"url": url}

            print(f"\n{'='*50}")
            print(f"[{i}/{len(urls_teste)}] URL: {url}")
            print("="*50)

            # Detecta tipo do contato
            tipo_contato = self.detectar_tipo_contato(url)

            # Busca etapa apropriada
            etapa, _ = self.cadencia.get_proxima_etapa(url, tipo_contato)

            if not etapa:
                print("⚠️ Nenhuma etapa disponível para este contato")
                continue

            # Carrega e personaliza template
            template = self.carregar_template(etapa['template'])

            # Tenta extrair nome do perfil (já estamos na página)
            nome = "Desconhecido"
            try:
                nome_element = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "h1.text-heading-xlarge"))
                )
                nome = nome_element.text
            except:
                pass

            msg_personalizada = self.personalizar_mensagem(template, nome, dados)

            # Mostra informações
            print(f"\n📊 RESUMO DO TESTE:")
            print(f"   👤 Nome: {nome}")
            print(f"   🏷️  Tipo: {'Conexão existente' if tipo_contato == 'conexao_existente' else 'Novo contato'}")
            print(f"   📌 Etapa: {etapa['nome']} (ID: {etapa['id']})")
            print(f"   📄 Tipo ação: {etapa['tipo']}")
            print(f"   📁 Template: {etapa['template']}")
            print(f"\n   📝 MENSAGEM QUE SERÁ ENVIADA:")
            print("   " + "-"*40)
            for linha in msg_personalizada.split('\n'):
                print(f"   {linha}")
            print("   " + "-"*40)
            print(f"   📏 Tamanho: {len(msg_personalizada)} caracteres")

            if len(msg_personalizada) > 300 and etapa['tipo'] in ['convite', 'convite_com_mensagem']:
                print(f"   ⚠️  AVISO: Mensagem excede 300 chars (limite convite)")

            if modo_teste == "1":
                print("\n✅ Detecção concluída (nenhum envio realizado)")
                continue

            elif modo_teste == "2":
                print("\n🔄 SIMULAÇÃO: Nenhum envio realizado")
                print(f"   Ação que seria executada: {etapa['tipo']}")
                continue

            elif modo_teste == "3":
                # Confirmação antes de enviar
                print("\n⚠️  ATENÇÃO: Isso vai enviar de verdade!")
                confirma = input("Deseja enviar? (s/n/p=pular): ").strip().lower()

                if confirma == 'n':
                    print("❌ Teste cancelado pelo usuário")
                    break
                elif confirma == 'p':
                    print("⏭️ Pulando para próximo...")
                    continue
                elif confirma == 's':
                    # Executa o envio real
                    print("\n🚀 Enviando...")

                    if etapa['tipo'] in ['convite', 'convite_com_mensagem']:
                        usar_msg = etapa['tipo'] == 'convite_com_mensagem'
                        sucesso, status = self.enviar_convite(
                            url,
                            template if usar_msg else None,
                            dados
                        )
                    else:
                        sucesso, status = self.enviar_mensagem(url, template, dados)

                    if sucesso:
                        # Registra no estado
                        self.cadencia.definir_tipo_contato(url, tipo_contato)
                        self.cadencia.registrar_etapa_concluida(url, etapa['id'], tipo_contato, True)
                        self.cadencia.registrar_envio(url, True)
                        print("✅ Envio realizado e registrado!")
                    else:
                        print(f"❌ Falha no envio: {status}")

            # Pausa entre URLs
            if i < len(urls_teste):
                continuar = input("\nContinuar para próxima URL? (s/n): ").strip().lower()
                if continuar != 's':
                    print("⏹️ Teste interrompido")
                    break

        print("\n" + "="*50)
        print("🧪 TESTE FINALIZADO")
        print("="*50)

    def validar_templates(self):
        """Valida se todos os templates existem e mostra preview"""
        print("\n" + "="*50)
        print("📄 VALIDAÇÃO DE TEMPLATES")
        print("="*50)

        # Templates de novos contatos
        print("\n📌 Sequência: NOVOS CONTATOS")
        seq_novos = self.cadencia.config.get('sequencia_novos_contatos', {})
        for etapa in seq_novos.get('etapas', []):
            template_path = etapa['template']
            template = self.carregar_template(template_path)
            status = "✅" if template else "❌"
            print(f"   {status} Etapa {etapa['id']}: {etapa['nome']}")
            print(f"      Arquivo: {template_path}")
            if template:
                print(f"      Tamanho: {len(template)} chars")
                print(f"      Preview: {template[:80]}...")
            print()

        # Templates de conexões existentes
        print("📌 Sequência: CONEXÕES EXISTENTES")
        seq_conexoes = self.cadencia.config.get('sequencia_conexoes_existentes', {})
        for etapa in seq_conexoes.get('etapas', []):
            template_path = etapa['template']
            template = self.carregar_template(template_path)
            status = "✅" if template else "❌"
            print(f"   {status} Etapa {etapa['id']}: {etapa['nome']}")
            print(f"      Arquivo: {template_path}")
            if template:
                print(f"      Tamanho: {len(template)} chars")
                print(f"      Preview: {template[:80]}...")
            print()


# ============================================
# FUNÇÕES AUXILIARES
# ============================================

def carregar_urls(arquivo):
    """Carrega URLs do arquivo"""
    try:
        if arquivo.endswith('.csv'):
            df = pd.read_csv(arquivo)
            return df.to_dict('records')
        else:
            with open(arquivo, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"❌ Arquivo não encontrado: {arquivo}")
        return []

def validar_configuracao():
    """Valida configurações"""
    erros = []

    if EMAIL == "seu_email@example.com":
        erros.append("❌ Configure seu email")

    if SENHA == "sua_senha_aqui":
        erros.append("❌ Configure sua senha")

    if erros:
        print("\n🚨 ERROS:")
        for erro in erros:
            print(erro)
        return False

    return True


# ============================================
# FUNÇÃO PRINCIPAL
# ============================================

def main():
    print("""
    ╔════════════════════════════════════════════╗
    ║   LinkedIn Bot com Cadência v3.1           ║
    ║   ⚠️  Use com responsabilidade             ║
    ╚════════════════════════════════════════════╝
    """)

    if not validar_configuracao():
        return

    # Carrega dados
    print("📂 Carregando arquivos...")
    urls = carregar_urls(ARQUIVO_URLS)

    if not urls:
        print("❌ Nenhuma URL para processar!")
        return

    print(f"✅ {len(urls)} URLs carregadas")

    # Menu de opções
    print("\n📋 Opções:")
    print("1. Executar uma sessão (com cadência)")
    print("2. Modo contínuo (fica rodando)")
    print("3. Ver status da cadência")
    print("4. Resetar estado da cadência")
    print("─" * 40)
    print("5. 🧪 MODO TESTE - Testar URLs da lista")
    print("6. 🧪 MODO TESTE - Testar URL específica")
    print("7. 📄 Validar templates")

    opcao = input("\nEscolha (1-7): ").strip()

    bot = LinkedInBotCadencia()

    try:
        if opcao == "3":
            status = bot.cadencia.status()
            print("\n📊 Status da Cadência:")
            print(f"   Pode enviar: {'✅' if status['pode_enviar'] else '❌'} - {status['motivo']}")
            print(f"   Dentro da janela: {'✅' if status['dentro_janela'] else '❌'}")
            print(f"   Envios hoje: {status['envios_hoje']}/{status['limite_diario']}")
            print(f"   Envios esta hora: {status['envios_hora']}/{status['limite_hora']}")
            if status['proxima_janela']:
                print(f"   Próxima janela: {status['proxima_janela']}")

            # Mostra contatos
            pendentes = bot.cadencia.get_contatos_pendentes(urls)
            print(f"\n   Contatos pendentes: {len(pendentes)}")

            # Mostra breakdown por tipo
            novos = sum(1 for p in pendentes if p.get('tipo') == 'novo' or p.get('tipo') is None)
            conexoes = sum(1 for p in pendentes if p.get('tipo') == 'conexao_existente')
            print(f"   - Novos/Não detectados: {novos}")
            print(f"   - Conexões existentes: {conexoes}")
            return

        elif opcao == "4":
            confirma = input("Tem certeza? Isso vai resetar todo o progresso (s/n): ")
            if confirma.lower() == 's':
                bot.cadencia.estado = bot.cadencia._estado_inicial()
                bot.cadencia.salvar_estado()
                print("✅ Estado resetado!")
            return

        elif opcao == "7":
            # Validar templates não precisa de login
            bot.validar_templates()
            return

        # Opções que precisam de login
        bot.inicializar_driver()

        if not bot.fazer_login():
            print("❌ Falha no login")
            return

        if opcao == "2":
            bot.modo_continuo(urls)
        elif opcao == "5":
            bot.modo_teste(urls)
            bot.salvar_log()
        elif opcao == "6":
            url_teste = input("\nDigite a URL do LinkedIn para testar: ").strip()
            if url_teste:
                bot.modo_teste(urls, url_especifica=url_teste)
                bot.salvar_log()
            else:
                print("❌ URL não fornecida")
        else:  # opcao == "1" ou default
            bot.processar_cadencia(urls)
            bot.salvar_log()

    except KeyboardInterrupt:
        print("\n\n⚠️ Interrompido")
        bot.salvar_log()

    except Exception as e:
        print(f"\n❌ Erro: {str(e)}")
        bot.salvar_log()

    finally:
        bot.fechar()

    print("\n✅ Finalizado!")
    print(f"📊 Log: {ARQUIVO_LOG}")


if __name__ == "__main__":
    main()
