# Instruções para Desenvolvimento

## 🎯 Objetivo do Projeto

Desenvolver um Monitor de Sinal Wi-Fi com interface gráfica minimalista e funcional, capaz de:
1. Escanear e exibir redes Wi-Fi disponíveis
2. Listar dispositivos conectados na rede
3. Monitorar a "saúde" da conexão de internet em tempo real

## 🚀 Como Começar

### 1. Setup do Ambiente

```bash
# Clone o repositório
git clone <url-do-repositorio>
cd wifi-monitor

# Crie um ambiente virtual
python -m venv venv

# Ative o ambiente virtual
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Windows CMD:
.\venv\Scripts\activate.bat
# Linux/Mac:
source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt
```

### 2. Permissões Necessárias

**Windows:**
- Execute o PowerShell ou CMD como Administrador
- Algumas funcionalidades do Scapy requerem privilégios elevados

**Linux:**
```bash
sudo apt-get install python3-scapy
sudo setcap cap_net_raw,cap_net_admin=eip $(which python3)
```

**macOS:**
```bash
sudo pip install scapy
```

## 📐 Padrões de Código

### Estilo Python (PEP 8)

```python
# ✅ Bom
class WifiScanner:
    """Classe para escanear redes Wi-Fi."""
    
    def __init__(self):
        self.networks = []
    
    def scan_networks(self) -> list:
        """Escaneia redes Wi-Fi disponíveis."""
        pass

# ❌ Evitar
class wifi_scanner:
    def __init__(self):
        self.Networks = []
    def ScanNetworks(self):
        pass
```

### Nomenclatura

- **Classes:** PascalCase (`WifiScanner`, `HealthTracker`)
- **Funções/Métodos:** snake_case (`scan_networks`, `get_signal_strength`)
- **Constantes:** UPPER_SNAKE_CASE (`MAX_RETRY`, `DEFAULT_TIMEOUT`)
- **Variáveis:** snake_case (`signal_strength`, `network_list`)

### Documentação

```python
def scan_networks(self, timeout: int = 5) -> list:
    """
    Escaneia redes Wi-Fi disponíveis.
    
    Args:
        timeout (int): Tempo máximo de scan em segundos. Default: 5
        
    Returns:
        list: Lista de dicionários com informações das redes
              [{'ssid': str, 'bssid': str, 'rssi': int, 'channel': int}]
    
    Raises:
        PermissionError: Se não houver privilégios suficientes
        TimeoutError: Se o scan exceder o tempo limite
    """
    pass
```

## 🏗️ Arquitetura

### Separação de Responsabilidades

```
src/
├── main.py              # Ponto de entrada, inicializa GUI
├── core/                # Lógica de negócio
│   ├── wifi_scanner.py  # Scans de Wi-Fi
│   ├── network_scanner.py # Scans de dispositivos
│   └── health_tracker.py  # Monitoramento de saúde
└── ui/
    └── gui.py           # Interface gráfica
```

### Fluxo de Dados

```
main.py → GUI → Core Classes → GUI (atualiza display)
```

## 🎨 Design da Interface

### Princípios

1. **Minimalista:** Apenas informações essenciais
2. **Responsivo:** Atualizações em tempo real sem travar
3. **Intuitivo:** Não requer manual para usar
4. **Consistente:** Padrões visuais uniformes

### Paleta de Cores Sugerida

```python
COLORS = {
    'background': '#1e1e1e',      # Preto suave
    'surface': '#2d2d2d',         # Cinza escuro
    'primary': '#00d4ff',         # Azul ciano
    'secondary': '#00ff9f',       # Verde ciano
    'text': '#ffffff',            # Branco
    'text_secondary': '#b0b0b0',  # Cinza claro
    'success': '#00ff9f',         # Verde
    'warning': '#ffd700',         # Amarelo/Ouro
    'danger': '#ff4444',          # Vermelho
}
```

### Componentes UI

```python
# Exemplo de estilo para widgets Tkinter
style = ttk.Style()
style.theme_use('clam')
style.configure('Custom.TFrame', background=COLORS['background'])
style.configure('Custom.TLabel', 
                background=COLORS['background'],
                foreground=COLORS['text'],
                font=('Segoe UI', 10))
```

## 🔧 Funcionalidades Core

### WifiScanner

```python
class WifiScanner:
    """Escaneia redes Wi-Fi disponíveis."""
    
    def __init__(self):
        self.networks = []
        self.interface = None
    
    def scan_networks(self) -> list:
        """Retorna lista de redes Wi-Fi."""
        # Implementação usando Scapy ou comandos SO
        pass
    
    def get_signal_strength(self, bssid: str) -> int:
        """Retorna RSSI de uma rede específica."""
        pass
```

### NetworkScanner

```python
class NetworkScanner:
    """Escaneia dispositivos na rede local."""
    
    def __init__(self, network_range: str = '192.168.1.0/24'):
        self.network_range = network_range
        self.devices = []
    
    def scan_devices(self) -> list:
        """Retorna lista de dispositivos conectados."""
        # Implementação usando python-nmap
        pass
```

### HealthTracker

```python
class HealthTracker:
    """Monitora saúde da conexão."""
    
    def __init__(self):
        self.metrics = []
        self.is_monitoring = False
    
    def start_monitoring(self):
        """Inicia monitoramento contínuo."""
        pass
    
    def ping_test(self, host: str = '8.8.8.8') -> float:
        """Retorna latência em ms."""
        pass
    
    def get_health_score(self) -> int:
        """Retorna score de 0-100."""
        pass
```

## 🧵 Threading

Para não travar a interface:

```python
import threading

def scan_in_background(self):
    """Executa scan em thread separada."""
    thread = threading.Thread(target=self._perform_scan, daemon=True)
    thread.start()

def _perform_scan(self):
    """Método interno para scan."""
    results = self.scanner.scan_networks()
    # Atualiza GUI usando queue ou after()
    self.root.after(0, self.update_display, results)
```

## 📝 Sistema de Logs

```python
import logging

# Configurar logger
logging.basicConfig(
    filename='logs/app.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Uso
logger.info("Scan iniciado")
logger.error("Falha ao escanear: %s", error)
```

## 🐛 Tratamento de Erros

```python
try:
    networks = scanner.scan_networks()
except PermissionError:
    logger.error("Permissões insuficientes")
    messagebox.showerror("Erro", "Execute como administrador")
except TimeoutError:
    logger.warning("Scan timeout")
    messagebox.showwarning("Aviso", "Scan demorou demais")
except Exception as e:
    logger.exception("Erro inesperado")
    messagebox.showerror("Erro", f"Erro: {str(e)}")
```

## 🧪 Testes

```python
# Criar testes unitários em tests/
def test_wifi_scanner():
    scanner = WifiScanner()
    networks = scanner.scan_networks()
    assert isinstance(networks, list)
    if networks:
        assert 'ssid' in networks[0]
        assert 'rssi' in networks[0]
```

## 📦 Git Workflow

```bash
# Criar branch para nova feature
git checkout -b feature/wifi-scanner

# Commits descritivos
git commit -m "feat: implementa WifiScanner com Scapy"
git commit -m "fix: corrige timeout no scan de redes"
git commit -m "docs: atualiza README com instruções"

# Push e Pull Request
git push origin feature/wifi-scanner
```

### Convenção de Commits

- `feat:` Nova funcionalidade
- `fix:` Correção de bug
- `docs:` Documentação
- `style:` Formatação
- `refactor:` Refatoração
- `test:` Testes
- `chore:` Tarefas gerais

## 🚀 Deploy/Entrega

### Checklist Final

- [ ] Código funciona em Windows
- [ ] Todas as features implementadas
- [ ] Interface está responsiva e bonita
- [ ] Logs estão sendo gerados
- [ ] README atualizado
- [ ] Documentação completa
- [ ] Sem erros críticos
- [ ] Testes básicos passando

### Executável (Opcional)

```bash
# Criar executável com PyInstaller
pip install pyinstaller
pyinstaller --onefile --windowed --icon=icon.ico src/main.py
```

## 📚 Recursos Úteis

- [Scapy Tutorial](https://scapy.readthedocs.io/en/latest/usage.html)
- [Tkinter Tutorial](https://docs.python.org/3/library/tkinter.html)
- [Python Nmap](https://pypi.org/project/python-nmap/)
- [Threading Guide](https://docs.python.org/3/library/threading.html)

## 💡 Dicas

1. **Teste frequentemente:** Rode o código após cada mudança
2. **Commits pequenos:** Faça commits incrementais
3. **Documente conforme desenvolve:** Não deixe para depois
4. **Use logs:** Facilita debug
5. **Peça ajuda:** Use os prompts em PROMPTS.md

## ⚠️ Avisos Importantes

- **Nunca comitar senhas ou dados sensíveis**
- **Respeitar privacidade:** Não salvar dados pessoais sem consentimento
- **Uso ético:** Ferramenta apenas para redes próprias
- **Teste com cuidado:** Scans podem impactar a rede

---

**Última Atualização:** 29/10/2025
