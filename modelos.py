class Empleado:
    def __init__(self, nombre, correo="", id_empleado=None, activo=True):
        self.__id = id_empleado
        self.__nombre = nombre.strip()
        self.__correo = correo.strip()
        self.__activo = bool(activo)
    @property
    def id(self): return self.__id
    @property
    def nombre(self): return self.__nombre
    @property
    def correo(self): return self.__correo
    @property
    def activo(self): return self.__activo
    def actualizar_datos(self, nombre=None, correo=None):
        if nombre: self.__nombre = nombre.strip()
        if correo is not None: self.__correo = correo.strip()
    def activar(self): self.__activo = True
    def desactivar(self): self.__activo = False

class Departamento:
    def __init__(self, nombre, id_departamento=None, activo=True):
        self.__id = id_departamento
        self.__nombre = nombre.strip()
        self.__activo = bool(activo)
    @property
    def id(self): return self.__id
    @property
    def nombre(self): return self.__nombre
    @property
    def activo(self): return self.__activo

class Proyecto:
    ESTADOS = ("Pendiente", "Activo", "Cerrado")
    def __init__(self, nombre, descripcion="", estado="Pendiente", id_proyecto=None):
        self.__id = id_proyecto
        self.__nombre = nombre.strip()
        self.__descripcion = descripcion.strip()
        self.__estado = estado if estado in self.ESTADOS else "Pendiente"
    @property
    def id(self): return self.__id
    @property
    def nombre(self): return self.__nombre
    @property
    def descripcion(self): return self.__descripcion
    @property
    def estado(self): return self.__estado
    def activar(self): self.__estado = "Activo"
    def cerrar(self): self.__estado = "Cerrado"

class AsignacionProyecto:
    def __init__(self, empleado_id, proyecto_id, id_asignacion=None, activa=True):
        self.__id = id_asignacion
        self.__empleado_id = empleado_id
        self.__proyecto_id = proyecto_id
        self.__activa = bool(activa)
    @property
    def id(self): return self.__id
    @property
    def empleado_id(self): return self.__empleado_id
    @property
    def proyecto_id(self): return self.__proyecto_id
    @property
    def activa(self): return self.__activa
    def cerrar(self): self.__activa = False

class RegistroTiempo:
    def __init__(self, empleado_id, proyecto_id, horas, descripcion="", id_registro=None):
        self.__id = id_registro
        self.__empleado_id = empleado_id
        self.__proyecto_id = proyecto_id
        self.__horas = float(horas)
        self.__descripcion = descripcion.strip()
    @property
    def horas(self): return self.__horas
    @property
    def descripcion(self): return self.__descripcion
    def validar_horas(self): return 0 < self.__horas <= 24

class Usuario:
    def __init__(self, nombre_usuario, password_hash="", activo=True, id_usuario=None):
        self.__id = id_usuario
        self.__nombre_usuario = nombre_usuario.strip()
        self.__password_hash = password_hash
        self.__activo = bool(activo)
    @property
    def nombre_usuario(self): return self.__nombre_usuario
    @property
    def password_hash(self): return self.__password_hash
    @property
    def activo(self): return self.__activo
