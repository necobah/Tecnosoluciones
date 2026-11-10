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