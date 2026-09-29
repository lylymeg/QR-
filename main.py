import sys
import qrcode
from PIL import Image
from pyzbar.pyzbar import decode

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QLineEdit, QPushButton, QFileDialog,
    QColorDialog, QFrame, QMessageBox, QTextEdit
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap, QImage, QColor


class QRCodeTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Générateur & Lecteur de QR Code 📲")
        self.setFixedSize(520, 580)
        self.setStyleSheet("background-color: #1E222B;")

        self.qr_color = QColor("#000000")
        self.bg_color = QColor("#FFFFFF")
        self.generated_pil_img = None

        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Onglets principaux
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #3E4451;
                border-radius: 8px;
                background-color: #21252B;
            }
            QTabBar::tab {
                background-color: #282C34;
                color: #ABB2BF;
                padding: 10px 20px;
                font-weight: bold;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
            QTabBar::tab:selected {
                background-color: #61AFEF;
                color: #1E222B;
            }
        """)

        self.tab_generator = QWidget()
        self.tab_reader = QWidget()

        self.setup_generator_tab()
        self.setup_reader_tab()

        self.tabs.addTab(self.tab_generator, "✨ Générer")
        self.tabs.addTab(self.tab_reader, "🔍 Lire / Décoder")

        main_layout.addWidget(self.tabs)

    # ------------------ ONGLET GÉNÉRATEUR ------------------
    def setup_generator_tab(self):
        layout = QVBoxLayout(self.tab_generator)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)

        # Saisie du contenu
        self.input_text = QLineEdit()
        self.input_text.setPlaceholderText("Entrez une URL ou un texte...")
        self.input_text.setFont(QFont("Segoe UI", 10))
        self.input_text.setStyleSheet("""
            QLineEdit {
                background-color: #282C34;
                color: #ECEFF4;
                border: 1px solid #3E4451;
                border-radius: 6px;
                padding: 8px;
            }
        """)
        layout.addWidget(self.input_text)

        # Choix des couleurs
        colors_layout = QHBoxLayout()

        self.btn_qr_color = QPushButton("Couleur Code")
        self.btn_qr_color.setCursor(Qt.PointingHandCursor)
        self.btn_qr_color.setStyleSheet(self.get_button_style("#98C379", "#1E222B"))
        self.btn_qr_color.clicked.connect(self.choose_qr_color)

        self.btn_bg_color = QPushButton("Couleur Fond")
        self.btn_bg_color.setCursor(Qt.PointingHandCursor)
        self.btn_bg_color.setStyleSheet(self.get_button_style("#E5C07B", "#1E222B"))
        self.btn_bg_color.clicked.connect(self.choose_bg_color)

        colors_layout.addWidget(self.btn_qr_color)
        colors_layout.addWidget(self.btn_bg_color)
        layout.addLayout(colors_layout)

        # Bouton Générer
        btn_generate = QPushButton("Générer le QR Code")
        btn_generate.setFont(QFont("Segoe UI", 10, QFont.Bold))
        btn_generate.setCursor(Qt.PointingHandCursor)
        btn_generate.setStyleSheet(self.get_button_style("#61AFEF", "#1E222B"))
        btn_generate.clicked.connect(self.generate_qr)
        layout.addWidget(btn_generate)

        # Aperçu
        self.lbl_qr_preview = QLabel("L'aperçu du QR code s'affichera ici")
        self.lbl_qr_preview.setAlignment(Qt.AlignCenter)
        self.lbl_qr_preview.setFont(QFont("Segoe UI", 9))
        self.lbl_qr_preview.setStyleSheet("""
            QLabel {
                background-color: #1E222B;
                color: #5C6370;
                border: 1px dashed #3E4451;
                border-radius: 8px;
            }
        """)
        self.lbl_qr_preview.setFixedSize(240, 240)
        layout.addWidget(self.lbl_qr_preview, alignment=Qt.AlignCenter)

        # Bouton Enregistrer
        self.btn_save = QPushButton("💾 Enregistrer l'image")
        self.btn_save.setEnabled(False)
        self.btn_save.setCursor(Qt.PointingHandCursor)
        self.btn_save.setStyleSheet(self.get_button_style("#3E4451", "#ECEFF4"))
        self.btn_save.clicked.connect(self.save_qr)
        layout.addWidget(self.btn_save)

    # ------------------ ONGLET LECTEUR ------------------
    def setup_reader_tab(self):
        layout = QVBoxLayout(self.tab_reader)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)

        # Bouton d'importation
        btn_load = QPushButton("📁 Importer une image de QR Code")
        btn_load.setFont(QFont("Segoe UI", 10, QFont.Bold))
        btn_load.setCursor(Qt.PointingHandCursor)
        btn_load.setStyleSheet(self.get_button_style("#61AFEF", "#1E222B"))
        btn_load.clicked.connect(self.load_and_decode_qr)
        layout.addWidget(btn_load)

        # Zone d'aperçu de l'image importée
        self.lbl_read_preview = QLabel("Aucune image chargée")
        self.lbl_read_preview.setAlignment(Qt.AlignCenter)
        self.lbl_read_preview.setFont(QFont("Segoe UI", 9))
        self.lbl_read_preview.setStyleSheet("""
            QLabel {
                background-color: #1E222B;
                color: #5C6370;
                border: 1px dashed #3E4451;
                border-radius: 8px;
            }
        """)
        self.lbl_read_preview.setFixedSize(200, 200)
        layout.addWidget(self.lbl_read_preview, alignment=Qt.AlignCenter)

        # Zone de résultat texte
        lbl_res_title = QLabel("Résultat du décodage :")
        lbl_res_title.setFont(QFont("Segoe UI", 9, QFont.Bold))
        lbl_res_title.setStyleSheet("color: #ABB2BF;")
        layout.addWidget(lbl_res_title)

        self.txt_result = QTextEdit()
        self.txt_result.setReadOnly(True)
        self.txt_result.setFont(QFont("Consolas", 10))
        self.txt_result.setStyleSheet("""
            QTextEdit {
                background-color: #282C34;
                color: #98C379;
                border: 1px solid #3E4451;
                border-radius: 6px;
                padding: 8px;
            }
        """)
        layout.addWidget(self.txt_result)

    # ------------------ LOGIQUE DE L'APPLICATION ------------------
    def choose_qr_color(self):
        color = QColorDialog.getColor(self.qr_color, self, "Choisir la couleur du code")
        if color.isValid():
            self.qr_color = color

    def choose_bg_color(self):
        color = QColorDialog.getColor(self.bg_color, self, "Choisir la couleur de fond")
        if color.isValid():
            self.bg_color = color

    def generate_qr(self):
        content = self.input_text.text().strip()
        if not content:
            QMessageBox.warning(self, "Attention", "Veuillez saisir du texte ou une URL !")
            return

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=2,
        )
        qr.add_data(content)
        qr.make(fit=True)

        self.generated_pil_img = qr.make_image(
            fill_color=self.qr_color.name(),
            back_color=self.bg_color.name()
        ).convert('RGB')

        # Conversion PIL Image -> QPixmap
        data = self.generated_pil_img.tobytes("raw", "RGB")
        qimg = QImage(
            data,
            self.generated_pil_img.size[0],
            self.generated_pil_img.size[1],
            QImage.Format_RGB888
        )
        pixmap = QPixmap.fromImage(qimg)

        self.lbl_qr_preview.setPixmap(
            pixmap.scaled(230, 230, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )
        self.btn_save.setEnabled(True)
        self.btn_save.setStyleSheet(self.get_button_style("#98C379", "#1E222B"))

    def save_qr(self):
        if not self.generated_pil_img:
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Enregistrer le QR Code", "", "Images PNG (*.png);;Images JPG (*.jpg)"
        )
        if file_path:
            self.generated_pil_img.save(file_path)
            QMessageBox.information(self, "Succès", "QR Code enregistré avec succès !")

    def load_and_decode_qr(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Ouvrir une image de QR Code", "", "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        if not file_path:
            return

        pixmap = QPixmap(file_path)
        self.lbl_read_preview.setPixmap(
            pixmap.scaled(190, 190, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )

        try:
            img = Image.open(file_path)
            decoded_objects = decode(img)

            if decoded_objects:
                result_text = ""
                for obj in decoded_objects:
                    result_text += f"{obj.data.decode('utf-8')}\n"
                self.txt_result.setText(result_text.strip())
            else:
                self.txt_result.setText("⚠️ Aucun QR Code détecté dans cette image.")
        except Exception as e:
            self.txt_result.setText(f"❌ Erreur de lecture : {str(e)}")

    def get_button_style(self, bg_color, text_color):
        return f"""
            QPushButton {{
                background-color: {bg_color};
                color: {text_color};
                border-radius: 6px;
                padding: 8px;
                font-weight: bold;
                border: none;
            }}
            QPushButton:hover {{
                opacity: 0.9;
            }}
        """


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QRCodeTool()
    window.show()
    sys.exit(app.exec_())
    