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
