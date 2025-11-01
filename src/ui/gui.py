"""
MonitorGUI - Interface gráfica principal do Monitor Wi-Fi

Interface minimalista usando Tkinter com tema escuro.
"""

import logging
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from typing import Optional
from datetime import datetime
from collections import deque


# Paleta de cores
COLORS = {
    'background': '#1e1e1e',
    'surface': '#2d2d2d',
    'surface_light': '#3d3d3d',
    'primary': '#00d4ff',
    'secondary': '#00ff9f',
    'text': '#ffffff',
    'text_secondary': '#b0b0b0',
    'success': '#00ff9f',
    'warning': '#ffd700',
    'danger': '#ff4444',
}


class MonitorGUI:
    """
    Classe principal da interface gráfica.
    
    Attributes:
        root (tk.Tk): Janela principal
        wifi_scanner: Instância do WifiScanner
        network_scanner: Instância do NetworkScanner
        health_tracker: Instância do HealthTracker
    """
    
    def __init__(self, wifi_scanner, network_scanner, health_tracker):
        """
        Inicializa a interface gráfica.
        
        Args:
            wifi_scanner: Instância do WifiScanner
            network_scanner: Instância do NetworkScanner
            health_tracker: Instância do HealthTracker
        """
        self.logger = logging.getLogger(__name__)
        
        # Instâncias dos scanners
        self.wifi_scanner = wifi_scanner
        self.network_scanner = network_scanner
        self.health_tracker = health_tracker
        
        # Criar janela principal
        self.root = tk.Tk()
        self.root.title("Monitor Wi-Fi")
        self.root.geometry("1200x700")
        self.root.configure(bg=COLORS['background'])
        
        # Configurar estilo
        self._setup_style()
        
        # Criar interface
        self._create_widgets()
        
        # Flags de controle
        self.is_scanning = False
        self.auto_refresh = True
        self.is_closing = False
        
        # Dados do gráfico (últimos 60 pontos = 5 minutos a 5s cada)
        self.health_history = deque(maxlen=60)
        self.health_timestamps = deque(maxlen=60)
        
        # Canvas do gráfico
        self.health_canvas = None
        
        # Iniciar atualização automática
        self._schedule_auto_refresh()
        
        self.logger.info("GUI inicializada")
    
    def _setup_style(self):
        """Configura o estilo dos widgets."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Frame style
        style.configure('Custom.TFrame',
                       background=COLORS['background'])
        
        style.configure('Surface.TFrame',
                       background=COLORS['surface'])
        
        # Label style
        style.configure('Title.TLabel',
                       background=COLORS['background'],
                       foreground=COLORS['primary'],
                       font=('Segoe UI', 20, 'bold'))
        
        style.configure('Header.TLabel',
                       background=COLORS['surface'],
                       foreground=COLORS['text'],
                       font=('Segoe UI', 12, 'bold'))
        
        style.configure('Normal.TLabel',
                       background=COLORS['surface'],
                       foreground=COLORS['text'],
                       font=('Segoe UI', 10))
        
        style.configure('Secondary.TLabel',
                       background=COLORS['surface'],
                       foreground=COLORS['text_secondary'],
                       font=('Segoe UI', 9))
        
        # Button style
        style.configure('Primary.TButton',
                       background=COLORS['primary'],
                       foreground=COLORS['background'],
                       font=('Segoe UI', 10, 'bold'),
                       borderwidth=0)
        
        style.map('Primary.TButton',
                 background=[('active', COLORS['secondary'])])
    
    def _create_widgets(self):
        """Cria todos os widgets da interface."""
        # Container principal
        main_container = ttk.Frame(self.root, style='Custom.TFrame')
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        title_label = ttk.Label(
            main_container,
            text="📡 Monitor Wi-Fi",
            style='Title.TLabel'
        )
        title_label.pack(pady=(0, 20))
        
        # Container dos painéis (3 colunas)
        panels_container = ttk.Frame(main_container, style='Custom.TFrame')
        panels_container.pack(fill=tk.BOTH, expand=True)
        
        # Configurar grid com 3 colunas - cada coluna com largura mínima
        panels_container.columnconfigure(0, weight=1, minsize=350)
        panels_container.columnconfigure(1, weight=1, minsize=350)
        panels_container.columnconfigure(2, weight=1, minsize=350)
        panels_container.rowconfigure(0, weight=1, minsize=400)
        
        # Painel 1: Redes Wi-Fi 
        self.wifi_panel = self._create_wifi_panel(panels_container)
        self.wifi_panel.grid(row=0, column=0, padx=(0, 5), sticky='nsew')
        
        # Painel 2: Dispositivos
        self.devices_panel = self._create_devices_panel(panels_container)
        self.devices_panel.grid(row=0, column=1, padx=5, sticky='nsew')
        
        # Painel 3: Health Tracker
        self.health_panel = self._create_health_panel(panels_container)
        self.health_panel.grid(row=0, column=2, padx=(5, 0), sticky='nsew')
        
        # Barra de ações no rodapé
        self._create_action_bar(main_container)
    
    def _create_wifi_panel(self, parent) -> ttk.Frame:
        """
        Cria painel de redes Wi-Fi com scroll.
        
        Args:
            parent: Widget pai
            
        Returns:
            ttk.Frame: Frame do painel
        """
        panel = ttk.Frame(parent, style='Surface.TFrame', width=350)
        
        # Header fixo (não rola)
        self.wifi_header = ttk.Label(panel, text="Redes Wi-Fi", style='Header.TLabel')
        self.wifi_header.pack(pady=10, padx=10, anchor='w')
        
        # Container com scroll
        scroll_container = ttk.Frame(panel, style='Surface.TFrame')
        scroll_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Canvas para scroll
        self.wifi_canvas = tk.Canvas(
            scroll_container,
            bg=COLORS['surface'],
            highlightthickness=0
        )
        scrollbar = ttk.Scrollbar(scroll_container, orient="vertical", command=self.wifi_canvas.yview)
        self.wifi_scrollable = ttk.Frame(self.wifi_canvas, style='Surface.TFrame')
        
        self.wifi_scrollable.bind(
            "<Configure>",
            lambda e: self.wifi_canvas.configure(scrollregion=self.wifi_canvas.bbox("all"))
        )
        
        self.wifi_canvas.create_window((0, 0), window=self.wifi_scrollable, anchor="nw")
        self.wifi_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.wifi_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Placeholder inicial
        placeholder = ttk.Label(
            self.wifi_scrollable,
            text="Clique em 'Escanear Wi-Fi' para começar",
            style='Secondary.TLabel'
        )
        placeholder.pack(expand=True, pady=20)
        
        return panel
    
    def _create_devices_panel(self, parent) -> ttk.Frame:
        """
        Cria painel de dispositivos com scroll.
        
        Args:
            parent: Widget pai
            
        Returns:
            ttk.Frame: Frame do painel
        """
        panel = ttk.Frame(parent, style='Surface.TFrame', width=350)
        
        # Header fixo (não rola)
        self.devices_header = ttk.Label(panel, text="Dispositivos Conectados", style='Header.TLabel')
        self.devices_header.pack(pady=10, padx=10, anchor='w')
        
        # Container com scroll
        scroll_container = ttk.Frame(panel, style='Surface.TFrame')
        scroll_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Canvas para scroll
        self.devices_canvas = tk.Canvas(
            scroll_container,
            bg=COLORS['surface'],
            highlightthickness=0
        )
        scrollbar = ttk.Scrollbar(scroll_container, orient="vertical", command=self.devices_canvas.yview)
        self.devices_scrollable = ttk.Frame(self.devices_canvas, style='Surface.TFrame')
        
        self.devices_scrollable.bind(
            "<Configure>",
            lambda e: self.devices_canvas.configure(scrollregion=self.devices_canvas.bbox("all"))
        )
        
        self.devices_canvas.create_window((0, 0), window=self.devices_scrollable, anchor="nw")
        self.devices_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.devices_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Placeholder inicial
        placeholder = ttk.Label(
            self.devices_scrollable,
            text="Clique em 'Escanear Rede' para começar",
            style='Secondary.TLabel'
        )
        placeholder.pack(expand=True, pady=20)
        
        return panel
    
    def _create_health_panel(self, parent) -> ttk.Frame:
        """
        Cria painel de health tracker.
        
        Args:
            parent: Widget pai
            
        Returns:
            ttk.Frame: Frame do painel
        """
        panel = ttk.Frame(parent, style='Surface.TFrame')
        
        # Header fixo (não rola)
        self.health_header = ttk.Label(panel, text="Saúde da Conexão", style='Header.TLabel')
        self.health_header.pack(pady=10, padx=10, anchor='w')
        
        # Área de conteúdo scrollável (se necessário no futuro)
        self.health_content = ttk.Frame(panel, style='Surface.TFrame')
        self.health_content.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Placeholder - Score
        score_label = ttk.Label(
            self.health_content,
            text="--",
            font=('Segoe UI', 48, 'bold'),
            foreground=COLORS['text_secondary'],
            background=COLORS['surface']
        )
        score_label.pack(expand=True, pady=(10, 0))
        
        category_label = ttk.Label(
            self.health_content,
            text="Verificando...",
            style='Secondary.TLabel'
        )
        category_label.pack()
        
        return panel
    
    def _create_action_bar(self, parent):
        """
        Cria barra de ações no rodapé.
        
        Args:
            parent: Widget pai
        """
        action_bar = ttk.Frame(parent, style='Custom.TFrame')
        action_bar.pack(fill=tk.X, pady=(20, 0))
        
        # Botão: Escanear Wi-Fi
        btn_scan_wifi = ttk.Button(
            action_bar,
            text="📡 Escanear Wi-Fi",
            command=self._on_scan_wifi,
            style='Primary.TButton'
        )
        btn_scan_wifi.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botão: Escanear Rede
        btn_scan_network = ttk.Button(
            action_bar,
            text="🌐 Escanear Rede",
            command=self._on_scan_network,
            style='Primary.TButton'
        )
        btn_scan_network.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botão: Verificar Saúde
        btn_health = ttk.Button(
            action_bar,
            text="💚 Verificar Saúde",
            command=self._on_check_health,
            style='Primary.TButton'
        )
        btn_health.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botão: Auto-refresh
        self.btn_auto_refresh = ttk.Button(
            action_bar,
            text="⏸️ Pausar Auto-Refresh",
            command=self._toggle_auto_refresh,
            style='Primary.TButton'
        )
        self.btn_auto_refresh.pack(side=tk.LEFT)
        
        # Spacer
        ttk.Frame(action_bar, style='Custom.TFrame').pack(side=tk.LEFT, expand=True)
        
        # Status label
        self.status_label = ttk.Label(
            action_bar,
            text="Pronto • Auto-refresh: 5s",
            style='Secondary.TLabel'
        )
        self.status_label.pack(side=tk.RIGHT)
    
    def _on_scan_wifi(self):
        """Handler para botão de scan Wi-Fi."""
        if self.is_scanning:
            self.logger.warning("Scan já em andamento")
            return
        
        self.logger.info("Iniciando scan Wi-Fi...")
        self.status_label.config(text="Escaneando redes Wi-Fi...")
        
        # Executar em thread separada
        thread = threading.Thread(target=self._scan_wifi_thread, daemon=True)
        thread.start()
    
    def _scan_wifi_thread(self):
        """Thread para executar scan Wi-Fi."""
        try:
            self.is_scanning = True
            networks = self.wifi_scanner.scan_networks()
            
            # Atualizar GUI na thread principal
            self.root.after(0, self._update_wifi_display, networks)
            
        except Exception as e:
            self.logger.exception("Erro ao escanear Wi-Fi")
            self.root.after(0, self._show_error, f"Erro ao escanear Wi-Fi: {str(e)}")
        finally:
            self.is_scanning = False
            self.root.after(0, lambda: self.status_label.config(text="Pronto"))
    
    def _update_wifi_display(self, networks):
        """
        Atualiza display de redes Wi-Fi no frame scrollável.
        
        Args:
            networks (list): Lista de redes detectadas
        """
        self.logger.info(f"Exibindo {len(networks)} redes")
        
        # Atualizar apenas o header fixo
        self.wifi_header.config(text=f"Redes Wi-Fi ({len(networks)})")
        
        # Limpar apenas o conteúdo scrollável
        for widget in self.wifi_scrollable.winfo_children():
            widget.destroy()
        
        if not networks:
            placeholder = ttk.Label(
                self.wifi_scrollable,
                text="Nenhuma rede encontrada",
                style='Secondary.TLabel'
            )
            placeholder.pack(expand=True, pady=20)
            self.status_label.config(text="Nenhuma rede encontrada")
            return
        
        # Ordenar por sinal (melhor primeiro)
        networks_sorted = sorted(networks, key=lambda x: x.get('signal_percent', 0), reverse=True)
        
        # Exibir cada rede no frame scrollável
        for net in networks_sorted:
            self._create_wifi_item(self.wifi_scrollable, net)
        
        # Forçar atualização do canvas
        self.wifi_scrollable.update_idletasks()
        self.wifi_canvas.configure(scrollregion=self.wifi_canvas.bbox("all"))
        
        self.status_label.config(text=f"Encontradas {len(networks)} redes")
    
    def _on_scan_network(self):
        """Handler para botão de scan de rede."""
        if self.is_scanning:
            self.logger.warning("Scan já em andamento")
            return
        
        self.logger.info("Iniciando scan de rede...")
        self.status_label.config(text="Escaneando dispositivos...")
        
        # Executar em thread separada
        thread = threading.Thread(target=self._scan_network_thread, daemon=True)
        thread.start()
    
    def _scan_network_thread(self):
        """Thread para executar scan de rede."""
        try:
            self.is_scanning = True
            devices = self.network_scanner.scan_devices(use_nmap=False)
            
            # Atualizar GUI na thread principal
            self.root.after(0, self._update_devices_display, devices)
            
        except Exception as e:
            self.logger.exception("Erro ao escanear rede")
            self.root.after(0, self._show_error, f"Erro ao escanear rede: {str(e)}")
        finally:
            self.is_scanning = False
            self.root.after(0, lambda: self.status_label.config(text="Pronto"))
    
    def _update_devices_display(self, devices):
        """
        Atualiza display de dispositivos no frame scrollável.
        
        Args:
            devices (list): Lista de dispositivos detectados
        """
        self.logger.info(f"Exibindo {len(devices)} dispositivos")
        
        # Atualizar apenas o header fixo
        self.devices_header.config(text=f"Dispositivos Conectados ({len(devices)})")
        
        # Limpar apenas o conteúdo scrollável
        for widget in self.devices_scrollable.winfo_children():
            widget.destroy()
        
        if not devices:
            placeholder = ttk.Label(
                self.devices_scrollable,
                text="Nenhum dispositivo encontrado",
                style='Secondary.TLabel'
            )
            placeholder.pack(expand=True, pady=20)
            self.status_label.config(text="Nenhum dispositivo encontrado")
            return
        
        # Exibir cada dispositivo no frame scrollável
        for device in devices:
            self._create_device_item(self.devices_scrollable, device)
        
        # Forçar atualização do canvas
        self.devices_scrollable.update_idletasks()
        self.devices_canvas.configure(scrollregion=self.devices_canvas.bbox("all"))
        
        self.status_label.config(text=f"Encontrados {len(devices)} dispositivos")
    
    def _on_check_health(self):
        """Handler para botão de verificar saúde."""
        self.logger.info("Verificando saúde da conexão...")
        self.status_label.config(text="Verificando saúde...")
        
        # Executar em thread separada
        thread = threading.Thread(target=self._check_health_thread, daemon=True)
        thread.start()
    
    def _check_health_thread(self):
        """Thread para verificar saúde."""
        try:
            # Obter score detalhado
            health_data = self.health_tracker.get_health_score(detailed=True)
            
            # Extrair score e categoria
            if isinstance(health_data, dict):
                score = health_data['score']
                category = health_data['category']
            else:
                # Fallback para versão antiga
                score = health_data
                category = self.health_tracker.get_health_category(score)
            
            # Atualizar GUI na thread principal
            self.root.after(0, self._update_health_display, score, category)
            
        except Exception as e:
            self.logger.exception("Erro ao verificar saúde")
            self.root.after(0, self._show_error, f"Erro ao verificar saúde: {str(e)}")
        finally:
            self.root.after(0, lambda: self.status_label.config(text="Pronto"))
    
    def _create_wifi_item(self, parent, network):
        """
        Cria item visual melhorado para uma rede Wi-Fi.
        
        Args:
            parent: Widget pai
            network (dict): Dados da rede
        """
        # Container do item com borda arredondada e sombra sutil
        item_frame = tk.Frame(
            parent,
            bg=COLORS['surface_light'],
            highlightbackground=COLORS['background'],
            highlightthickness=1,
            bd=0,
        )
        # Remover margens laterais para ocupar toda largura
        item_frame.pack(fill=tk.X, pady=1, padx=0)

        # Cor baseada no sinal
        signal = network.get('signal_percent', 0)
        if signal >= 70:
            signal_color = COLORS['success']
        elif signal >= 40:
            signal_color = COLORS['warning']
        else:
            signal_color = COLORS['danger']

        # Layout horizontal super compacto
        ssid = network.get('ssid', 'Unknown')
        channel = network.get('channel', '?')
        security = network.get('security', 'Unknown')
        info_text = f"Canal {channel} • {security}"

        # Frame principal horizontal
        row = tk.Frame(item_frame, bg=COLORS['surface_light'])
        row.pack(fill=tk.X, expand=True, padx=0, pady=6)

        # Coluna esquerda: SSID e info
        left = tk.Frame(row, bg=COLORS['surface_light'])
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ssid_label = tk.Label(
            left,
            text=f"📡 {ssid}",
            font=('Segoe UI', 10, 'bold'),
            fg=COLORS['text'],
            bg=COLORS['surface_light'],
            anchor='w',
            padx=0, pady=0
        )
        ssid_label.pack(anchor='w')
        info_label = tk.Label(
            left,
            text=info_text,
            font=('Segoe UI', 8),
            fg=COLORS['text_secondary'],
            bg=COLORS['surface_light'],
            anchor='w',
            padx=0, pady=0
        )
        info_label.pack(anchor='w')

        # Coluna direita: Sinal
        right = tk.Frame(row, bg=COLORS['surface_light'])
        right.pack(side=tk.RIGHT, padx=(6, 0))
        signal_label = tk.Label(
            right,
            text=f"{signal}%",
            font=('Segoe UI', 13, 'bold'),
            fg=signal_color,
            bg=COLORS['surface_light'],
            padx=0, pady=0
        )
        signal_label.pack()
    
    def _create_device_item(self, parent, device):
        """
        Cria item visual melhorado para um dispositivo.
        
        Args:
            parent: Widget pai
            device (dict): Dados do dispositivo
        """
        # Container do item com borda arredondada e sombra sutil
        item_frame = tk.Frame(
            parent,
            bg=COLORS['surface_light'],
            highlightbackground=COLORS['background'],
            highlightthickness=1,
            bd=0,
        )
        # Remover margens laterais para ocupar toda largura
        item_frame.pack(fill=tk.X, pady=2, padx=0)
        
        # Layout horizontal compacto
        ip = device.get('ip', 'Unknown')
        hostname = device.get('hostname', 'Unknown')
        mac = device.get('mac', 'Unknown')
        if hostname and hostname != 'Unknown' and hostname != mac:
            info_text = f"{hostname} • {mac}"
        else:
            info_text = f"MAC: {mac}"
        
        # Frame principal horizontal
        row = tk.Frame(item_frame, bg=COLORS['surface_light'])
        row.pack(fill=tk.X, expand=True, padx=0, pady=6)
        
        # Coluna esquerda: IP e info
        left = tk.Frame(row, bg=COLORS['surface_light'])
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ip_label = tk.Label(
            left,
            text=f"🖥️ {ip}",
            font=('Segoe UI', 10, 'bold'),
            fg=COLORS['text'],
            bg=COLORS['surface_light'],
            anchor='w'
        )
        ip_label.pack(anchor='w')
        info_label = tk.Label(
            left,
            text=info_text,
            font=('Segoe UI', 8),
            fg=COLORS['text_secondary'],
            bg=COLORS['surface_light'],
            anchor='w'
        )
        info_label.pack(anchor='w', pady=(2, 0))
        
        # Coluna direita: Status
        right = tk.Frame(row, bg=COLORS['surface_light'])
        right.pack(side=tk.RIGHT, padx=(10, 0))
        status_label = tk.Label(
            right,
            text="●",
            font=('Segoe UI', 14),
            fg=COLORS['success'],
            bg=COLORS['surface_light']
        )
        status_label.pack()
    
    def _update_health_display(self, score, category):
        """
        Atualiza display de saúde com gráfico em tempo real.
        
        Args:
            score (int): Score de saúde
            category (str): Categoria de saúde
        """
        self.logger.info(f"Score: {score}, Categoria: {category}")
        
        # Adicionar ao histórico
        now = datetime.now()
        self.health_history.append(score)
        self.health_timestamps.append(now)
        
        # Limpar apenas o conteúdo (não o header)
        for widget in self.health_content.winfo_children():
            widget.destroy()
        
        # Cor baseada no score
        if score >= 80:
            score_color = COLORS['success']
        elif score >= 60:
            score_color = COLORS['warning']
        else:
            score_color = COLORS['danger']
        
        # Score grande (com tamanho limitado para não sair da tela)
        score_label = tk.Label(
            self.health_content,
            text=str(score),
            font=('Segoe UI', 60, 'bold'),
            fg=score_color,
            bg=COLORS['surface'],
            wraplength=280
        )
        score_label.pack(pady=(15, 0))
        
        # Categoria
        category_label = tk.Label(
            self.health_content,
            text=category,
            font=('Segoe UI', 14),
            fg=score_color,
            bg=COLORS['surface']
        )
        category_label.pack(pady=(0, 10))
        
        # Obter informações detalhadas
        health_data = self.health_tracker.get_health_score(detailed=True)
        
        # Frame para métricas detalhadas (centralizado)
        metrics_frame = tk.Frame(self.health_content, bg=COLORS['surface'])
        metrics_frame.pack(pady=(5, 0))
        
        # Latência
        latency = health_data.get('latency')
        if latency is not None and isinstance(latency, (int, float)) and latency > 0:
            latency_color = COLORS['success'] if latency < 50 else (COLORS['warning'] if latency < 100 else COLORS['danger'])
            latency_label = tk.Label(
                metrics_frame,
                text=f"📡 {latency:.0f}ms",
                font=('Segoe UI', 9),
                fg=latency_color,
                bg=COLORS['surface']
            )
            latency_label.pack(side=tk.LEFT, padx=8)
        
        # Perda de pacotes (apenas se houver perda > 0)
        packet_loss = health_data.get('packet_loss')
        if packet_loss is not None and isinstance(packet_loss, (int, float)) and packet_loss > 0:
            loss_color = COLORS['warning'] if packet_loss < 10 else COLORS['danger']
            loss_label = tk.Label(
                metrics_frame,
                text=f"⚠️ {packet_loss:.0f}% perda",
                font=('Segoe UI', 9),
                fg=loss_color,
                bg=COLORS['surface']
            )
            loss_label.pack(side=tk.LEFT, padx=8)
        
        # Jitter (apenas se > 5ms para não poluir)
        jitter = health_data.get('jitter')
        if jitter is not None and isinstance(jitter, (int, float)) and jitter > 5:
            jitter_color = COLORS['warning'] if jitter < 30 else COLORS['danger']
            jitter_label = tk.Label(
                metrics_frame,
                text=f"📈 {jitter:.0f}ms",
                font=('Segoe UI', 9),
                fg=jitter_color,
                bg=COLORS['surface']
            )
            jitter_label.pack(side=tk.LEFT, padx=8)
        
        # Separador visual
        separator = tk.Frame(self.health_content, bg=COLORS['surface_light'], height=1)
        separator.pack(fill=tk.X, pady=(20, 10), padx=30)
        
        # Gráfico de histórico
        if len(self.health_history) >= 2:
            self._draw_health_graph(self.health_content)
        
        self.status_label.config(text=f"Saúde: {category} ({score}/100)")
    
    def _draw_health_graph(self, parent):
        """
        Desenha gráfico minimalista e limpo de histórico de saúde.
        
        Args:
            parent: Widget pai
        """
        # Dimensões do canvas (maior e mais espaçoso)
        canvas_width = 320
        canvas_height = 160
        padding_left = 40
        padding_right = 15
        padding_top = 20
        padding_bottom = 30
        
        self.health_canvas = tk.Canvas(
            parent,
            width=canvas_width,
            height=canvas_height,
            bg=COLORS['surface'],
            highlightthickness=0
        )
        self.health_canvas.pack(pady=(10, 15))
        
        # Área útil do gráfico
        graph_width = canvas_width - padding_left - padding_right
        graph_height = canvas_height - padding_top - padding_bottom
        
        # Desenhar linhas de referência sutis (apenas 3 linhas)
        reference_values = [100, 50, 0]
        for value in reference_values:
            y = padding_top + graph_height - (graph_height * value / 100)
            
            # Linha tracejada
            dash_length = 3
            for x in range(padding_left, canvas_width - padding_right, dash_length * 2):
                self.health_canvas.create_line(
                    x, y, min(x + dash_length, canvas_width - padding_right), y,
                    fill=COLORS['surface_light'], width=1
                )
            
            # Label do valor
            self.health_canvas.create_text(
                padding_left - 8, y,
                text=str(value),
                fill=COLORS['text_secondary'],
                font=('Segoe UI', 9),
                anchor='e'
            )
        
        # Desenhar área preenchida sob a linha (gradiente visual)
        if len(self.health_history) >= 2:
            points = []
            
            # Calcular pontos da linha
            for i, score in enumerate(self.health_history):
                x = padding_left + (graph_width * i / (len(self.health_history) - 1))
                y = padding_top + graph_height - (graph_height * score / 100)
                points.append((x, y))
            
            # Desenhar área preenchida (polígono)
            if len(points) >= 2:
                poly_points = []
                
                # Começar do canto inferior esquerdo
                poly_points.extend([points[0][0], padding_top + graph_height])
                
                # Adicionar todos os pontos da linha
                for x, y in points:
                    poly_points.extend([x, y])
                
                # Fechar no canto inferior direito
                poly_points.extend([points[-1][0], padding_top + graph_height])
                
                # Criar polígono com transparência simulada
                self.health_canvas.create_polygon(
                    poly_points,
                    fill=COLORS['primary'],
                    outline='',
                    stipple='gray25'  # Padrão pontilhado para simular transparência
                )
            
            # Desenhar linha principal (mais grossa)
            line_points = []
            for x, y in points:
                line_points.extend([x, y])
            
            self.health_canvas.create_line(
                line_points,
                fill=COLORS['primary'],
                width=3,
                smooth=True,
                capstyle=tk.ROUND,
                joinstyle=tk.ROUND
            )
            
            # Desenhar apenas o último ponto (mais destaque)
            last_x, last_y = points[-1]
            last_score = self.health_history[-1]
            
            # Cor do ponto baseada no score
            if last_score >= 80:
                point_color = COLORS['success']
            elif last_score >= 60:
                point_color = COLORS['warning']
            else:
                point_color = COLORS['danger']
            
            # Círculo externo (halo)
            self.health_canvas.create_oval(
                last_x - 6, last_y - 6, last_x + 6, last_y + 6,
                fill='',
                outline=point_color,
                width=2
            )
            
            # Círculo interno (preenchido)
            self.health_canvas.create_oval(
                last_x - 3, last_y - 3, last_x + 3, last_y + 3,
                fill=point_color,
                outline=''
            )
            
            # Mostrar valor do último ponto (posicionado dinamicamente)
            # Se o ponto está muito no topo, mostrar embaixo ao invés de em cima
            text_y = last_y - 15 if last_y > 30 else last_y + 15
            text_anchor = 's' if last_y > 30 else 'n'
            
            self.health_canvas.create_text(
                last_x, text_y,
                text=f"{last_score}",
                fill=point_color,
                font=('Segoe UI', 10, 'bold'),
                anchor=text_anchor
            )
        
        # Informação de tempo no rodapé
        if self.health_timestamps:
            elapsed = (datetime.now() - self.health_timestamps[0]).total_seconds()
            if elapsed < 60:
                time_info = f"Últimos {int(elapsed)}s"
            else:
                time_info = f"Últimos {int(elapsed / 60)}min"
            
            self.health_canvas.create_text(
                canvas_width / 2, canvas_height - 12,
                text=f"{len(self.health_history)} pontos • {time_info}",
                fill=COLORS['text_secondary'],
                font=('Segoe UI', 8),
                anchor='center'
            )
    
    def _toggle_auto_refresh(self):
        """Alterna o auto-refresh."""
        self.auto_refresh = not self.auto_refresh
        
        if self.auto_refresh:
            self.btn_auto_refresh.config(text="⏸️ Pausar Auto-Refresh")
            self.status_label.config(text="Pronto • Auto-refresh: 5s")
            self.logger.info("Auto-refresh ativado")
        else:
            self.btn_auto_refresh.config(text="▶️ Retomar Auto-Refresh")
            self.status_label.config(text="Pronto • Auto-refresh pausado")
            self.logger.info("Auto-refresh pausado")
    
    def _schedule_auto_refresh(self):
        """Agenda atualização automática a cada 5 segundos."""
        if self.is_closing:
            return
        
        # Verificar saúde automaticamente a cada 5 segundos
        if self.auto_refresh and not self.is_scanning:
            self._on_check_health()
        
        # Agendar próxima atualização
        self.root.after(5000, self._schedule_auto_refresh)  # 5 segundos
    
    def _show_error(self, message):
        """
        Exibe mensagem de erro.
        
        Args:
            message (str): Mensagem de erro
        """
        messagebox.showerror("Erro", message)
    
    def run(self):
        """Inicia o loop principal da GUI."""
        self.logger.info("Iniciando loop da GUI")
        
        # Protocolo de fechamento
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Iniciar loop
        self.root.mainloop()
    
    def _on_closing(self):
        """Handler para fechamento da janela."""
        self.logger.info("Fechando aplicação...")
        
        # Sinalizar que está fechando
        self.is_closing = True
        self.auto_refresh = False
        
        # Parar monitoramento
        if self.health_tracker.is_monitoring:
            self.health_tracker.stop_monitoring()
        
        # Fechar janela
        self.root.destroy()


if __name__ == "__main__":
    # Teste básico
    logging.basicConfig(level=logging.DEBUG)
    
    # Mock dos scanners para teste
    class MockScanner:
        def scan_networks(self):
            return []
        def scan_devices(self, use_nmap=True):
            return []
        def get_health_score(self):
            return 85
        def get_health_category(self, score):
            return "Excelente"
    
    mock = MockScanner()
    app = MonitorGUI(mock, mock, mock)
    app.run()
