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