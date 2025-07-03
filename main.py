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
                             QListWidgetItem, QCheckBox)
from PyQt5.QtCore import Qt, QFileSystemWatcher, QTimer
from PyQt5.QtGui import QFont, QIcon


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
                background-color: #e8e8e8;
                border: 1px solid #cccccc;
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
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.setFixedSize(500, 400)
        
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
        form_layout.addRow("Button Size:", self.button_size_combo)
        
        # Theme setting
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark"])
        self.theme_combo.setCurrentText(parent.current_theme if parent else "Light")
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)  # Add this line
        form_layout.addRow("Theme:", self.theme_combo)
        
        layout.addLayout(form_layout)
        
        # External paths section
        self.external_paths_label = QLabel("External App Paths:")
        layout.addWidget(self.external_paths_label)
        
        self.external_paths_list = QListWidget()
        self.external_paths_list.setMaximumHeight(100)
        if parent:
            for path in parent.settings.get('external_paths', []):
                self.external_paths_list.addItem(path)
        layout.addWidget(self.external_paths_list)
        
        # External path buttons
        path_buttons_layout = QHBoxLayout()
        
        self.add_path_btn = QPushButton("➕ Add Path")
        self.add_path_btn.clicked.connect(self.add_external_path)
        path_buttons_layout.addWidget(self.add_path_btn)
        
        self.remove_path_btn = QPushButton("➖ Remove")
        self.remove_path_btn.clicked.connect(self.remove_external_path)
        path_buttons_layout.addWidget(self.remove_path_btn)
        
        path_buttons_layout.addStretch()
        layout.addLayout(path_buttons_layout)
        
        # App name customization
        self.app_names_label = QLabel("Custom App Names:")
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
        
        # Main dialog styling
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {theme['main_bg']};
                color: {theme['text_color']};
            }}
            QLabel {{
                color: {theme['text_color']};
                font-weight: bold;
                margin: 5px 0px;
            }}
            QSpinBox {{
                background-color: {theme['content_bg']};
                border: 1px solid {theme['border_color']};
                border-radius: 4px;
                padding: 5px;
                color: {theme['text_color']};
                min-height: 20px;
            }}
            QSpinBox:focus {{
                border-color: {theme['title_color']};
            }}
            QComboBox {{
                background-color: {theme['content_bg']};
                border: 1px solid {theme['border_color']};
                border-radius: 4px;
                padding: 5px;
                color: {theme['text_color']};
                min-height: 20px;
            }}
            QComboBox:focus {{
                border-color: {theme['title_color']};
            }}
            QComboBox::drop-down {{
                border: none;
                background-color: {theme['button_bg']};
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
                border: 1px solid {theme['border_color']};
                border-radius: 4px;
                color: {theme['text_color']};
                padding: 5px;
            }}
            QListWidget::item {{
                padding: 3px;
                border-radius: 2px;
            }}
            QListWidget::item:selected {{
                background-color: {theme['button_hover']};
                color: {theme['title_color']};
            }}
            QLineEdit {{
                background-color: {theme['content_bg']};
                border: 1px solid {theme['border_color']};
                border-radius: 4px;
                padding: 5px;
                color: {theme['text_color']};
                min-height: 20px;
            }}
            QLineEdit:focus {{
                border-color: {theme['title_color']};
            }}
            QPushButton {{
                background-color: {theme['button_bg']};
                color: {theme['text_color']};
                border: 1px solid {theme['button_border']};
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
                min-height: 20px;
            }}
            QPushButton:hover {{
                background-color: {theme['button_hover']};
                border-color: {theme['title_color']};
            }}
            QPushButton:pressed {{
                background-color: {theme['button_pressed']};
            }}
        """)
    
    def add_external_path(self):
        """Add an external app path"""
        folder = QFileDialog.getExistingDirectory(self, "Select App Folder")
        if folder:
            # Check if it contains main.py
            main_py = Path(folder) / "main.py"
            if main_py.exists():
                self.external_paths_list.addItem(folder)
            else:
                QMessageBox.warning(self, "Invalid App", 
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
        
        # Theme definitions - Updated with light grey colors
        self.themes = {
            "Light": {
                "main_bg": "#f0f0f0",        # Changed from "#f5f5f5" to light grey
                "content_bg": "#e8e8e8",     # Changed from "#ffffff" to light grey
                "text_color": "#333333",
                "title_color": "#2c3e50",
                "border_color": "#cccccc",   # Slightly darker border for contrast
                "button_bg": "#e8e8e8",      # Changed from "#ffffff" to light grey
                "button_hover": "#d8d8d8",   # Changed from "#f0f8ff" to darker grey
                "button_pressed": "#c8c8c8", # Changed from "#e6f3ff" to darker grey
                "button_border": "#bbbbbb",  # Changed from "#e9ecef" to darker grey
                "status_bg": "#d0d0d0",      # Changed from "#ecf0f1" to grey
                "status_text": "#555555"     # Changed from "#7f8c8d" to darker text
            },
            "Dark": {
                "main_bg": "#2b2b2b",
                "content_bg": "#3c3c3c",
                "text_color": "#ffffff",
                "title_color": "#61dafb",
                "border_color": "#555555",
                "button_bg": "#404040",
                "button_hover": "#4a4a4a",
                "button_pressed": "#555555",
                "button_border": "#606060",
                "status_bg": "#484848",
                "status_text": "#cccccc"
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
        """Initialize the user interface"""
        self.setWindowTitle("Sigma's Toolkit Launcher")
        self.setGeometry(100, 100, 1000, 700)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_layout = QHBoxLayout()
        self.title_label = QLabel("🔧 Sigma's Toolkit Launcher")
        self.title_label.setFont(QFont("Arial", 18, QFont.Bold))
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        
        # Header buttons
        self.settings_btn = QPushButton("⚙️ Settings")
        self.settings_btn.clicked.connect(self.open_settings)
        header_layout.addWidget(self.settings_btn)
        
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.refresh_apps)
        header_layout.addWidget(self.refresh_btn)
        
        main_layout.addLayout(header_layout)
        
        # Separator
        self.separator = QFrame()
        self.separator.setFrameShape(QFrame.HLine)
        self.separator.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(self.separator)
        
        # Scroll area for apps
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Apps container
        self.apps_container = QWidget()
        self.apps_layout = QGridLayout(self.apps_container)
        self.apps_layout.setSpacing(15)
        self.apps_layout.setContentsMargins(20, 20, 20, 20)
        
        self.scroll_area.setWidget(self.apps_container)
        main_layout.addWidget(self.scroll_area)
        
        # Status bar
        self.status_label = QLabel("Ready")
        main_layout.addWidget(self.status_label)
    
    def apply_theme(self):
        """Apply the current theme to the interface"""
        theme = self.themes[self.current_theme]
        
        # Main window styling - more comprehensive
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {theme['main_bg']};
                color: {theme['text_color']};
            }}
            QWidget {{
                background-color: {theme['main_bg']};
                color: {theme['text_color']};
            }}
            QLabel {{
                color: {theme['text_color']};
                background-color: transparent;
            }}
            QScrollArea {{
                background-color: {theme['content_bg']};
                border: 1px solid {theme['border_color']};
                border-radius: 8px;
            }}
            QScrollArea > QWidget > QWidget {{
                background-color: {theme['content_bg']};
            }}
            QScrollBar:vertical {{
                background-color: {theme['content_bg']};
                border: 1px solid {theme['border_color']};
                border-radius: 4px;
                width: 12px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {theme['button_bg']};
                border-radius: 4px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {theme['button_hover']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                border: none;
                background: none;
            }}
        """)
        
        # Title styling
        self.title_label.setStyleSheet(f"""
            QLabel {{
                color: {theme['title_color']}; 
                margin-bottom: 10px;
                background-color: transparent;
                font-weight: bold;
            }}
        """)
        
        # Header button styling
        header_button_style = f"""
            QPushButton {{
                background-color: {theme['button_bg']};
                color: {theme['text_color']};
                border: 1px solid {theme['button_border']};
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {theme['button_hover']};
                border-color: {theme['title_color']};
                color: {theme['title_color']};
            }}
            QPushButton:pressed {{
                background-color: {theme['button_pressed']};
            }}
        """
        
        self.settings_btn.setStyleSheet(header_button_style)
        self.refresh_btn.setStyleSheet(header_button_style)
        
        # Separator styling
        self.separator.setStyleSheet(f"""
            QFrame {{
                color: {theme['border_color']};
                background-color: {theme['border_color']};
            }}
        """)
        
        # Status label styling
        self.status_label.setStyleSheet(f"""
            QLabel {{
                background-color: {theme['status_bg']};
                padding: 8px;
                border-radius: 4px;
                color: {theme['status_text']};
                border: 1px solid {theme['border_color']};
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
                skip_msg = f"Skipped protected packages: {', '.join(skipped_packages)}"
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
                
                message = "Requirements installed successfully"
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
        self.status_label.setText(f"Found {len(self.discovered_apps)} apps")
    
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
        """Update the UI with discovered apps"""
        # Clear existing buttons
        for button in self.app_buttons.values():
            button.deleteLater()
        self.app_buttons.clear()
        
        # Calculate how many apps we have and how to distribute them
        app_items = list(self.discovered_apps.items())
        total_apps = len(app_items)
        
        if total_apps == 0:
            return
            
        # Calculate rows per column
        apps_per_column = (total_apps + self.grid_columns - 1) // self.grid_columns
        
        # Create buttons and place them column by column
        for i, (app_name, app_info) in enumerate(app_items):
            col = i // apps_per_column
            row = i % apps_per_column
            
            # Make sure we don't exceed the column limit
            if col >= self.grid_columns:
                col = self.grid_columns - 1
                row = i - (col * apps_per_column)
            
            app_button = self.create_app_button(app_name, app_info)
            self.apps_layout.addWidget(app_button, row, col, Qt.AlignTop)
            self.app_buttons[app_name] = app_button
            
        # Set column stretch to make columns equal width
        for col in range(self.grid_columns):
            self.apps_layout.setColumnStretch(col, 1)
            
        # Add stretch at the bottom to push buttons to top
        self.apps_layout.setRowStretch(apps_per_column, 1)
                
    def create_app_button(self, app_name, app_info):
        """Create a button for an app"""
        button = QPushButton()
        
        # Get button size - making them more compact for vertical layout
        size_map = {
            "Small": (200, 60),
            "Medium": (240, 70),
            "Large": (280, 80)
        }
        width, height = size_map.get(self.button_size, (240, 70))
        button.setFixedSize(width, height)
        
        # Get display name (custom name if set)
        display_name = self.settings.get('custom_names', {}).get(app_name, app_info['name'])
        display_name = display_name.replace('_', ' ').title()
        
        # Get theme colors
        theme = self.themes[self.current_theme]
        
        # Create button styling - more compact for list view
        button_style = f"""
            QPushButton {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 {theme['button_bg']}, stop: 1 {theme['content_bg']});
                border: 2px solid {theme['button_border']};
                border-radius: 8px;
                font-size: 12px;
                font-weight: bold;
                color: {theme['text_color']};
                text-align: left;
                padding: 8px 12px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 {theme['button_hover']}, stop: 1 {theme['button_bg']});
                border-color: {theme['title_color']};
                color: {theme['title_color']};
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 {theme['button_pressed']}, stop: 1 {theme['button_hover']});
                border-color: {theme['title_color']};
            }}
        """
        button.setStyleSheet(button_style)
        
        # Create button content - more compact layout
        icon_text = "📱" if app_info['requirements'].exists() else "🚀"
        
        # Add source indicator for external apps
        source_indicator = " 🔗" if app_info['source'] == "external" else ""
        
        # Left-aligned, single line layout
        status_info = "📦" if app_info['requirements'].exists() else "✨"
        readme_info = " 📖" if app_info['readme'].exists() else ""
        
        button_text = f"{icon_text} {display_name}{source_indicator}    {status_info}{readme_info}"
            
        button.setText(button_text)
        
        # Connect left click to launch app
        button.clicked.connect(lambda checked, name=app_name: self.launch_app(name))
        
        # Set up right-click context menu using mousePressEvent
        def mouse_press_event(event):
            if event.button() == Qt.RightButton:
                print(f"Right click detected on {app_name}")  # Debug
                self.show_context_menu(app_name, event.globalPos())
            else:
                QPushButton.mousePressEvent(button, event)
        
        button.mousePressEvent = mouse_press_event
        
        # Add tooltip for user guidance
        button.setToolTip(f"Left click: Launch {display_name}\nRight click: View menu options")
        
        return button

    def show_context_menu(self, app_name, position):
        """Show context menu for app buttons"""
        print(f"Context menu requested for: {app_name} at position: {position}")  # Debug
        
        if app_name not in self.discovered_apps:
            print(f"App {app_name} not found in discovered apps")  # Debug
            return
            
        app_info = self.discovered_apps[app_name]
        print(f"Showing context menu for: {app_info['name']}")  # Debug
        
        # Get theme colors for menu styling
        theme = self.themes[self.current_theme]
        
        # Create context menu
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: {theme['content_bg']};
                border: 1px solid {theme['border_color']};
                border-radius: 5px;
                padding: 5px;
                color: {theme['text_color']};
            }}
            QMenu::item {{
                padding: 8px 20px;
                border-radius: 3px;
                background-color: transparent;
            }}
            QMenu::item:selected {{
                background-color: {theme['button_hover']};
                color: {theme['title_color']};
            }}
        """)
        
        # Add "View README" action
        readme_action = QAction("📖 View README", self)
        readme_action.triggered.connect(lambda: self.show_readme(app_name))
        menu.addAction(readme_action)
        
        # Add "Open Folder" action
        folder_action = QAction("📁 Open Folder", self)
        folder_action.triggered.connect(lambda: self.open_app_folder(app_name))
        menu.addAction(folder_action)
        
        # Add a test action to verify menu works
        test_action = QAction("🔧 Test Action", self)
        test_action.triggered.connect(lambda: print(f"Test action clicked for {app_name}"))
        menu.addAction(test_action)
        
        print("About to show context menu...")  # Debug
        # Show the menu
        menu.exec_(position)
    
    def show_readme(self, app_name):
        """Show README dialog for an app"""
        if app_name not in self.discovered_apps:
            return
            
        app_info = self.discovered_apps[app_name]
        display_name = self.settings.get('custom_names', {}).get(app_name, app_info['name'])
        display_name = display_name.replace('_', ' ').title()
        
        dialog = ReadmeDialog(display_name, app_info['readme'], self)
        dialog.exec_()
    
    def open_app_folder(self, app_name):
        """Open the app folder in file explorer"""
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
        """Open settings dialog"""
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
                # Update all existing buttons with new theme
                self.update_ui()
            elif old_columns != self.grid_columns or old_button_size != self.button_size:
                # Only update UI if layout changed
                self.update_ui()
            
            self.save_settings()
            self.refresh_apps()  # Refresh to include external paths
            self.status_label.setText("Settings updated")
        else:
            # If dialog was cancelled, make sure we restore the original theme
            self.apply_theme()
            
    def launch_app(self, app_name):
        """Launch a Python application"""
        if app_name not in self.discovered_apps:
            QMessageBox.warning(self, "Error", f"App '{app_name}' not found")
            return
            
        app_info = self.discovered_apps[app_name]
        
        try:
            # Check if requirements need to be installed
            if app_info['requirements'].exists():
                needs_install, reason = self.check_requirements_needed(app_info)
                
                if needs_install:
                    self.status_label.setText(f"Installing requirements for {app_name}... ({reason})")
                    QApplication.processEvents()  # Update UI
                    
                    success, message = self.install_requirements(app_info)
                    if not success:
                        QMessageBox.warning(self, "Requirements Error", 
                                          f"Failed to install requirements:\n{message}")
                        self.status_label.setText("Requirements installation failed")
                        return
                    else:
                        self.status_label.setText(f"Requirements updated: {message}")
                else:
                    self.status_label.setText(f"Requirements OK: {reason}")
                    
            # Launch the app
            self.status_label.setText(f"Launching {app_name}...")
            QApplication.processEvents()
            
            subprocess.Popen([
                sys.executable, "main.py"
            ], cwd=str(app_info['path']))
            
            self.status_label.setText(f"Launched {app_name}")
            
        except Exception as e:
            QMessageBox.critical(self, "Launch Error", 
                               f"Failed to launch {app_name}:\n{str(e)}")
            self.status_label.setText("Error launching app")
            
    def refresh_apps(self):
        """Refresh the apps list"""
        self.status_label.setText("Refreshing apps...")
        QApplication.processEvents()
        
        # Small delay to ensure file operations are complete
        QTimer.singleShot(100, self.scan_apps)


def main():
    app = QApplication(sys.argv)
    launcher = AppLauncher()
    launcher.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()