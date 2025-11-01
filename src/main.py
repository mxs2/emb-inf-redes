"""
Monitor de Sinal Wi-Fi
Ponto de entrada da aplicação

Author: Equipe Monitor Wi-Fi
Date: 29/10/2025
"""

import sys
import logging
from pathlib import Path

# Adicionar src ao path para imports
sys.path.insert(0, str(Path(__file__).parent))

from core.wifi_scanner import WifiScanner
from core.network_scanner import NetworkScanner
from core.health_tracker import HealthTracker
from ui.gui import MonitorGUI


def setup_logging():
    """Configura sistema de logging da aplicação."""
    log_dir = Path(__file__).parent.parent / 'logs'
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / 'app.log', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)


def check_permissions():
    """
    Verifica se a aplicação tem permissões necessárias.
    
    Returns:
        bool: True se tem permissões adequadas
    """
    import platform
    
    if platform.system() == "Windows":
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            return False
    else:
        # Linux/Mac: verificar se é root
        import os
        return os.geteuid() == 0 if hasattr(os, 'geteuid') else True


def main():
    """Função principal da aplicação."""
    # Configurar logging
    logger = setup_logging()
    logger.info("Iniciando Monitor de Sinal Wi-Fi")
    
    # Verificar permissões
    if not check_permissions():
        logger.warning("Permissões insuficientes. Algumas funcionalidades podem não funcionar.")
        print("⚠️ AVISO: Execute como Administrador para funcionalidade completa")
    
    try:
        # Inicializar componentes core
        logger.info("Inicializando componentes...")
        wifi_scanner = WifiScanner()
        network_scanner = NetworkScanner()
        health_tracker = HealthTracker()
        
        # Criar e executar GUI
        logger.info("Iniciando interface gráfica...")
        app = MonitorGUI(
            wifi_scanner=wifi_scanner,
            network_scanner=network_scanner,
            health_tracker=health_tracker
        )
        
        # Iniciar aplicação
        app.run()
        
    except KeyboardInterrupt:
        logger.info("Aplicação interrompida pelo usuário")
        print("\n👋 Encerrando aplicação...")
    except Exception as e:
        logger.exception("Erro fatal na aplicação")
        print(f"❌ Erro: {str(e)}")
        return 1
    finally:
        logger.info("Aplicação encerrada")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
