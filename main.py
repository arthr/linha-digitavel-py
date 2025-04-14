import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from dotenv import load_dotenv
import logging

from ui import MainWindow
from db import db_connection

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Verificar se o arquivo .env existe
if not os.path.exists('.env'):
    logger.warning("Arquivo .env não encontrado. Criando arquivo de exemplo...")
    with open('.env', 'w') as f:
        f.write("""# Configurações de conexão com o banco de dados
DB_SERVER=seu_servidor.amazonaws.com
DB_DATABASE=wba
DB_USERNAME=seu_usuario
DB_PASSWORD=sua_senha

# Configurações fixas para a linha digitável
BANCO=341
MOEDA=9
CARTEIRA=109
AGENCIA=1704
FIDC_CONTA=26957
FIDC_DAC_CONTA=8
SEC_CONTA=26957
SEC_DAC_CONTA=8
""")

# Carregar variáveis de ambiente
load_dotenv()

def main():
    """Função principal que inicia a aplicação."""
    app = QApplication(sys.argv)
    app.setApplicationName("Gerador de Linha Digitável - WBA")
    
    # Verificar se as variáveis de ambiente estão configuradas
    required_env_vars = ['DB_SERVER', 'DB_DATABASE', 'DB_USERNAME', 'DB_PASSWORD',
                         'BANCO', 'MOEDA', 'CARTEIRA', 'AGENCIA', 'FIDC_CONTA', 'FIDC_DAC_CONTA', 'SEC_CONTA', 'SEC_DAC_CONTA']
    
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(f"Variáveis de ambiente não configuradas: {', '.join(missing_vars)}")
        from PyQt5.QtWidgets import QMessageBox
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Erro de Configuração")
        msg.setText("Configuração Incompleta")
        msg.setInformativeText(f"As seguintes variáveis de ambiente não estão configuradas no arquivo .env:\n{', '.join(missing_vars)}")
        msg.setDetailedText("Edite o arquivo .env na raiz do projeto e configure as variáveis necessárias.")
        msg.exec_()
        return 1
    
    # Testar conexão com o banco de dados
    if not db_connection.connect():
        from PyQt5.QtWidgets import QMessageBox
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Erro de Conexão")
        msg.setText("Não foi possível conectar ao banco de dados.")
        msg.setInformativeText("Verifique as configurações de conexão no arquivo .env")
        msg.exec_()
        return 1
    
    logger.info("Aplicação iniciada com sucesso")
    window = MainWindow()
    window.show()
    
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main()) 