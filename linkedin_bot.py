"""
LinkedIn Automation Bot
Envia convites de conexão e mensagens personalizadas

Desenvolvido por: João Bruno Palermo
GitHub: https://github.com/joaobrunopalermo
Versão: 2.0

AVISO: Use com moderação para evitar restrições do LinkedIn
"""

import time
import random
import csv
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# ============================================
# CONFIGURAÇÕES - EDITE AQUI
# ============================================

# Suas credenciais do LinkedIn
EMAIL = "seu_email@example.com"
SENHA = "sua_senha_aqui"

# Arquivos de entrada
ARQUIVO_URLS = "urls.csv"  # ou "urls.txt" para arquivo simples
ARQUIVO_TEMPLATE = "template.txt"

# Modo de operação
# Opções: "convites", "convites_com_mensagem", "mensagens"
MODO = "convites_com_mensagem"

# Configurações de segurança
DELAY_MIN = 3  # Segundos mínimos entre ações
DELAY_MAX = 7  # Segundos máximos entre ações
MAX_CONVITES = 50  # Máximo de convites/mensagens por execução
TIMEOUT = 15  # Timeout para elementos da página

# Arquivo de log
ARQUIVO_LOG = "log_envios.csv"

# ============================================
# CLASSES E FUNÇÕES
# ============================================

class LinkedInBot:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.contador_enviados = 0
        self.log_data = []
        
    def inicializar_driver(self):
        """Inicializa o navegador Chrome"""
        print("🚀 Iniciando navegador...")
        
        chrome_options = Options()
        # Descomente a linha abaixo para modo headless (sem interface gráfica)
        # chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Simula um navegador real
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        self.wait = WebDriverWait(self.driver, TIMEOUT)
        
        print("✅ Navegador iniciado com sucesso!")
        
    def fazer_login(self):
        """Faz login no LinkedIn"""
        print("\n🔐 Fazendo login no LinkedIn...")
        
        try:
            self.driver.get("https://www.linkedin.com/login")
            time.sleep(random.uniform(2, 4))
            
            # Preenche email
            email_field = self.wait.until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            email_field.send_keys(EMAIL)
            time.sleep(random.uniform(0.5, 1.5))
            
            # Preenche senha
            password_field = self.driver.find_element(By.ID, "password")
            password_field.send_keys(SENHA)
            time.sleep(random.uniform(0.5, 1.5))
            
            # Clica no botão de login
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            
            # Aguarda carregar a página inicial
            time.sleep(5)
            
            # Verifica se login foi bem-sucedido
            if "feed" in self.driver.current_url or "check" not in self.driver.current_url:
                print("✅ Login realizado com sucesso!")
                return True
            else:
                print("⚠️ Pode haver verificação adicional (captcha ou 2FA)")
                print("Complete manualmente se necessário e pressione ENTER")
                input()
                return True
                
        except Exception as e:
            print(f"❌ Erro no login: {str(e)}")
            return False
    
    def delay_aleatorio(self):
        """Adiciona delay aleatório entre ações"""
        delay = random.uniform(DELAY_MIN, DELAY_MAX)
        time.sleep(delay)
    
    def enviar_convite(self, url, mensagem=None, dados_perfil=None):
        """Envia convite de conexão"""
        try:
            print(f"\n📨 Acessando perfil: {url}")
            self.driver.get(url)
            time.sleep(random.uniform(2, 4))
            
            nome = "Desconhecido"
            
            # Tenta extrair nome do perfil
            try:
                nome_element = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "h1.text-heading-xlarge"))
                )
                nome = nome_element.text
                print(f"👤 Perfil: {nome}")
            except:
                print("⚠️ Não foi possível extrair o nome")
            
            # Procura botão "Conectar"
            try:
                # Tenta diferentes variações de botão
                botoes = self.driver.find_elements(By.TAG_NAME, "button")
                botao_conectar = None
                
                for botao in botoes:
                    texto = botao.text.lower()
                    if "conectar" in texto or "connect" in texto:
                        botao_conectar = botao
                        break
                
                if not botao_conectar:
                    print("⚠️ Botão 'Conectar' não encontrado - pode já ser conexão")
                    self.registrar_log(url, nome, "já_conectado", "convite", "")
                    return False
                
                botao_conectar.click()
                time.sleep(random.uniform(1, 2))
                
                # Se tiver mensagem personalizada
                if mensagem and MODO == "convites_com_mensagem":
                    try:
                        # Procura botão "Adicionar nota"
                        botao_nota = self.wait.until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "button[aria-label*='nota'], button[aria-label*='note']"))
                        )
                        botao_nota.click()
                        time.sleep(1)
                        
                        # Personaliza mensagem com dados do perfil
                        msg_personalizada = self.personalizar_mensagem(mensagem, nome, dados_perfil)
                        
                        # Limita a 300 caracteres (limite do LinkedIn)
                        if len(msg_personalizada) > 300:
                            msg_personalizada = msg_personalizada[:297] + "..."
                            print("⚠️ Mensagem truncada para 300 caracteres")
                        
                        # Preenche mensagem
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
                
                print("✅ Convite enviado com sucesso!")
                self.contador_enviados += 1
                self.registrar_log(url, nome, "sucesso", "convite", mensagem if mensagem else "")
                return True
                
            except TimeoutException:
                print("⏱️ Timeout - elemento não encontrado")
                self.registrar_log(url, nome, "timeout", "convite", "")
                return False
            except Exception as e:
                print(f"❌ Erro ao enviar convite: {str(e)}")
                self.registrar_log(url, nome, "erro", "convite", str(e))
                return False
                
        except Exception as e:
            print(f"❌ Erro geral: {str(e)}")
            self.registrar_log(url, "Erro", "erro_geral", "convite", str(e))
            return False
    
    def enviar_mensagem(self, url, mensagem, dados_perfil=None):
        """Envia mensagem para conexão existente"""
        try:
            print(f"\n📨 Acessando perfil: {url}")
            self.driver.get(url)
            time.sleep(random.uniform(2, 4))
            
            nome = "Desconhecido"
            
            # Extrai nome
            try:
                nome_element = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "h1.text-heading-xlarge"))
                )
                nome = nome_element.text
                print(f"👤 Perfil: {nome}")
            except:
                pass
            
            # Procura botão "Mensagem"
            try:
                botao_mensagem = self.wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label*='Mensagem'], button[aria-label*='Message']"))
                )
                botao_mensagem.click()
                time.sleep(2)
                
                # Personaliza mensagem
                msg_personalizada = self.personalizar_mensagem(mensagem, nome, dados_perfil)
                
                # Preenche mensagem
                campo_mensagem = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.msg-form__contenteditable"))
                )
                campo_mensagem.send_keys(msg_personalizada)
                time.sleep(1)
                
                print(f"📝 Mensagem: {msg_personalizada[:50]}...")
                
                # Envia
                botao_enviar = self.wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.msg-form__send-button"))
                )
                botao_enviar.click()
                
                print("✅ Mensagem enviada com sucesso!")
                self.contador_enviados += 1
                self.registrar_log(url, nome, "sucesso", "mensagem", msg_personalizada)
                return True
                
            except Exception as e:
                print(f"❌ Erro ao enviar mensagem: {str(e)}")
                self.registrar_log(url, nome, "erro", "mensagem", str(e))
                return False
                
        except Exception as e:
            print(f"❌ Erro geral: {str(e)}")
            self.registrar_log(url, "Erro", "erro_geral", "mensagem", str(e))
            return False
    
    def personalizar_mensagem(self, template, nome, dados_perfil):
        """Personaliza mensagem com dados do perfil"""
        mensagem = template
        
        # Remove saudações formais que possam estar duplicadas
        primeiro_nome = nome.split()[0] if nome != "Desconhecido" else nome
        
        # Substitui variáveis
        mensagem = mensagem.replace("{nome}", primeiro_nome)
        mensagem = mensagem.replace("{nome_completo}", nome)
        
        if dados_perfil:
            for chave, valor in dados_perfil.items():
                mensagem = mensagem.replace(f"{{{chave}}}", str(valor))
        
        return mensagem
    
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
            df = pd.DataFrame(self.log_data)
            
            # Adiciona ao arquivo existente ou cria novo
            try:
                df_existente = pd.read_csv(ARQUIVO_LOG)
                df = pd.concat([df_existente, df], ignore_index=True)
            except FileNotFoundError:
                pass
            
            df.to_csv(ARQUIVO_LOG, index=False, encoding='utf-8-sig')
            print(f"\n📊 Log salvo em: {ARQUIVO_LOG}")
        except Exception as e:
            print(f"⚠️ Erro ao salvar log: {str(e)}")
    
    def processar_lista(self, urls, template):
        """Processa lista de URLs"""
        total = len(urls)
        print(f"\n📋 Total de perfis: {total}")
        print(f"🎯 Modo: {MODO}")
        print(f"⚡ Limite: {MAX_CONVITES} ações")
        print(f"⏱️ Delay entre ações: {DELAY_MIN}-{DELAY_MAX}s")
        print("\n" + "="*50)
        
        for i, item in enumerate(urls, 1):
            if self.contador_enviados >= MAX_CONVITES:
                print(f"\n🛑 Limite de {MAX_CONVITES} ações atingido!")
                break
            
            print(f"\n[{i}/{total}] Processando...")
            
            # Extrai URL e dados
            if isinstance(item, dict):
                url = item.get('url', '')
                dados_perfil = item
            else:
                url = item
                dados_perfil = None
            
            if not url:
                print("⚠️ URL inválida, pulando...")
                continue
            
            # Executa ação baseada no modo
            if MODO == "mensagens":
                self.enviar_mensagem(url, template, dados_perfil)
            else:
                # convites ou convites_com_mensagem
                usar_mensagem = MODO == "convites_com_mensagem"
                self.enviar_convite(url, template if usar_mensagem else None, dados_perfil)
            
            # Delay entre ações
            if i < total and self.contador_enviados < MAX_CONVITES:
                self.delay_aleatorio()
        
        print("\n" + "="*50)
        print(f"✅ Processamento concluído!")
        print(f"📊 Total processado: {self.contador_enviados} de {total}")
    
    def fechar(self):
        """Fecha o navegador"""
        if self.driver:
            self.driver.quit()
            print("\n👋 Navegador fechado")

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
                urls = [line.strip() for line in f if line.strip()]
            return urls
    except FileNotFoundError:
        print(f"❌ Arquivo não encontrado: {arquivo}")
        return []
    except Exception as e:
        print(f"❌ Erro ao ler arquivo: {str(e)}")
        return []

def carregar_template(arquivo):
    """Carrega template de mensagem"""
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"❌ Arquivo não encontrado: {arquivo}")
        return ""
    except Exception as e:
        print(f"❌ Erro ao ler template: {str(e)}")
        return ""

def validar_configuracao():
    """Valida configurações antes de executar"""
    erros = []
    
    if EMAIL == "seu_email@example.com":
        erros.append("❌ Configure seu email no script")
    
    if SENHA == "sua_senha_aqui":
        erros.append("❌ Configure sua senha no script")
    
    if MODO not in ["convites", "convites_com_mensagem", "mensagens"]:
        erros.append(f"❌ Modo inválido: {MODO}")
    
    if erros:
        print("\n🚨 ERROS DE CONFIGURAÇÃO:")
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
    ║   LinkedIn Automation Bot v1.0             ║
    ║   ⚠️  Use com responsabilidade             ║
    ╚════════════════════════════════════════════╝
    """)
    
    # Valida configuração
    if not validar_configuracao():
        return
    
    # Carrega dados
    print("📂 Carregando arquivos...")
    urls = carregar_urls(ARQUIVO_URLS)
    template = carregar_template(ARQUIVO_TEMPLATE) if MODO != "convites" else ""
    
    if not urls:
        print("❌ Nenhuma URL para processar!")
        return
    
    print(f"✅ {len(urls)} URLs carregadas")
    
    if template:
        print(f"✅ Template carregado ({len(template)} caracteres)")
    
    # Confirmação
    print(f"\n⚠️  Você está prestes a enviar {min(len(urls), MAX_CONVITES)} {MODO}")
    resposta = input("Deseja continuar? (s/n): ").lower()
    
    if resposta != 's':
        print("❌ Operação cancelada")
        return
    
    # Executa bot
    bot = LinkedInBot()
    
    try:
        bot.inicializar_driver()
        
        if bot.fazer_login():
            bot.processar_lista(urls, template)
            bot.salvar_log()
        else:
            print("❌ Não foi possível fazer login")
    
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrompido pelo usuário")
        bot.salvar_log()
    
    except Exception as e:
        print(f"\n❌ Erro fatal: {str(e)}")
        bot.salvar_log()
    
    finally:
        bot.fechar()
    
    print("\n✅ Processo finalizado!")
    print(f"📊 Confira o log em: {ARQUIVO_LOG}")

if __name__ == "__main__":
    main()
