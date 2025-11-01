# Documento de Planejamento Inicial - Monitor de Sinal Wi-Fi

**Data:** 29 de Outubro de 2025  
**Versão:** 1.0

---

## 1. Tema do Projeto

**Monitor de Sinal Wi-Fi com Health Tracker**

Aplicação desktop para monitoramento em tempo real de redes Wi-Fi, permitindo visualizar intensidade de sinal, redes disponíveis, dispositivos conectados e análise de saúde da conexão de internet.

---

## 2. Escopo do Projeto

### 2.1 Funcionalidades Principais

#### Possibilidade 1: Scanner de Redes Wi-Fi
- ✅ Coletar informações de redes Wi-Fi próximas em tempo real
- ✅ Exibir intensidade de sinal (RSSI)
- ✅ Mostrar MAC Address e SSID
- ✅ Identificar canais utilizados
- ✅ Indicar se a rede é aberta ou protegida

#### Possibilidade 2: Scanner de Dispositivos
- ✅ Varrer a rede local
- ✅ Listar dispositivos conectados
- ✅ Exibir endereços IP e MAC
- ✅ Identificar hostname quando disponível

#### Funcionalidade Extra: Health Tracker
- ✅ Monitorar latência (ping)
- ✅ Testar velocidade de conexão
- ✅ Exibir status de conectividade
- ✅ Gráfico de histórico de qualidade

### 2.2 Requisitos Não-Funcionais
- Interface gráfica minimalista e moderna
- Atualização em tempo real
- Baixo consumo de recursos
- Logs de atividades
- Exportação de dados em CSV/JSON

### 2.3 Fora do Escopo (V1)
- Ataque ou invasão de redes
- Descriptografia de senhas
- Análise de tráfego profunda
- Suporte a redes 5G

---

## 3. Tecnologias Utilizadas

### 3.1 Linguagem
- **Python 3.8+**: Linguagem principal do projeto

### 3.2 Bibliotecas Core

#### Interface Gráfica
- **Tkinter**: Interface gráfica nativa
- **tkinter.ttk**: Widgets modernos

#### Networking
- **Scapy**: Captura e análise de pacotes
- **Python-nmap**: Escaneamento de rede
- **Subprocess**: Execução de comandos do sistema
- **Socket**: Operações de rede

#### Utilitários
- **Threading**: Processamento paralelo
- **JSON**: Persistência de dados
- **CSV**: Exportação de relatórios
- **Logging**: Sistema de logs
- **DateTime**: Timestamps

### 3.3 Ferramentas de Desenvolvimento
- **Git/GitHub**: Controle de versão
- **VSCode**: IDE recomendada
- **pip**: Gerenciador de pacotes
- **Virtual Environment**: Isolamento de dependências

---

## 4. Arquitetura do Sistema

### 4.1 Estrutura de Pastas

```
wifi-monitor/
├── .github/
│   ├── INSTRUCTIONS.md       # Instruções para contribuidores
│   └── PROMPTS.md           # Prompts para desenvolvimento
├── docs/
│   ├── planejamento.md      # Este documento
│   ├── api_reference.pdf    # Documentação de APIs (futuro)
│   └── user_manual.pdf      # Manual do usuário (futuro)
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
├── logs/
│   └── app.log              # Logs da aplicação
├── exports/
│   └── (arquivos CSV/JSON exportados)
├── requirements.txt         # Dependências Python
├── .gitignore              # Arquivos ignorados pelo Git
└── README.md               # Documentação principal
```

### 4.2 Classes Principais

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

---

## 5. Divisão de Tarefas

### 5.1 Sprint 1 - Semana 1 (Setup e Estrutura)
**Responsável:** Todos

- [ ] Configurar ambiente Python (virtualenv)
- [ ] Instalar dependências
- [ ] Criar estrutura de pastas
- [ ] Configurar Git/GitHub
- [ ] Criar classes base (esqueleto)
- [ ] Documentação inicial (.github/)

### 5.2 Sprint 2 - Semana 2-3 (Core Functionality)

#### Backend (Core)
**Responsável:** Dev 1

- [ ] Implementar `WifiScanner`
  - [ ] Método scan com Scapy
  - [ ] Método usando comandos do SO (netsh/iwlist)
  - [ ] Parsing de resultados
  - [ ] Tratamento de erros

- [ ] Implementar `NetworkScanner`
  - [ ] Integração com python-nmap
  - [ ] Scan de range de IPs
  - [ ] Resolução de hostnames

- [ ] Implementar `HealthTracker`
  - [ ] Testes de ping
  - [ ] Cálculo de métricas
  - [ ] Persistência de histórico

#### Frontend (UI)
**Responsável:** Dev 2

- [ ] Criar layout principal (Tkinter)
- [ ] Implementar painel de redes
- [ ] Implementar painel de dispositivos
- [ ] Implementar painel de health
- [ ] Adicionar gráficos/visualizações
- [ ] Implementar tema minimalista

### 5.3 Sprint 3 - Semana 4 (Integração)
**Responsável:** Todos

- [ ] Integrar backend com frontend
- [ ] Implementar threading para scans
- [ ] Adicionar sistema de logs
- [ ] Implementar exportação de dados
- [ ] Testes de integração

### 5.4 Sprint 4 - Semana 5 (Finalização)
**Responsável:** Todos

- [ ] Testes finais
- [ ] Correção de bugs
- [ ] Documentação completa
- [ ] README atualizado
- [ ] Preparar apresentação
- [ ] Entrega final

---

## 6. Cronograma

| Semana | Marco | Entregáveis |
|--------|-------|-------------|
| 1 | Setup Completo | Ambiente configurado, estrutura criada, docs iniciais |
| 2-3 | Core Features | Classes implementadas e testadas individualmente |
| 4 | Integração | Aplicação funcional com UI básica |
| 5 | Release | Aplicação completa, testada e documentada |

---

## 7. Requisitos de Sistema

### 7.1 Sistema Operacional
- Windows 10/11 (principal)
- Linux (suporte secundário)
- macOS (suporte secundário)

### 7.2 Permissões
- Privilégios de administrador (para Scapy e nmap)
- Acesso à interface de rede

### 7.3 Hardware
- Adaptador Wi-Fi
- 4GB RAM (mínimo)
- 100MB espaço em disco

---

## 8. Riscos e Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|-------|--------------|---------|-----------|
| Scapy requer admin | Alta | Médio | Implementar fallback com comandos SO |
| Incompatibilidade SO | Média | Alto | Testes em múltiplos SOs, abstrair comandos |
| Performance lenta | Média | Médio | Threading, otimização de scans |
| Falso positivos | Baixa | Baixo | Validação de dados, tratamento de erros |

---

## 9. Critérios de Sucesso

- ✅ Aplicação escaneia redes Wi-Fi com sucesso
- ✅ Aplicação lista dispositivos conectados
- ✅ Health tracker funciona em tempo real
- ✅ Interface gráfica é intuitiva e responsiva
- ✅ Logs são gerados corretamente
- ✅ Dados podem ser exportados
- ✅ Aplicação não trava ou apresenta erros críticos
- ✅ Documentação está completa

---

## 10. Referências

- [Scapy Documentation](https://scapy.readthedocs.io/)
- [Python-nmap Documentation](https://pypi.org/project/python-nmap/)
- [Tkinter Documentation](https://docs.python.org/3/library/tkinter.html)
- [Network Programming in Python](https://docs.python.org/3/library/socket.html)

---

**Última Atualização:** 29/10/2025  
**Status:** Em Desenvolvimento
