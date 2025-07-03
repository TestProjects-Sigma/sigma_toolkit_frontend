import sys
import os
import subprocess
import json
import hashlib
try:
    from importlib.metadata import distribution, PackageNotFoundError
except ImportError:
    # Fallback for Python < 3.8
    from importlib_metadata import distribution, PackageNotFoundError
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QScrollArea, QPushButton, QLabel, 
                             QMessageBox, QGridLayout, QFrame, QDialog, QLineEdit,
                             QDialogButtonBox, QFormLayout, QSpinBox, QComboBox,
                             QTextEdit, QMenu, QAction, QFileDialog, QListWidget,
                             QListWidgetItem, QCheckBox, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, QFileSystemWatcher, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt5.QtGui import QFont, QIcon, QPainter, QPainterPath, QLinearGradient, QColor, QPen


class AnimatedButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._animation = QPropertyAnimation(self, b"geometry")
        self._animation.setDuration(200)
        self._animation.setEasingCurve(QEasingCurve.OutCubic)
        
    def enterEvent(self, event):
        super().enterEvent(event)
        # Add subtle scale animation on hover
        
    def leaveEvent(self, event):
        super().leaveEvent(event)


class NetworkToolCard(QPushButton):
    def __init__(self, app_name, app_info, theme, button_size):
        super().__init__()
        self.app_name = app_name
        self.app_info = app_info
        self.theme = theme
        
        # Determine tool category and icon
        self.category, self.icon = self.categorize_tool(app_name, app_info)
        
        # Set up the card
        self.setup_card(button_size)
        
    def categorize_tool(self, app_name, app_info):
        """Categorize the tool based on name and assign appropriate icon"""
        name_lower = app_name.lower()
        
        categories = {
            'scanner': ('🔍', ['scan', 'nmap', 'port', 'discover', 'probe']),
            'monitor': ('📊', ['monitor', 'watch', 'status', 'health', 'ping']),
            'analyzer': ('📈', ['analyze', 'packet', 'traffic', 'wireshark', 'tcpdump']),
            'security': ('🔒', ['security', 'audit', 'vuln', 'password', 'auth']),
            'config': ('⚙️', ['config', 'setup', 'manage', 'admin']),
            'backup': ('💾', ['backup', 'restore', 'archive', 'sync']),
            'vpn': ('🔐', ['vpn', 'tunnel', 'proxy', 'gateway']),
            'dns': ('🌐', ['dns', 'domain', 'resolve', 'lookup']),
            'firewall': ('🛡️', ['firewall', 'fw', 'iptables', 'filter']),
            'wireless': ('📡', ['wifi', 'wireless', 'wlan', 'ap']),
            'automation': ('🤖', ['auto', 'script', 'deploy', 'ansible']),
            'reporting': ('📋', ['report', 'log', 'audit', 'compliance'])
        }
        
        for category, (icon, keywords) in categories.items():
            if any(keyword in name_lower for keyword in keywords):
                return category.title(), icon
                
        # Default for networking tools
        return 'Network Tool', '🔧'
    
    def setup_card(self, button_size):
        """Set up the visual card design"""
        # Card dimensions
        size_map = {
            "Small": (180, 100),
            "Medium": (220, 120),
            "Large": (260, 140)
        }
        width, height = size_map.get(button_size, (220, 120))
        self.setFixedSize(width, height)
        
        # Get display name
        display_name = self.app_info.get('display_name', self.app_info['name'])
        display_name = display_name.replace('_', ' ').title()
        
        # Status indicators
        has_requirements = self.app_info['requirements'].exists()
        has_readme = self.app_info['readme'].exists()
        is_external = self.app_info['source'] == 'external'
        
        # Create card styling with modern design
        card_style = f"""
            QPushButton {{
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 {self.theme['button_bg']}, 
                    stop: 0.5 {self.theme['content_bg']},
                    stop: 1 {self.theme['button_bg']});
                border: 2px solid {self.theme['button_border']};
                border-radius: 12px;
                font-size: 11px;
                font-weight: bold;
                color: {self.theme['text_color']};
                text-align: left;
                padding: 12px;
                margin: 2px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 {self.theme['button_hover']}, 
                    stop: 0.5 {self.theme['title_color']},
                    stop: 1 {self.theme['button_hover']});
                border-color: {self.theme['title_color']};
                color: white;
                transform: translateY(-2px);
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 {self.theme['button_pressed']}, 
                    stop: 1 {self.theme['button_hover']});
                transform: translateY(1px);
            }}
        """
        self.setStyleSheet(card_style)
        
        # Create card content with better layout
        status_line = ""
        if has_requirements:
            status_line += "📦 "
        if has_readme:
            status_line += "📖 "
        if is_external:
            status_line += "🔗"
            
        # Multi-line text with icon, name, category, and status
        card_text = f"{self.icon}  {display_name}\n{self.category}\n{status_line}"
        self.setText(card_text)
        
        # Add shadow effect for depth
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(8)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(2, 2)
        self.setGraphicsEffect(shadow)
        
        # Tooltip with detailed info
        tooltip_text = f"""
        <b>{display_name}</b><br>
        Category: {self.category}<br>
        Type: {'External' if is_external else 'Local'}<br>
        Dependencies: {'Yes' if has_requirements else 'No'}<br>
        Documentation: {'Yes' if has_readme else 'No'}<br>
        <br>
        <i>Left click: Launch tool<br>
        Right click: View options</i>
        """
        self.setToolTip(tooltip_text)


class ReadmeDialog(QDialog):
    def __init__(self, app_name, readme_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"README - {app_name}")
        self.setModal(True)
        self.resize(700, 500)
        
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel(f"📖 {app_name} - Documentation")
        header_label.setFont(QFont("Arial", 14, QFont.Bold))
        header_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(header_label)
        
        # Text area for readme content
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        self.text_area.setStyleSheet("""
            QTextEdit {
                background-color: #ffffff;
                border: 1px solid #dddddd;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
                line-height: 1.4;
            }
        """)
        
        # Load readme content
        self.load_readme(readme_path)
        layout.addWidget(self.text_area)
        
        # Close button
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.close)
        layout.addWidget(button_box)
    
    def load_readme(self, readme_path):
        """Load and display readme content"""
        try:
            if readme_path.exists():
                with open(readme_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.text_area.setPlainText(content)
            else:
                self.text_area.setPlainText("No README.md file found for this application.")
        except Exception as e:
            self.text_area.setPlainText(f"Error loading README.md: {str(e)}")


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.setWindowTitle("⚙️ Network Tools Settings")
        self.setModal(True)
        self.setFixedSize(520, 420)
        
        layout = QVBoxLayout(self)
        
        # Form layout for settings
        form_layout = QFormLayout()
        
        # Grid columns setting
        self.columns_spinbox = QSpinBox()
        self.columns_spinbox.setRange(1, 6)
        self.columns_spinbox.setValue(parent.grid_columns if parent else 3)
        form_layout.addRow("Grid Columns:", self.columns_spinbox)
        
        # Button size setting
        self.button_size_combo = QComboBox()
        self.button_size_combo.addItems(["Small", "Medium", "Large"])
        self.button_size_combo.setCurrentText(parent.button_size if parent else "Medium")
        form_layout.addRow("Card Size:", self.button_size_combo)
        
        # Theme setting
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark"])
        self.theme_combo.setCurrentText(parent.current_theme if parent else "Light")
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        form_layout.addRow("Theme:", self.theme_combo)
        
        layout.addLayout(form_layout)
        
        # External paths section
        self.external_paths_label = QLabel("External Tool Paths:")
        layout.addWidget(self.external_paths_label)
        
        self.external_paths_list = QListWidget()
        self.external_paths_list.setMaximumHeight(100)
        if parent:
            for path in parent.settings.get('external_paths', []):
                self.external_paths_list.addItem(path)
        layout.addWidget(self.external_paths_list)
        
        # External path buttons
        path_buttons_layout = QHBoxLayout()
        
        self.add_path_btn = QPushButton("➕ Add Tool Path")
        self.add_path_btn.clicked.connect(self.add_external_path)
        path_buttons_layout.addWidget(self.add_path_btn)
        
        self.remove_path_btn = QPushButton("➖ Remove")
        self.remove_path_btn.clicked.connect(self.remove_external_path)
        path_buttons_layout.addWidget(self.remove_path_btn)
        
        path_buttons_layout.addStretch()
        layout.addLayout(path_buttons_layout)
        
        # App name customization
        self.app_names_label = QLabel("Custom Tool Names:")
        layout.addWidget(self.app_names_label)
        
        self.app_names_layout = QVBoxLayout()
        layout.addLayout(self.app_names_layout)
        
        # Dialog buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)
        
        # Load current app names
        if parent:
            self.load_app_names(parent.discovered_apps, parent.settings.get('custom_names', {}))
        
        # Apply initial theme
        self.apply_dialog_theme()
    
    def on_theme_changed(self, theme_name):
        """Handle theme change in real time"""
        if self.parent_window:
            # Temporarily update parent theme for preview
            old_theme = self.parent_window.current_theme
            self.parent_window.current_theme = theme_name
            self.apply_dialog_theme()
            # Restore original theme (will be applied when OK is clicked)
            self.parent_window.current_theme = old_theme
    
    def apply_dialog_theme(self):
        """Apply theme styling to the settings dialog"""
        if not self.parent_window:
            return
            
        theme = self.parent_window.themes[self.theme_combo.currentText()]
        
        # Main dialog styling with enhanced design
        self.setStyleSheet(f"""
            QDialog {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 {theme['main_bg']}, stop: 1 {theme['content_bg']});
                color: {theme['text_color']};
            }}
            QLabel {{
                color: {theme['text_color']};
                font-weight: bold;
                margin: 5px 0px;
            }}
            QSpinBox {{
                background-color: {theme['content_bg']};
                border: 2px solid {theme['border_color']};
                border-radius: 6px;
                padding: 8px;
                color: {theme['text_color']};
                min-height: 20px;
            }}
            QSpinBox:focus {{
                border-color: {theme['title_color']};
            }}
            QComboBox {{
                background-color: {theme['content_bg']};
                border: 2px solid {theme['border_color']};
                border-radius: 6px;
                padding: 8px;
                color: {theme['text_color']};
                min-height: 20px;
            }}
            QComboBox:focus {{
                border-color: {theme['title_color']};
            }}
            QComboBox::drop-down {{
                border: none;
                background-color: {theme['button_bg']};
                border-radius: 4px;
            }}
            QComboBox::down-arrow {{
                border: 2px solid {theme['text_color']};
                border-top: none;
                border-right: none;
                width: 6px;
                height: 6px;
                margin-right: 5px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {theme['content_bg']};
                border: 1px solid {theme['border_color']};
                color: {theme['text_color']};
                selection-background-color: {theme['button_hover']};
            }}
            QListWidget {{
                background-color: {theme['content_bg']};
                border: 2px solid {theme['border_color']};
                border-radius: 6px;
                color: {theme['text_color']};
                padding: 5px;
            }}
            QListWidget::item {{
                padding: 5px;
                border-radius: 3px;
                margin: 1px;
            }}
            QListWidget::item:selected {{
                background-color: {theme['button_hover']};
                color: {theme['title_color']};
            }}
            QLineEdit {{
                background-color: {theme['content_bg']};
                border: 2px solid {theme['border_color']};
                border-radius: 6px;
                padding: 8px;
                color: {theme['text_color']};
                min-height: 20px;
            }}
            QLineEdit:focus {{
                border-color: {theme['title_color']};
            }}
            QPushButton {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 {theme['button_bg']}, stop: 1 {theme['content_bg']});
                color: {theme['text_color']};
                border: 2px solid {theme['button_border']};
                border-radius: 6px;
                padding: 10px 16px;
                font-weight: bold;
                min-height: 20px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 {theme['button_hover']}, stop: 1 {theme['button_bg']});
                border-color: {theme['title_color']};
                color: {theme['title_color']};
            }}
            QPushButton:pressed {{
                background-color: {theme['button_pressed']};
            }}
        """)
    
    def add_external_path(self):
        """Add an external app path"""
        folder = QFileDialog.getExistingDirectory(self, "Select Network Tool Folder")
        if folder:
            # Check if it contains main.py
            main_py = Path(folder) / "main.py"
            if main_py.exists():
                self.external_paths_list.addItem(folder)
            else:
                QMessageBox.warning(self, "Invalid Tool", 
                                  "Selected folder must contain a main.py file.")
    
    def remove_external_path(self):
        """Remove selected external path"""
        current_row = self.external_paths_list.currentRow()
        if current_row >= 0:
            self.external_paths_list.takeItem(current_row)
    
    def load_app_names(self, discovered_apps, custom_names):
        """Load current apps for name customization"""
        for app_name in discovered_apps.keys():
            row_layout = QHBoxLayout()
            
            label = QLabel(f"{app_name}:")
            label.setMinimumWidth(150)
            row_layout.addWidget(label)
            
            line_edit = QLineEdit()
            line_edit.setText(custom_names.get(app_name, app_name))
            line_edit.setObjectName(app_name)  # Store original name
            row_layout.addWidget(line_edit)
            
            self.app_names_layout.addLayout(row_layout)
    
    def get_settings(self):
        """Get the current settings from the dialog"""
        # Get custom names
        custom_names = {}
        for i in range(self.app_names_layout.count()):
            layout_item = self.app_names_layout.itemAt(i)
            if layout_item and layout_item.layout():
                row_layout = layout_item.layout()
                if row_layout.count() >= 2:
                    line_edit = row_layout.itemAt(1).widget()
                    if isinstance(line_edit, QLineEdit):
                        original_name = line_edit.objectName()
                        custom_name = line_edit.text().strip()
                        if custom_name and custom_name != original_name:
                            custom_names[original_name] = custom_name
        
        # Get external paths
        external_paths = []
        for i in range(self.external_paths_list.count()):
            item = self.external_paths_list.item(i)
            if item:
                external_paths.append(item.text())
        
        return {
            'grid_columns': self.columns_spinbox.value(),
            'button_size': self.button_size_combo.currentText(),
            'theme': self.theme_combo.currentText(),
            'custom_names': custom_names,
            'external_paths': external_paths
        }


class AppLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.apps_folder = Path("apps")  # Main apps directory
        self.settings_file = Path("launcher_settings.json")
        self.requirements_cache_file = Path("requirements_cache.json")
        self.discovered_apps = {}
        self.app_buttons = {}
        self.requirements_cache = {}
        
        # Load requirements cache
        self.load_requirements_cache()
        
        # Default settings
        self.grid_columns = 3
        self.button_size = "Medium"
        self.current_theme = "Light"
        self.settings = {}
        
        # Enhanced theme definitions for network tools
        self.themes = {
            "Light": {
                "main_bg": "#f8fafc",
                "content_bg": "#ffffff",
                "text_color": "#1e293b",
                "title_color": "#0f172a",
                "accent_color": "#3b82f6",
                "border_color": "#e2e8f0",
                "button_bg": "#ffffff",
                "button_hover": "#f1f5f9",
                "button_pressed": "#e2e8f0",
                "button_border": "#cbd5e1",
                "status_bg": "#f1f5f9",
                "status_text": "#64748b",
                "header_bg": "qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #3b82f6, stop: 1 #1d4ed8)"
            },
            "Dark": {
                "main_bg": "#0f172a",
                "content_bg": "#1e293b",
                "text_color": "#f1f5f9",
                "title_color": "#60a5fa",
                "accent_color": "#3b82f6",
                "border_color": "#334155",
                "button_bg": "#374151",
                "button_hover": "#4b5563",
                "button_pressed": "#6b7280",
                "button_border": "#4b5563",
                "status_bg": "#374151",
                "status_text": "#9ca3af",
                "header_bg": "qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #1e40af, stop: 1 #3730a3)"
            }
        }
        
        # Load settings
        self.load_settings()
        
        # Create apps folder if it doesn't exist
        self.apps_folder.mkdir(exist_ok=True)
        
        # Setup file watcher for dynamic updates
        self.file_watcher = QFileSystemWatcher()
        self.file_watcher.addPath(str(self.apps_folder))
        self.file_watcher.directoryChanged.connect(self.refresh_apps)
        
        self.init_ui()
        self.apply_theme()
        self.scan_apps()
        
    def init_ui(self):
        """Initialize the user interface with enhanced design"""
        self.setWindowTitle("🔧 Sigma's Network Toolkit Launcher")
        self.setGeometry(100, 100, 1200, 800)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Enhanced Header with gradient background
        header_widget = QWidget()
        header_widget.setFixedHeight(140)
        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(30, 15, 30, 15)
        header_layout.setSpacing(8)
        
        # Title and subtitle
        title_layout = QHBoxLayout()
        
        # Logo and title section
        logo_title_layout = QVBoxLayout()
        
        self.title_label = QLabel("🔧 Sigma's Network Toolkit Launcher")
        self.title_label.setFont(QFont("Arial", 20, QFont.Bold))
        logo_title_layout.addWidget(self.title_label)
        
        self.subtitle_label = QLabel("Professional Network Administration & Security Tools")
        self.subtitle_label.setFont(QFont("Arial", 11))
        logo_title_layout.addWidget(self.subtitle_label)
        
        title_layout.addLayout(logo_title_layout)
        title_layout.addStretch()
        
        # Header buttons with better styling
        buttons_layout = QHBoxLayout()
        
        self.settings_btn = QPushButton("⚙️ Settings")
        self.settings_btn.setFont(QFont("Arial", 9, QFont.Bold))
        self.settings_btn.setFixedSize(120, 40)
        self.settings_btn.clicked.connect(self.open_settings)
        buttons_layout.addWidget(self.settings_btn)
        
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.setFont(QFont("Arial", 9, QFont.Bold))
        self.refresh_btn.setFixedSize(120, 40)
        self.refresh_btn.clicked.connect(self.refresh_apps)
        buttons_layout.addWidget(self.refresh_btn)
        
        title_layout.addLayout(buttons_layout)
        header_layout.addLayout(title_layout)
        
        # Stats section
        self.stats_label = QLabel("Loading network tools...")
        self.stats_label.setFont(QFont("Arial", 9))
        self.stats_label.setMinimumHeight(20)
        header_layout.addWidget(self.stats_label)
        
        main_layout.addWidget(header_widget)
        
        # Content area with better spacing
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        # Scroll area for apps with enhanced design
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Apps container
        self.apps_container = QWidget()
        self.apps_layout = QGridLayout(self.apps_container)
        self.apps_layout.setSpacing(20)
        self.apps_layout.setContentsMargins(20, 20, 20, 20)
        
        self.scroll_area.setWidget(self.apps_container)
        content_layout.addWidget(self.scroll_area)
        
        main_layout.addWidget(content_widget)
        
        # Enhanced status bar
        status_widget = QWidget()
        status_widget.setFixedHeight(50)
        status_layout = QHBoxLayout(status_widget)
        status_layout.setContentsMargins(30, 10, 30, 10)
        
        self.status_label = QLabel("🚀 Ready to launch network tools")
        self.status_label.setFont(QFont("Arial", 10))
        status_layout.addWidget(self.status_label)
        
        status_layout.addStretch()
        
        # Version info
        version_label = QLabel("Sigma's Toolkit v2.0")
        version_label.setFont(QFont("Arial", 9))
        status_layout.addWidget(version_label)
        
        main_layout.addWidget(status_widget)
    
    def apply_theme(self):
        """Apply enhanced theme with network-focused design"""
        theme = self.themes[self.current_theme]
        
        # Main window styling
        self.setStyleSheet(f"""
            QMainWindow {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 {theme['main_bg']}, stop: 1 {theme['content_bg']});
                color: {theme['text_color']};
            }}
            QWidget {{
                background-color: transparent;
                color: {theme['text_color']};
            }}
        """)
        
        # Header styling with gradient
        header_widget = self.findChild(QWidget)
        if header_widget:
            header_widget.setStyleSheet(f"""
                QWidget {{
                    background: {theme['header_bg']};
                    border-radius: 0px;
                }}
            """)
        
        # Title and subtitle styling
        self.title_label.setStyleSheet(f"""
            QLabel {{
                color: white;
                background-color: transparent;
                font-weight: bold;
            }}
        """)
        
        self.subtitle_label.setStyleSheet(f"""
            QLabel {{
                color: rgba(255, 255, 255, 180);
                background-color: transparent;
                font-style: italic;
            }}
        """)
        
        # Stats label styling
        self.stats_label.setStyleSheet(f"""
            QLabel {{
                color: rgba(255, 255, 255, 160);
                background-color: transparent;
            }}
        """)
        
        # Header button styling
        header_button_style = f"""
            QPushButton {{
                background-color: rgba(255, 255, 255, 20);
                color: white;
                border: 2px solid rgba(255, 255, 255, 40);
                border-radius: 6px;
                padding: 8px 20px;
                font-weight: bold;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background-color: rgba(255, 255, 255, 30);
                border-color: rgba(255, 255, 255, 60);
            }}
            QPushButton:pressed {{
                background-color: rgba(255, 255, 255, 40);
            }}
        """
        
        self.settings_btn.setStyleSheet(header_button_style)
        self.refresh_btn.setStyleSheet(header_button_style)
        
        # Scroll area styling
        self.scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background-color: {theme['content_bg']};
                border: 2px solid {theme['border_color']};
                border-radius: 12px;
            }}
            QScrollBar:vertical {{
                background-color: {theme['content_bg']};
                border: 1px solid {theme['border_color']};
                border-radius: 6px;
                width: 14px;
            }}
            QScrollBar::handle:vertical {{
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 {theme['accent_color']}, stop: 1 {theme['button_hover']});
                border-radius: 6px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {theme['accent_color']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                border: none;
                background: none;
            }}
        """)
        
        # Status area styling
        status_widget = self.centralWidget().layout().itemAt(2).widget()
        if status_widget:
            status_widget.setStyleSheet(f"""
                QWidget {{
                    background-color: {theme['status_bg']};
                    border-top: 1px solid {theme['border_color']};
                }}
            """)
        
        # Status label styling
        self.status_label.setStyleSheet(f"""
            QLabel {{
                color: {theme['status_text']};
                background-color: transparent;
                font-weight: bold;
            }}
        """)
        
        # Apps container styling
        self.apps_container.setStyleSheet(f"""
            QWidget {{
                background-color: {theme['content_bg']};
            }}
        """)

    def load_requirements_cache(self):
        """Load requirements installation cache"""
        try:
            if self.requirements_cache_file.exists():
                with open(self.requirements_cache_file, 'r') as f:
                    self.requirements_cache = json.load(f)
        except Exception as e:
            print(f"Error loading requirements cache: {e}")
            self.requirements_cache = {}
    
    def save_requirements_cache(self):
        """Save requirements installation cache"""
        try:
            with open(self.requirements_cache_file, 'w') as f:
                json.dump(self.requirements_cache, f, indent=2)
        except Exception as e:
            print(f"Error saving requirements cache: {e}")
    
    def get_file_hash(self, file_path):
        """Get MD5 hash of a file"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return None
    
    def check_requirements_needed(self, app_info):
        """Check if requirements need to be installed or updated"""
        requirements_file = app_info['requirements']
        
        if not requirements_file.exists():
            return False, "No requirements file"
        
        # Get current hash of requirements file
        current_hash = self.get_file_hash(requirements_file)
        if not current_hash:
            return False, "Could not read requirements file"
        
        app_path = str(app_info['path'])
        cached_info = self.requirements_cache.get(app_path, {})
        cached_hash = cached_info.get('requirements_hash')
        
        # If hash changed or no cache, need to install
        if current_hash != cached_hash:
            return True, "Requirements file changed"
        
        # Check if all packages are actually installed
        try:
            with open(requirements_file, 'r') as f:
                requirements = f.read().strip().split('\n')
            
            for requirement in requirements:
                requirement = requirement.strip()
                if requirement and not requirement.startswith('#'):
                    # Parse package name (handle version specifiers)
                    package_name = requirement.split('==')[0].split('>=')[0].split('<=')[0].split('>')[0].split('<')[0].split('!=')[0].strip()
                    try:
                        distribution(package_name)
                    except PackageNotFoundError:
                        return True, f"Package {package_name} not installed"
                        
            return False, "All requirements satisfied"
            
        except Exception as e:
            return True, f"Error checking packages: {str(e)}"
    
    def filter_requirements(self, requirements_file):
        """Filter out problematic packages and create a safe requirements file"""
        protected_packages = {
            'pyqt5', 'pyqt5-qt5', 'pyqt5-sip', 'pyqt5-tools',
            'importlib-metadata', 'setuptools', 'pip'
        }
        
        try:
            with open(requirements_file, 'r') as f:
                requirements = f.read().strip().split('\n')
            
            safe_requirements = []
            skipped_packages = []
            
            for requirement in requirements:
                requirement = requirement.strip()
                if requirement and not requirement.startswith('#'):
                    # Parse package name
                    package_name = requirement.split('==')[0].split('>=')[0].split('<=')[0].split('>')[0].split('<')[0].split('!=')[0].strip().lower()
                    
                    if package_name in protected_packages:
                        skipped_packages.append(requirement)
                        continue
                    
                    safe_requirements.append(requirement)
                elif requirement:  # Keep comments
                    safe_requirements.append(requirement)
            
            # Create temporary safe requirements file
            safe_req_file = requirements_file.parent / "temp_requirements.txt"
            with open(safe_req_file, 'w') as f:
                f.write('\n'.join(safe_requirements))
            
            return safe_req_file, skipped_packages
            
        except Exception as e:
            return None, [f"Error processing requirements: {str(e)}"]

    def install_requirements(self, app_info):
        """Install requirements for an app"""
        requirements_file = app_info['requirements']
        app_path = str(app_info['path'])
        
        try:
            # Create safe requirements file (without PyQt5 and other protected packages)
            safe_req_file, skipped_packages = self.filter_requirements(requirements_file)
            
            if not safe_req_file:
                return False, "Could not process requirements file"
            
            # Show what we're skipping
            if skipped_packages:
                skip_msg = f"⚠️ Skipped protected packages: {', '.join(skipped_packages)}"
                self.status_label.setText(skip_msg)
                QApplication.processEvents()
            
            # Install safe requirements
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", 
                str(safe_req_file)
            ], capture_output=True, text=True)
            
            # Clean up temp file
            try:
                safe_req_file.unlink()
            except:
                pass
            
            if result.returncode == 0:
                # Update cache with new hash
                current_hash = self.get_file_hash(requirements_file)
                self.requirements_cache[app_path] = {
                    'requirements_hash': current_hash,
                    'last_installed': str(Path(requirements_file).stat().st_mtime),
                    'skipped_packages': skipped_packages
                }
                self.save_requirements_cache()
                
                message = "✅ Requirements installed successfully"
                if skipped_packages:
                    message += f" (skipped {len(skipped_packages)} protected packages)"
                
                return True, message
            else:
                return False, result.stderr
                
        except Exception as e:
            return False, str(e)

    def scan_apps(self):
        """Scan the apps folder and external paths for valid Python applications"""
        self.discovered_apps.clear()
        
        # Scan main apps folder
        if self.apps_folder.exists():
            self._scan_folder(self.apps_folder, "local")
        
        # Scan external paths
        for external_path in self.settings.get('external_paths', []):
            path_obj = Path(external_path)
            if path_obj.exists() and (path_obj / "main.py").exists():
                self._scan_single_app(path_obj, "external")
                
        self.update_ui()
        
        # Update stats display
        total_tools = len(self.discovered_apps)
        local_tools = sum(1 for app in self.discovered_apps.values() if app['source'] == 'local')
        external_tools = total_tools - local_tools
        
        self.stats_label.setText(f"📊 {total_tools} network tools available • {local_tools} local • {external_tools} external")
        self.status_label.setText(f"🔍 Discovered {total_tools} network administration tools")
    
    def _scan_folder(self, folder_path, source_type):
        """Scan a folder for apps"""
        for app_folder in folder_path.iterdir():
            if app_folder.is_dir() and not app_folder.name.startswith('.'):
                main_py = app_folder / "main.py"
                if main_py.exists():
                    self._scan_single_app(app_folder, source_type)
    
    def _scan_single_app(self, app_folder, source_type):
        """Scan a single app folder"""
        # Create unique key for external apps to avoid conflicts
        if source_type == "external":
            app_key = f"ext_{app_folder.name}_{hash(str(app_folder))}"
        else:
            app_key = app_folder.name
            
        app_info = {
            'name': app_folder.name,
            'display_name': app_folder.name,
            'path': app_folder,
            'main_file': app_folder / "main.py",
            'requirements': app_folder / "requirements.txt",
            'readme': app_folder / "readme.md",
            'source': source_type
        }
        self.discovered_apps[app_key] = app_info

    def update_ui(self):
        """Update the UI with discovered apps using enhanced card design"""
        # Clear existing buttons
        for button in self.app_buttons.values():
            button.deleteLater()
        self.app_buttons.clear()
        
        # Calculate how many apps we have and how to distribute them
        app_items = list(self.discovered_apps.items())
        total_apps = len(app_items)
        
        if total_apps == 0:
            # Show empty state
            empty_label = QLabel("🔧 No network tools found\n\nAdd your Python network tools to the 'apps' folder\nor configure external tool paths in Settings")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet(f"""
                QLabel {{
                    color: {self.themes[self.current_theme]['status_text']};
                    font-size: 14px;
                    padding: 40px;
                    background-color: {self.themes[self.current_theme]['status_bg']};
                    border: 2px dashed {self.themes[self.current_theme]['border_color']};
                    border-radius: 12px;
                }}
            """)
            self.apps_layout.addWidget(empty_label, 0, 0, 1, self.grid_columns)
            return
            
        # Calculate rows per column
        apps_per_column = (total_apps + self.grid_columns - 1) // self.grid_columns
        
        # Create enhanced network tool cards
        for i, (app_name, app_info) in enumerate(app_items):
            col = i // apps_per_column
            row = i % apps_per_column
            
            # Make sure we don't exceed the column limit
            if col >= self.grid_columns:
                col = self.grid_columns - 1
                row = i - (col * apps_per_column)
            
            # Create enhanced network tool card
            app_card = NetworkToolCard(app_name, app_info, self.themes[self.current_theme], self.button_size)
            
            # Connect events
            app_card.clicked.connect(lambda checked, name=app_name: self.launch_app(name))
            
            # Set up right-click context menu
            def mouse_press_event(event, app_name=app_name):
                if event.button() == Qt.RightButton:
                    self.show_context_menu(app_name, event.globalPos())
                else:
                    NetworkToolCard.mousePressEvent(app_card, event)
            
            app_card.mousePressEvent = mouse_press_event
            
            self.apps_layout.addWidget(app_card, row, col, Qt.AlignTop)
            self.app_buttons[app_name] = app_card
            
        # Set column stretch to make columns equal width
        for col in range(self.grid_columns):
            self.apps_layout.setColumnStretch(col, 1)
            
        # Add stretch at the bottom to push cards to top
        self.apps_layout.setRowStretch(apps_per_column, 1)

    def show_context_menu(self, app_name, position):
        """Show enhanced context menu for network tools"""
        if app_name not in self.discovered_apps:
            return
            
        app_info = self.discovered_apps[app_name]
        theme = self.themes[self.current_theme]
        
        # Create enhanced context menu
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 {theme['content_bg']}, stop: 1 {theme['button_bg']});
                border: 2px solid {theme['accent_color']};
                border-radius: 8px;
                padding: 8px;
                color: {theme['text_color']};
            }}
            QMenu::item {{
                padding: 10px 20px;
                border-radius: 6px;
                background-color: transparent;
                font-weight: bold;
            }}
            QMenu::item:selected {{
                background-color: {theme['accent_color']};
                color: white;
            }}
        """)
        
        # Add enhanced menu actions
        readme_action = QAction("📖 View Documentation", self)
        readme_action.triggered.connect(lambda: self.show_readme(app_name))
        menu.addAction(readme_action)
        
        folder_action = QAction("📁 Open Tool Folder", self)
        folder_action.triggered.connect(lambda: self.open_app_folder(app_name))
        menu.addAction(folder_action)
        
        menu.addSeparator()
        
        info_action = QAction("ℹ️ Tool Information", self)
        info_action.triggered.connect(lambda: self.show_tool_info(app_name))
        menu.addAction(info_action)
        
        menu.exec_(position)
    
    def show_tool_info(self, app_name):
        """Show detailed tool information"""
        if app_name not in self.discovered_apps:
            return
            
        app_info = self.discovered_apps[app_name]
        display_name = self.settings.get('custom_names', {}).get(app_name, app_info['name'])
        
        info_text = f"""
        <h3>🔧 {display_name}</h3>
        <p><b>Type:</b> {'External Tool' if app_info['source'] == 'external' else 'Local Tool'}</p>
        <p><b>Path:</b> {app_info['path']}</p>
        <p><b>Dependencies:</b> {'Yes' if app_info['requirements'].exists() else 'No'}</p>
        <p><b>Documentation:</b> {'Available' if app_info['readme'].exists() else 'Not available'}</p>
        """
        
        QMessageBox.information(self, f"Tool Information - {display_name}", info_text)
    
    def show_readme(self, app_name):
        """Show README dialog for a tool"""
        if app_name not in self.discovered_apps:
            return
            
        app_info = self.discovered_apps[app_name]
        display_name = self.settings.get('custom_names', {}).get(app_name, app_info['name'])
        display_name = display_name.replace('_', ' ').title()
        
        dialog = ReadmeDialog(display_name, app_info['readme'], self)
        dialog.exec_()
    
    def open_app_folder(self, app_name):
        """Open the tool folder in file explorer"""
        if app_name not in self.discovered_apps:
            return
            
        app_info = self.discovered_apps[app_name]
        try:
            if sys.platform == "win32":
                os.startfile(str(app_info['path']))
            elif sys.platform == "darwin":  # macOS
                subprocess.run(["open", str(app_info['path'])])
            else:  # Linux
                subprocess.run(["xdg-open", str(app_info['path'])])
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not open folder:\n{str(e)}")

    def load_settings(self):
        """Load settings from file"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    self.settings = json.load(f)
                    self.grid_columns = self.settings.get('grid_columns', 3)
                    self.button_size = self.settings.get('button_size', 'Medium')
                    self.current_theme = self.settings.get('theme', 'Light')
        except Exception as e:
            print(f"Error loading settings: {e}")
            self.settings = {}
    
    def save_settings(self):
        """Save settings to file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def open_settings(self):
        """Open enhanced settings dialog"""
        dialog = SettingsDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            new_settings = dialog.get_settings()
            self.settings.update(new_settings)
            
            # Store old values for comparison
            old_theme = self.current_theme
            old_columns = self.grid_columns
            old_button_size = self.button_size
            
            # Update settings
            self.grid_columns = new_settings['grid_columns']
            self.button_size = new_settings['button_size']
            self.current_theme = new_settings['theme']
            
            # Apply theme if changed
            if old_theme != self.current_theme:
                self.apply_theme()
                # Update all existing cards with new theme
                self.update_ui()
            elif old_columns != self.grid_columns or old_button_size != self.button_size:
                # Only update UI if layout changed
                self.update_ui()
            
            self.save_settings()
            self.refresh_apps()  # Refresh to include external paths
            self.status_label.setText("⚙️ Settings updated successfully")
        else:
            # If dialog was cancelled, restore the original theme
            self.apply_theme()
            
    def launch_app(self, app_name):
        """Launch a network tool with enhanced feedback"""
        if app_name not in self.discovered_apps:
            QMessageBox.warning(self, "Error", f"Network tool '{app_name}' not found")
            return
            
        app_info = self.discovered_apps[app_name]
        display_name = self.settings.get('custom_names', {}).get(app_name, app_info['name'])
        
        try:
            # Check if requirements need to be installed
            if app_info['requirements'].exists():
                needs_install, reason = self.check_requirements_needed(app_info)
                
                if needs_install:
                    self.status_label.setText(f"📦 Installing dependencies for {display_name}... ({reason})")
                    QApplication.processEvents()  # Update UI
                    
                    success, message = self.install_requirements(app_info)
                    if not success:
                        QMessageBox.warning(self, "Dependency Error", 
                                          f"Failed to install dependencies for {display_name}:\n{message}")
                        self.status_label.setText("❌ Dependency installation failed")
                        return
                    else:
                        self.status_label.setText(message)
                else:
                    self.status_label.setText(f"✅ Dependencies OK: {reason}")
                    
            # Launch the tool
            self.status_label.setText(f"🚀 Launching {display_name}...")
            QApplication.processEvents()
            
            subprocess.Popen([
                sys.executable, "main.py"
            ], cwd=str(app_info['path']))
            
            self.status_label.setText(f"✅ {display_name} launched successfully")
            
        except Exception as e:
            QMessageBox.critical(self, "Launch Error", 
                               f"Failed to launch {display_name}:\n{str(e)}")
            self.status_label.setText(f"❌ Error launching {display_name}")
            
    def refresh_apps(self):
        """Refresh the network tools list"""
        self.status_label.setText("🔄 Refreshing network tools...")
        QApplication.processEvents()
        
        # Small delay to ensure file operations are complete
        QTimer.singleShot(100, self.scan_apps)


def main():
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Sigma's Network Toolkit Launcher")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("Sigma Tools")
    
    launcher = AppLauncher()
    launcher.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()