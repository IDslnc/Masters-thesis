import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import DentalApp
from ui.login_window import LoginWindow
from ui.admin_window import AdminWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)

    login_window = LoginWindow()
    if login_window.exec_() == LoginWindow.Accepted:
        user = login_window.user

        if user.user_role.lower() == "администратор":
            admin_window = AdminWindow()
            admin_window.show()
        else:
            window = DentalApp(user=user)
            window.show()

        sys.exit(app.exec_())
