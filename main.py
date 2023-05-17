from PyQt5 import QtCore, QtGui, QtWidgets
import os
import zipfile
import rarfile
import py7zr
import datetime
import patoolib
import shutil

class ArchiveMerger(QtWidgets.QWidget):

    output_files: dict[str, bytes] = {}
    fileList: list[str] = []
    destinationFolder: str = None

    def setFont(self,fontSize) -> QtGui.QFont:
        font = QtGui.QFont()
        font.setPointSize(fontSize)
        return font

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setEnabled(True)
        MainWindow.setFixedSize(537, 650)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.selectButton = QtWidgets.QPushButton(self.centralwidget)
        self.selectButton.setGeometry(QtCore.QRect(160, 30, 220, 50))
        self.selectButton.setFont(self.setFont(13))
        self.selectButton.setObjectName("selectButton")
        self.selectButton.clicked.connect(self.selectFiles)

        self.pathButton = QtWidgets.QPushButton(self.centralwidget)
        self.pathButton.setGeometry(QtCore.QRect(160, 190, 220, 50))
        self.pathButton.setFont(self.setFont(13))
        self.pathButton.setObjectName("pathButton")
        self.pathButton.clicked.connect(self.selectPath)

        self.selectLabel = QtWidgets.QLabel(self.centralwidget)
        self.selectLabel.setGeometry(QtCore.QRect(160, 90, 221, 16))
        self.selectLabel.setFont(self.setFont(10))
        self.selectLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.selectLabel.setObjectName("selectLabel")

        self.pathLabel = QtWidgets.QLabel(self.centralwidget)
        self.pathLabel.setGeometry(QtCore.QRect(160, 250, 221, 16))
        self.pathLabel.setFont(self.setFont(10))
        self.pathLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.pathLabel.setObjectName("pathLabel")

        self.typeLabel = QtWidgets.QLabel(self.centralwidget)
        self.typeLabel.setGeometry(QtCore.QRect(160, 370, 211, 31))
        self.typeLabel.setFont(self.setFont(13))
        self.typeLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.typeLabel.setObjectName("typeLabel")

        self.horizontalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(130, 410, 331, 80))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")

        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(5)
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.radioRAR = QtWidgets.QRadioButton(self.horizontalLayoutWidget)
        self.radioRAR.setFont(self.setFont(13))
        self.radioRAR.setChecked(True)
        self.radioRAR.setObjectName("radioRAR")
        self.horizontalLayout.addWidget(self.radioRAR)

        self.radioZIP = QtWidgets.QRadioButton(self.horizontalLayoutWidget)
        self.radioZIP.setFont(self.setFont(13))
        self.radioZIP.setObjectName("radioZIP")
        self.horizontalLayout.addWidget(self.radioZIP)

        self.radio7Z = QtWidgets.QRadioButton(self.horizontalLayoutWidget)
        self.radio7Z.setFont(self.setFont(13))
        self.radio7Z.setObjectName("radio7Z")

        self.horizontalLayout.addWidget(self.radio7Z)

        self.mergeButton = QtWidgets.QPushButton(self.centralwidget)
        self.mergeButton.setGeometry(QtCore.QRect(170, 520, 211, 81))
        self.mergeButton.setFont(self.setFont(16))
        self.mergeButton.setObjectName("mergeButton")
        self.mergeButton.clicked.connect(self.mergeFiles)

        MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Archive Merger"))
        self.selectButton.setText(_translate("MainWindow", "Select files"))
        self.pathButton.setText(_translate("MainWindow", "Select destination folder"))
        self.selectLabel.setText(_translate("MainWindow", "Selected files: 0"))
        self.pathLabel.setText(_translate("MainWindow", "Path not selected"))
        self.typeLabel.setText(_translate("MainWindow", "Save as:"))
        self.radioRAR.setText(_translate("MainWindow", ".rar"))
        self.radioZIP.setText(_translate("MainWindow", ".zip"))
        self.radio7Z.setText(_translate("MainWindow", ".7z"))
        self.mergeButton.setText(_translate("MainWindow", "Merge files!"))

    def selectFiles(self):
        try:
            dialog = QtWidgets.QFileDialog()
            fileNames = dialog.getOpenFileNames(self,"Select files to merge",os.getcwd(),"Archives (*.zip *.rar *.7z)")
            self.fileList = fileNames[0]
            sum = 0
            for file in self.fileList:
                sum = sum + os.path.getsize(file)

            print(sum)

            # Modify label beneath the "select" button
            self.selectLabel.setText(f"Selected files: {len(self.fileList)}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Error when selecting files: {e}", QtWidgets.QMessageBox.Ok)

    def selectPath(self):
        try:
            dialog = QtWidgets.QFileDialog()
            self.destinationFolder = dialog.getExistingDirectory(self,"Select destination folder")

            # Modify label beneath the "path" button
            self.pathLabel.setText(f"Path selected!")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Error when selecting path: {e}", QtWidgets.QMessageBox.Ok)

    def unpackZIP(self, archivePath: str):
        with zipfile.ZipFile(archivePath) as archive:
            for filename in archive.namelist():
                with archive.open(filename) as file:
                    content = file.read()
                    if filename in self.output_files.keys():
                        self.addDuplicate(filename, content)
                        print(filename)
                    else:
                        self.output_files.update({filename: content})
                        print(filename)

    def unpackRAR(self, archivePath: str):
        with rarfile.RarFile(archivePath) as archive:
            for filename in archive.namelist():
                with archive.open(filename) as file:
                    content = file.read()
                    if filename in self.output_files.keys():
                        self.addDuplicate(filename,content)
                    else:
                        self.output_files.update({filename: content})


    def unpack7Z(self, archivePath: str):
        with py7zr.SevenZipFile(archivePath, mode='r') as archive:
            result_dict = archive.readall()
            for filename,content in result_dict.items():
                if filename in self.output_files.keys():
                    self.addDuplicate(filename,content.read())
                else:
                    self.output_files.update({filename: content.read()})

    def packZIP(self):
        output_archive = zipfile.ZipFile(f"{self.destinationFolder}{os.path.sep}merged-{datetime.datetime.today().strftime('%Y-%m-%d')}.zip","w",zipfile.ZIP_DEFLATED)
        for filename, data in self.output_files.items():
            output_archive.writestr(filename,data)
        output_archive.close()

    def packRAR(self):
        filelist = []
        folderlist = []
        for filename, data in self.output_files.items():
            if filename[-1] == "/":
                os.mkdir(filename)
                folderlist.append(filename)
            else:
                with open(filename, 'wb') as f:
                    filelist.append(filename)
                    f.write(data)

        patoolib.create_archive(f"{self.destinationFolder}{os.path.sep}merged-{datetime.datetime.today().strftime('%Y-%m-%d')}.rar", filelist, program='rar')
        for file in filelist:
            os.remove(file)

        for folder in folderlist:
            shutil.rmtree(folder, ignore_errors=True)

    def pack7Z(self):
        filelist = []
        folderlist = []
        for filename, data in self.output_files.items():
            if filename[-1] == "/":
                os.mkdir(filename)
                folderlist.append(filename)
            else:
                with open(filename, 'wb') as f:
                    filelist.append(filename)
                    f.write(data)

        with py7zr.SevenZipFile(f"{self.destinationFolder}{os.path.sep}merged-{datetime.datetime.today().strftime('%Y-%m-%d')}.7z", mode='w') as archive:
            for file in filelist:
                archive.write(file)
                os.remove(file)

        for folder in folderlist:
            shutil.rmtree(folder, ignore_errors=True)

    def addDuplicate(self,filename,content):
        counter = 0

        if filename[-1] == "/":
            pass
        else:
            base_name, extension = os.path.splitext(filename)
            while (True):
                counter = counter + 1
                filename = f"{base_name}({counter}){extension}"
                if filename in self.output_files.keys():
                    continue
                else:
                    self.output_files.update({filename: content})
                    break

    def mergeFiles(self):
        try:
            if len(self.fileList) < 1:
                QtWidgets.QMessageBox.critical(self, "Error", "No files were selected!", QtWidgets.QMessageBox.Ok)
            else:
                if not self.destinationFolder:
                    QtWidgets.QMessageBox.critical(self, "Error", "You have to select destination folder!", QtWidgets.QMessageBox.Ok)
                else:
                    for archive in self.fileList:
                        if archive.endswith(".rar"):
                            self.unpackRAR(archive)
                        elif archive.endswith(".zip"):
                            self.unpackZIP(archive)
                        elif archive.endswith(".7z"):
                            self.unpack7Z(archive)

                    print(self.output_files)

                    if self.radio7Z.isChecked():
                        self.pack7Z()
                    elif self.radioRAR.isChecked():
                        self.packRAR()
                    else:
                        self.packZIP()

                    QtWidgets.QMessageBox.information(self, "Success", f"Archives merged!:", QtWidgets.QMessageBox.Ok)
                    self.output_files = {}

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Merge failed: {e}", QtWidgets.QMessageBox.Ok)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = ArchiveMerger()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
