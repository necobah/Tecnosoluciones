from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QTextEdit,
    QListWidget,
    QInputDialog,
    QTabWidget,
    QFrame,
)

from services.exceptions import ServicioExternoError
from services.clima_service import consultar_clima
from services.moneda_service import consultar_tipo_cambio
from PyQt6.QtCore import Qt

class Principal(QWidget):

    def __init__(self, db):

        if not db.esta_autenticado:
            raise PermissionError(
                "Debe iniciar sesión para acceder al sistema."
            )

        super().__init__()

        self.db = db

        self.setWindowTitle(
            "Tecno Soluciones - Gestión Interna"
        )

        self.resize(1120, 760)
        self.setMinimumSize(900, 620)

        self.setStyleSheet("""
            QWidget {
                background-color: #f3f6f4;
                color: #23332d;
                font-family: "Segoe UI";
                font-size: 14px;
            }
            QLabel {
                color: #23332d;
            }
            QLabel#marca {
                background: #16735b;
                color: white;
                border-radius: 9px;
                font-size: 17px;
                font-weight: 700;
            }
            QLabel#titulo {
                color: #1e3029;
                font-size: 25px;
                font-weight: 700;
            }
            QLabel#subtitulo, QLabel#metrica_titulo {
                color: #687970;
                font-size: 12px;
            }
            QLabel#estado {
                background: #e4f2eb;
                color: #17684f;
                border: 1px solid #c9e5d7;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 12px;
                font-weight: 600;
            }
            QFrame#resumen {
                background: white;
                border: 1px solid #dfe7e2;
                border-radius: 8px;
            }
            QLabel#metrica_valor {
                color: #1e3029;
                font-size: 23px;
                font-weight: 700;
            }
            QPushButton {
                background-color: #16735b;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 14px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #105b48;
            }
            QPushButton:pressed {
                background-color: #0c493a;
            }
            QListWidget {
                background-color: white;
                border: 1px solid #dfe7e2;
                border-radius: 7px;
                padding: 8px;
                outline: none;
            }
            QListWidget::item {
                padding: 12px 10px;
                border-bottom: 1px solid #edf1ee;
            }
            QListWidget::item:hover {
                background: #f2f7f4;
            }
            QListWidget::item:selected {
                background: #e4f2eb;
                color: #145a45;
            }
            QLineEdit {
                background-color: white;
                border: 1px solid #d5dfd9;
                border-radius: 6px;
                padding: 9px 10px;
            }
            QLineEdit:focus {
                border: 1px solid #16735b;
            }

            QTabWidget::pane {
                background: white;
                border: 1px solid #dfe7e2;
                border-radius: 7px;
            }
            QTabBar::tab {
                background: transparent;
                color: #687970;
                padding: 11px 18px;
                margin-right: 4px;
                border-bottom: 2px solid transparent;
                font-weight: 600;
            }
            QTabBar::tab:selected {
                color: #16735b;
                border-bottom: 2px solid #16735b;
            }
            QTextEdit {
                background: white;
                border: 1px solid #dfe7e2;
                border-radius: 7px;
                padding: 10px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(26, 22, 26, 24)
        layout.setSpacing(16)

        encabezado = QHBoxLayout()
        encabezado.setSpacing(14)
        marca = QLabel("TS")
        marca.setObjectName("marca")
        marca.setAlignment(Qt.AlignmentFlag.AlignCenter)
        marca.setFixedSize(54, 54)
        encabezado.addWidget(marca)

        identidad = QVBoxLayout()
        identidad.setSpacing(3)
        titulo = QLabel("Tecno Soluciones")
        titulo.setObjectName("titulo")
        identidad.addWidget(titulo)
        subtitulo = QLabel("Gestión interna de equipo y proyectos")
        subtitulo.setObjectName("subtitulo")
        identidad.addWidget(subtitulo)
        encabezado.addLayout(identidad)
        encabezado.addStretch(1)

        ok, msg = db.probar_conexion()
        self.estado = QLabel(
            "Base de datos conectada" if ok else "Error de conexión con la base de datos"
        )
        self.estado.setObjectName("estado")
        if not ok:
            self.estado.setStyleSheet(
                "background: #fbe9e7; color: #a63e35; border-color: #f0c9c4;"
            )
        self.estado.setToolTip(msg)
        encabezado.addWidget(self.estado)
        layout.addLayout(encabezado)

        resumen = QHBoxLayout()
        resumen.setSpacing(12)
        self.metricas = {}
        for clave, etiqueta in (
            ("empleados", "EMPLEADOS"),
            ("proyectos", "PROYECTOS"),
            ("registros", "REGISTROS DE HORAS"),
        ):
            tarjeta = QFrame()
            tarjeta.setObjectName("resumen")
            tarjeta_layout = QVBoxLayout(tarjeta)
            tarjeta_layout.setContentsMargins(16, 12, 16, 12)
            tarjeta_layout.setSpacing(3)
            nombre = QLabel(etiqueta)
            nombre.setObjectName("metrica_titulo")
            valor = QLabel("0")
            valor.setObjectName("metrica_valor")
            tarjeta_layout.addWidget(nombre)
            tarjeta_layout.addWidget(valor)
            resumen.addWidget(tarjeta)
            self.metricas[clave] = valor
        layout.addLayout(resumen)

        self.tabs = QTabWidget()

        layout.addWidget(self.tabs)

        self.tabs_emp()
        self.tabs_pro()
        self.tabs_horas()
        self.tabs_api()

        self.refrescar()

    def tabs_emp(self):

        w = QWidget()
        l = QVBoxLayout(w)

        self.le = QListWidget()

        l.addWidget(self.le)

        b = QPushButton("Agregar empleado")

        b.clicked.connect(
            self.agregar_empleado
        )

        l.addWidget(b)

        self.tabs.addTab(
            w,
            "Empleados"
        )

    def tabs_pro(self):

        w = QWidget()

        l = QVBoxLayout(w)

        self.lp = QListWidget()

        l.addWidget(self.lp)

        f = QHBoxLayout()

        b = QPushButton(
            "Crear proyecto"
        )

        b.clicked.connect(
            self.crear_proyecto
        )

        a = QPushButton(
            "Asignar empleado"
        )

        a.clicked.connect(self.asignar)

        f.addWidget(b)
        f.addWidget(a)

        l.addLayout(f)

        self.tabs.addTab(
            w,
            "Proyectos"
        )

    def tabs_horas(self):

        w = QWidget()

        l = QVBoxLayout(w)

        self.lr = QListWidget()

        l.addWidget(self.lr)

        b = QPushButton(
            "Registrar horas"
        )

        b.clicked.connect(
            self.horas
        )

        l.addWidget(b)

        self.tabs.addTab(
            w,
            "Horas"
        )

    def tabs_api(self):

        w = QWidget()

        l = QVBoxLayout(w)

        l.addWidget(
            QLabel("Clima por ciudad")
        )

        self.ciudad_api = QLineEdit()

        self.ciudad_api.setPlaceholderText(
            "Ejemplo: Santiago"
        )

        l.addWidget(self.ciudad_api)

        b_clima = QPushButton(
            "Consultar clima"
        )

        b_clima.clicked.connect(
            self.consumir_clima
        )

        l.addWidget(b_clima)

        l.addWidget(
            QLabel("Tipo de cambio")
        )

        monedas = QHBoxLayout()

        self.moneda_origen = QLineEdit(
            "USD"
        )

        self.moneda_destino = QLineEdit(
            "CLP"
        )

        self.moneda_origen.setMaxLength(3)
        self.moneda_destino.setMaxLength(3)

        monedas.addWidget(
            QLabel("Desde:")
        )

        monedas.addWidget(
            self.moneda_origen
        )

        monedas.addWidget(
            QLabel("Hacia:")
        )

        monedas.addWidget(
            self.moneda_destino
        )

        l.addLayout(monedas)

        b_cambio = QPushButton(
            "Consultar tipo de cambio"
        )

        b_cambio.clicked.connect(
            self.consumir_tipo_cambio
        )

        l.addWidget(b_cambio)

        self.api = QTextEdit()

        self.api.setReadOnly(True)

        l.addWidget(self.api)

        self.tabs.addTab(
            w,
            "API externa"
        )

    def refrescar(self):

        self.le.clear()

        self.emps = self.db.empleados()
        self.metricas["empleados"].setText(str(len(self.emps)))

        for e in self.emps:

            self.le.addItem(
                f"{e['nombre']} | "
                f"{e['correo'] or '-'} | "
                f"{e['departamento'] or '-'} | "
                f"Proyectos: {e['proyectos'] or 'Ninguno'}"
            )

        self.lp.clear()

        self.pros = self.db.proyectos()
        self.metricas["proyectos"].setText(str(len(self.pros)))

        for p in self.pros:

            self.lp.addItem(
                f"{p['nombre']} | "
                f"{p['estado']} | "
                f"Equipo: {p['equipo'] or 'Sin asignaciones'}"
            )

        self.lr.clear()

        registros = self.db.registros()
        self.metricas["registros"].setText(str(len(registros)))

        for r in registros:

            self.lr.addItem(
                f"{r['fecha']} | "
                f"{r['empleado']} | "
                f"{r['proyecto']} | "
                f"{r['horas']} h | "
                f"{r['descripcion'] or ''}"
            )

    def agregar_empleado(self):

        n, ok = QInputDialog.getText(
            self,
            "Nuevo empleado",
            "Nombre completo:"
        )

        if not ok or not n.strip():
            return

        c, ok = QInputDialog.getText(
            self,
            "Nuevo empleado",
            "Correo:"
        )

        if ok:

            self.db.agregar_empleado(
                n,
                c
            )

            self.refrescar()

    def crear_proyecto(self):

        n, ok = QInputDialog.getText(
            self,
            "Nuevo proyecto",
            "Nombre:"
        )

        if not ok or not n.strip():
            return

        d, ok = QInputDialog.getText(
            self,
            "Nuevo proyecto",
            "Descripcion:"
        )

        if ok:

            try:

                self.db.crear_proyecto(
                    n,
                    d
                )

                self.refrescar()

            except Exception as e:

                QMessageBox.warning(
                    self,
                    "Proyecto",
                    str(e)
                )

    def asignar(self):

        es = {
            e["nombre"]: e["id"]
            for e in self.db.empleados()
        }

        ps = {
            p["nombre"]: p["id"]
            for p in self.db.proyectos()
        }

        en, ok = QInputDialog.getItem(
            self,
            "Asignacion",
            "Empleado:",
            list(es),
            0,
            False
        )

        if not ok:
            return

        pn, ok = QInputDialog.getItem(
            self,
            "Asignacion",
            "Proyecto:",
            list(ps),
            0,
            False
        )

        if not ok:
            return

        if self.db.asignar(
            es[en],
            ps[pn]
        ):

            QMessageBox.information(
                self,
                "Asignacion",
                "Empleado asignado correctamente."
            )

        else:

            QMessageBox.warning(
                self,
                "Asignacion",
                "Ya existe esa asignacion."
            )

        self.refrescar()

    def horas(self):

        es = {
            e["nombre"]: e["id"]
            for e in self.db.empleados()
        }

        en, ok = QInputDialog.getItem(
            self,
            "Horas",
            "Empleado:",
            list(es),
            0,
            False
        )

        if not ok:
            return

        prows = self.db.proyectos_de_empleado(
            es[en]
        )

        if not prows:

            QMessageBox.warning(
                self,
                "Horas",
                "El empleado no tiene proyectos asignados."
            )

            return

        ps = {
            p["nombre"]: p["id"]
            for p in prows
        }

        pn, ok = QInputDialog.getItem(
            self,
            "Horas",
            "Proyecto:",
            list(ps),
            0,
            False
        )

        if not ok:
            return

        h, ok = QInputDialog.getDouble(
            self,
            "Horas",
            "Horas trabajadas:",
            1,
            0.1,
            24,
            1
        )

        if not ok:
            return

        d, ok = QInputDialog.getText(
            self,
            "Horas",
            "Descripcion:"
        )

        if ok:

            self.db.registrar_horas(
                es[en],
                ps[pn],
                h,
                d
            )

            self.refrescar()

    def consumir_clima(self):

        try:

            datos = consultar_clima(
                self.ciudad_api.text()
            )

            lugar = (
                f"{datos['ciudad']}, {datos['pais']}"
                if datos["pais"]
                else datos["ciudad"]
            )

            self.api.setPlainText(
                f"Clima actual en {lugar}\n"
                f"Temperatura: {datos['temperatura']} °C\n"
                f"Estado: {datos['estado']}\n"
                f"Humedad: {datos['humedad']}%\n"
                f"Hora local: {datos['hora']}"
            )

        except (
            ValueError,
            ServicioExternoError
        ) as exc:

            QMessageBox.warning(
                self,
                "Consulta de clima",
                str(exc)
            )

        except Exception:

            QMessageBox.warning(
                self,
                "Consulta de clima",
                "Ocurrió un error inesperado. Intente nuevamente."
            )

    def consumir_tipo_cambio(self):

        try:

            datos = consultar_tipo_cambio(
                self.moneda_origen.text(),
                self.moneda_destino.text()
            )

            self.api.setPlainText(
                f"Tipo de cambio ({datos['fecha']})\n"
                f"1 {datos['origen']} = "
                f"{datos['tasa']} "
                f"{datos['destino']}"
            )

        except (
            ValueError,
            ServicioExternoError
        ) as exc:

            QMessageBox.warning(
                self,
                "Tipo de cambio",
                str(exc)
            )

        except Exception:

            QMessageBox.warning(
                self,
                "Tipo de cambio",
                "Ocurrió un error inesperado. Intente nuevamente."
            )