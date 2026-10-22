import sys
from PyQt6.QtWidgets import QApplication,QWidget,QVBoxLayout,QHBoxLayout,QLabel,QLineEdit,QPushButton,QMessageBox,QTextEdit,QListWidget,QInputDialog,QTabWidget
from database import BaseDatos
from servicios_externos import ServicioExternoError, consultar_clima, consultar_tipo_cambio

class Login(QWidget):
    def __init__(self, db):
        super().__init__(); self.db=db; self.setWindowTitle("Tecno Soluciones - Acceso"); self.resize(380,300); l=QVBoxLayout(self)
        inicial=not db.usuarios_configurados()
        t=QLabel("Crear administrador" if inicial else "Autenticacion de Usuario"); t.setStyleSheet("font-size:16px;font-weight:bold"); l.addWidget(t)
        l.addWidget(QLabel("Crea el primer usuario administrador." if inicial else "Ingresa tus credenciales."))
        l.addWidget(QLabel("Usuario:")); self.u=QLineEdit(); self.u.setMaxLength(50); l.addWidget(self.u)
        l.addWidget(QLabel("Contrasena:")); self.p=QLineEdit(); self.p.setEchoMode(QLineEdit.EchoMode.Password); l.addWidget(self.p)
        self.confirmar=None
        if inicial:
            l.addWidget(QLabel("Confirmar contrasena:")); self.confirmar=QLineEdit(); self.confirmar.setEchoMode(QLineEdit.EchoMode.Password); l.addWidget(self.confirmar)
            b=QPushButton("Crear administrador"); b.clicked.connect(self.crear_administrador)
        else:
            b=QPushButton("Ingresar"); b.clicked.connect(self.entrar)
        l.addWidget(b)
    def entrar(self):
        if not self.u.text().strip() or not self.p.text():
            QMessageBox.warning(self,"Acceso denegado","Ingresa usuario y contraseña.")
            return
        if self.db.autenticar(self.u.text(),self.p.text()): self.abrir_principal()
        else: QMessageBox.warning(self,"Acceso denegado","Credenciales incorrectas.")

    def crear_administrador(self):
        if self.p.text()!=self.confirmar.text():
            QMessageBox.warning(self,"Crear administrador","Las contrasenas no coinciden.")
            return
        try:
            self.db.crear_usuario_inicial(self.u.text(),self.p.text())
        except ValueError as exc:
            QMessageBox.warning(self,"Crear administrador",str(exc))
            return
        if self.db.autenticar(self.u.text(),self.p.text()): self.abrir_principal()
        else: QMessageBox.warning(self,"Acceso denegado","No fue posible iniciar sesión.")

    def abrir_principal(self):
        self.v=Principal(self.db); self.v.show(); self.close()

class Principal(QWidget):
    def __init__(self,db):
        if not db.esta_autenticado:
            raise PermissionError("Debe iniciar sesión para acceder al sistema.")
        super().__init__(); self.db=db; self.setWindowTitle("Tecno Soluciones - Gestion Interna"); self.resize(820,560); l=QVBoxLayout(self)
        t=QLabel("Tecno Soluciones - Sistema de Gestion"); t.setStyleSheet("font-size:18px;font-weight:bold;color:#2C3E50"); l.addWidget(t)
        ok,msg=db.probar_conexion(); self.estado=QLabel(("BD: " if ok else "BD ERROR: ")+msg); l.addWidget(self.estado)
        self.tabs=QTabWidget(); l.addWidget(self.tabs); self.tabs_emp(); self.tabs_pro(); self.tabs_horas(); self.tabs_api(); self.refrescar()
    def tabs_emp(self):
        w=QWidget(); l=QVBoxLayout(w); self.le=QListWidget(); l.addWidget(self.le); b=QPushButton("Agregar empleado"); b.clicked.connect(self.agregar_empleado); l.addWidget(b); self.tabs.addTab(w,"Empleados")
    def tabs_pro(self):
        w=QWidget(); l=QVBoxLayout(w); self.lp=QListWidget(); l.addWidget(self.lp); f=QHBoxLayout(); b=QPushButton("Crear proyecto"); b.clicked.connect(self.crear_proyecto); a=QPushButton("Asignar empleado"); a.clicked.connect(self.asignar); f.addWidget(b);f.addWidget(a);l.addLayout(f);self.tabs.addTab(w,"Proyectos")
    def tabs_horas(self):
        w=QWidget(); l=QVBoxLayout(w); self.lr=QListWidget(); l.addWidget(self.lr); b=QPushButton("Registrar horas");b.clicked.connect(self.horas);l.addWidget(b);self.tabs.addTab(w,"Horas")
    def tabs_api(self):
        w=QWidget();l=QVBoxLayout(w)
        l.addWidget(QLabel("Clima por ciudad"))
        self.ciudad_api=QLineEdit();self.ciudad_api.setPlaceholderText("Ejemplo: Santiago");l.addWidget(self.ciudad_api)
        b_clima=QPushButton("Consultar clima");b_clima.clicked.connect(self.consumir_clima);l.addWidget(b_clima)
        l.addWidget(QLabel("Tipo de cambio"))
        monedas=QHBoxLayout();self.moneda_origen=QLineEdit("USD");self.moneda_destino=QLineEdit("CLP")
        self.moneda_origen.setMaxLength(3);self.moneda_destino.setMaxLength(3)
        monedas.addWidget(QLabel("Desde:"));monedas.addWidget(self.moneda_origen);monedas.addWidget(QLabel("Hacia:"));monedas.addWidget(self.moneda_destino);l.addLayout(monedas)
        b_cambio=QPushButton("Consultar tipo de cambio");b_cambio.clicked.connect(self.consumir_tipo_cambio);l.addWidget(b_cambio)
        self.api=QTextEdit();self.api.setReadOnly(True);l.addWidget(self.api)
        self.tabs.addTab(w,"API externa")
    def refrescar(self):
        self.le.clear(); self.emps=self.db.empleados()
        for e in self.emps:self.le.addItem(f"{e['nombre']} | {e['correo'] or '-'} | {e['departamento'] or '-'} | Proyectos: {e['proyectos'] or 'Ninguno'}")
        self.lp.clear();self.pros=self.db.proyectos()
        for p in self.pros:self.lp.addItem(f"{p['nombre']} | {p['estado']} | Equipo: {p['equipo'] or 'Sin asignaciones'}")
        self.lr.clear()
        for r in self.db.registros():self.lr.addItem(f"{r['fecha']} | {r['empleado']} | {r['proyecto']} | {r['horas']} h | {r['descripcion'] or ''}")
    def agregar_empleado(self):
        n,ok=QInputDialog.getText(self,"Nuevo empleado","Nombre completo:");
        if not ok or not n.strip():return
        c,ok=QInputDialog.getText(self,"Nuevo empleado","Correo:");
        if ok:self.db.agregar_empleado(n,c);self.refrescar()
    def crear_proyecto(self):
        n,ok=QInputDialog.getText(self,"Nuevo proyecto","Nombre:");
        if not ok or not n.strip():return
        d,ok=QInputDialog.getText(self,"Nuevo proyecto","Descripcion:");
        if ok:
            try:self.db.crear_proyecto(n,d);self.refrescar()
            except Exception as e: QMessageBox.warning(self,"Proyecto",str(e))
    def asignar(self):
        es={e['nombre']:e['id'] for e in self.db.empleados()}; ps={p['nombre']:p['id'] for p in self.db.proyectos()}
        en,ok=QInputDialog.getItem(self,"Asignacion","Empleado:",list(es),0,False)
        if not ok:return
        pn,ok=QInputDialog.getItem(self,"Asignacion","Proyecto:",list(ps),0,False)
        if not ok:return
        if self.db.asignar(es[en],ps[pn]):QMessageBox.information(self,"Asignacion","Empleado asignado correctamente.")
        else:QMessageBox.warning(self,"Asignacion","Ya existe esa asignacion.")
        self.refrescar()
    def horas(self):
        es={e['nombre']:e['id'] for e in self.db.empleados()};en,ok=QInputDialog.getItem(self,"Horas","Empleado:",list(es),0,False)
        if not ok:return
        prows=self.db.proyectos_de_empleado(es[en])
        if not prows:QMessageBox.warning(self,"Horas","El empleado no tiene proyectos asignados.");return
        ps={p['nombre']:p['id'] for p in prows};pn,ok=QInputDialog.getItem(self,"Horas","Proyecto:",list(ps),0,False)
        if not ok:return
        h,ok=QInputDialog.getDouble(self,"Horas","Horas trabajadas:",1,0.1,24,1)
        if not ok:return
        d,ok=QInputDialog.getText(self,"Horas","Descripcion:")
        if ok:self.db.registrar_horas(es[en],ps[pn],h,d);self.refrescar()
    def consumir_clima(self):
        try:
            datos=consultar_clima(self.ciudad_api.text())
            lugar=f"{datos['ciudad']}, {datos['pais']}" if datos["pais"] else datos["ciudad"]
            self.api.setPlainText(f"Clima actual en {lugar}\nTemperatura: {datos['temperatura']} °C\nEstado: {datos['estado']}\nHumedad: {datos['humedad']}%\nHora local: {datos['hora']}")
        except (ValueError, ServicioExternoError) as exc:
            QMessageBox.warning(self,"Consulta de clima",str(exc))
        except Exception:
            QMessageBox.warning(self,"Consulta de clima","Ocurrió un error inesperado. Intente nuevamente.")

    def consumir_tipo_cambio(self):
        try:
            datos=consultar_tipo_cambio(self.moneda_origen.text(),self.moneda_destino.text())
            self.api.setPlainText(f"Tipo de cambio ({datos['fecha']})\n1 {datos['origen']} = {datos['tasa']} {datos['destino']}")
        except (ValueError, ServicioExternoError) as exc:
            QMessageBox.warning(self,"Tipo de cambio",str(exc))
        except Exception:
            QMessageBox.warning(self,"Tipo de cambio","Ocurrió un error inesperado. Intente nuevamente.")

def main():
    app=QApplication(sys.argv);db=BaseDatos();v=Login(db);v.show();sys.exit(app.exec())
if __name__=="__main__":main()

