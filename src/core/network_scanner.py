"""
NetworkScanner - Classe para escanear dispositivos na rede local

Este módulo implementa scanning de dispositivos conectados usando:
1. Python-nmap (requer nmap instalado)
2. ARP scan com Scapy como alternativa
"""

import logging
import socket
from typing import List, Dict, Optional


class NetworkScanner:
    """
    Classe responsável por escanear dispositivos na rede local.
    
    Attributes:
        devices (list): Lista de dispositivos detectados
        network_range (str): Range de IPs a escanear (ex: '192.168.1.0/24')
    """
    
    def __init__(self, network_range: str = None):
        """
        Inicializa o scanner de rede.
        
        Args:
            network_range (str): Range de IPs no formato CIDR (auto-detecta se None)
        """
        self.logger = logging.getLogger(__name__)
        self.devices = []
        
        # Auto-detectar range se não especificado
        if network_range is None:
            network_range = self._detect_network_range()
        
        self.network_range = network_range
        
        self.logger.info(f"NetworkScanner inicializado com range: {network_range}")
    
    def scan_devices(self, use_nmap: bool = True) -> List[Dict[str, any]]:
        """
        Escaneia dispositivos conectados na rede.
        
        Args:
            use_nmap (bool): Se True, tenta usar nmap. Se False ou falhar, usa ARP
            
        Returns:
            list: Lista de dicionários com informações dos dispositivos
                  [{'ip': str, 'mac': str, 'hostname': str, 'vendor': str}]
        
        Raises:
            Exception: Se houver erro no scan
        """
        self.logger.info(f"Iniciando scan de dispositivos em {self.network_range}...")
        
        try:
            if use_nmap:
                return self._scan_with_nmap()
            else:
                return self._scan_with_arp()
                
        except Exception as e:
            self.logger.exception("Erro ao escanear dispositivos")
            raise
    
    def _scan_with_nmap(self) -> List[Dict[str, any]]:
        """
        Escaneia rede usando python-nmap.
        
        Returns:
            list: Lista de dispositivos detectados
        """
        self.logger.info("Executando scan com nmap...")
        
        try:
            import nmap
            
            nm = nmap.PortScanner()
            self.logger.debug(f"Iniciando scan nmap em {self.network_range}")
            
            # Ping scan (-sn) - rápido e não escaneia portas
            nm.scan(hosts=self.network_range, arguments='-sn')
            
            devices = []
            for host in nm.all_hosts():
                if nm[host].state() == 'up':
                    device = {
                        'ip': host,
                        'mac': 'N/A',
                        'hostname': None,
                        'vendor': None
                    }
                    
                    # Tentar obter MAC address
                    if 'mac' in nm[host]['addresses']:
                        device['mac'] = nm[host]['addresses']['mac']
                    
                    # Tentar obter vendor (fabricante)
                    if 'vendor' in nm[host] and nm[host]['vendor']:
                        device['vendor'] = list(nm[host]['vendor'].values())[0] if nm[host]['vendor'] else None
                    
                    # Tentar obter hostname
                    if 'hostnames' in nm[host] and nm[host]['hostnames']:
                        hostnames = [h['name'] for h in nm[host]['hostnames'] if h['name']]
                        if hostnames:
                            device['hostname'] = hostnames[0]
                    
                    # Fallback para resolver hostname
                    if not device['hostname']:
                        device['hostname'] = self.resolve_hostname(host)
                    
                    devices.append(device)
                    self.logger.debug(f"Dispositivo encontrado: {host}")
            
            self.devices = devices
            self.logger.info(f"Scan nmap concluído: {len(devices)} dispositivos")
            return devices
            
        except ImportError:
            self.logger.warning("python-nmap não instalado, usando ARP")
            return self._scan_with_arp()
        except Exception as e:
            self.logger.error(f"Erro no scan nmap: {e}")
            self.logger.warning("Tentando método alternativo...")
            return self._scan_with_arp()
    
    def _scan_with_arp(self) -> List[Dict[str, any]]:
        """
        Escaneia rede usando ARP (Scapy) ou fallback com ping.
        
        Returns:
            list: Lista de dispositivos detectados
        """
        self.logger.info("Executando scan com ARP (Scapy)...")
        
        try:
            from scapy.all import ARP, Ether, srp
            
            # Criar pacote ARP
            arp = ARP(pdst=self.network_range)
            ether = Ether(dst="ff:ff:ff:ff:ff:ff")
            packet = ether / arp
            
            # Enviar pacote e receber respostas
            self.logger.debug(f"Enviando ARP requests para {self.network_range}")
            result = srp(packet, timeout=3, verbose=0)[0]
            
            # Processar respostas
            devices = []
            for sent, received in result:
                device = {
                    'ip': received.psrc,
                    'mac': received.hwsrc,
                    'hostname': None,
                    'vendor': None
                }
                
                # Tentar resolver hostname
                hostname = self.resolve_hostname(received.psrc)
                if hostname:
                    device['hostname'] = hostname
                
                devices.append(device)
                self.logger.debug(f"Dispositivo encontrado: {received.psrc} ({received.hwsrc})")
            
            self.devices = devices
            self.logger.info(f"Scan ARP concluído: {len(devices)} dispositivos")
            return devices
            
        except ImportError:
            self.logger.error("Scapy não instalado. Use: pip install scapy")
            return self._scan_with_ping()
        except RuntimeError as e:
            if "winpcap" in str(e).lower() or "npcap" in str(e).lower():
                self.logger.warning("Npcap não instalado, usando método alternativo (ping)")
                return self._scan_with_ping()
            raise
        except PermissionError:
            self.logger.error("Permissão negada. Execute como administrador!")
            return self._scan_with_ping()
        except Exception as e:
            self.logger.exception(f"Erro no scan ARP: {e}")
            return self._scan_with_ping()
    
    def get_device_info(self, ip: str) -> Optional[Dict[str, any]]:
        """
        Retorna informações detalhadas de um dispositivo específico.
        
        Args:
            ip (str): Endereço IP do dispositivo
            
        Returns:
            dict: Informações do dispositivo, ou None se não encontrado
        """
        for device in self.devices:
            if device.get('ip') == ip:
                return device
        return None
    
    def resolve_hostname(self, ip: str) -> Optional[str]:
        """
        Tenta resolver o hostname de um endereço IP.
        
        Args:
            ip (str): Endereço IP
            
        Returns:
            str: Hostname resolvido, ou None se falhar
        """
        try:
            hostname = socket.gethostbyaddr(ip)[0]
            self.logger.debug(f"Hostname resolvido: {ip} -> {hostname}")
            return hostname
        except socket.herror:
            self.logger.debug(f"Não foi possível resolver hostname para {ip}")
            return None
        except Exception as e:
            self.logger.error(f"Erro ao resolver hostname: {e}")
            return None
    
    def get_local_ip(self) -> str:
        """
        Obtém o IP local da máquina.
        
        Returns:
            str: Endereço IP local
        """
        try:
            # Conecta a um servidor externo para descobrir IP local
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except Exception as e:
            self.logger.error(f"Erro ao obter IP local: {e}")
            return "127.0.0.1"
    
    def _detect_network_range(self) -> str:
        """
        Detecta automaticamente o range da rede local.
        
        Returns:
            str: Range no formato CIDR
        """
        try:
            import ipaddress
            
            # Obter IP local
            local_ip = self.get_local_ip()
            
            # Criar range /24 baseado no IP local
            ip_obj = ipaddress.IPv4Address(local_ip)
            network = ipaddress.IPv4Network(f"{local_ip}/24", strict=False)
            
            self.logger.info(f"Range detectado automaticamente: {network}")
            return str(network)
            
        except Exception as e:
            self.logger.error(f"Erro ao detectar range: {e}")
            return "192.168.1.0/24"  # Fallback padrão
    
    def update_network_range(self, new_range: str):
        """
        Atualiza o range de rede para scanning.
        
        Args:
            new_range (str): Novo range no formato CIDR
        """
        self.network_range = new_range
        self.logger.info(f"Range de rede atualizado para: {new_range}")
    
    def _scan_with_ping(self) -> List[Dict[str, any]]:
        """
        Escaneia rede usando ping (fallback quando Scapy/ARP não funciona).
        
        Returns:
            list: Lista de dispositivos detectados
        """
        self.logger.info("Executando scan com ping (método alternativo)...")
        import subprocess
        import platform
        import ipaddress
        import concurrent.futures
        
        devices = []
        
        try:
            # Extrair base IP do range
            network = ipaddress.IPv4Network(self.network_range, strict=False)
            
            # Função para pingar um IP
            def ping_host(ip_str):
                try:
                    if platform.system().lower() == "windows":
                        command = ['ping', '-n', '1', '-w', '500', str(ip_str)]
                    else:
                        command = ['ping', '-c', '1', '-W', '1', str(ip_str)]
                    
                    result = subprocess.run(
                        command,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        timeout=2
                    )
                    
                    if result.returncode == 0:
                        return str(ip_str)
                    return None
                except:
                    return None
            
            # Limitar a 100 IPs para equilibrar velocidade e cobertura
            ips_to_scan = list(network.hosts())[:100]
            total_ips = len(ips_to_scan)
            self.logger.info(f"Escaneando {total_ips} IPs com ping no range {self.network_range}...")
            
            # Usar ThreadPoolExecutor para pingar múltiplos IPs em paralelo
            with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
                results = list(executor.map(ping_host, ips_to_scan))
                
                # Processar resultados
                found_count = 0
                for ip in results:
                    if ip:
                        found_count += 1
                        device = {
                            'ip': ip,
                            'mac': 'N/A',
                            'hostname': 'Desconhecido',
                            'vendor': 'N/A'
                        }
                        
                        # Tentar resolver hostname
                        hostname = self.resolve_hostname(ip)
                        if hostname:
                            device['hostname'] = hostname
                        
                        devices.append(device)
                        self.logger.info(f"✓ Dispositivo {found_count} encontrado: {ip} ({device['hostname']})")
                
                if found_count == 0:
                    self.logger.warning(f"Nenhum dispositivo respondeu ao ping no range {self.network_range}")
                    self.logger.info("Dicas: Verifique se você está conectado à rede e se o range está correto")
            
            self.devices = devices
            self.logger.info(f"Scan com ping concluído: {len(devices)} dispositivos")
            return devices
            
        except Exception as e:
            self.logger.exception(f"Erro no scan com ping: {e}")
            return []
    
    def get_device_count(self) -> int:
        """
        Retorna o número de dispositivos detectados.
        
        Returns:
            int: Quantidade de dispositivos
        """
        return len(self.devices)


if __name__ == "__main__":
    # Teste básico
    logging.basicConfig(level=logging.DEBUG)
    scanner = NetworkScanner()
    
    # Teste de IP local
    local_ip = scanner.get_local_ip()
    print(f"IP Local: {local_ip}")
    
    # Teste de hostname
    hostname = scanner.resolve_hostname(local_ip)
    print(f"Hostname: {hostname}")
    
    # Teste de scan (ainda não implementado)
    devices = scanner.scan_devices(use_nmap=False)
    print(f"Dispositivos encontrados: {len(devices)}")
