# Troubleshooting - Solução de Problemas

## 🔧 Problemas Comuns

### 1. Erro ao Executar: "ModuleNotFoundError"

**Problema:**
```
ModuleNotFoundError: No module named 'scapy'
```

**Solução:**
```powershell
# Ative o ambiente virtual primeiro
.\venv\Scripts\Activate.ps1

# Instale as dependências
pip install -r requirements.txt
```

---

### 2. Erro de Permissão (Scapy)

**Problema:**
```
PermissionError: Operation not permitted
```

**Solução:**
Execute o PowerShell ou CMD como **Administrador**:
1. Clique com botão direito no PowerShell
2. Selecione "Executar como Administrador"
3. Execute novamente a aplicação

---

### 3. Comando netsh Falha

**Problema:**
```
Erro ao executar netsh: 'netsh' não é reconhecido
```

**Solução:**
Netsh é nativo do Windows. Se não funcionar:
1. Verifique se está no Windows
2. Tente reiniciar o terminal
3. Verifique variáveis de ambiente PATH

---

### 4. Python-nmap Não Funciona

**Problema:**
```
nmap not found
```

**Solução:**
Instale o nmap:
1. Baixe de: https://nmap.org/download.html
2. Instale (adicione ao PATH)
3. Reinicie o terminal
4. Teste: `nmap --version`

**Alternativa:**
Use ARP scan em vez de nmap:
```python
devices = network_scanner.scan_devices(use_nmap=False)
```

---

### 5. GUI Não Abre / Trava

**Problema:**
Interface não responde ou não abre.

**Solução:**
1. Verifique se há erros no terminal
2. Verifique logs em `logs/app.log`
3. Teste componentes individualmente:
```powershell
python src\core\wifi_scanner.py
python src\core\health_tracker.py
python src\ui\gui.py
```

---

### 6. Scan Muito Lento

**Problema:**
Scan de rede demora muito tempo.

**Solução:**
1. Reduza o range de IPs:
```python
# Em vez de /24 (256 IPs), use /28 (16 IPs)
scanner = NetworkScanner('192.168.1.0/28')
```

2. Use ARP em vez de nmap (mais rápido)
3. Verifique se não há problemas de rede

---

### 7. Nenhuma Rede Encontrada (Wi-Fi)

**Problema:**
Scan retorna lista vazia.

**Solução:**
1. Verifique se adaptador Wi-Fi está ativo
2. Execute como administrador
3. Teste comando manual:
```powershell
netsh wlan show networks mode=bssid
```

4. Se falhar, verifique drivers do Wi-Fi

---

### 8. Erro ao Importar Módulos

**Problema:**
```
ImportError: cannot import name 'WifiScanner'
```

**Solução:**
1. Verifique estrutura de pastas
2. Certifique-se que está executando do diretório raiz
3. Verifique `__init__.py` nas pastas

---

### 9. Encoding Error (Windows)

**Problema:**
```
UnicodeDecodeError: 'utf-8' codec can't decode
```

**Solução:**
Já tratado no código com `encoding='cp850'` para Windows.
Se persistir, verifique configurações regionais do Windows.

---

### 10. Virtual Environment Não Ativa

**Problema:**
```
.\venv\Scripts\Activate.ps1 cannot be loaded
```

**Solução:**
PowerShell bloqueia scripts por padrão:
```powershell
# Execute como Admin
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Tente novamente
.\venv\Scripts\Activate.ps1
```

---

## 🔍 Diagnóstico

### Verificar Instalação Python

```powershell
python --version
# Deve mostrar: Python 3.8.x ou superior
```

### Verificar Pacotes Instalados

```powershell
pip list
# Deve conter: scapy, python-nmap
```

### Verificar Logs

```powershell
# Ver últimas linhas do log
Get-Content logs\app.log -Tail 50
```

### Testar Componentes

```powershell
# Testar Health Tracker (mais simples)
python -c "from src.core.health_tracker import HealthTracker; t=HealthTracker(); print(t.ping_test())"
```

---

## 🐛 Reportar Bugs

Se encontrar um bug não listado aqui:

1. Verifique logs em `logs/app.log`
2. Anote o erro completo (stacktrace)
3. Descreva o que estava fazendo
4. Inclua:
   - Versão do Python
   - Sistema operacional
   - Passos para reproduzir

---

## 💡 Dicas de Performance

### Para Scans Mais Rápidos:

1. **Reduza o range de IPs**
   ```python
   NetworkScanner('192.168.1.1/29')  # Apenas 8 IPs
   ```

2. **Use timeouts menores**
   ```python
   wifi_scanner.scan_networks(timeout=5)
   ```

3. **Desative logs DEBUG**
   ```python
   logging.basicConfig(level=logging.INFO)  # Em vez de DEBUG
   ```

---

## 🔐 Problemas de Segurança

### Firewall Bloqueia Aplicação

**Windows Defender:**
1. Configurações > Privacidade e Segurança
2. Segurança do Windows > Firewall
3. Permitir aplicativo pelo firewall
4. Adicione Python

### Antivírus Bloqueia Scapy

Alguns antivírus bloqueiam Scapy (captura de pacotes):
1. Adicione exceção para Python
2. Adicione exceção para pasta do projeto
3. Temporariamente desative (não recomendado)

---

## 📞 Suporte

### Recursos:
- **Documentação:** `docs/planejamento.md`
- **Exemplos:** `docs/exemplos.md`
- **Prompts:** `.github/PROMPTS.md`
- **Instruções:** `.github/INSTRUCTIONS.md`

### Comunidade:
- GitHub Issues (quando disponível)
- Discussões do projeto

---

## 🔄 Reinstalação Completa

Se nada funcionar, reinstale do zero:

```powershell
# 1. Remover ambiente virtual
Remove-Item -Recurse -Force venv

# 2. Limpar cache Python
Remove-Item -Recurse -Force src\__pycache__
Remove-Item -Recurse -Force src\core\__pycache__
Remove-Item -Recurse -Force src\ui\__pycache__

# 3. Recriar ambiente
python -m venv venv
.\venv\Scripts\Activate.ps1

# 4. Reinstalar dependências
pip install --upgrade pip
pip install -r requirements.txt

# 5. Testar
python src\main.py
```

---

**Última Atualização:** 29/10/2025
