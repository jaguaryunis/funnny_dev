import sys
import json
import requests
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton, QMessageBox, QComboBox, QHBoxLayout
)
from PyQt5.QtCore import QFile, QIODevice

class WebhookSender(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.webhooks = self.load_webhooks()

    def init_ui(self):
        self.setWindowTitle("Webhook 消息发送工具")
        self.setGeometry(100, 100, 500, 400)

        # 创建布局
        main_layout = QVBoxLayout()

        # Webhook 别名选择
        self.webhook_label = QLabel("选择 Webhook（或输入新地址）:")
        self.webhook_combo = QComboBox()
        self.webhook_combo.setEditable(True)
        main_layout.addWidget(self.webhook_label)
        main_layout.addWidget(self.webhook_combo)

        # 新 Webhook 别名
        alias_layout = QHBoxLayout()
        self.alias_label = QLabel("别名（保存时使用）:")
        self.alias_input = QLineEdit()
        alias_layout.addWidget(self.alias_label)
        alias_layout.addWidget(self.alias_input)
        main_layout.addLayout(alias_layout)

        # 消息内容输入
        self.message_label = QLabel("发送的消息:")
        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("请输入要发送的消息")
        main_layout.addWidget(self.message_label)
        main_layout.addWidget(self.message_input)

        # 按钮布局
        button_layout = QHBoxLayout()
        self.send_button = QPushButton("发送消息")
        self.save_button = QPushButton("保存 Webhook")
        self.send_button.clicked.connect(self.send_message)
        self.save_button.clicked.connect(self.save_webhook)
        button_layout.addWidget(self.send_button)
        button_layout.addWidget(self.save_button)
        main_layout.addLayout(button_layout)

        # 设置主布局
        self.setLayout(main_layout)

    def load_webhooks(self):
        """加载保存的 Webhook 地址及别名"""
        try:
            with open("webhooks.json", "r", encoding="utf-8") as f:
                webhooks = json.load(f)
                for alias in webhooks:
                    self.webhook_combo.addItem(f"{alias} ({webhooks[alias]})")
                return webhooks
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_webhooks_to_file(self):
        """保存 Webhook 地址及别名到文件"""
        with open("webhooks.json", "w", encoding="utf-8") as f:
            json.dump(self.webhooks, f, ensure_ascii=False, indent=4)

    def save_webhook(self):
        """保存新的 Webhook 地址及别名"""
        webhook_url = self.webhook_combo.currentText().strip()
        alias = self.alias_input.text().strip()

        if not webhook_url or not alias:
            QMessageBox.warning(self, "错误", "Webhook 地址和别名不能为空！")
            return

        self.webhooks[alias] = webhook_url
        self.save_webhooks_to_file()
        self.webhook_combo.addItem(f"{alias} ({webhook_url})")
        QMessageBox.information(self, "成功", "Webhook 已保存！")

    def send_message(self):
        """发送消息到选定的 Webhook"""
        selected_text = self.webhook_combo.currentText().strip()
        webhook_url = None
        for alias, url in self.webhooks.items():
            if selected_text.startswith(f"{alias} ("):
                webhook_url = url
                break
        if webhook_url is None:
            webhook_url = selected_text

        message_content = self.message_input.toPlainText().strip()

        if not webhook_url:
            QMessageBox.warning(self, "错误", "Webhook 地址不能为空！")
            return

        if not message_content:
            QMessageBox.warning(self, "错误", "消息内容不能为空！")
            return

        data = {
            "msgtype": "text",
            "text": {
                "content": message_content
            }
        }

        try:
            response = requests.post(
                webhook_url,
                headers={"Content-Type": "application/json"},
                data=json.dumps(data)
            )

            if response.status_code == 200:
                QMessageBox.information(self, "成功", "消息发送成功！")
            else:
                QMessageBox.critical(
                    self, "失败", f"消息发送失败！状态码: {response.status_code}\n响应: {response.text}"
                )
        except Exception as e:
            QMessageBox.critical(self, "错误", f"发生异常: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WebhookSender()
    window.show()
    sys.exit(app.exec_())
