#!/usr/bin/env python3
# Argo: Another Robocopy Gui Organiser
# Provides a GUI interface to Microsoft Window's 'robocopy' utility.
# Copyright (C) 2017 Fred Barclay <BugsAteFred@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from os.path import expanduser
import sys
import subprocess
import urllib3
from PyQt5 import QtWidgets
from argoUi import Ui_MainWindow

class Gui(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.actionOpen_Log.triggered.connect(self.openLog)
        self.ui.actionQuit.triggered.connect(self.abort)
        self.ui.actionCheckUp.triggered.connect(self.checkUp)
        self.ui.actionAbout.triggered.connect(self.About)
        self.ui.actionAbout_Qt.triggered.connect(self.AboutQt)
        self.ui.pushButton_SB.clicked.connect(self.sourceBrowse)
        self.ui.pushButton_DB.clicked.connect(self.destBrowse)
        self.ui.pushButton_OK.clicked.connect(self.backUp)
        self.ui.pushButton_FilesX.clicked.connect(self.excludeFiles)
        self.ui.pushButton_FoldersX.clicked.connect(self.excludeFolders)
        self.ui.pushButton_Abort.clicked.connect(self.abort)

        self.log = expanduser('~')+'\Argo.log'

        self.options = []
        self.filesX = []
        self.foldersX = []
        self.filetypesX = []
        self.source = 0
        self.dest = 0
        self.shutdown = 0
        self.version = '0.0.0'


    def openLog(self):
        subprocess.call(['notepad', self.log])


    def abort(self):
        sys.exit(0)


    def checkUp(self):
        http = urllib3.PoolManager()
        out = http.request('GET', 'https://gitlab.com/Fred-Barclay/Argo/tags')
        print(out.status)
        if out.status != 200:
            print ('Cannot connect to the update server at this time.')
            return
        data = str(out.data)
        index = data.find('Version')
        ver = data[index + 8] + data[index + 9] + data[index + 10] + data[index + 11] + data[index + 12]
        if ver > self.version:
            print('There is a new version available!')
        elif ver == self.version:
            print('You have the latest available version!')


    def About(self):
        '''Brief description of the program.'''
        title = 'About'
        msg =('\nARGO:'
            '\nAnother Robocopy Gui Organiser\n'
            '\nCopyright (C) 2017 Fred Barclay\n'
            '\nLicensed under the GPL v3 or (at your option) any later version.\n')
        QtWidgets.QMessageBox.about(self, title, msg)


    def AboutQt(self):
        '''Description of Qt (useful for debugging).'''
        QtWidgets.QMessageBox.aboutQt(self)

    def sourceBrowse(self):
        '''Choose the backup source (the directory to be backed up)'''
        self.source = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Backup Source")
        self.source = str(self.source)
        self.ui.text_Source.clear()
        self.ui.text_Source.append(self.source)

    def destBrowse(self):
        '''Choose the destination.'''
        self.dest = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Backup Destination")
        self.dest = str(self.dest)
        self.ui.text_Dest.clear()
        self.ui.text_Dest.append(self.dest)

    def checkOptions(self):
        '''Get options from tickboxes.'''
        if self.ui.checkBox_Mir.isChecked() == True:
            self.options.append('/mir')
        if self.ui.checkBox_Verb.isChecked() == True:
            pass
        if self.ui.checkBox_Log.isChecked() == True:
            self.options.append('/log+:'+self.log)
        if self.ui.checkBox_Shutdown.isChecked() == True:
            self.shutdown = 1
        if self.ui.checkBox_Skip.isChecked() == True:
            self.options.append('/r:0')
            self.options.append('/w:0')


    def excludeFiles(self):
        '''Exclude individual files from being backed up.'''
        filename = str(QtWidgets.QFileDialog.getOpenFileName(self, 'Select File')[0])
        self.filesX.append(filename)
        self.ui.textBrowser_FilesX.append(filename)

    def excludeFolders(self):
        '''Exclude individual folders from being backed up.'''
        foldername = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Folder"))
        self.foldersX.append(foldername)
        self.ui.textBrowser_FoldersX.append(foldername)

    def backUp(self):
        '''Main backup function.'''
        # Get runtime options
        self.checkOptions()

        XFiles = []
        XFolders = []
        XFileType = []
        # Setup for excluding files
        if len(self.filesX) != 0 and self.filesX != ['']:
            for file in self.filesX:
                XFiles.append('/xf')
                XFiles.append(file)
        # Setup for excluding folders
        if len(self.foldersX) != 0 and self.foldersX != ['']:
            for folder in self.foldersX:
                XFolders.append('/xd')
                XFolders.append(folder)
        # Setup for excluding file types (like .mp4)
        typeX = self.ui.textEdit_FileTypesX.toPlainText().split(',')
        print(typeX)
        if len(typeX) != 0 and typeX != ['']:
            for type in typeX:
                XFileType.append('/xf ')
                XFileType.append(type)

        # Exclude files over a certain size
        maxSize = str(self.ui.plainTextEdit_FSize.toPlainText())
        if not maxSize == '':
            max_cmd = ['/max:'+maxSize]
        else:
            max_cmd = []

        print(XFiles)
        print(XFolders)
        print(XFileType)

        # Main command
        base_cmd = ['robocopy'] + [self.source] + [self.dest]
        # Options
        opt_cmd = self.options
        # All exclusions
        ex_cmd = XFiles + XFolders + XFileType

        #Final command
        cmd = base_cmd + opt_cmd + ex_cmd + max_cmd

        print(cmd)

        subprocess.call(cmd)

        # Shutdown in 15 seconds
        if self.shutdown == 1:
            subprocess.call(['shutdown', '/s', '/t', '15'])


def main():
    app=QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication(sys.argv)
    ex1 = Gui()
    ex1.setWindowTitle('Argo')
    ex1.raise_()
    ex1.show()
    ex1.activateWindow()
    app.exec_()
    sys.exit(0)


if __name__ == "__main__":
    main()
