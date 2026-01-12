#!/usr/bin/env python3
"""
Script de Setup Inicial
LinkedIn Automation Bot por João Bruno Palermo

Este script ajuda na configuração inicial do projeto
"""

import os
import sys
import shutil

def print_header():
    print("""
    ╔════════════════════════════════════════════════════════╗
    ║                                                        ║
    ║   LinkedIn Automation Bot - Setup Inicial             ║
    ║   Por: João Bruno Palermo                             ║
    ║                                                        ║
    ╚════════════════════════════════════════════════════════╝
    """)

def check_python_version():
    """Verifica versão do Python"""
    print("\n🐍 Verificando versão do Python...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - MUITO ANTIGO")
        print("⚠️  Necessário Python 3.8 ou superior")
        return False

def install_dependencies():
    """Instala dependências"""
    print("\n📦 Instalando dependências...")
    
    if not os.path.exists('requirements.txt'):
        print("❌ Arquivo requirements.txt não encontrado!")
        return False
    
    print("Executando: pip install -r requirements.txt")
    resposta = input("Continuar? (s/n): ").lower()
    
    if resposta == 's':
        import subprocess
        try:
            result = subprocess.run(
                ['pip', 'install', '-r', 'requirements.txt', '--break-system-packages'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print("✅ Dependências instaladas com sucesso!")
                return True
            else:
                print("⚠️ Erro na instalação:")
                print(result.stderr)
                return False
        except Exception as e:
            print(f"❌ Erro: {str(e)}")
            return False
    else:
        print("⏭️ Pulando instalação de dependências")
        return True

def create_config_file():
    """Cria arquivo config.py a partir do exemplo"""
    print("\n⚙️ Configurando arquivo de credenciais...")
    
    if os.path.exists('config.py'):
        print("⚠️ Arquivo config.py já existe!")
        resposta = input("Deseja sobrescrevê-lo? (s/n): ").lower()
        if resposta != 's':
            print("⏭️ Mantendo config.py existente")
            return True
    
    if not os.path.exists('config.example.py'):
        print("❌ Arquivo config.example.py não encontrado!")
        return False
    
    try:
        shutil.copy('config.example.py', 'config.py')
        print("✅ Arquivo config.py criado!")
        print("\n📝 PRÓXIMO PASSO:")
        print("   Edite o arquivo config.py com suas credenciais:")
        print("   nano config.py")
        print("\n⚠️  IMPORTANTE: Nunca commite config.py no Git!")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar config.py: {str(e)}")
        return False

def create_urls_file():
    """Cria arquivo de URLs personalizado"""
    print("\n📋 Configurando arquivo de URLs...")
    
    nome_arquivo = input("Nome do arquivo de URLs (padrão: minhas_urls.csv): ").strip()
    if not nome_arquivo:
        nome_arquivo = "minhas_urls.csv"
    
    if os.path.exists(nome_arquivo):
        print(f"⚠️ Arquivo {nome_arquivo} já existe!")
        return True
    
    print(f"\nCriando {nome_arquivo}...")
    
    with open(nome_arquivo, 'w', encoding='utf-8') as f:
        f.write("nome,url,empresa,cargo\n")
        f.write("# Adicione seus leads aqui\n")
        f.write("# Exemplo:\n")
        f.write("# João Silva,https://www.linkedin.com/in/joaosilva/,Tech Corp,Desenvolvedor\n")
    
    print(f"✅ Arquivo {nome_arquivo} criado!")
    print(f"\n📝 Edite este arquivo e adicione suas URLs:")
    print(f"   nano {nome_arquivo}")
    
    return True

def show_next_steps():
    """Mostra próximos passos"""
    print("\n" + "="*60)
    print("🎉 SETUP CONCLUÍDO!")
    print("="*60)
    
    print("\n📝 PRÓXIMOS PASSOS:\n")
    
    print("1️⃣  Configure suas credenciais:")
    print("   nano config.py")
    print("   (Edite LINKEDIN_EMAIL e LINKEDIN_PASSWORD)\n")
    
    print("2️⃣  Adicione suas URLs:")
    print("   nano minhas_urls.csv")
    print("   (ou o nome que você escolheu)\n")
    
    print("3️⃣  Teste a instalação:")
    print("   python verificar_instalacao.py\n")
    
    print("4️⃣  Execute o bot:")
    print("   python linkedin_bot.py       # Versão simples")
    print("   python linkedin_bot_ia.py    # Versão IA\n")
    
    print("📚 DOCUMENTAÇÃO:")
    print("   cat README.md              # Visão geral")
    print("   cat GUIA_TERMINAL.md       # Guia de uso")
    print("   cat GUIA_IA.md            # Guia da versão IA\n")
    
    print("💡 DICAS:")
    print("   • Comece com MAX_CONVITES = 10 para testar")
    print("   • Leia a documentação antes de começar")
    print("   • Use o configurador interativo: python configurador.py")
    print("   • Veja a comparação: python demo_comparacao.py\n")
    
    print("="*60)
    print("Desenvolvido por João Bruno Palermo")
    print("GitHub: https://github.com/joaobrunopalermo")
    print("="*60)

def main():
    """Função principal"""
    print_header()
    
    print("\nBem-vindo ao setup inicial do LinkedIn Automation Bot!")
    print("Este script vai te ajudar a configurar tudo.\n")
    
    # Verificar Python
    if not check_python_version():
        print("\n❌ Atualize o Python antes de continuar")
        sys.exit(1)
    
    # Instalar dependências
    print("\n" + "-"*60)
    resposta = input("\nDeseja instalar as dependências agora? (s/n): ").lower()
    if resposta == 's':
        if not install_dependencies():
            print("\n⚠️ Erro na instalação de dependências")
            print("Você pode instalá-las manualmente depois:")
            print("pip install -r requirements.txt")
    
    # Criar config.py
    print("\n" + "-"*60)
    resposta = input("\nDeseja criar arquivo de configuração? (s/n): ").lower()
    if resposta == 's':
        create_config_file()
    
    # Criar arquivo de URLs
    print("\n" + "-"*60)
    resposta = input("\nDeseja criar arquivo de URLs personalizado? (s/n): ").lower()
    if resposta == 's':
        create_urls_file()
    
    # Mostrar próximos passos
    show_next_steps()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Setup interrompido pelo usuário")
        print("Execute novamente quando quiser: python setup.py")
        sys.exit(0)
