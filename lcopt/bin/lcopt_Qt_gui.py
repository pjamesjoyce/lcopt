from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtPrintSupport import *

import webbrowser

import os
import sys

from lcopt import *
from lcopt.utils import find_port

import threading

from pathlib import Path

ROOT_HOST = "127.0.0.1"
ROOT_URL = "http://" + ROOT_HOST + ":{}"

image_path = os.path.join(Path(os.path.dirname(os.path.realpath(__file__))).parent, 'assets', 'gui_images')


class ModelWebView(QWebEngineView):

    def __init__(self):
        super(ModelWebView, self).__init__()

        self.model = None


class OpenForm(QDialog):

    def __init__(self, parent=None):
        super(OpenForm, self).__init__(parent)

        self.setWindowTitle("Create a new model")
        self.setModal(True)

        self.model_name = QLineEdit("Name of model")
        self.button = QPushButton("OK")

        layout = QVBoxLayout()
        layout.addWidget(self.model_name)
        layout.addWidget(self.button)

        self.setLayout(layout)

        self.button.clicked.connect(self.ok_create)

    def ok_create(self):
        print("Creating a new model called {}".format(self.model_name.text()))

        self.accept()

        return self.model_name.text()



class AboutDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(AboutDialog, self).__init__(*args, **kwargs)

        QBtn = QDialogButtonBox.Ok  # No cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout = QVBoxLayout()

        title = QLabel("Lcopt")
        font = title.font()
        font.setPointSize(20)
        title.setFont(font)

        layout.addWidget(title)

        logo = QLabel()
        logo.setPixmap(QPixmap(os.path.join(image_path, 'lcopt_icon2.png')))
        layout.addWidget(logo)

        layout.addWidget(QLabel("Version 0.4.2-dev"))
        layout.addWidget(QLabel("Copyright 2018 P. James Joyce"))

        for i in range(0, layout.count()):
            layout.itemAt(i).setAlignment(Qt.AlignHCenter)

        layout.addWidget(self.buttonBox)

        self.setLayout(layout)


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        #self.tabs.tabBarDoubleClicked.connect(self.tab_open_doubleclick)
        #self.tabs.currentChanged.connect(self.current_tab_changed)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)

        self.setCentralWidget(self.tabs)

        self.status = QStatusBar()
        self.setStatusBar(self.status)

        #navtb = QToolBar("Navigation")
        #navtb.setIconSize(QSize(16, 16))
        #self.addToolBar(navtb)


        #back_btn = QAction(QIcon(os.path.join('images', 'arrow-180.png')), "Back", self)
        #back_btn.setStatusTip("Back to previous page")
        #back_btn.triggered.connect(lambda: self.tabs.currentWidget().back())
        #navtb.addAction(back_btn)

        #next_btn = QAction(QIcon(os.path.join('images', 'arrow-000.png')), "Forward", self)
        #next_btn.setStatusTip("Forward to next page")
        #next_btn.triggered.connect(lambda: self.tabs.currentWidget().forward())
        #navtb.addAction(next_btn)

        #reload_btn = QAction(QIcon(os.path.join('images', 'arrow-circle-315.png')), "Reload", self)
        #reload_btn.setStatusTip("Reload page")
        #reload_btn.triggered.connect(lambda: self.tabs.currentWidget().reload())
        #navtb.addAction(reload_btn)

        #home_btn = QAction(QIcon(os.path.join('images', 'home.png')), "Home", self)
        #home_btn.setStatusTip("Go home")
        #home_btn.triggered.connect(self.navigate_home)
        #navtb.addAction(home_btn)

        #navtb.addSeparator()

        #self.httpsicon = QLabel()  # Yes, really!
        #self.httpsicon.setPixmap(QPixmap(os.path.join('images', 'lock-nossl.png')))
        #navtb.addWidget(self.httpsicon)

        #self.urlbar = QLineEdit()
        #self.urlbar.returnPressed.connect(self.navigate_to_url)
        #navtb.addWidget(self.urlbar)

        #stop_btn = QAction(QIcon(os.path.join('images', 'cross-circle.png')), "Stop", self)
        #stop_btn.setStatusTip("Stop loading current page")
        #stop_btn.triggered.connect(lambda: self.tabs.currentWidget().stop())
        #navtb.addAction(stop_btn)

        # Uncomment to disable native menubar on Mac
        # self.menuBar().setNativeMenuBar(False)

        actiontb = QToolBar("Actions")
        actiontb.setIconSize(QSize(16, 16))
        #self.addToolBarBreak()
        self.addToolBar(actiontb)

        new_action_btn = QAction(QIcon(os.path.join(image_path, 'document--plus.png')), "Create model...", self)
        new_action_btn.setStatusTip("Create model")
        new_action_btn.triggered.connect(self.new_dialog)
        actiontb.addAction(new_action_btn)

        load_action_btn = QAction(QIcon(os.path.join(image_path, 'folder-horizontal.png')), "Open model...", self)
        load_action_btn.setStatusTip("Open model file")
        load_action_btn.triggered.connect(self.open_file)
        actiontb.addAction(load_action_btn)

        save_action_btn = QAction(QIcon(os.path.join(image_path, 'disk.png')), "Save", self)
        save_action_btn.setStatusTip("Save")
        save_action_btn.triggered.connect(self.save_file)
        actiontb.addAction(save_action_btn)

        save_as_action_btn = QAction(QIcon(os.path.join(image_path, 'disk--pencil.png')), "Save As...", self)
        save_as_action_btn.setStatusTip("Save As...")
        save_as_action_btn.triggered.connect(self.save_file_as)
        actiontb.addAction(save_as_action_btn)

        file_menu = self.menuBar().addMenu("&File")

        #new_tab_action = QAction(QIcon(os.path.join('images', 'document--plus.png')), "New model...", self)
        #new_tab_action.setStatusTip("Create a new model")
        #new_tab_action.triggered.connect(lambda _: self.add_new_tab()) #check how this works
        #file_menu.addAction(new_tab_action)

        #new_model_action = QAction(QIcon(os.path.join('images', 'document--plus.png')), "New model...", self)
        #new_model_action.setStatusTip("Create a new model")
        #new_model_action.triggered.connect(self.new_dialog)  # check how this works
        #file_menu.addAction(new_model_action)

        #open_file_action = QAction(QIcon(os.path.join('images', 'disk--arrow.png')), "Open model...", self)
        #open_file_action.setStatusTip("Open from file")
        #open_file_action.triggered.connect(self.open_file)
        #file_menu.addAction(open_file_action)

        file_menu.addAction(new_action_btn)
        file_menu.addAction(load_action_btn)
        file_menu.addAction(save_action_btn)
        file_menu.addAction(save_as_action_btn)

        #save_file_action = QAction(QIcon(os.path.join('images', 'disk--pencil.png')), "Save Page As...", self)
        #save_file_action.setStatusTip("Save current page to file")
        #save_file_action.triggered.connect(self.save_file)
        #file_menu.addAction(save_file_action)

        #print_action = QAction(QIcon(os.path.join('images', 'printer.png')), "Print...", self)
        #print_action.setStatusTip("Print current page")
        #print_action.triggered.connect(self.print_page)
        #file_menu.addAction(print_action)

        help_menu = self.menuBar().addMenu("&Help")

        about_action = QAction(QIcon(os.path.join(image_path, 'question.png')), "About Lcopt", self)
        about_action.setStatusTip("Find out more about Lcopt")
        about_action.triggered.connect(self.about)
        help_menu.addAction(about_action)

        navigate_docs_action = QAction(QIcon(os.path.join(image_path, 'document--arrow.png')),
                                       "Lcopt documentation", self)
        navigate_docs_action.setStatusTip("Go to lcopt documentation")
        navigate_docs_action.triggered.connect(self.navigate_docs)
        help_menu.addAction(navigate_docs_action)

        navigate_github_action = QAction(QIcon(os.path.join(image_path, 'GitHub-Mark-32px.png')),
                                            "Lcopt Github page", self)
        navigate_github_action.setStatusTip("Go to lcopt Github page")
        navigate_github_action.triggered.connect(self.navigate_github)
        help_menu.addAction(navigate_github_action)




        #self.add_new_tab(QUrl('http://www.google.com'), 'Homepage')

        self.setGeometry(100, 100, 1400, 800)

        self.show()

        self.setWindowTitle("Lcopt")
        self.setWindowIcon(QIcon(os.path.join(image_path, 'lcopt_icon.png')))

    def download_request(self, item):

        filename, _ = QFileDialog.getSaveFileName(self, "Save As", item.path(),
                                                  "All files (*.*)")
        item.setPath(filename)
        item.accept()

    def info(self):
        this_model = self.tabs.currentWidget().model
        print("model name: {}\ndatabase:{}".format(this_model.name, this_model.database['items']))

    def add_new_tab(self, qurl=None, label="Blank"):

        if qurl is None:
            qurl = QUrl('')

        browser = ModelWebView() #QWebEngineView()

        profile = QWebEngineProfile('test_profile', browser)
        profile.downloadRequested.connect(self.download_request)
        webpage = QWebEnginePage(profile, browser)
        browser.setPage(webpage)
        browser.setUrl(qurl)
        i = self.tabs.addTab(browser, label)

        self.tabs.setCurrentIndex(i)

        # More difficult! We only want to update the url when it's from the
        # correct tab
        #browser.urlChanged.connect(lambda qurl, browser=browser:
        #                           self.update_urlbar(qurl, browser))

        #browser.loadFinished.connect(lambda _, i=i, browser=browser:
        #                             self.tabs.setTabText(i, browser.page().title()))

        return i

    #def tab_open_doubleclick(self, i):
    #    if i == -1:  # No tab under the click
    #        self.add_new_tab()

    #def current_tab_changed(self, i):
    #    qurl = self.tabs.currentWidget().url()
    #    #self.update_urlbar(qurl, self.tabs.currentWidget())
    #    self.update_title(self.tabs.currentWidget())

    def close_current_tab(self, i):
        self.tabs.setCurrentIndex(i)
        port = self.tabs.currentWidget().url().port()
        if self.tabs.currentWidget().url().host() == ROOT_HOST:
            self.tabs.currentWidget().setUrl(QUrl(ROOT_URL.format(port) + "/shutdown"))
        #if self.tabs.count() < 2:
        #    return

        self.tabs.removeTab(i)

    def update_title(self, browser):
        if browser != self.tabs.currentWidget():
            # If this signal is not from the current tab, ignore
            return

        title = self.tabs.currentWidget().page().title()
        self.setWindowTitle("%s - Mozarella Ashbadger" % title)

    def navigate_github(self):
        webbrowser.open("https://www.github.com/pjamesjoyce/lcopt")

    def navigate_docs(self):
        webbrowser.open("http://lcopt.rtfd.io")

    def about(self):
        dlg = AboutDialog()
        dlg.exec_()

    def new_dialog(self):
        nd = OpenForm(self)
        if nd.exec_():
            self.create_model(nd.model_name.text())

    def create_model(self, model_name):
        gui_model = LcoptModel(model_name)
        self.launch_to_browser(gui_model)

    def launch_to_browser(self, gui_model):
        flask_app = FlaskSandbox(gui_model)
        port = find_port()

        t = threading.Thread(target=flask_app.run, kwargs={'open_browser': False, 'port': port})
        t.daemon = True
        t.start()

        i = self.add_new_tab()
        self.tabs.currentWidget().setUrl(QUrl(ROOT_URL.format(port)))
        self.tabs.currentWidget().model = gui_model
        print("the model is called {}".format(self.tabs.currentWidget().model.name))
        self.tabs.setTabText(i, gui_model.name)

    def open_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open file", storage.model_dir,
                                                  "Lcopt models (*.lcopt);;"
                                                  "All files (*.*)")

        if filename:
            gui_model = LcoptModel(load=filename)
            self.launch_to_browser(gui_model)

    def save_file(self):
        gui_model = self.tabs.currentWidget().model
        gui_model.save()

    def save_file_as(self):
        gui_model = self.tabs.currentWidget().model
        print(gui_model.save_option)

        if gui_model.save_option == 'curdir':
            model_path = os.path.join(
                os.getcwd(),
                '{}.lcopt'.format(gui_model.name)
            )
        else: # default to appdir
            model_path = os.path.join(
                storage.model_dir,
                '{}.lcopt'.format(gui_model.name)
            )

        filename, _ = QFileDialog.getSaveFileName(self, "Save Page As", model_path,
                                                  "Lcopt model (*.lcopt);;"
                                                  )

        if filename:
            gui_model.save_path = filename
            gui_model.save()

#    def print_page(self):
#        dlg = QPrintPreviewDialog()
#        dlg.paintRequested.connect(self.browser.print_)
#        dlg.exec_()

#   def navigate_home(self):
#       self.tabs.currentWidget().setUrl(QUrl("http://www.google.com"))

#    def navigate_to_url(self):  # Does not receive the Url
#        q = QUrl(self.urlbar.text())
#        if q.scheme() == "":
#            q.setScheme("http")

#        self.tabs.currentWidget().setUrl(q)

#    def update_urlbar(self, q, browser=None):

#        if browser != self.tabs.currentWidget():
#            # If this signal is not from the current tab, ignore
#            return

#        if q.scheme() == 'https':
#            # Secure padlock icon
#            self.httpsicon.setPixmap(QPixmap(os.path.join('images', 'lock-ssl.png')))

#        else:
#            # Insecure padlock icon
#            self.httpsicon.setPixmap(QPixmap(os.path.join('images', 'lock-nossl.png')))

#        self.urlbar.setText(q.toString())
#        self.urlbar.setCursorPosition(0)


def main():

    app = QApplication(sys.argv)
    app.setApplicationName("Lcopt")
    app.setOrganizationName("Lcopt")
    app.setOrganizationDomain("lcopt.org")

    window = MainWindow()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()