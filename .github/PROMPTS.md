# Prompts de Desenvolvimento - Monitor Wi-Fi

Este arquivo contém prompts úteis para auxiliar no desenvolvimento do projeto usando IA/Copilot.

---

## 🎯 Prompts Gerais

### Iniciar Feature
```
Preciso implementar [FEATURE]. O projeto é um monitor de Wi-Fi em Python com Tkinter.
Contexto: [descrever contexto]
Requisitos: [listar requisitos]
Por favor, sugira uma implementação seguindo PEP 8 e os padrões do projeto.
```

### Debug de Erro
```
Estou encontrando o seguinte erro:
[colar erro]

Contexto: [o que você estava tentando fazer]
Código relevante: [colar código]

Por favor, ajude a identificar e corrigir o problema.
```

---

## 📡 Prompts - WifiScanner

### Implementação Base
```
Preciso implementar a classe WifiScanner em Python que:
1. Escaneia redes Wi-Fi disponíveis
2. Retorna lista com SSID, BSSID, RSSI, canal
3. Funciona em Windows usando comandos netsh
4. Tem fallback para Scapy caso netsh falhe
5. Inclui tratamento de erros e logging

Por favor, forneça implementação completa com docstrings.
```

### Scapy Integration
```
Como usar Scapy para escanear redes Wi-Fi em Python?
Preciso capturar:
- SSID
- BSSID (MAC)
- Intensidade do sinal (RSSI)
- Canal
- Segurança (WPA/WPA2/Open)

Inclua tratamento para permissões de admin.
```

### Windows netsh Command
```
Preciso fazer parsing do comando 'netsh wlan show networks mode=bssid' em Python.
O output é em português do Windows.
Extrair: SSID, BSSID, Sinal (%), Canal, Tipo de autenticação.
Retornar como lista de dicionários.
```

---

## 🌐 Prompts - NetworkScanner

### Implementação com python-nmap
```
Implementar classe NetworkScanner que usa python-nmap para:
1. Escanear range de IPs (ex: 192.168.1.0/24)
2. Detectar dispositivos ativos
3. Identificar IP, MAC, hostname
4. Executar em thread separada
5. Atualizar progressão para GUI

Incluir tratamento de erros se nmap não estiver instalado.
```

### ARP Scan Alternative
```
Implementar scan de rede usando ARP com Scapy como alternativa ao nmap.
Deve:
- Escanear subnet local
- Retornar IP e MAC de cada dispositivo
- Ser mais rápido que nmap
- Funcionar sem nmap instalado
```

### Device Info Enrichment
```
Após obter lista de IPs e MACs, como enriquecer dados com:
1. Hostname via DNS reverso
2. Vendor do MAC address (OUI lookup)
3. Portas abertas comuns (opcional)

Implementar função que recebe lista de dispositivos e retorna com info adicional.
```

---

## 💚 Prompts - HealthTracker

### Ping Implementation
```
Implementar método ping_test() que:
1. Faz ping para 8.8.8.8 (Google DNS)
2. Retorna latência em ms
3. Funciona cross-platform (Windows/Linux/Mac)
4. Usa subprocess sem bloquear GUI
5. Timeout de 2 segundos

Incluir tratamento para quando não há conexão.
```

### Connection Quality Algorithm
```
Criar algoritmo para calcular "health score" (0-100) baseado em:
- Latência (ping): peso 40%
  * <20ms = excelente
  * 20-50ms = bom
  * 50-100ms = regular
  * >100ms = ruim
- Packet loss: peso 30%
- Jitter: peso 20%
- Uptime: peso 10%

Retornar score e categoria (Excelente/Bom/Regular/Ruim).
```

### Historical Data
```
Implementar sistema para salvar métricas históricas:
1. Salvar ping, timestamp a cada minuto
2. Armazenar em arquivo JSON
3. Limitar últimos 1000 registros
4. Função para ler e retornar últimos N registros
5. Função para calcular estatísticas (média, min, max)
```

---

## 🎨 Prompts - GUI (Tkinter)

### Layout Minimalista
```
Criar interface Tkinter minimalista e moderna com:
- Tema escuro (#1e1e1e background)
- 3 painéis principais: Redes Wi-Fi, Dispositivos, Health
- Cores: ciano (#00d4ff) para destaques
- Fonte: Segoe UI
- Cantos arredondados (se possível)
- Sem bordas tradicionais

Fornecer código completo do layout base.
```

### Network List Display
```
Implementar widget Tkinter para exibir lista de redes Wi-Fi:
- Usar Treeview ou Frame com Labels
- Mostrar: SSID, Sinal (barra/%), Canal, Segurança
- Ordenar por intensidade de sinal
- Cor do sinal: verde (>70%), amarelo (40-70%), vermelho (<40%)
- Refresh button
- Visual minimalista
```

### Real-time Health Indicator
```
Criar widget para mostrar saúde da conexão em tempo real:
- Circle/Arc que preenche baseado no score (0-100)
- Cor: verde (80-100), amarelo (50-79), vermelho (<50)
- Mostrar latência numérica
- Último update timestamp
- Animação suave ao atualizar

Pode usar Canvas do Tkinter.
```

### Threading in Tkinter
```
Como executar scans em background sem travar GUI Tkinter?
Preciso:
1. Botão que inicia scan
2. Scan roda em thread separada
3. Mostrar "loading" durante scan
4. Atualizar GUI com resultados quando pronto
5. Permitir cancelar scan

Fornecer exemplo completo com threading e queue.
```

---

## 🔧 Prompts - Integração

### Main.py Structure
```
Criar main.py que:
1. Inicializa instâncias de WifiScanner, NetworkScanner, HealthTracker
2. Cria janela GUI
3. Passa instâncias das classes para GUI
4. Configura logging
5. Trata CTRL+C para fechar gracefully
6. Verifica permissões de admin no Windows

Fornecer código completo.
```

### Auto-refresh System
```
Implementar sistema de auto-refresh que:
1. Atualiza dados a cada X segundos (configurável)
2. Usa threading para não bloquear
3. Pode ser pausado/resumido
4. Mostra countdown até próximo refresh
5. Permite refresh manual imediato

Integrar com GUI Tkinter.
```

### Export Functionality
```
Implementar exportação de dados para:
1. CSV: lista de redes ou dispositivos
2. JSON: dados completos incluindo timestamps
3. Dialog para escolher local e formato
4. Incluir metadados (data/hora da exportação)

Usar tkinter.filedialog.
```

---

## 📊 Prompts - Visualização

### Signal Strength Chart
```
Criar gráfico de barras horizontais em Tkinter Canvas mostrando:
- SSID no lado esquerdo
- Barra colorida proporcional ao sinal (%)
- Cores: verde/amarelo/vermelho
- Valor numérico (dBm ou %)
- Ordenado do melhor para pior sinal
```

### Historical Ping Graph
```
Implementar gráfico de linha mostrando latência ao longo do tempo:
- Eixo X: tempo (últimos 30 minutos)
- Eixo Y: latência (ms)
- Usar Canvas do Tkinter
- Atualizar em tempo real
- Linha suave, cor ciano
```

---

## 🐛 Prompts - Debug/Troubleshooting

### Permission Issues
```
Scapy está dando erro de permissão no Windows.
Erro: [colar erro]

Como:
1. Detectar se tenho permissões admin?
2. Solicitar elevação se necessário?
3. Implementar fallback que não requer admin?
```

### Cross-platform Issues
```
Meu código funciona no Windows mas precisa suportar Linux/Mac.
Feature: [descrever]
Código atual: [colar]

Como fazer detecção de SO e adaptar comandos?
Usar `platform.system()` e abstrair comandos.
```

---

## 📝 Prompts - Documentação

### Generate Docstrings
```
Adicionar docstrings Google Style para esta classe/função:
[colar código]

Incluir:
- Descrição
- Args com tipos
- Returns com tipo
- Raises (exceções)
- Example
```

### README Generation
```
Atualizar README.md com:
- Seção de screenshots/demo
- Troubleshooting comum
- FAQ
- Como contribuir
- Badges (Python version, license)

Baseado no estado atual do projeto.
```

---

## 🚀 Prompts - Otimização

### Performance Optimization
```
Meu scan está demorando muito (>30s).
Código: [colar]

Como otimizar para:
1. Reduzir tempo de scan
2. Melhorar responsividade
3. Usar threads/async eficientemente
4. Cachear resultados quando apropriado
```

### Memory Management
```
Aplicação está consumindo muita memória após várias horas rodando.
Suspeito: [logs históricos/cache/threads]

Como:
1. Limitar tamanho de listas/caches
2. Limpar threads antigas
3. Implementar garbage collection manual se necessário
```

---

## 🎓 Prompts - Aprendizado

### Understand Scapy
```
Explique como Scapy funciona para capturar pacotes Wi-Fi.
Conceitos: beacon frames, probe requests/responses.
Como extrair SSID e RSSI de packets?
Exemplo prático simples.
```

### Network Fundamentals
```
Explique conceitos para entender melhor o projeto:
- RSSI vs dBm vs percentual de sinal
- SSID vs BSSID
- Canais Wi-Fi e overlap
- ARP protocol
- Como funciona scan de rede
```

---

## 💡 Prompts - Features Extras (Opcional)

### Notification System
```
Adicionar notificações quando:
1. Novo dispositivo conecta na rede
2. Sinal cai abaixo de threshold
3. Conexão cai

Usar sistema de notificações do Windows (toast).
```

### Channel Recommendation
```
Analisar redes Wi-Fi próximas e recomendar melhor canal:
1. Identificar canais menos congestionados
2. Considerar overlap de canais (1, 6, 11)
3. Mostrar gráfico de uso por canal
4. Sugerir melhor canal para configurar router
```

### Speed Test Integration
```
Integrar teste de velocidade (download/upload) na aplicação.
Usar speedtest-cli library ou implementação própria.
Mostrar resultado no health tracker.
Executar em thread separada.
```

---

## 🛡️ Prompts - Segurança/Ética

### Ethical Considerations
```
Listar considerações éticas e legais para esta aplicação:
1. O que NÃO devemos implementar
2. Como garantir uso apenas em redes próprias
3. Disclaimers necessários
4. Dados que não devem ser salvos

Gerar texto de disclaimer para README.
```

---

**Como Usar Este Arquivo:**

1. Copie o prompt relevante
2. Adapte com detalhes específicos do seu caso
3. Cole no chat do GitHub Copilot / ChatGPT / Claude
4. Refine baseado na resposta

**Dica:** Seja específico e forneça contexto. Quanto mais informação, melhor a resposta!

---

**Última Atualização:** 29/10/2025
