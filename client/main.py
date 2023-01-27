from app import App
import sys

from PyQt5.QtWidgets import QApplication

if __name__=="__main__":
    app = QApplication(sys.argv)
    a = App()
    a.show()
    sys.exit(app.exec_())