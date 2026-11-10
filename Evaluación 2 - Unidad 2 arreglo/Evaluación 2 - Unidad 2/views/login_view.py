from views.access_view import Login

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
    QTabWidget
)

from services.exceptions import ServicioExternoError
from services.clima_service import consultar_clima
from services.moneda_service import consultar_tipo_cambio


class Principal(QWidget):

    def __init__(self, db):

        if not db.esta_autenticado:
            raise PermissionError(
                "Debe iniciar sesión para acceder al sistema."
            )

        super().__init__()

        self.db = db

        self.setWindowTitle(
            "Tecno Soluciones - Gestion Interna"
        )

        self.resize(820, 560)

        layout = QVBoxLayout(self)

        titulo = QLabel(
            "Tecno Soluciones - Sistema de Gestion"
        )

        titulo.setStyleSheet(
            "font-size:18px;font-weight:bold;color:#2C3E50"
        )

        layout.addWidget(titulo)

        ok, msg = db.probar_conexion()

        self.estado = QLabel(
            ("BD: " if ok else "BD ERROR: ") + msg
        )

        layout.addWidget(self.estado)

        self.tabs = QTabWidget()

        layout.addWidget(self.tabs)

        self.tabs_emp()
        self.tabs_pro()
        self.tabs_horas()
        self.tabs_api()

        self.refrescar()

    def tabs_emp(self):

        w = QWidget()

        layout = QVBoxLayout(w)

        self.le = QListWidget()

        layout.addWidget(self.le)

        boton = QPushButton("Agregar empleado")

        boton.clicked.connect(
            self.agregar_empleado
        )

        layout.addWidget(boton)

        self.tabs.addTab(
            w,
            "Empleados"
        )

    def tabs_pro(self):

        w = QWidget()

        layout = QVBoxLayout(w)

        self.lp = QListWidget()

        layout.addWidget(self.lp)

        fila = QHBoxLayout()

        crear = QPushButton(
            "Crear proyecto"
        )

        crear.clicked.connect(
            self.crear_proyecto
        )

        asignar = QPushButton(
            "Asignar empleado"
        )

        asignar.clicked.connect(
            self.asignar
        )

        fila.addWidget(crear)
        fila.addWidget(asignar)

        layout.addLayout(fila)

        self.tabs.addTab(
            w,
            "Proyectos"
        )

    def tabs_horas(self):

        w = QWidget()

        layout = QVBoxLayout(w)

        self.lr = QListWidget()

        layout.addWidget(self.lr)

        boton = QPushButton(
            "Registrar horas"
        )

        boton.clicked.connect(
            self.horas
        )

        layout.addWidget(boton)

        self.tabs.addTab(
            w,
            "Horas"
        )

    def tabs_api(self):

        w = QWidget()

        layout = QVBoxLayout(w)

        layout.addWidget(
            QLabel("Clima por ciudad")
        )

        self.ciudad_api = QLineEdit()

        self.ciudad_api.setPlaceholderText(
            "Ejemplo: Santiago"
        )

        layout.addWidget(
            self.ciudad_api
        )

        boton_clima = QPushButton(
            "Consultar clima"
        )

        boton_clima.clicked.connect(
            self.consumir_clima
        )

        layout.addWidget(
            boton_clima
        )

        layout.addWidget(
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

        layout.addLayout(monedas)

        boton_cambio = QPushButton(
            "Consultar tipo de cambio"
        )

        boton_cambio.clicked.connect(
            self.consumir_tipo_cambio
        )

        layout.addWidget(
            boton_cambio
        )

        self.api = QTextEdit()

        self.api.setReadOnly(True)

        layout.addWidget(self.api)

        self.tabs.addTab(
            w,
            "API externa"
        )

    def refrescar(self):

        self.le.clear()

        self.emps = self.db.empleados()

        for e in self.emps:

            self.le.addItem(
                f"{e['nombre']} | "
                f"{e['correo'] or '-'} | "
                f"{e['departamento'] or '-'} | "
                f"Proyectos: {e['proyectos'] or 'Ninguno'}"
            )

        self.lp.clear()

        self.pros = self.db.proyectos()

        for p in self.pros:

            self.lp.addItem(
                f"{p['nombre']} | "
                f"{p['estado']} | "
                f"Equipo: {p['equipo'] or 'Sin asignaciones'}"
            )

        self.lr.clear()

        for r in self.db.registros():

            self.lr.addItem(
                f"{r['fecha']} | "
                f"{r['empleado']} | "
                f"{r['proyecto']} | "
                f"{r['horas']} h | "
                f"{r['descripcion'] or ''}"
            )

    def agregar_empleado(self):

        nombre, ok = QInputDialog.getText(
            self,
            "Nuevo empleado",
            "Nombre completo:"
        )

        if not ok or not nombre.strip():
            return

        correo, ok = QInputDialog.getText(
            self,
            "Nuevo empleado",
            "Correo:"
        )

        if ok:

            self.db.agregar_empleado(
                nombre,
                correo
            )

            self.refrescar()

    def crear_proyecto(self):

        nombre, ok = QInputDialog.getText(
            self,
            "Nuevo proyecto",
            "Nombre:"
        )

        if not ok or not nombre.strip():
            return

        descripcion, ok = QInputDialog.getText(
            self,
            "Nuevo proyecto",
            "Descripcion:"
        )

        if ok:

            try:

                self.db.crear_proyecto(
                    nombre,
                    descripcion
                )

                self.refrescar()

            except Exception as e:

                QMessageBox.warning(
                    self,
                    "Proyecto",
                    str(e)
                )

    def asignar(self):

        empleados = {
            e["nombre"]: e["id"]
            for e in self.db.empleados()
        }

        proyectos = {
            p["nombre"]: p["id"]
            for p in self.db.proyectos()
        }

        empleado, ok = QInputDialog.getItem(
            self,
            "Asignacion",
            "Empleado:",
            list(empleados),
            0,
            False
        )

        if not ok:
            return

        proyecto, ok = QInputDialog.getItem(
            self,
            "Asignacion",
            "Proyecto:",
            list(proyectos),
            0,
            False
        )

        if not ok:
            return

        if self.db.asignar(
            empleados[empleado],
            proyectos[proyecto]
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

        empleados = {
            e["nombre"]: e["id"]
            for e in self.db.empleados()
        }

        empleado, ok = QInputDialog.getItem(
            self,
            "Horas",
            "Empleado:",
            list(empleados),
            0,
            False
        )

        if not ok:
            return

        proyectos = self.db.proyectos_de_empleado(
            empleados[empleado]
        )

        if not proyectos:

            QMessageBox.warning(
                self,
                "Horas",
                "El empleado no tiene proyectos asignados."
            )

            return

        opciones = {
            p["nombre"]: p["id"]
            for p in proyectos
        }

        proyecto, ok = QInputDialog.getItem(
            self,
            "Horas",
            "Proyecto:",
            list(opciones),
            0,
            False
        )

        if not ok:
            return

        horas, ok = QInputDialog.getDouble(
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

        descripcion, ok = QInputDialog.getText(
            self,
            "Horas",
            "Descripcion:"
        )

        if ok:

            self.db.registrar_horas(
                empleados[empleado],
                opciones[proyecto],
                horas,
                descripcion
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
                "Ocurrió un error inesperado."
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
                f"{datos['tasa']} {datos['destino']}"
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
                "Ocurrió un error inesperado."
            )