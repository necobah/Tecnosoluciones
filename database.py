import sqlite3
import hashlib
import hmac
import re
from contextlib import contextmanager
from pathlib import Path

import bcrypt

DB_PATH = Path(__file__).with_name("tecno_soluciones.db")
LEGACY_DEMO_HASH = hashlib.sha256("Tecno2026".encode("utf-8")).hexdigest()

class BaseDatos:
    def __init__(self, ruta=DB_PATH):
        self.ruta = str(ruta)
        self.usuario_autenticado_id = None
        self.inicializar()

    @property
    def esta_autenticado(self):
        return self.usuario_autenticado_id is not None

    def _exigir_autenticacion(self):
        if not self.esta_autenticado:
            raise PermissionError("Debe iniciar sesión para acceder a esta función.")

    @contextmanager
    def conectar(self):
        con = sqlite3.connect(self.ruta)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA foreign_keys = ON")
        try:
            yield con
            con.commit()
        except Exception:
            con.rollback()
            raise
        finally:
            con.close()

    def probar_conexion(self):
        try:
            with self.conectar() as con:
                con.execute("SELECT 1").fetchone()
            return True, "Conexion exitosa con la base de datos SQLite."
        except sqlite3.Error:
            return False, "No fue posible conectar con la base de datos."

    def inicializar(self):
        with self.conectar() as con:
            con.executescript('''
            CREATE TABLE IF NOT EXISTS departamentos(id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT UNIQUE NOT NULL, activo INTEGER NOT NULL DEFAULT 1);
            CREATE TABLE IF NOT EXISTS empleados(id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT NOT NULL, correo TEXT, activo INTEGER NOT NULL DEFAULT 1, departamento_id INTEGER, FOREIGN KEY(departamento_id) REFERENCES departamentos(id));
            CREATE TABLE IF NOT EXISTS proyectos(id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT UNIQUE NOT NULL, descripcion TEXT, estado TEXT NOT NULL DEFAULT 'Pendiente');
            CREATE TABLE IF NOT EXISTS asignaciones(id INTEGER PRIMARY KEY AUTOINCREMENT, empleado_id INTEGER NOT NULL, proyecto_id INTEGER NOT NULL, activa INTEGER NOT NULL DEFAULT 1, fecha_asignacion TEXT NOT NULL DEFAULT CURRENT_DATE, UNIQUE(empleado_id, proyecto_id), FOREIGN KEY(empleado_id) REFERENCES empleados(id), FOREIGN KEY(proyecto_id) REFERENCES proyectos(id));
            CREATE TABLE IF NOT EXISTS registros_tiempo(id INTEGER PRIMARY KEY AUTOINCREMENT, empleado_id INTEGER NOT NULL, proyecto_id INTEGER NOT NULL, horas REAL NOT NULL CHECK(horas > 0 AND horas <= 24), descripcion TEXT, fecha TEXT NOT NULL DEFAULT CURRENT_DATE, FOREIGN KEY(empleado_id) REFERENCES empleados(id), FOREIGN KEY(proyecto_id) REFERENCES proyectos(id));
            CREATE TABLE IF NOT EXISTS usuarios(id INTEGER PRIMARY KEY AUTOINCREMENT, nombre_usuario TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, activo INTEGER NOT NULL DEFAULT 1);
            ''')
            dept = con.execute("SELECT id FROM departamentos WHERE nombre = ?", ("Tecnologia",)).fetchone()
            if not dept:
                con.execute("INSERT INTO departamentos(nombre) VALUES(?)", ("Tecnologia",))
                dept_id = con.execute("SELECT last_insert_rowid()").fetchone()[0]
            else: dept_id = dept[0]
            for nombre, correo in [("Gabrielle Saavedra", "gabrielle@tecno.cl"), ("Javiera Astorga", "javiera@tecno.cl")]:
                existentes = con.execute(
                    "SELECT id FROM empleados WHERE lower(correo)=lower(?) ORDER BY id",
                    (correo,),
                ).fetchall()
                if existentes:
                    empleado_principal = existentes[0]["id"]
                    for duplicado in existentes[1:]:
                        empleado_duplicado = duplicado["id"]
                        con.execute(
                            "INSERT OR IGNORE INTO asignaciones(empleado_id,proyecto_id,activa,fecha_asignacion) "
                            "SELECT ?,proyecto_id,activa,fecha_asignacion FROM asignaciones WHERE empleado_id=?",
                            (empleado_principal, empleado_duplicado),
                        )
                        con.execute(
                            "UPDATE registros_tiempo SET empleado_id=? WHERE empleado_id=?",
                            (empleado_principal, empleado_duplicado),
                        )
                        con.execute("DELETE FROM empleados WHERE id=?", (empleado_duplicado,))
                else:
                    con.execute(
                        "INSERT INTO empleados(nombre, correo, departamento_id) VALUES(?,?,?)",
                        (nombre, correo, dept_id),
                    )
            for nombre, desc in [("Sistema de Gestion Interna", "Optimizacion del sistema interno de TecnoSoluciones"), ("Control de Proyectos", "Organizacion y seguimiento de proyectos")]:
                con.execute("INSERT OR IGNORE INTO proyectos(nombre, descripcion) VALUES(?,?)", (nombre, desc))
            con.execute(
                "DELETE FROM usuarios WHERE nombre_usuario=? AND password_hash=?",
                ("admin", LEGACY_DEMO_HASH),
            )

    def usuarios_configurados(self):
        with self.conectar() as con:
            return con.execute("SELECT 1 FROM usuarios LIMIT 1").fetchone() is not None

    def crear_usuario_inicial(self, usuario, password):
        usuario = usuario.strip() if isinstance(usuario, str) else ""
        password = password if isinstance(password, str) else ""
        if not re.fullmatch(r"[A-Za-z0-9_.-]{3,50}", usuario):
            raise ValueError("El usuario debe tener entre 3 y 50 caracteres: letras, números, punto, guion o guion bajo.")
        if len(password) < 12 or len(password.encode("utf-8")) > 72:
            raise ValueError("La contraseña debe tener al menos 12 caracteres y no superar 72 bytes.")

        password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("ascii")
        try:
            with self.conectar() as con:
                if con.execute("SELECT 1 FROM usuarios LIMIT 1").fetchone():
                    raise ValueError("Ya existe un usuario configurado.")
                con.execute(
                    "INSERT INTO usuarios(nombre_usuario, password_hash) VALUES(?,?)",
                    (usuario, password_hash),
                )
        except sqlite3.IntegrityError as exc:
            raise ValueError("No se pudo crear el usuario inicial.") from exc

    def autenticar(self, usuario, password):
        self.usuario_autenticado_id = None
        if not isinstance(usuario, str) or not isinstance(password, str):
            return False
        usuario = usuario.strip()
        if not usuario or not password or len(password.encode("utf-8")) > 72:
            return False

        with self.conectar() as con:
            fila = con.execute(
                "SELECT id, password_hash FROM usuarios WHERE nombre_usuario=? AND activo=1",
                (usuario,),
            ).fetchone()
            if not fila:
                return False

            guardado = fila["password_hash"]
            try:
                if guardado.startswith(("$2a$", "$2b$", "$2y$")):
                    valido = bcrypt.checkpw(password.encode("utf-8"), guardado.encode("ascii"))
                else:
                    legado = hashlib.sha256(password.encode("utf-8")).hexdigest()
                    valido = hmac.compare_digest(guardado, legado)
                    if valido:
                        nuevo_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("ascii")
                        con.execute(
                            "UPDATE usuarios SET password_hash=? WHERE id=?",
                            (nuevo_hash, fila["id"]),
                        )
            except (ValueError, TypeError):
                return False

            if valido:
                self.usuario_autenticado_id = fila["id"]
            return valido

    def cerrar_sesion(self):
        self.usuario_autenticado_id = None

    def empleados(self):
        self._exigir_autenticacion()
        with self.conectar() as con:
            return con.execute('''SELECT e.id,e.nombre,e.correo,d.nombre departamento, GROUP_CONCAT(p.nombre, ', ') proyectos FROM empleados e LEFT JOIN departamentos d ON d.id=e.departamento_id LEFT JOIN asignaciones a ON a.empleado_id=e.id AND a.activa=1 LEFT JOIN proyectos p ON p.id=a.proyecto_id WHERE e.activo=1 GROUP BY e.id ORDER BY e.nombre''').fetchall()
    def proyectos(self):
        self._exigir_autenticacion()
        with self.conectar() as con:
            return con.execute('''SELECT p.id,p.nombre,p.descripcion,p.estado,GROUP_CONCAT(e.nombre, ', ') equipo FROM proyectos p LEFT JOIN asignaciones a ON a.proyecto_id=p.id AND a.activa=1 LEFT JOIN empleados e ON e.id=a.empleado_id GROUP BY p.id ORDER BY p.nombre''').fetchall()
    def agregar_empleado(self, nombre, correo):
        self._exigir_autenticacion()
        with self.conectar() as con:
            dep=con.execute("SELECT id FROM departamentos WHERE nombre=?",("Tecnologia",)).fetchone()[0]
            con.execute("INSERT INTO empleados(nombre,correo,departamento_id) VALUES(?,?,?)",(nombre.strip(),correo.strip(),dep))
    def crear_proyecto(self, nombre, descripcion):
        self._exigir_autenticacion()
        with self.conectar() as con: con.execute("INSERT INTO proyectos(nombre,descripcion) VALUES(?,?)",(nombre.strip(),descripcion.strip()))
    def asignar(self, empleado_id, proyecto_id):
        self._exigir_autenticacion()
        try:
            with self.conectar() as con:
                con.execute("INSERT INTO asignaciones(empleado_id,proyecto_id) VALUES(?,?)",(empleado_id,proyecto_id))
                con.execute("UPDATE proyectos SET estado='Activo' WHERE id=?",(proyecto_id,))
            return True
        except sqlite3.IntegrityError: return False
    def registrar_horas(self, empleado_id, proyecto_id, horas, descripcion):
        self._exigir_autenticacion()
        with self.conectar() as con: con.execute("INSERT INTO registros_tiempo(empleado_id,proyecto_id,horas,descripcion) VALUES(?,?,?,?)",(empleado_id,proyecto_id,horas,descripcion.strip()))
    def proyectos_de_empleado(self, empleado_id):
        self._exigir_autenticacion()
        with self.conectar() as con:
            return con.execute("SELECT p.id,p.nombre FROM proyectos p JOIN asignaciones a ON a.proyecto_id=p.id WHERE a.empleado_id=? AND a.activa=1 ORDER BY p.nombre",(empleado_id,)).fetchall()
    def registros(self):
        self._exigir_autenticacion()
        with self.conectar() as con:
            return con.execute('''SELECT r.fecha,e.nombre empleado,p.nombre proyecto,r.horas,r.descripcion FROM registros_tiempo r JOIN empleados e ON e.id=r.empleado_id JOIN proyectos p ON p.id=r.proyecto_id ORDER BY r.id DESC''').fetchall()
