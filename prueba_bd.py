from tempfile import TemporaryDirectory
from pathlib import Path

from database import BaseDatos

with TemporaryDirectory() as directorio:
	db=BaseDatos(Path(directorio) / "prueba.db")
	db.inicializar()
	ok,msg=db.probar_conexion()
	assert ok,msg
	try:
		db.empleados()
	except PermissionError:
		pass
	else:
		raise AssertionError("La consulta debe requerir autenticación")
	db.crear_usuario_inicial("evaluador", "ClaveSegura2026!")
	assert db.autenticar("evaluador", "ClaveSegura2026!")
	assert len(db.empleados()) >= 2
	assert sum(e["correo"] == "gabrielle@ecotech.cl" for e in db.empleados()) == 1
	assert sum(e["correo"] == "javiera@ecotech.cl" for e in db.empleados()) == 1
	assert len(db.proyectos()) >= 2
	print(msg)
	print("Empleados iniciales:", ", ".join(e["nombre"] for e in db.empleados()))
	print("Prueba de persistencia, autenticación y esquema: OK")
