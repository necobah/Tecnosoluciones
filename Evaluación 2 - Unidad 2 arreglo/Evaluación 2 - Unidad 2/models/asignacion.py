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