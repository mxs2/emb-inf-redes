# Monitor de Sinal Wi-Fi

Aplicação Python para monitoramento em tempo real de redes Wi-Fi, exibindo informações como intensidade de sinal (RSSI), MAC/SSID de redes próximas e dispositivos conectados.

## Funcionalidades

- **Monitoramento em Tempo Real**: Coleta contínua de dados de redes Wi-Fi
- **Análise de Sinal**: Exibe RSSI, SSID, MAC Address e canal
- **Scanner de Dispositivos**: Lista dispositivos conectados na rede
- **Health Tracker**: Monitora a "saúde" da conexão de internet
- **Interface Gráfica Minimalista**: UI moderna e intuitiva usando Tkinter

## Tecnologias Utilizadas

- **Python 3.8+**
- **Tkinter**: Interface gráfica
- **Scapy**: Captura e análise de pacotes de rede
- **Python-nmap**: Escaneamento de rede
- **Subprocess**: Comandos do sistema operacional

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/wifi-monitor.git
cd wifi-monitor
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Execute a aplicação:
```bash
python src/main.py
```

## Estrutura do Projeto

```
wifi-monitor/
├── .github/
│   ├── INSTRUCTIONS.md
│   └── PROMPTS.md
├── docs/
│   └── planejamento.md
├── src/
│   ├── main.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── wifi_scanner.py
│   │   ├── network_scanner.py
│   │   └── health_tracker.py
│   └── ui/
│       ├── __init__.py
│       └── gui.py
├── logs/
├── requirements.txt
└── README.md
```

## Equipe e Divisão de Tarefas

Ver [docs/planejamento.md](docs/planejamento.md) para detalhes completos.

## 📄 Licença

MIT License
