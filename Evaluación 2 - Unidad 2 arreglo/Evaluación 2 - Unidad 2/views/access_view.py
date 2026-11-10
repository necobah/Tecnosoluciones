from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from views.principal_view import Principal


class Login(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.ventana_principal = None
        self.configuracion_inicial = not db.usuarios_configurados()

        self.setWindowTitle("Tecno Soluciones | Acceso")
        self.setFixedSize(460, 570 if self.configuracion_inicial else 490)
        self.setStyleSheet("""
            QWidget {
                background: #f3f6f4;
                color: #23332d;
                font-family: "Segoe UI";
                font-size: 14px;
            }
            QFrame#panel {
                background: #ffffff;
                border: 1px solid #dfe7e2;
                border-radius: 12px;
            }
            QLabel#marca {
                color: #16735b;
                font-size: 13px;
                font-weight: 700;
            }
            QLabel#titulo {
                color: #1e3029;
                font-size: 26px;
                font-weight: 700;
            }
            QLabel#ayuda, QLabel.etiqueta { color: #64746c; }
            QLineEdit {
                min-height: 22px;
                padding: 10px 12px;
                border: 1px solid #d5dfd9;
                border-radius: 6px;
                background: #fbfcfb;
                selection-background-color: #16735b;
            }
            QLineEdit:focus {
                border: 1px solid #16735b;
                background: #ffffff;
            }
            QPushButton {
                min-height: 24px;
                padding: 10px 14px;
                border: none;
                border-radius: 6px;
                background: #16735b;
                color: white;
                font-weight: 700;
            }
            QPushButton:hover { background: #105b48; }
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 28, 28, 28)
        root.addStretch(1)

        panel = QFrame()
        panel.setObjectName("panel")
        content = QVBoxLayout(panel)
        content.setContentsMargins(32, 30, 32, 30)
        content.setSpacing(12)

        marca = QLabel("TECNO SOLUCIONES")
        marca.setObjectName("marca")
        content.addWidget(marca)

        titulo = QLabel(
            "Configura tu acceso" if self.configuracion_inicial else "Bienvenido"
        )
        titulo.setObjectName("titulo")
        content.addWidget(titulo)

        ayuda = QLabel(
            "Crea la cuenta administradora para comenzar."
            if self.configuracion_inicial
            else "Ingresa tus credenciales para continuar."
        )
        ayuda.setObjectName("ayuda")
        ayuda.setWordWrap(True)
        content.addWidget(ayuda)
        content.addSpacing(8)

        content.addWidget(self._label("Usuario"))
        self.usuario = QLineEdit()
        self.usuario.setPlaceholderText("Nombre de usuario")
        self.usuario.setMaxLength(50)
        content.addWidget(self.usuario)

        content.addWidget(self._label("Contraseña"))
        self.password = QLineEdit()
        self.password.setPlaceholderText(
            "Mínimo 12 caracteres" if self.configuracion_inicial else "Contraseña"
        )
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        content.addWidget(self.password)

        self.confirmacion = None
        if self.configuracion_inicial:
            content.addWidget(self._label("Confirmar contraseña"))
            self.confirmacion = QLineEdit()
            self.confirmacion.setPlaceholderText("Repite la contraseña")
            self.confirmacion.setEchoMode(QLineEdit.EchoMode.Password)
            content.addWidget(self.confirmacion)

        content.addSpacing(8)
        boton = QPushButton(
            "Crear cuenta y entrar" if self.configuracion_inicial else "Iniciar sesión"
        )
        boton.setCursor(Qt.CursorShape.PointingHandCursor)
        boton.clicked.connect(self._continuar)
        content.addWidget(boton)
        root.addWidget(panel)

        pie = QLabel("Gestión interna · Acceso seguro")
        pie.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pie.setStyleSheet("color: #73827a; font-size: 12px; padding-top: 12px;")
        root.addWidget(pie)
        root.addStretch(1)

        self.password.returnPressed.connect(self._continuar)
        self.usuario.setFocus()

    @staticmethod
    def _label(texto):
        etiqueta = QLabel(texto)
        etiqueta.setProperty("class", "etiqueta")
        return etiqueta

    def _continuar(self):
        usuario = self.usuario.text().strip()
        password = self.password.text()

        try:
            if self.configuracion_inicial:
                if password != self.confirmacion.text():
                    QMessageBox.warning(
                        self, "Validación", "Las contraseñas no coinciden."
                    )
                    return
                self.db.crear_usuario_inicial(usuario, password)

            if not self.db.autenticar(usuario, password):
                QMessageBox.warning(
                    self, "Acceso denegado", "El usuario o la contraseña no son correctos."
                )
                return

            self.ventana_principal = Principal(self.db)
            self.ventana_principal.show()
            self.close()
        except ValueError as exc:
            QMessageBox.warning(self, "No se pudo continuar", str(exc))
        except Exception as exc:
            QMessageBox.critical(
                self,
                "Error de acceso",
                f"No fue posible abrir el sistema.\n{exc}",
            )
