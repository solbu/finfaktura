###########################################################################
#    Copyright (C) 2008 Håvard Gulldahl
#    <havard@gulldahl.no>
#
#    Lisens: GPL2
#
# $Id: faktura.py 260 2008-05-11 08:59:23Z havard.gulldahl $
#
###########################################################################

import sys
import logging
import os.path
import glob
from PyQt5 import QtCore, QtWidgets
from .ui import finfaktura_oppsett_ui


class finfakturaOppsett(finfaktura_oppsett_ui.Ui_FinFakturaOppsett):
    def __init__(self, faktura):
        self.faktura = faktura
        self.gui = QtWidgets.QDialog()
        self.setupUi(self.gui)
        self.oppsettFakturakatalogSok.clicked.connect(self.endreFakturakatalog)
        self.oppsettProgrammerVisSok.clicked.connect(self.endreProgramVis)

        self.vis()
        self.gui.show()

    def exec_(self):
        res = self.gui.exec_()
        if res == QtWidgets.QDialog.Accepted:
            logging.debug('oppdaterer')
            self.oppdater()
        return res

    def vis(self):
        logging.debug('Fakturakatalog fra db: %s', repr(self.faktura.oppsett.fakturakatalog))
        logging.debug('pdf-prog fra db: %s', repr(self.faktura.oppsett.vispdf))
        self.oppsettFakturakatalog.setText(self.faktura.oppsett.fakturakatalog)
        if self.faktura.oppsett.vispdf:
            self.oppsettProgramVisPDF.addItem('Gjeldende valg (%s)' % self.faktura.oppsett.vispdf,
                                              QtCore.QVariant(self.faktura.oppsett.vispdf))
        p = {
         'Standard PDF-program ': '/usr/bin/xdg-open',
         'kpdf (KDE3)': '/usr/bin/kpdf',
         'okular (KDE4)': '/usr/bin/okular',
         'evince (Gnome)': '/usr/bin/evince',
         'xpdf (X11)': '/usr/bin/xpdf',
         'epdfview (X11)': '/usr/bin/epdfview',
         'Acrobat reader (win)': '%SYSTEMDRIVE%\\%PROGRAMFILES%\\Adobe\\Reader*\\Reader\\AcroRd32.exe',
         'Foxit reader (win)': '%SYSTEMDRIVE%\\%PROGRAMFILES%\\Foxit Software\\Foxit Reader\\Foxit Reader.exe'
        }
        for tekst, s in p.items():
            sti = os.path.expandvars(s)
            logging.debug('sti %s, exists: %s', sti, os.path.exists(sti))
            if os.path.exists(sti):
                self.oppsettProgramVisPDF.addItem(tekst, QtCore.QVariant(sti + ' %s'))
            elif '*' in sti:
                for _sti in [_s for _s in glob.glob(sti) if os.path.exists(_s)]:
                    self.oppsettProgramVisPDF.addItem(tekst, QtCore.QVariant(_sti + ' %s'))
        if sys.platform.startswith('win'):
            self.oppsettProgramVisPDF.addItem('Vis i Utforsker (win)', QtCore.QVariant('explorer /c,%s'))

    def endreFakturakatalog(self):
        nu = self.oppsettFakturakatalog.text()
        startdir = nu
        ny = QtWidgets.QFileDialog.getExistingDirectory(
            self.gui,
            "Velg katalog fakturaene skal lagres i",
            startdir,
            QtWidgets.QFileDialog.ShowDirsOnly)
        if len(str(ny)) > 0:
            logging.debug("Setter ny fakturakataolg: %s" % ny)
            self.faktura.oppsett.fakturakatalog = str(ny)
            self.oppsettFakturakatalog.setText(str(ny))

    def endreProgramVis(self):
        (ny, _mimetype) = QtWidgets.QFileDialog.getOpenFileName(
            self.gui,
            "Velg et program å åpne PDF i",
            self.oppsettProgramVisPDF.itemData(self.oppsettProgramVisPDF.currentIndex()))
        if len(ny) > 0:
            logging.debug("Setter nytt visningsprogram: %s (%s)"
                          % (ny, _mimetype))
            self.faktura.oppsett.vispdf = ny
            self.oppsettProgramVisPDF.insertItem(0, ny, QtCore.QVariant(ny))

    def oppdater(self):
        logging.debug("Lager oppsett")
        self.faktura.oppsett.fakturakatalog = str(self.oppsettFakturakatalog.text())
        self.faktura.oppsett.vispdf = self.oppsettProgramVisPDF.itemData(
            self.oppsettProgramVisPDF.currentIndex())


# kate: indent-width 4;
