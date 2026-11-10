import sys

from PyQt6.QtWidgets import QApplication

from database.database import BaseDatos
from views.login_view import Login


def main():
    app = QApplication(sys.argv)

    db = BaseDatos()

    ventana = Login(db)
    ventana.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()