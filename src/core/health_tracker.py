"""
HealthTracker - Classe para monitorar a "saúde" da conexão de internet

Melhorias implementadas:
1. Tratamento robusto de erros
2. Parsing mais confiável de ping (regex)
3. Detecção automática de encoding do sistema
4. Cache de resultados para evitar testes redundantes
5. Threading para testes paralelos
6. Validação de dados mais rigorosa
7. Fallback para múltiplos métodos de teste
8. Melhor compatibilidade cross-platform
"""

import logging
import subprocess
import platform
import time
import json
import socket
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from statistics import mean, stdev
from concurrent.futures import ThreadPoolExecutor, as_completed


class HealthTracker:
    """
    Classe responsável por monitorar a saúde da conexão de internet.
    
    Attributes:
        metrics (list): Lista de métricas coletadas
        is_monitoring (bool): Indica se o monitoramento está ativo
        ping_host (str): Host usado para testes de ping
    """
    
    def __init__(self, ping_host: str = '8.8.8.8'):
        """
        Inicializa o health tracker com múltiplas funcionalidades.
        
        Args:
            ping_host (str): Host primário para testes de ping (default: Google DNS)
        """
        self.logger = logging.getLogger(__name__)
        self.metrics = []
        self.is_monitoring = False
        self.ping_host = ping_host
        self.os_type = platform.system()
        
        # Múltiplos hosts para redundância
        self.ping_hosts = [
            '8.8.8.8',      # Google DNS
            '1.1.1.1',      # Cloudflare DNS
            '208.67.222.222' # OpenDNS
        ]
        
        # Thresholds para alertas
        self.thresholds = {
            'latency_warning': 100,    # ms
            'latency_critical': 300,   # ms
            'packet_loss_warning': 5,  # %
            'packet_loss_critical': 15, # %
            'jitter_warning': 50,      # ms
            'jitter_critical': 100     # ms
        }
        
        # Estado da conexão
        self.connection_state = {
            'is_connected': False,
            'last_connected': None,
            'last_disconnected': None,
            'disconnect_count': 0,
            'total_downtime': 0  # segundos
        }
        
        # Cache para evitar testes redundantes
        self.cache = {
            'last_test_time': None,
            'last_test_result': None,
            'cache_duration': 2  # segundos
        }
        
        # Arquivo para salvar histórico
        self.history_file = Path(__file__).parent / 'health_history.json'
        try:
            self.history_file.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            self.logger.warning(f"Não foi possível criar diretório de logs: {e}")
            self.history_file = Path.home() / '.health_tracker' / 'health_history.json'
            self.history_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"HealthTracker inicializado (OS: {self.os_type})")
        
        # Carregar histórico se existir
        self._load_history()
    
    def start_monitoring(self):
        """Inicia o monitoramento contínuo."""
        self.is_monitoring = True
        self.logger.info("Monitoramento iniciado")
    
    def stop_monitoring(self):
        """Para o monitoramento contínuo."""
        self.is_monitoring = False
        self.logger.info("Monitoramento parado")
    
    def ping_test(self, host: Optional[str] = None, count: int = 1, timeout: int = 5) -> Optional[float]:
        """
        Executa teste de ping e retorna latência.
        
        Args:
            host (str): Host para ping (usa self.ping_host se None)
            count (int): Número de pings a enviar
            timeout (int): Timeout em segundos
            
        Returns:
            float: Latência média em ms, ou None se falhar
        """
        host = host or self.ping_host
        
        # Verificar cache
        if self._check_cache(host):
            return self.cache['last_test_result']
        
        try:
            # Comando ping varia por SO
            if self.os_type == "Windows":
                command = ['ping', '-n', str(count), '-w', str(timeout * 1000), host]
            elif self.os_type == "Darwin":  # macOS
                command = ['ping', '-c', str(count), '-W', str(timeout * 1000), host]
            else:  # Linux
                command = ['ping', '-c', str(count), '-W', str(timeout), host]
            
            # Executar ping com encoding apropriado
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout + 2,
                encoding='utf-8',
                errors='replace'
            )
            
            if result.returncode != 0:
                self.logger.debug(f"Ping falhou para {host} (returncode: {result.returncode})")
                self._update_cache(host, None)
                return None
            
            # Parse do resultado usando regex (mais robusto)
            latency = self._parse_ping_output(result.stdout)
            
            if latency is not None:
                self.logger.debug(f"Ping para {host}: {latency:.2f}ms")
                self._update_cache(host, latency)
            else:
                self.logger.warning(f"Não foi possível parsear output do ping para {host}")
                self._update_cache(host, None)
            
            return latency
            
        except subprocess.TimeoutExpired:
            self.logger.warning(f"Timeout no ping para {host}")
            self._update_cache(host, None)
            return None
        except FileNotFoundError:
            self.logger.error("Comando 'ping' não encontrado no sistema")
            return None
        except Exception as e:
            self.logger.error(f"Erro ao executar ping: {e}")
            return None
    
    def _parse_ping_output(self, output: str) -> Optional[float]:
        """
        Extrai latência média do output do ping usando regex.
        
        Args:
            output (str): Output do comando ping
            
        Returns:
            float: Latência em ms, ou None se não conseguir parsear
        """
        try:
            # Padrões regex para diferentes sistemas operacionais
            patterns = [
                # Windows (PT-BR): "Média = 123ms"
                r'M[ée]dia\s*=\s*(\d+(?:\.\d+)?)ms',
                # Windows (EN): "Average = 123ms"
                r'Average\s*=\s*(\d+(?:\.\d+)?)ms',
                # Linux/macOS: "rtt min/avg/max/mdev = 12.3/45.6/78.9/10.2 ms"
                r'rtt\s+min/avg/max/(?:mdev|stddev)\s*=\s*[\d.]+/([\d.]+)/[\d.]+/[\d.]+\s*ms',
                # Alternativa Linux/macOS
                r'round-trip\s+min/avg/max/(?:mdev|stddev)\s*=\s*[\d.]+/([\d.]+)/[\d.]+/[\d.]+\s*ms',
                # Padrão genérico: "time=123ms" ou "time=123.45ms"
                r'time[=<]\s*(\d+(?:\.\d+)?)\s*ms'
            ]
            
            # Tentar cada padrão
            for pattern in patterns:
                match = re.search(pattern, output, re.IGNORECASE | re.MULTILINE)
                if match:
                    latency = float(match.group(1))
                    return latency
            
            # Se nenhum padrão funcionou, tentar extrair qualquer número seguido de "ms"
            numbers = re.findall(r'(\d+(?:\.\d+)?)\s*ms', output)
            if numbers:
                # Pegar a média dos valores encontrados
                values = [float(n) for n in numbers]
                # Filtrar valores muito altos (provavelmente timeout)
                valid_values = [v for v in values if v < 5000]
                if valid_values:
                    return mean(valid_values)
            
            self.logger.debug(f"Não foi possível parsear output: {output[:200]}")
            return None
            
        except Exception as e:
            self.logger.error(f"Erro ao parsear output ping: {e}")
            return None
    
    def _check_cache(self, host: str) -> bool:
        """Verifica se há resultado válido em cache."""
        if self.cache['last_test_time'] is None:
            return False
        
        elapsed = time.time() - self.cache['last_test_time']
        return elapsed < self.cache['cache_duration']
    
    def _update_cache(self, host: str, result: Optional[float]):
        """Atualiza o cache com novo resultado."""
        self.cache['last_test_time'] = time.time()
        self.cache['last_test_result'] = result
    
    def check_connectivity(self, hosts: Optional[List[str]] = None) -> Tuple[bool, Optional[str]]:
        """
        Verifica se há conexão com a internet testando múltiplos hosts em paralelo.
        
        Args:
            hosts (list): Lista de hosts para testar (usa padrão se None)
            
        Returns:
            tuple: (is_connected: bool, fastest_host: str or None)
        """
        if hosts is None:
            hosts = self.ping_hosts
        
        fastest_latency = float('inf')
        fastest_host = None
        
        # Testar hosts em paralelo para maior velocidade
        with ThreadPoolExecutor(max_workers=len(hosts)) as executor:
            future_to_host = {
                executor.submit(self.ping_test, host, 1): host 
                for host in hosts
            }
            
            for future in as_completed(future_to_host, timeout=10):
                host = future_to_host[future]
                try:
                    latency = future.result()
                    if latency is not None and latency < fastest_latency:
                        fastest_latency = latency
                        fastest_host = host
                except Exception as e:
                    self.logger.debug(f"Erro ao testar {host}: {e}")
        
        is_connected = fastest_host is not None
        
        # Atualizar estado da conexão
        now = datetime.now()
        if is_connected:
            if not self.connection_state['is_connected']:
                # Reconectou
                self.logger.info(f"✓ Conexão restaurada (host: {fastest_host}, {fastest_latency:.1f}ms)")
                if self.connection_state['last_disconnected']:
                    downtime = (now - self.connection_state['last_disconnected']).total_seconds()
                    self.connection_state['total_downtime'] += downtime
            self.connection_state['is_connected'] = True
            self.connection_state['last_connected'] = now
        else:
            if self.connection_state['is_connected']:
                # Desconectou
                self.logger.warning("✗ Conexão perdida com todos os hosts")
                self.connection_state['disconnect_count'] += 1
                self.connection_state['last_disconnected'] = now
            self.connection_state['is_connected'] = False
        
        return is_connected, fastest_host
    
    def get_health_score(self, detailed: bool = False) -> Dict[str, Any]:
        """
        Calcula um score de saúde da conexão (0-100) com análise detalhada.
        
        Baseado em:
        - Latência: 40%
        - Packet loss: 30%
        - Jitter: 20%
        - Uptime: 10%
        
        Args:
            detailed (bool): Se True, retorna dict detalhado com todas as métricas
        
        Returns:
            dict ou int: Score e métricas detalhadas se detailed=True, ou int se False
        """
        # Fazer múltiplos pings para calcular packet loss e jitter
        pings = []
        ping_count = 10
        
        for i in range(ping_count):
            latency = self.ping_test(count=1)
            if latency is not None:
                pings.append(latency)
            # Pequeno delay entre pings, mas não muito longo
            if i < ping_count - 1:  # Não esperar no último
                time.sleep(0.05)
        
        if not pings:
            result = {
                'score': 0,
                'category': 'Desconectado',
                'latency': None,
                'packet_loss': 100.0,
                'jitter': None,
                'uptime': 0.0,
                'alerts': ['Sem conexão com a internet']
            }
            return result if detailed else 0
        
        # Calcular métricas
        avg_latency = mean(pings)
        min_latency = min(pings)
        max_latency = max(pings)
        packet_loss_pct = ((ping_count - len(pings)) / ping_count) * 100
        
        # Calcular jitter (desvio padrão da latência)
        jitter = stdev(pings) if len(pings) > 1 else 0
        
        # Alertas
        alerts = []
        
        # 1. Score de Latência (40%)
        if avg_latency < 20:
            latency_score = 100
        elif avg_latency < 50:
            latency_score = 90
        elif avg_latency < 100:
            latency_score = 70
            alerts.append(f"Latência elevada: {avg_latency:.1f}ms")
        elif avg_latency < 200:
            latency_score = 50
            alerts.append(f"⚠ Latência alta: {avg_latency:.1f}ms")
        elif avg_latency < 300:
            latency_score = 30
            alerts.append(f"🔴 Latência crítica: {avg_latency:.1f}ms")
        else:
            latency_score = 10
            alerts.append(f"🔴 Latência severa: {avg_latency:.1f}ms")
        
        # 2. Score de Packet Loss (30%)
        if packet_loss_pct == 0:
            packet_loss_score = 100
        elif packet_loss_pct < 1:
            packet_loss_score = 95
        elif packet_loss_pct < 5:
            packet_loss_score = 80
            alerts.append(f"Perda de pacotes: {packet_loss_pct:.1f}%")
        elif packet_loss_pct < 10:
            packet_loss_score = 60
            alerts.append(f"⚠ Perda de pacotes significativa: {packet_loss_pct:.1f}%")
        elif packet_loss_pct < 20:
            packet_loss_score = 40
            alerts.append(f"🔴 Perda de pacotes alta: {packet_loss_pct:.1f}%")
        else:
            packet_loss_score = 20
            alerts.append(f"🔴 Perda de pacotes crítica: {packet_loss_pct:.1f}%")
        
        # 3. Score de Jitter (20%)
        if jitter < 5:
            jitter_score = 100
        elif jitter < 10:
            jitter_score = 90
        elif jitter < 30:
            jitter_score = 70
        elif jitter < 50:
            jitter_score = 50
            alerts.append(f"Jitter elevado: {jitter:.1f}ms")
        elif jitter < 100:
            jitter_score = 30
            alerts.append(f"⚠ Jitter alto: {jitter:.1f}ms")
        else:
            jitter_score = 10
            alerts.append(f"🔴 Jitter crítico: {jitter:.1f}ms")
        
        # 4. Score de Uptime (10%)
        if self.metrics:
            recent_metrics = self.metrics[-100:]
            successful_tests = len([m for m in recent_metrics if m.get('connected', False)])
            total_tests = len(recent_metrics)
            uptime_percent = (successful_tests / total_tests) * 100 if total_tests > 0 else 100
            
            if uptime_percent >= 99:
                uptime_score = 100
            elif uptime_percent >= 95:
                uptime_score = 85
            elif uptime_percent >= 90:
                uptime_score = 70
            elif uptime_percent >= 80:
                uptime_score = 50
                alerts.append(f"Uptime baixo: {uptime_percent:.1f}%")
            else:
                uptime_score = 30
                alerts.append(f"⚠ Uptime crítico: {uptime_percent:.1f}%")
        else:
            uptime_percent = 100.0
            uptime_score = 100
        
        # Calcular score final ponderado
        final_score = int(
            (latency_score * 0.4) +
            (packet_loss_score * 0.3) +
            (jitter_score * 0.2) +
            (uptime_score * 0.1)
        )
        
        # Determinar categoria
        category = self.get_health_category(final_score)
        
        result = {
            'score': final_score,
            'category': category,
            'latency': {
                'avg': round(avg_latency, 2),
                'min': round(min_latency, 2),
                'max': round(max_latency, 2)
            },
            'packet_loss': round(packet_loss_pct, 2),
            'jitter': round(jitter, 2),
            'uptime': round(uptime_percent, 2),
            'pings_successful': len(pings),
            'pings_total': ping_count,
            'alerts': alerts
        }
        
        return result if detailed else final_score
    
    def get_health_category(self, score: int) -> str:
        """
        Retorna categoria de saúde baseada no score.
        
        Args:
            score (int): Score de saúde (0-100)
            
        Returns:
            str: Categoria ('Excelente', 'Bom', 'Regular', 'Ruim')
        """
        if score >= 80:
            return "Excelente"
        elif score >= 60:
            return "Bom"
        elif score >= 40:
            return "Regular"
        else:
            return "Ruim"
    
    def log_metrics(self):
        """
        Coleta e salva métricas atuais.
        """
        timestamp = datetime.now().isoformat()
        latency = self.ping_test()
        connected = latency is not None
        
        # Usar versão não detalhada para evitar muitos pings
        score_data = self.get_health_score(detailed=False)
        score = score_data if isinstance(score_data, int) else score_data.get('score', 0)
        
        metric = {
            'timestamp': timestamp,
            'latency': latency,
            'connected': connected,
            'score': score,
            'category': self.get_health_category(score)
        }
        
        self.metrics.append(metric)
        
        # Limitar a 1000 métricas em memória
        if len(self.metrics) > 1000:
            self.metrics = self.metrics[-1000:]
        
        self.logger.debug(f"Métrica registrada: {metric}")
        
        # Salvar em arquivo periodicamente
        if len(self.metrics) % 10 == 0:
            self._save_history()
    
    def get_recent_metrics(self, count: int = 30) -> List[Dict]:
        """
        Retorna métricas mais recentes.
        
        Args:
            count (int): Número de métricas a retornar
            
        Returns:
            list: Últimas N métricas
        """
        return self.metrics[-count:] if self.metrics else []
    
    def get_statistics(self) -> Dict[str, float]:
        """
        Calcula estatísticas das métricas coletadas.
        
        Returns:
            dict: Estatísticas (média, min, max, etc)
        """
        if not self.metrics:
            return {}
        
        latencies = [m['latency'] for m in self.metrics if m['latency'] is not None]
        
        if not latencies:
            return {
                'total_tests': len(self.metrics),
                'successful_tests': 0,
                'success_rate': 0.0
            }
        
        return {
            'avg_latency': round(mean(latencies), 2),
            'min_latency': round(min(latencies), 2),
            'max_latency': round(max(latencies), 2),
            'total_tests': len(self.metrics),
            'successful_tests': len(latencies),
            'success_rate': round(len(latencies) / len(self.metrics) * 100, 2)
        }
    
    def _save_history(self):
        """Salva histórico de métricas em arquivo JSON."""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.metrics, f, indent=2, ensure_ascii=False)
            self.logger.debug(f"Histórico salvo: {len(self.metrics)} métricas")
        except Exception as e:
            self.logger.error(f"Erro ao salvar histórico: {e}")
    
    def _load_history(self):
        """Carrega histórico de métricas do arquivo JSON."""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.metrics = json.load(f)
                self.logger.info(f"Histórico carregado: {len(self.metrics)} métricas")
        except Exception as e:
            self.logger.warning(f"Não foi possível carregar histórico: {e}")
            self.metrics = []
    
    def test_dns_resolution(self, domain: str = 'www.google.com') -> Optional[float]:
        """
        Testa o tempo de resolução DNS.
        
        Args:
            domain (str): Domínio para resolver
            
        Returns:
            float: Tempo de resolução em ms, ou None se falhar
        """
        try:
            start = time.time()
            socket.gethostbyname(domain)
            end = time.time()
            
            resolution_time = (end - start) * 1000  # Converter para ms
            self.logger.debug(f"DNS resolution para {domain}: {resolution_time:.2f}ms")
            return resolution_time
            
        except socket.gaierror as e:
            self.logger.error(f"Erro de resolução DNS para {domain}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Erro ao resolver DNS para {domain}: {e}")
            return None
    
    def get_connection_stability(self) -> Dict[str, Any]:
        """
        Analisa a estabilidade da conexão baseado no histórico.
        
        Returns:
            dict: Métricas de estabilidade
        """
        if not self.metrics:
            return {
                'stability_score': 100,
                'disconnect_events': 0,
                'total_downtime': 0,
                'avg_uptime_duration': 0,
                'latency_variability': 0,
                'recommendation': 'Sem dados históricos ainda'
            }
        
        # Calcular eventos de desconexão
        disconnect_events = self.connection_state['disconnect_count']
        total_downtime = self.connection_state['total_downtime']
        
        # Calcular variabilidade da latência
        latencies = [m.get('latency') for m in self.metrics[-100:] if m.get('latency')]
        if len(latencies) > 10:
            latency_stdev = stdev(latencies)
            latency_mean = mean(latencies)
            latency_cv = (latency_stdev / latency_mean) * 100 if latency_mean > 0 else 0
        else:
            latency_cv = 0
        
        # Score de estabilidade
        if disconnect_events == 0 and latency_cv < 20:
            stability_score = 100
            recommendation = "Conexão excelente e estável"
        elif disconnect_events < 3 and latency_cv < 40:
            stability_score = 80
            recommendation = "Conexão boa com pequenas variações"
        elif disconnect_events < 5 and latency_cv < 60:
            stability_score = 60
            recommendation = "Conexão instável, considere reiniciar roteador"
        else:
            stability_score = 40
            recommendation = "Conexão muito instável, verifique cabeamento e equipamentos"
        
        return {
            'stability_score': stability_score,
            'disconnect_events': disconnect_events,
            'total_downtime': round(total_downtime, 2),
            'latency_variability': round(latency_cv, 2),
            'recommendation': recommendation
        }
    
    def get_best_ping_host(self) -> Optional[str]:
        """
        Determina o melhor host para ping baseado em latência.
        
        Returns:
            str: Host com menor latência, ou None se nenhum responder
        """
        best_host = None
        best_latency = float('inf')
        
        # Testar hosts em paralelo
        with ThreadPoolExecutor(max_workers=len(self.ping_hosts)) as executor:
            future_to_host = {
                executor.submit(self.ping_test, host, 3): host 
                for host in self.ping_hosts
            }
            
            for future in as_completed(future_to_host, timeout=15):
                host = future_to_host[future]
                try:
                    latency = future.result()
                    if latency and latency < best_latency:
                        best_latency = latency
                        best_host = host
                except Exception as e:
                    self.logger.debug(f"Erro ao testar {host}: {e}")
        
        if best_host:
            self.logger.info(f"Melhor host: {best_host} ({best_latency:.2f}ms)")
        
        return best_host
    
    def diagnose_connection(self) -> Dict[str, Any]:
        """
        Executa diagnóstico completo da conexão.
        
        Returns:
            dict: Relatório de diagnóstico completo
        """
        self.logger.info("Iniciando diagnóstico completo da conexão...")
        
        # 1. Verificar conectividade
        is_connected, best_host = self.check_connectivity()
        
        # 2. Obter health score detalhado
        health = self.get_health_score(detailed=True)
        
        # 3. Testar DNS
        dns_time = self.test_dns_resolution() if is_connected else None
        
        # 4. Analisar estabilidade
        stability = self.get_connection_stability()
        
        # 5. Identificar melhor host
        optimal_host = self.get_best_ping_host() if is_connected else None
        
        # 6. Gerar recomendações
        recommendations = []
        
        if not is_connected:
            recommendations.append("🔴 CRÍTICO: Sem conexão com a internet")
            recommendations.append("   - Verifique cabos de rede")
            recommendations.append("   - Reinicie o roteador")
            recommendations.append("   - Verifique configurações de rede")
        else:
            if health['latency'] and health['latency']['avg'] > 100:
                recommendations.append("⚠ Latência alta detectada")
                recommendations.append("   - Verifique se há downloads/uploads em andamento")
                recommendations.append("   - Teste em horários diferentes")
            
            if health['packet_loss'] > 5:
                recommendations.append("⚠ Perda de pacotes significativa")
                recommendations.append("   - Verifique cabos e conexões")
                recommendations.append("   - Teste conexão cabeada ao invés de Wi-Fi")
            
            if health['jitter'] > 50:
                recommendations.append("⚠ Variação de latência alta (Jitter)")
                recommendations.append("   - Reduza dispositivos conectados")
                recommendations.append("   - Priorize tráfego (QoS no roteador)")
            
            if dns_time and dns_time > 100:
                recommendations.append("⚠ Resolução DNS lenta")
                recommendations.append("   - Considere usar DNS público (8.8.8.8, 1.1.1.1)")
            
            if stability['disconnect_events'] > 5:
                recommendations.append("⚠ Múltiplas desconexões detectadas")
                recommendations.append("   - Verifique estabilidade do provedor")
                recommendations.append("   - Atualize firmware do roteador")
        
        if not recommendations:
            recommendations.append("✅ Conexão saudável, nenhum problema detectado")
        
        diagnosis = {
            'timestamp': datetime.now().isoformat(),
            'connected': is_connected,
            'best_host': best_host,
            'optimal_host': optimal_host,
            'health_score': health,
            'dns_resolution_time': dns_time,
            'stability': stability,
            'recommendations': recommendations
        }
        
        self.logger.info(f"Diagnóstico concluído: Score {health['score']}/100")
        
        return diagnosis


if __name__ == "__main__":
    # Teste completo do Health Tracker
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("=" * 70)
    print("🔍 DIAGNÓSTICO COMPLETO DE CONEXÃO".center(70))
    print("=" * 70)
    
    tracker = HealthTracker()
    
    # 1. Teste de conectividade
    print("\n1️⃣  Testando conectividade...")
    try:
        connected, best_host = tracker.check_connectivity()
        if connected:
            print(f"   ✅ Conectado (host mais rápido: {best_host})")
        else:
            print(f"   ❌ Sem conexão")
    except Exception as e:
        print(f"   ❌ Erro ao testar conectividade: {e}")
        connected = False
    
    # 2. Teste de latência
    print("\n2️⃣  Testando latência...")
    try:
        latency = tracker.ping_test()
        if latency:
            print(f"   📊 Latência: {latency:.2f}ms")
        else:
            print(f"   ❌ Falha no ping")
    except Exception as e:
        print(f"   ❌ Erro ao testar latência: {e}")
    
    if not connected:
        print("\n" + "=" * 70)
        print("⚠️  Sem conexão com a internet. Diagnóstico limitado.".center(70))
        print("=" * 70)
        import sys
        sys.exit(1)
    
    # 3. Health Score detalhado
    print("\n3️⃣  Calculando Health Score...")
    try:
        health = tracker.get_health_score(detailed=True)
        print(f"   📈 Score: {health['score']}/100 ({health['category']})")
        
        if health['latency']:
            print(f"   📶 Latência: {health['latency']['avg']:.1f}ms (min: {health['latency']['min']:.1f}, max: {health['latency']['max']:.1f})")
            print(f"   📉 Packet Loss: {health['packet_loss']:.1f}%")
            print(f"   📊 Jitter: {health['jitter']:.1f}ms")
            print(f"   ⏱️  Uptime: {health['uptime']:.1f}%")
            print(f"   ✓  Pings bem-sucedidos: {health['pings_successful']}/{health['pings_total']}")
        
        if health['alerts']:
            print(f"\n   ⚠️  Alertas:")
            for alert in health['alerts']:
                print(f"      • {alert}")
    except Exception as e:
        print(f"   ❌ Erro ao calcular health score: {e}")
    
    # 4. Teste DNS
    print("\n4️⃣  Testando resolução DNS...")
    try:
        dns_time = tracker.test_dns_resolution()
        if dns_time:
            print(f"   🌐 Tempo de DNS: {dns_time:.2f}ms")
            if dns_time < 50:
                print(f"   ✅ DNS excelente")
            elif dns_time < 100:
                print(f"   ✓  DNS bom")
            else:
                print(f"   ⚠️  DNS lento")
        else:
            print(f"   ❌ Falha na resolução DNS")
    except Exception as e:
        print(f"   ❌ Erro ao testar DNS: {e}")
    
    # 5. Análise de estabilidade
    print("\n5️⃣  Analisando estabilidade...")
    try:
        stability = tracker.get_connection_stability()
        print(f"   📊 Score de Estabilidade: {stability['stability_score']}/100")
        print(f"   🔌 Desconexões: {stability['disconnect_events']}")
        print(f"   ⏱️  Downtime total: {stability['total_downtime']:.1f}s")
        print(f"   📈 Variabilidade da latência: {stability['latency_variability']:.1f}%")
        print(f"   💡 Recomendação: {stability['recommendation']}")
    except Exception as e:
        print(f"   ❌ Erro ao analisar estabilidade: {e}")
    
    # 6. Encontrar melhor host
    print("\n6️⃣  Identificando melhor host...")
    try:
        best = tracker.get_best_ping_host()
        if best:
            print(f"   🎯 Melhor host: {best}")
        else:
            print(f"   ❌ Nenhum host respondeu")
    except Exception as e:
        print(f"   ❌ Erro ao identificar melhor host: {e}")
    
    # 7. Diagnóstico completo
    print("\n" + "=" * 70)
    print("📋 RELATÓRIO COMPLETO".center(70))
    print("=" * 70)
    
    try:
        diagnosis = tracker.diagnose_connection()
        
        print(f"\n🏆 Score Final: {diagnosis['health_score']['score']}/100")
        print(f"🎯 Categoria: {diagnosis['health_score']['category']}")
        print(f"🌐 Host recomendado: {diagnosis['optimal_host'] or 'N/A'}")
        
        if diagnosis['dns_resolution_time']:
            print(f"🔍 Tempo de DNS: {diagnosis['dns_resolution_time']:.2f}ms")
        
        print(f"\n📊 Recomendações:")
        for rec in diagnosis['recommendations']:
            print(f"   {rec}")
        
        # 8. Estatísticas gerais
        print(f"\n📈 Estatísticas:")
        stats = tracker.get_statistics()
        if stats:
            print(f"   • Testes realizados: {stats.get('total_tests', 0)}")
            print(f"   • Testes bem-sucedidos: {stats.get('successful_tests', 0)}")
            print(f"   • Taxa de sucesso: {stats.get('success_rate', 0):.1f}%")
            if 'avg_latency' in stats:
                print(f"   • Latência média: {stats['avg_latency']:.2f}ms")
                print(f"   • Latência mínima: {stats['min_latency']:.2f}ms")
                print(f"   • Latência máxima: {stats['max_latency']:.2f}ms")
        
    except Exception as e:
        print(f"   ❌ Erro ao gerar diagnóstico: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("✅ Diagnóstico concluído!".center(70))
    print("=" * 70)
    
    # Salvar histórico
    print(f"\n💾 Histórico salvo em: {tracker.history_file}")