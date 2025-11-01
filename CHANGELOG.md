# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [1.0.0] - 2025-10-29 🎉

### ✅ Lançamento Completo e Funcional

#### Adicionado
- ✅ **Wi-Fi Scanner** totalmente funcional
  - Parser completo de netsh (Windows)
  - Suporte Linux (nmcli/iwlist) e macOS (airport)
  - Testado: 5 redes encontradas
- ✅ **Network Scanner** totalmente funcional
  - Auto-detecção de range de rede
  - Métodos: nmap, ARP (Scapy), ping
  - Testado: 5 dispositivos encontrados em ~15s
- ✅ **Health Tracker** completo
  - Score 0-100 com 4 métricas
  - Latência (40%), Packet Loss (30%), Jitter (20%), Uptime (10%)
  - Persistência em JSON
- ✅ **Interface Gráfica** completa
  - Design dark theme minimalista
  - 3 painéis responsivos
  - Threading para não travar
  - Auto-refresh a cada 30s
- ✅ Scripts de execução como admin (run_admin.bat, run_admin.ps1)
- ✅ Script de teste dedicado (test_network.py)
- ✅ Documentação completa (8+ arquivos markdown)

#### Corrigido
- 🐛 Network Scanner retornando 0 dispositivos (auto-detecção implementada)
- 🐛 Wi-Fi Scanner não parseava saída do netsh (parser implementado)
- 🐛 Scapy falhando sem Npcap (fallback para ping)
- 🐛 Todos os TODOs do código resolvidos

#### Documentação Adicionada
- docs/NETWORK_SCANNER_FIX.md - Documentação da correção
- QUICKSTART.md - Guia de início rápido
- SCANS_FUNCIONANDO.md - Evidência dos testes
- SUMMARY.md - Resumo executivo

## [Não Lançado]

### Planejado para v1.1.0
- 📊 Exportação de dados (CSV/JSON)
- 🔔 Alertas de dispositivos novos/perdidos
- 📈 Gráficos históricos de saúde
- 🌐 Suporte a múltiplas interfaces
- 🔍 Detecção de vendor por MAC (API)
- ⚙️ Configurações persistentes

## [0.1.0] - 2025-10-29

### Adicionado (Versão Inicial - Esqueletos)
- Estrutura inicial do projeto MVC
- Documentação base (README, INSTRUCTIONS, PROMPTS)
- Esqueleto de código para WifiScanner
- Esqueleto de código para NetworkScanner
- Esqueleto de código para HealthTracker
- Interface gráfica base com Tkinter
- Sistema de logging
- Documento de planejamento detalhado
- Arquivo de requisitos (requirements.txt)
- Script de setup (setup.ps1)
- Exemplos de uso
- Licença MIT

### Em Desenvolvimento
- Parsing de output netsh (Windows)
- Scan ARP com Scapy
- Display de redes na GUI
- Display de dispositivos na GUI
- Gráficos de histórico

---

## Notas de Versão

### Versão 0.1.0 - Setup Inicial
Esta é a primeira versão do projeto, contendo a estrutura base e documentação.
O código está funcional mas muitas features ainda precisam ser implementadas.

**Status dos Componentes:**

- ✅ **Estrutura de Projeto**: Completa
- ✅ **Documentação**: Completa
- ✅ **Sistema de Logging**: Funcional
- ✅ **GUI Base**: Funcional
- 🚧 **WifiScanner**: Parcialmente implementado
- 🚧 **NetworkScanner**: Parcialmente implementado
- ✅ **HealthTracker**: Funcional
- ❌ **Exportação**: Não implementado
- ❌ **Gráficos**: Não implementado

**Funcionalidades Testadas:**
- [x] Estrutura de pastas
- [x] Importação de módulos
- [x] Inicialização da GUI
- [x] Sistema de logging
- [x] Health tracker básico
- [ ] Scan completo de Wi-Fi
- [ ] Scan completo de rede
- [ ] Visualização de dados

**Requisitos:**
- Python 3.8+
- Windows 10/11 (recomendado)
- Privilégios de administrador
- Scapy
- python-nmap (opcional)

**Problemas Conhecidos:**
- Parsing netsh ainda não implementado
- ARP scan com Scapy não implementado
- Visualização de dados na GUI não implementada
- Sistema de exportação não implementado

---

### Próximas Versões

#### Versão 0.2.0 (Planejada)
- Implementar parsing completo netsh
- Implementar ARP scan
- Adicionar visualização de redes na GUI
- Adicionar visualização de dispositivos na GUI

#### Versão 0.3.0 (Planejada)
- Implementar gráficos de histórico
- Adicionar sistema de exportação
- Melhorar interface visual
- Adicionar configurações

#### Versão 1.0.0 (Planejada)
- Todas as features principais implementadas
- Testes completos
- Documentação finalizada
- Release estável
