"""
WifiScanner - Classe para escanear redes Wi-Fi disponíveis

Este módulo implementa scanning de redes Wi-Fi usando:
1. Comandos do sistema operacional (netsh no Windows)
2. Scapy como alternativa (requer privilégios elevados)
"""

import logging
import subprocess
import platform
from typing import List, Dict, Optional


class WifiScanner:
    """
    Classe responsável por escanear e coletar informações de redes Wi-Fi.
    
    Attributes:
        networks (list): Lista de redes Wi-Fi detectadas
        interface (str): Interface de rede sendo utilizada
    """
    
    def __init__(self):
        """Inicializa o scanner Wi-Fi."""
        self.logger = logging.getLogger(__name__)
        self.networks = []
        self.interface = None
        self.os_type = platform.system()
        
        self.logger.info(f"WifiScanner inicializado para {self.os_type}")
    
    def scan_networks(self, timeout: int = 10) -> List[Dict[str, any]]:
        """
        Escaneia redes Wi-Fi disponíveis.
        
        Args:
            timeout (int): Tempo máximo de scan em segundos. Default: 10
            
        Returns:
            list: Lista de dicionários com informações das redes
                  [{'ssid': str, 'bssid': str, 'rssi': int, 'signal_percent': int,
                    'channel': int, 'security': str}]
        
        Raises:
            PermissionError: Se não houver privilégios suficientes
            TimeoutError: Se o scan exceder o tempo limite
        """
        self.logger.info("Iniciando scan de redes Wi-Fi...")
        
        try:
            if self.os_type == "Windows":
                return self._scan_windows()
            elif self.os_type == "Linux":
                return self._scan_linux()
            elif self.os_type == "Darwin":  # macOS
                return self._scan_macos()
            else:
                self.logger.error(f"Sistema operacional não suportado: {self.os_type}")
                return []
                
        except Exception as e:
            self.logger.exception("Erro ao escanear redes Wi-Fi")
            raise
    
    def _scan_windows(self) -> List[Dict[str, any]]:
        """
        Escaneia redes Wi-Fi no Windows usando netsh.
        
        Returns:
            list: Lista de redes detectadas
        """
        self.logger.info("Executando scan Windows (netsh)...")
        
        try:
            # Executar comando netsh
            result = subprocess.run(
                ['netsh', 'wlan', 'show', 'networks', 'mode=bssid'],
                capture_output=True,
                text=True,
                encoding='cp850',  # Encoding do Windows
                timeout=10
            )
            
            if result.returncode != 0:
                self.logger.error(f"Erro ao executar netsh: {result.stderr}")
                return []
            
            # Parse do output
            networks = self._parse_netsh_output(result.stdout)
            self.networks = networks
            
            self.logger.info(f"Scan concluído: {len(networks)} redes encontradas")
            return networks
            
        except subprocess.TimeoutExpired:
            self.logger.error("Timeout ao executar netsh")
            raise TimeoutError("Scan de redes excedeu tempo limite")
        except FileNotFoundError:
            self.logger.error("Comando netsh não encontrado")
            return []
    
    def _parse_netsh_output(self, output: str) -> List[Dict[str, any]]:
        """
        Faz parsing do output do comando netsh.
        
        Args:
            output (str): Output do comando netsh
            
        Returns:
            list: Lista de redes parseadas
        """
        networks = []
        current_network = {}
        
        lines = output.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Detectar início de uma nova rede (SSID)
            if 'SSID' in line and ':' in line and 'BSSID' not in line:
                # Salvar rede anterior se existir
                if current_network and current_network.get('ssid'):
                    networks.append(current_network)
                
                # Iniciar nova rede
                ssid = line.split(':', 1)[1].strip()
                current_network = {
                    'ssid': ssid,
                    'bssid': '',
                    'rssi': -100,
                    'signal_percent': 0,
                    'channel': 0,
                    'security': 'Unknown'
                }
            
            # BSSID / MAC Address
            elif 'BSSID' in line and ':' in line:
                parts = line.split(':', 1)
                if len(parts) > 1:
                    current_network['bssid'] = parts[1].strip()
            
            # Sinal (pode estar como "Sinal" ou "Signal")
            elif ('Sinal' in line or 'Signal' in line) and ':' in line:
                parts = line.split(':', 1)
                if len(parts) > 1:
                    signal_str = parts[1].strip().replace('%', '')
                    try:
                        signal_percent = int(signal_str)
                        current_network['signal_percent'] = signal_percent
                        # Converter % para RSSI aproximado
                        # 100% ≈ -30dBm, 0% ≈ -100dBm
                        current_network['rssi'] = -100 + int(signal_percent * 0.7)
                    except ValueError:
                        pass
            
            # Canal (pode estar como "Canal" ou "Channel")
            elif ('Canal' in line or 'Channel' in line) and ':' in line:
                parts = line.split(':', 1)
                if len(parts) > 1:
                    try:
                        current_network['channel'] = int(parts[1].strip())
                    except ValueError:
                        pass
            
            # Tipo de autenticação/segurança
            elif ('Autenticação' in line or 'Authentication' in line) and ':' in line:
                parts = line.split(':', 1)
                if len(parts) > 1:
                    current_network['security'] = parts[1].strip()
        
        # Adicionar última rede
        if current_network and current_network.get('ssid'):
            networks.append(current_network)
        
        self.logger.debug(f"Parsing concluído: {len(networks)} redes parseadas")
        return networks
    
    def _scan_linux(self) -> List[Dict[str, any]]:
        """
        Escaneia redes Wi-Fi no Linux usando iwlist ou nmcli.
        
        Returns:
            list: Lista de redes detectadas
        """
        self.logger.info("Executando scan Linux...")
        
        try:
            # Tentar nmcli primeiro (mais moderno)
            result = subprocess.run(
                ['nmcli', '-t', '-f', 'SSID,BSSID,CHAN,SIGNAL,SECURITY', 'dev', 'wifi'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return self._parse_nmcli_output(result.stdout)
            
            # Fallback para iwlist
            result = subprocess.run(
                ['iwlist', 'scanning'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return self._parse_iwlist_output(result.stdout)
            
            self.logger.error("Nenhum comando de scan Wi-Fi disponível")
            return []
            
        except FileNotFoundError:
            self.logger.error("nmcli ou iwlist não encontrado. Instale network-manager ou wireless-tools")
            return []
        except Exception as e:
            self.logger.exception(f"Erro no scan Linux: {e}")
            return []
    
    def _parse_nmcli_output(self, output: str) -> List[Dict[str, any]]:
        """Parse output do nmcli."""
        networks = []
        
        for line in output.strip().split('\n'):
            if not line:
                continue
            
            parts = line.split(':')
            if len(parts) >= 5:
                ssid = parts[0].strip()
                if not ssid or ssid == '--':
                    continue
                
                signal = int(parts[3]) if parts[3].isdigit() else 0
                
                networks.append({
                    'ssid': ssid,
                    'bssid': parts[1].strip(),
                    'rssi': -100 + int(signal * 0.7),
                    'signal_percent': signal,
                    'channel': int(parts[2]) if parts[2].isdigit() else 0,
                    'security': parts[4].strip() if len(parts) > 4 else 'Unknown'
                })
        
        return networks
    
    def _parse_iwlist_output(self, output: str) -> List[Dict[str, any]]:
        """Parse output do iwlist."""
        networks = []
        current_network = {}
        
        for line in output.split('\n'):
            line = line.strip()
            
            if 'Cell' in line and 'Address:' in line:
                if current_network:
                    networks.append(current_network)
                current_network = {'bssid': line.split('Address:')[1].strip()}
            
            elif 'ESSID:' in line:
                essid = line.split('ESSID:')[1].strip().strip('"')
                current_network['ssid'] = essid
            
            elif 'Signal level' in line:
                signal = line.split('Signal level=')[1].split()[0]
                try:
                    signal_val = int(signal.replace('dBm', ''))
                    current_network['rssi'] = signal_val
                    current_network['signal_percent'] = min(100, max(0, (signal_val + 100) * 2))
                except:
                    pass
            
            elif 'Channel:' in line:
                try:
                    current_network['channel'] = int(line.split('Channel:')[1].strip())
                except:
                    pass
        
        if current_network:
            networks.append(current_network)
        
        return networks
    
    def _scan_macos(self) -> List[Dict[str, any]]:
        """
        Escaneia redes Wi-Fi no macOS usando airport.
        
        Returns:
            list: Lista de redes detectadas
        """
        self.logger.info("Executando scan macOS...")
        
        try:
            # Caminho do utilitário airport
            airport_path = '/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport'
            
            result = subprocess.run(
                [airport_path, '-s'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                self.logger.error(f"Erro ao executar airport: {result.stderr}")
                return []
            
            networks = self._parse_airport_output(result.stdout)
            self.networks = networks
            
            self.logger.info(f"Scan macOS concluído: {len(networks)} redes encontradas")
            return networks
            
        except FileNotFoundError:
            self.logger.error("Comando airport não encontrado")
            return []
        except Exception as e:
            self.logger.exception(f"Erro no scan macOS: {e}")
            return []
    
    def _parse_airport_output(self, output: str) -> List[Dict[str, any]]:
        """Parse output do airport."""
        networks = []
        lines = output.strip().split('\n')
        
        # Pular header
        if len(lines) < 2:
            return networks
        
        for line in lines[1:]:
            parts = line.split()
            if len(parts) < 3:
                continue
            
            try:
                ssid = parts[0]
                bssid = parts[1]
                rssi = int(parts[2])
                channel = parts[3] if len(parts) > 3 else '0'
                security = ' '.join(parts[6:]) if len(parts) > 6 else 'Open'
                
                # Converter RSSI para porcentagem
                signal_percent = min(100, max(0, (rssi + 100) * 2))
                
                networks.append({
                    'ssid': ssid,
                    'bssid': bssid,
                    'rssi': rssi,
                    'signal_percent': signal_percent,
                    'channel': int(channel.split(',')[0]) if channel.isdigit() else 0,
                    'security': security
                })
            except Exception as e:
                self.logger.debug(f"Erro ao parsear linha: {line} - {e}")
                continue
        
        return networks
    
    def get_signal_strength(self, ssid: str) -> Optional[int]:
        """
        Retorna a intensidade do sinal (RSSI) de uma rede específica.
        
        Args:
            ssid (str): Nome da rede (SSID)
            
        Returns:
            int: Valor RSSI em dBm, ou None se não encontrado
        """
        for network in self.networks:
            if network.get('ssid') == ssid:
                return network.get('rssi')
        return None
    
    def get_network_info(self, ssid: str) -> Optional[Dict[str, any]]:
        """
        Retorna informações completas de uma rede específica.
        
        Args:
            ssid (str): Nome da rede (SSID)
            
        Returns:
            dict: Dicionário com informações da rede, ou None se não encontrado
        """
        for network in self.networks:
            if network.get('ssid') == ssid:
                return network
        return None
    
    def get_strongest_network(self) -> Optional[Dict[str, any]]:
        """
        Retorna a rede com melhor sinal.
        
        Returns:
            dict: Rede com maior RSSI, ou None se não houver redes
        """
        if not self.networks:
            return None
        
        return max(self.networks, key=lambda x: x.get('rssi', -100))
    
    def filter_by_security(self, security_type: str) -> List[Dict[str, any]]:
        """
        Filtra redes por tipo de segurança.
        
        Args:
            security_type (str): Tipo de segurança ('Open', 'WPA2', etc)
            
        Returns:
            list: Lista de redes filtradas
        """
        return [n for n in self.networks if security_type.lower() in n.get('security', '').lower()]


if __name__ == "__main__":
    # Teste básico
    logging.basicConfig(level=logging.DEBUG)
    scanner = WifiScanner()
    networks = scanner.scan_networks()
    print(f"Redes encontradas: {len(networks)}")
    for net in networks:
        print(f"  - {net}")
