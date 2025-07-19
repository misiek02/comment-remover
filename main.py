# main.py
import sys
import re
import os
import json

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QFileDialog, QComboBox, QLabel,
    QFrame, QStyle, QMenu, QMenuBar, QColorDialog, QDialog,
    QFormLayout, QLineEdit, QDialogButtonBox
)
from PyQt6.QtGui import QIcon, QGuiApplication, QAction, QColor
from PyQt6.QtCore import Qt, QTimer

# --- Comment Removal Logic ---

class CommentRemoverLogic:
    """
    Class containing logic for removing comments for different languages.
    NOTE: The regex-based system may have issues with comments inside
    string literals (e.g., "this is not a #comment").
    However, it is sufficient for most cases.
    """
    def __init__(self):
        self.patterns = {
            'Python': {
                'single_line': r'#.*$',
                'multi_line': r'(\"\"\"(.|\n)*?\"\"\")|(\'\'\'(.|\n)*?\'\'\')'
            },
            'C/C++/Java/C#/JavaScript/Rust': {
                'single_line': r'//.*$',
                'multi_line': r'/\*(.|\n)*?\*/'
            },
            'HTML/XML': {
                'multi_line': r'<!--(.|\n)*?-->'
            },
            'SQL': {
                'single_line': r'--.*$',
                'multi_line': r'/\*(.|\n)*?\*/'
            },
            'Lua': {
                'single_line': r'--.*$',
                'multi_line': r'--\[\[(.|\n)*?\]\]'
            }
        }
        # File extension to language mapping
        self.extension_map = {
            '.py': 'Python', '.pyw': 'Python',
            '.c': 'C/C++/Java/C#/JavaScript/Rust', '.cpp': 'C/C++/Java/C#/JavaScript/Rust',
            '.h': 'C/C++/Java/C#/JavaScript/Rust', '.hpp': 'C/C++/Java/C#/JavaScript/Rust',
            '.java': 'C/C++/Java/C#/JavaScript/Rust', '.cs': 'C/C++/Java/C#/JavaScript/Rust',
            '.js': 'C/C++/Java/C#/JavaScript/Rust', '.ts': 'C/C++/Java/C#/JavaScript/Rust',
            '.rs': 'C/C++/Java/C#/JavaScript/Rust',
            '.html': 'HTML/XML', '.htm': 'HTML/XML', '.xml': 'HTML/XML',
            '.sql': 'SQL',
            '.lua': 'Lua'
        }

    def get_language_from_filename(self, filename):
        ext = os.path.splitext(filename)[1].lower()
        return self.extension_map.get(ext, 'Python') # Domyślnie Python

    def remove_comments(self, code, language):
        if language not in self.patterns:
            return code

        patterns = self.patterns[language]
        processed_code = code

        if 'multi_line' in patterns:
            processed_code = re.sub(patterns['multi_line'], '', processed_code)

        if 'single_line' in patterns:
            lines = processed_code.split('\n')
            result_lines = []
            for line in lines:
                is_originally_empty = not line.strip()
                cleaned_line = re.sub(patterns['single_line'], '', line)
                
                if cleaned_line.strip() or is_originally_empty:
                    result_lines.append(cleaned_line)

            processed_code = '\n'.join(result_lines)
            
        processed_code = re.sub(r'\n{3,}', '\n\n', processed_code)
        
        return processed_code.strip()


# --- Interfejs graficzny aplikacji ---

class ThemeManager:
    def __init__(self):
        self.themes = {
            'Dark': {
                'background': '#2B2B2B',
                'text': '#A9B7C6',
                'button': '#3C3F41',
                'button_hover': '#4B4D4F',
                'button_pressed': '#2A2C2E',
                'accent': '#007ACC',
                'accent_hover': '#008AE6',
                'accent_pressed': '#006AB3',
                'border': '#4B4B4B',
                'input_background': '#313335'
            },
            'Light': {
                'background': '#F5F5F5',
                'text': '#333333',
                'button': '#E0E0E0',
                'button_hover': '#D0D0D0',
                'button_pressed': '#C0C0C0',
                'accent': '#2196F3',
                'accent_hover': '#1976D2',
                'accent_pressed': '#1565C0',
                'border': '#CCCCCC',
                'input_background': '#FFFFFF'
            },
            'Monokai': {
                'background': '#272822',
                'text': '#F8F8F2',
                'button': '#3E3D32',
                'button_hover': '#4E4D42',
                'button_pressed': '#2E2D22',
                'accent': '#A6E22E',
                'accent_hover': '#B6F23E',
                'accent_pressed': '#96D21E',
                'border': '#3E3D32',
                'input_background': '#1E1F1C'
            }
        }
        self.current_theme = 'Dark'
        self.custom_colors = {}

    def get_theme(self, theme_name=None):
        if theme_name is None:
            theme_name = self.current_theme
        return self.themes.get(theme_name, self.themes['Dark'])

    def set_theme(self, theme_name):
        if theme_name in self.themes:
            self.current_theme = theme_name
            return True
        return False

    def get_style_sheet(self, theme_name=None):
        theme = self.get_theme(theme_name)
        return f"""
        QWidget {{
            background-color: {theme['background']}; 
            color: {theme['text']};
            font-family: 'Segoe UI', Arial, sans-serif; 
            font-size: 14px;
        }}
        QMainWindow {{ border: 1px solid {theme['border']}; }}
        QTextEdit {{
            background-color: {theme['input_background']}; 
            color: {theme['text']};
            border: 1px solid {theme['border']}; 
            border-radius: 4px; 
            padding: 8px;
            font-family: 'Consolas', 'Courier New', monospace; 
            font-size: 13px;
        }}
        QPushButton {{
            background-color: {theme['button']}; 
            color: {theme['text']};
            border: 1px solid {theme['border']}; 
            padding: 8px 16px; 
            border-radius: 4px;
        }}
        QPushButton:hover {{ 
            background-color: {theme['button_hover']}; 
            border: 1px solid {theme['border']}; 
        }}
        QPushButton:pressed {{ 
            background-color: {theme['button_pressed']}; 
        }}
        QPushButton#ProcessButton {{
            background-color: {theme['accent']}; 
            color: white; 
            font-weight: bold;
        }}
        QPushButton#ProcessButton:hover {{ 
            background-color: {theme['accent_hover']}; 
        }}
        QPushButton#ProcessButton:pressed {{ 
            background-color: {theme['accent_pressed']}; 
        }}
        QComboBox {{
            background-color: {theme['button']}; 
            border: 1px solid {theme['border']};
            border-radius: 4px; 
            padding: 5px;
        }}
        QComboBox::drop-down {{ border: none; }}
        QComboBox QAbstractItemView {{
            background-color: {theme['button']}; 
            border: 1px solid {theme['border']};
            selection-background-color: {theme['accent']};
        }}
        QLabel {{ color: {theme['text']}; }}
        QFrame[frameShape="5"] {{ color: {theme['border']}; }}
        QMenuBar {{
            background-color: {theme['background']};
            color: {theme['text']};
        }}
        QMenuBar::item:selected {{
            background-color: {theme['accent']};
        }}
        QMenu {{
            background-color: {theme['background']};
            color: {theme['text']};
            border: 1px solid {theme['border']};
        }}
        QMenu::item:selected {{
            background-color: {theme['accent']};
        }}
        """

class ColorCustomizationDialog(QDialog):
    def __init__(self, parent=None, theme_manager=None):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Customize Colors")
        layout = QFormLayout(self)

        self.color_inputs = {}
        current_theme = self.theme_manager.get_theme()

        for color_name, color_value in current_theme.items():
            color_input = QLineEdit(color_value)
            color_input.setReadOnly(True)
            color_button = QPushButton("Choose")
            color_button.clicked.connect(lambda checked, name=color_name, input=color_input: self.choose_color(name, input))
            
            color_layout = QHBoxLayout()
            color_layout.addWidget(color_input)
            color_layout.addWidget(color_button)
            
            layout.addRow(color_name.replace('_', ' ').title(), color_layout)
            self.color_inputs[color_name] = color_input

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def choose_color(self, color_name, input_field):
        color = QColorDialog.getColor(QColor(input_field.text()), self)
        if color.isValid():
            input_field.setText(color.name())

    def get_custom_colors(self):
        return {name: input.text() for name, input in self.color_inputs.items()}

class CommentRemoverApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.logic = CommentRemoverLogic()
        self.theme_manager = ThemeManager()
        self.current_filepath = None
        self.loading_file = False
        self.init_ui()
        self.init_menu()

    def init_menu(self):
        menubar = self.menuBar()
        
        # Theme menu
        theme_menu = menubar.addMenu('Theme')
        
        # Add default themes
        for theme_name in self.theme_manager.themes.keys():
            action = QAction(theme_name, self)
            action.triggered.connect(lambda checked, name=theme_name: self.change_theme(name))
            theme_menu.addAction(action)
        
        # Add color customization option
        custom_action = QAction('Customize Colors...', self)
        custom_action.triggered.connect(self.show_color_customization)
        theme_menu.addAction(custom_action)

    def change_theme(self, theme_name):
        if self.theme_manager.set_theme(theme_name):
            self.setStyleSheet(self.theme_manager.get_style_sheet())
            self.update_status(f"Theme changed to: {theme_name}")

    def show_color_customization(self):
        dialog = ColorCustomizationDialog(self, self.theme_manager)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            custom_colors = dialog.get_custom_colors()
            self.theme_manager.themes['Custom'] = custom_colors
            self.theme_manager.set_theme('Custom')
            self.setStyleSheet(self.theme_manager.get_style_sheet())
            self.update_status("Custom colors applied")

    def init_ui(self):
        self.setWindowTitle("Comment Remover Pro")
        self.setGeometry(100, 100, 1200, 700)
        self.setWindowIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_TrashIcon))

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # --- Top panel (controls) ---
        top_panel_layout = QHBoxLayout()

        self.lang_combo = QComboBox()
        self.lang_combo.addItems(self.logic.patterns.keys())
        self.lang_combo.setToolTip("Select programming language")
        top_panel_layout.addWidget(QLabel("Language:"))
        top_panel_layout.addWidget(self.lang_combo, 1)

        self.btn_open = QPushButton("Select File...")
        self.btn_open.clicked.connect(self.open_file_dialog)
        self.btn_open.setToolTip("Open source code file")
        top_panel_layout.addWidget(self.btn_open, 1)

        self.btn_process = QPushButton("🚀 Remove Comments")
        self.btn_process.clicked.connect(self.process_code)
        self.btn_process.setObjectName("ProcessButton")
        top_panel_layout.addWidget(self.btn_process, 2)
        
        main_layout.addLayout(top_panel_layout)

        # --- Editor panels (input/output) ---
        editors_layout = QHBoxLayout()

        input_layout = QVBoxLayout()
        input_label = QLabel("Input Code (paste here or select file)")
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Paste your code here...")
        
        self.text_input.textChanged.connect(self.reset_filepath_on_manual_edit)

        input_layout.addWidget(input_label)
        input_layout.addWidget(self.text_input)

        output_layout = QVBoxLayout()
        output_label = QLabel("Output Code (without comments)")
        self.text_output = QTextEdit()
        self.text_output.setReadOnly(True)
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.text_output)

        editors_layout.addLayout(input_layout, 1)
        
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        editors_layout.addWidget(separator)
        
        editors_layout.addLayout(output_layout, 1)

        main_layout.addLayout(editors_layout)

        # --- Bottom panel (action buttons and status) ---
        bottom_panel_layout = QHBoxLayout()
        
        self.btn_save = QPushButton("Save File...")
        self.btn_save.clicked.connect(self.save_file_dialog)
        self.btn_save.setToolTip("Save processed code to a new file")
        
        self.btn_copy = QPushButton("Copy to Clipboard")
        self.btn_copy.clicked.connect(self.copy_to_clipboard)
        self.btn_copy.setToolTip("Copy processed code to system clipboard")
        
        self.status_label = QLabel("Ready.")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        bottom_panel_layout.addWidget(self.btn_save)
        bottom_panel_layout.addWidget(self.btn_copy)
        bottom_panel_layout.addStretch()
        bottom_panel_layout.addWidget(self.status_label)
        main_layout.addLayout(bottom_panel_layout)
        
        self.setStyleSheet(self.theme_manager.get_style_sheet())

    def reset_filepath_on_manual_edit(self):
        if not self.loading_file:
            self.current_filepath = None
            
    def open_file_dialog(self):
        file_filters = "All Files (*);;Python Files (*.py *.pyw);;C/C++/Java/JS Files (*.c *.cpp *.h *.hpp *.java *.cs *.js *.ts *.rs);;HTML/XML Files (*.html *.htm *.xml);;SQL Files (*.sql);;Lua Files (*.lua)"
        filename, _ = QFileDialog.getOpenFileName(self, "Open Code File", "", file_filters)
        
        if filename:
            try:
                self.loading_file = True
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.text_input.setPlainText(content)
                self.current_filepath = filename
                self.update_status(f"File loaded: {os.path.basename(filename)}")
                lang = self.logic.get_language_from_filename(filename)
                self.lang_combo.setCurrentText(lang)
            except Exception as e:
                self.text_input.setPlainText(f"Error reading file: {e}")
                self.update_status("Error reading file.", is_error=True)
                self.current_filepath = None
            finally:
                self.loading_file = False

    def save_file_dialog(self):
        output_code = self.text_output.toPlainText()
        if not output_code:
            self.update_status("No code to save.", is_error=True)
            return

        default_filename = ""
        if self.current_filepath:
            base, ext = os.path.splitext(self.current_filepath)
            default_filename = f"{base}_nocomments{ext}"
        
        file_filters = "All Files (*);;Python Files (*.py *.pyw);;C/C++/Java/JS Files (*.c *.cpp *.h *.hpp *.java *.cs *.js *.ts *.rs);;HTML/XML Files (*.html *.htm *.xml);;SQL Files (*.sql);;Lua Files (*.lua)"
        
        filename, _ = QFileDialog.getSaveFileName(self, "Save File As", default_filename, file_filters)

        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(output_code)
                self.update_status(f"File saved: {os.path.basename(filename)}")
            except Exception as e:
                self.update_status(f"Error saving file: {e}", is_error=True)

    def process_code(self):
        input_code = self.text_input.toPlainText()
        if not input_code.strip():
            self.update_status("No code to process.", is_error=True)
            return

        language = self.lang_combo.currentText()
        
        self.update_status("Processing...", is_error=False)
        QApplication.processEvents()

        processed_code = self.logic.remove_comments(input_code, language)
        self.text_output.setPlainText(processed_code)
        
        self.update_status("Comments removed successfully.", is_error=False)

    def copy_to_clipboard(self):
        clipboard = QGuiApplication.clipboard()
        text_to_copy = self.text_output.toPlainText()
        if text_to_copy:
            clipboard.setText(text_to_copy)
            self.btn_copy.setText("Copied!")
            self.update_status("Code copied to clipboard.")
            QTimer.singleShot(2000, lambda: self.btn_copy.setText("Copy to Clipboard"))
        else:
            self.update_status("No text to copy.", is_error=True)

    def update_status(self, message, is_error=False):
        self.status_label.setText(message)
        if is_error:
            self.status_label.setStyleSheet("color: #FF5555;")
        else:
            self.status_label.setStyleSheet("color: #83AF74;")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CommentRemoverApp()
    window.show()
    sys.exit(app.exec())