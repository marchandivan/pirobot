from app import App
import argparse
import sys

from PyQt5.QtWidgets import QApplication

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Start robot')
    parser.add_argument('--host', type=str, help='Server host name')
    args = parser.parse_args()

    app = QApplication(sys.argv)

    a = App(hostname=args.host)
    a.show()
    sys.exit(app.exec_())