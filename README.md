# Monitor de Sinal Wi-Fi com Health Tracker

**Data:** 13 de Novembro de 2025  
**Versão:** 2.0

## Tema do Projeto

Aplicação desktop para monitoramento em tempo real de redes Wi-Fi, permitindo visualizar intensidade de sinal, redes disponíveis, dispositivos conectados e análise de saúde da conexão de internet.

## Funcionalidades

- **Monitoramento em Tempo Real**: Coleta contínua de dados de redes Wi-Fi
- **Análise de Sinal**: Exibe RSSI, SSID, MAC Address e canal
- **Scanner de Dispositivos**: Lista dispositivos conectados na rede
- **Health Tracker**: Monitora a "saúde" da conexão de internet
- **Interface Gráfica Minimalista**: UI moderna e intuitiva usando Tkinter

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/mxs2/emb-inf-redes.git
```

2. Crie um ambiente virtual:
```bash
python3 -m venv venv
```

3. Ative o ambiente virtual:
```bash
source venv/bin/activate
```

4. Instale as dependências:
```bash
pip install -r requirements.txt
```

5. Execute a aplicação:
```bash
python src/main.py
```

## Como Rodar os Testes

Siga estes passos para executar a suíte de testes do projeto:

- **Caso ainda não tenha criado**
1. Criar e ativar um ambiente virtual (macOS/Linux - zsh):
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Instalar dependências (inclui `pytest`):
```bash
pip install -r requirements.txt
```

3. Executar a suíte de testes:
```bash
pytest -q -s 
```

## Estrutura do Projeto

```
wifi-monitor/
├── .github/
│   ├── INSTRUCTIONS.md       
│   └── PROMPTS.md           
├── docs/
│   ├── planejamento.md      # Este documento
│   ├── api_reference.pdf    # Documentação de APIs (futuro)
│   └── user_manual.pdf      # Manual do usuário (futuro)
├── logs/
│   └── app.log              # Logs da aplicação
├── src/
│   ├── main.py              # Ponto de entrada da aplicação
│   ├── core/
│   │   ├── __init__.py
│   │   ├── wifi_scanner.py  # Classe WifiScanner
│   │   ├── network_scanner.py # Classe NetworkScanner
│   │   └── health_tracker.py  # Classe HealthTracker
│   └── ui/
│       ├── __init__.py
│       └── gui.py           # Classe GUI (Tkinter)
├── tests/
│   ├── __init__.py
│   ├── test_core_health_tracker.py     # Testes do health tracker
│   ├── test_core_network_scanner.py    # Testes do network scanner
│   └── test_core_wifi_scanner.py       # Testes do wifi scanner
├── CHANGELOG.md
├── LICENSE
├── requirements.txt         # Dependências Python
├── .gitignore              # Arquivos ignorados pelo Git
└── README.md               # Documentação principal
```

## Tecnologias Utilizadas

- **Python 3.8+**
- **Tkinter**: Interface gráfica
- **tkinter.ttk**: Widgets modernos
- **Scapy**: Captura e análise de pacotes de rede
- **Python-nmap**: Escaneamento de rede
- **Subprocess**: Comandos do sistema operacional
- **Socket**: Operações de rede

## Escopo do Projeto

### Funcionalidades Principais

#### Scanner de Redes Wi-Fi
- ✅ Coletar informações de redes Wi-Fi próximas em tempo real
- ✅ Exibir intensidade de sinal (RSSI)
- ✅ Mostrar MAC Address e SSID
- ✅ Identificar canais utilizados
- ✅ Indicar se a rede é aberta ou protegida

#### Scanner de Dispositivos
- ✅ Varrer a rede local
- ✅ Listar dispositivos conectados
- ✅ Exibir endereços IP e MAC
- ✅ Identificar hostname quando disponível

#### Health Tracker
- ✅ Monitorar latência (ping)
- ✅ Exibir status de conectividade
- ✅ Gráfico de histórico de qualidade

### Classes Principais

#### `WifiScanner`
Responsável por escanear redes Wi-Fi disponíveis.

**Métodos:**
- `scan_networks()`: Retorna lista de redes
- `get_signal_strength(ssid)`: Retorna RSSI
- `get_network_info(ssid)`: Retorna detalhes completos

#### `NetworkScanner`
Escaneia dispositivos na rede local.

**Métodos:**
- `scan_devices()`: Retorna dispositivos conectados
- `get_device_info(ip)`: Retorna detalhes do dispositivo
- `resolve_hostname(ip)`: Tenta resolver nome do host

#### `HealthTracker`
Monitora a saúde da conexão.

**Métodos:**
- `ping_test(host)`: Testa latência
- `check_connectivity()`: Verifica conexão com internet
- `get_connection_quality()`: Retorna score de qualidade
- `log_metrics()`: Salva métricas históricas

#### `GUI`
Interface gráfica principal.

**Componentes:**
- Painel de redes Wi-Fi
- Painel de dispositivos
- Painel de health tracker
- Menu de configurações
- Botões de ação (scan, export, refresh)

## Requisitos de Sistema

### Sistema Operacional
- Windows 10/11 (principal)
- Linux (suporte secundário)
- macOS (suporte secundário)

### Permissões
- Privilégios de administrador (para Scapy e nmap)
- Acesso à interface de rede

### Hardware
- Adaptador Wi-Fi
- 4GB RAM (mínimo)
- 100MB espaço em disco

## Critérios de Sucesso

- ✅ Aplicação escaneia redes Wi-Fi com sucesso
- ✅ Aplicação lista dispositivos conectados
- ✅ Health tracker funciona em tempo real
- ✅ Interface gráfica é intuitiva e responsiva
- ✅ Logs são gerados corretamente
- ✅ Dados podem ser exportados
- ✅ Aplicação não trava ou apresenta erros críticos
- ✅ Documentação está completa

## 9. Referências

- [Scapy Documentation](https://scapy.readthedocs.io/)
- [Python-nmap Documentation](https://pypi.org/project/python-nmap/)
- [Tkinter Documentation](https://docs.python.org/3/library/tkinter.html)
- [Network Programming in Python](https://docs.python.org/3/library/socket.html)

## 📄 Licença

MIT License