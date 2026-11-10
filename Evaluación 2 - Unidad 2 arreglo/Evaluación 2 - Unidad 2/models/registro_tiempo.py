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
