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