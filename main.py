import sys
import threading
import re
from typing import Optional

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QListWidgetItem, QLabel, QGridLayout, QStackedLayout
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QPoint, QTimer
from PyQt6.QtGui import QPixmap, QIcon

import subprocess
import os
from dotenv import load_dotenv

from core.agent import process_input
from input.vad import listen_full_phrase

from utils.constants import EXIT_COMMANDS
from utils.helpers import resource_path


# ---------- Утилиты нормализации ----------
def _normalize_text(s: str) -> str:
    s = (s or "").lower()
    s = s.replace("ё", "е")
    s = re.sub(r"[^\w\s]+", " ", s, flags=re.UNICODE)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def _normalize_set(items) -> set[str]:
    return { _normalize_text(x) for x in items if isinstance(x, str) and x.strip() }


# ---------- Виджет сообщения ----------
class ChatMessage(QWidget):
    def __init__(self, text: str, is_user: bool, parent: Optional[QWidget] = None):
        super().__init__(parent)
        layout = QHBoxLayout()
        label = QLabel(str(text))
        label.setWordWrap(True)
        label.setStyleSheet("""
            padding: 16px 10px;
            border-radius: 15px;
            color: white;
        """)
        if is_user:
            label.setAlignment(Qt.AlignmentFlag.AlignRight)
            label.setStyleSheet(label.styleSheet() + "background-color: #130A1D;")
            layout.addStretch()
            layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignRight)
        else:
            label.setAlignment(Qt.AlignmentFlag.AlignLeft)
            label.setStyleSheet(label.styleSheet() + "background-color: #FF462A;")
            layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignLeft)
            layout.addStretch()
        self.setLayout(layout)


class ListenerWorker(QThread):
    heard = pyqtSignal(str)
    finished_once = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._stop_event = threading.Event()

    def run(self):
        try:
            phrase = listen_full_phrase(stop_event=self._stop_event)
            if phrase is not None:
                self.heard.emit(str(phrase))
        finally:
            self.finished_once.emit()

    def stop(self):
        self._stop_event.set()


class ChatApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.resize(500, 700)
        self.setStyleSheet("background-color: #162334;")

        self._listener_thread: Optional[ListenerWorker] = None
        self._listening: bool = False
        self.oldPos = None

        self.exit_cmds = _normalize_set(EXIT_COMMANDS)

        main_layout = QVBoxLayout()

        # Header
        self.header = QWidget(self)
        self.header.setFixedHeight(60)
        header_layout = QGridLayout(self.header)
        header_layout.setContentsMargins(10, 0, 10, 0)
        header_layout.setColumnStretch(0, 1)
        header_layout.setColumnStretch(1, 1)
        header_layout.setColumnStretch(2, 1)

        self.logo_label = QLabel()
        self.logo_label.setPixmap(QPixmap(resource_path("images/logo.png")))
        self.logo_label.setFixedSize(200, 36)
        self.logo_label.setScaledContents(True)
        self.logo_label.setStyleSheet("background-color: transparent;")
        header_layout.addWidget(self.logo_label, 0, 1,
                                alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        btn_container = QWidget()
        btn_container.setStyleSheet("background-color: transparent;")
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(20)

        self.min_btn = QPushButton()
        self.min_btn.setFixedSize(20, 20)
        self.min_btn.setIcon(QIcon(resource_path("images/minimize.png")))
        self.min_btn.setIconSize(self.min_btn.size())
        self.min_btn.setStyleSheet("background-color: transparent; border: none;")
        self.min_btn.clicked.connect(self.showMinimized)

        self.close_btn = QPushButton()
        self.close_btn.setFixedSize(20, 20)
        self.close_btn.setIcon(QIcon(resource_path("images/close.png")))
        self.close_btn.setIconSize(self.close_btn.size())
        self.close_btn.setStyleSheet("background-color: transparent; border: none;")
        self.close_btn.clicked.connect(self.close)

        btn_layout.addWidget(self.min_btn)
        btn_layout.addWidget(self.close_btn)
        header_layout.addWidget(btn_container, 0, 2,
                                alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        main_layout.addWidget(self.header)

        # Чат
        self.chat_list = QListWidget()
        self.chat_list.setSpacing(10)
        self.chat_list.setStyleSheet("background-color: #1A293E; border-radius: 5px;")
        self.chat_list.setFixedHeight(560)
        self.chat_list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        main_layout.addWidget(self.chat_list)

        # Зона управления: стэк из (Start-кнопка) и (лейбл «Слушаю…»)
        self.control_host = QWidget()
        self.control_stack = QStackedLayout(self.control_host)

        self.start_button = QPushButton("Start")
        self.start_button.setStyleSheet(self._button_style())
        self.start_button.setFixedHeight(60)
        self.start_button.clicked.connect(self._on_start_clicked)

        self.listen_label = QLabel("Слушаю. Для остановки скажите стоп")
        self.listen_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.listen_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: 600;
                padding: 10px 20px;
                color: white;
                background-color: #304158;
                border-radius: 10px;
                min-height: 30px;
            }
        """)

        self.control_stack.addWidget(self.start_button)  # index 0
        self.control_stack.addWidget(self.listen_label)  # index 1
        self.control_stack.setCurrentIndex(0)  # показываем Start

        main_layout.addWidget(self.control_host)
        self.setLayout(main_layout)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.oldPos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self.oldPos is not None:
            delta = QPoint(event.globalPosition().toPoint() - self.oldPos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPosition().toPoint()

    # --- Стили ---
    def _button_style(self, bg_color="#FF604A"):
        return f"""
            QPushButton {{
                font-size: 18px;
                font-weight: bold;
                border-radius: 10px;
                padding: 10px 20px;
                background-color: {bg_color};
                color: white;
            }}
        """

    # --- Управление прослушкой ---
    def _on_start_clicked(self):
        self.control_stack.setCurrentIndex(1)
        self._start_listening()

    def _start_listening(self):
        if self._listener_thread is not None:
            return
        self._listening = True
        th = ListenerWorker()
        th.heard.connect(self.handle_user_message)
        th.finished_once.connect(self._on_listener_finished_once)
        self._listener_thread = th
        QTimer.singleShot(0, th.start)

    def _stop_listening(self):
        self.control_stack.setCurrentIndex(0)
        self._listening = False

        if self._listener_thread is not None:
            self._listener_thread.stop()

    def _on_listener_finished_once(self):
        self._listener_thread = None
        if self._listening:
            QTimer.singleShot(0, self._start_listening)

    # --- Проверка стоп-команд ---
    def _is_exit_command(self, text: str) -> bool:
        nt = _normalize_text(text)
        if not nt or not self.exit_cmds:
            return False
        return any(cmd in nt for cmd in self.exit_cmds)

    # --- Логика чата ---
    def handle_user_message(self, text: str):
        self.add_message(text, is_user=True)

        if self._is_exit_command(text):
            self.add_message("🛑 Останавливаю прослушивание.", is_user=False)
            self._stop_listening()
            return

        reply = self.generate_reply(text)
        self.add_message(reply, is_user=False)
        self.chat_list.scrollToBottom()

    def add_message(self, text: str, is_user: bool):
        widget = ChatMessage(text, is_user)
        item = QListWidgetItem(self.chat_list)
        item.setSizeHint(widget.sizeHint())
        self.chat_list.addItem(item)
        self.chat_list.setItemWidget(item, widget)

    def generate_reply(self, user_input: str) -> str:
        return process_input(user_input)


# ---------- Запуск локальной модели ----------
def launch_llama_model(model="llama3.1:latest"):
    if os.getenv("USE_OLLAMA_HTTP", "false").lower() == "true":
        return
    ollama_path = os.path.join(os.getcwd(), "ollama", "ollama.exe")
    try:
        print(f"🚀 Проверяем наличие модели LLM: {model}")
        result = subprocess.run([ollama_path, "list"], capture_output=True, text=True)
        if model not in result.stdout:
            print(f"📥 Модель {model} не найдена. Загружаем...")
            subprocess.run([ollama_path, "pull", model], check=True)
            print(f"✅ Модель {model} успешно загружена")
        print(f"🚀 Запускаем модель LLM: {model}")
        subprocess.Popen([ollama_path, "run", model],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"❌ Не удалось запустить модель: {e}")


if __name__ == "__main__":
    load_dotenv()
    launch_llama_model()
    app = QApplication(sys.argv)
    window = ChatApp()
    window.show()
    sys.exit(app.exec())