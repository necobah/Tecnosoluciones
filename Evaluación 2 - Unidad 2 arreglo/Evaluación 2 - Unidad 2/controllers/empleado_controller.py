class EmpleadoController:

    def __init__(self, db):
        self.db = db

    def obtener_empleados(self):
        return self.db.empleados()

    def agregar_empleado(
        self,
        nombre,
        correo
    ):
        if not nombre.strip():
            raise ValueError(
                "El nombre es obligatorio."
            )

        self.db.agregar_empleado(
            nombre,
            correo
        )