def registrar_horas(
    self,
    empleado_id,
    proyecto_id,
    horas,
    descripcion
):

    if horas <= 0:

        raise ValueError(
            "Las horas deben ser mayores a cero."
        )

    self.db.registrar_horas(
        empleado_id,
        proyecto_id,
        horas,
        descripcion
    )