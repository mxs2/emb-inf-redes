# Exemplo de Uso - Monitor Wi-Fi

## Exemplo 1: Usar WifiScanner Diretamente

```python
from src.core.wifi_scanner import WifiScanner
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)

# Criar scanner
scanner = WifiScanner()

# Escanear redes
networks = scanner.scan_networks()

# Exibir resultados
print(f"Encontradas {len(networks)} redes:")
for net in networks:
    print(f"  SSID: {net['ssid']}")
    print(f"  Sinal: {net['signal_percent']}%")
    print(f"  Canal: {net['channel']}")
    print(f"  Segurança: {net['security']}")
    print()

# Buscar rede mais forte
strongest = scanner.get_strongest_network()
if strongest:
    print(f"Rede mais forte: {strongest['ssid']} ({strongest['rssi']} dBm)")
```

## Exemplo 2: Usar HealthTracker

```python
from src.core.health_tracker import HealthTracker
import time

# Criar tracker
tracker = HealthTracker()

# Verificar conectividade
if tracker.check_connectivity():
    print("✓ Conectado à internet")
    
    # Fazer ping test
    latency = tracker.ping_test()
    print(f"Latência: {latency}ms")
    
    # Obter score
    score = tracker.get_health_score()
    category = tracker.get_health_category(score)
    print(f"Health Score: {score}/100 ({category})")
    
    # Monitorar por 1 minuto
    print("\nMonitorando por 1 minuto...")
    tracker.start_monitoring()
    
    for i in range(6):  # 6x de 10s = 1 minuto
        tracker.log_metrics()
        time.sleep(10)
    
    tracker.stop_monitoring()
    
    # Obter estatísticas
    stats = tracker.get_statistics()
    print(f"\nEstatísticas:")
    print(f"  Latência média: {stats['avg_latency']:.2f}ms")
    print(f"  Min: {stats['min_latency']:.2f}ms")
    print(f"  Max: {stats['max_latency']:.2f}ms")
    print(f"  Taxa de sucesso: {stats['success_rate']:.1f}%")
else:
    print("✗ Sem conexão com internet")
```

## Exemplo 3: Usar NetworkScanner

```python
from src.core.network_scanner import NetworkScanner

# Criar scanner
scanner = NetworkScanner()

# Obter IP local
local_ip = scanner.get_local_ip()
print(f"Seu IP: {local_ip}")

# Determinar range automaticamente
# (assumindo rede 192.168.1.x)
network_range = f"{'.'.join(local_ip.split('.')[:-1])}.0/24"
scanner.update_network_range(network_range)
print(f"Escaneando: {network_range}")

# Escanear dispositivos
devices = scanner.scan_devices(use_nmap=False)

print(f"\nEncontrados {len(devices)} dispositivos:")
for device in devices:
    print(f"  IP: {device['ip']}")
    print(f"  MAC: {device['mac']}")
    if device.get('hostname'):
        print(f"  Hostname: {device['hostname']}")
    print()
```

## Exemplo 4: Usar GUI Completa

```python
from src.main import main

# Simplesmente execute main.py
# ou importe e execute:
if __name__ == "__main__":
    main()
```

## Exemplo 5: Integração Completa

```python
from src.core.wifi_scanner import WifiScanner
from src.core.network_scanner import NetworkScanner
from src.core.health_tracker import HealthTracker
import json

# Inicializar componentes
wifi = WifiScanner()
network = NetworkScanner()
health = HealthTracker()

# Coletar dados
print("Coletando dados...")
networks = wifi.scan_networks()
devices = network.scan_devices(use_nmap=False)
score = health.get_health_score()

# Criar relatório
report = {
    'timestamp': '2025-10-29T12:00:00',
    'wifi_networks': len(networks),
    'connected_devices': len(devices),
    'health_score': score,
    'health_category': health.get_health_category(score),
    'networks': networks,
    'devices': devices
}

# Salvar relatório
with open('exports/report.json', 'w') as f:
    json.dump(report, f, indent=2)

print(f"Relatório salvo em exports/report.json")
print(f"\nResumo:")
print(f"  Redes Wi-Fi: {len(networks)}")
print(f"  Dispositivos: {len(devices)}")
print(f"  Saúde: {score}/100")
```

## Dicas de Uso

### Executar como Admin (Windows)

```powershell
# Abra PowerShell como Administrador
Start-Process powershell -Verb runAs

# Navegue até o projeto
cd "C:\Users\mateusxs\Documents\github\Nova pasta"

# Ative o ambiente virtual
.\venv\Scripts\Activate.ps1

# Execute
python src\main.py
```

### Debugging

```python
# Ativar logs detalhados
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Agora todos os logs DEBUG serão exibidos
```

### Tratamento de Erros

```python
from src.core.wifi_scanner import WifiScanner

scanner = WifiScanner()

try:
    networks = scanner.scan_networks()
except PermissionError:
    print("Execute como administrador!")
except TimeoutError:
    print("Scan demorou demais, tente novamente")
except Exception as e:
    print(f"Erro inesperado: {e}")
```
