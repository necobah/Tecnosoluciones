def crear_proyecto(
    self,
    nombre,
    descripcion
):

    if not nombre.strip():
        raise ValueError(
            "Debe ingresar un nombre."
        )

    self.db.crear_proyecto(
        nombre,
        descripcion
    )