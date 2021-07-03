###########################################################################
#    Copyright (C) 2008 Håvard Gulldahl
#    <havard@gulldahl.no>
#
#    Lisens: GPL2
#
# $Id: faktura.py 260 2008-05-11 08:59:23Z havard.gulldahl $
#
###########################################################################

import sys, os, logging, mimetypes, stat
from PyQt5 import QtWidgets
from .ui import sendepost_ui


class sendEpost(sendepost_ui.Ui_sendEpost):
    _vedlegg = []
    def __init__(self, parent, ordre):
        self.parent = parent
        self.gui = QtWidgets.QDialog()
        self.setupUi(self.gui)
        self.tittel.setText('Sender faktura til %s <b>&lt;%s</b>&gt;' % (ordre.kunde.navn, ordre.kunde.epost))
        self.tekst.setPlainText('Vedlagt følger epostfaktura #%i:\n%s\n\n-- \n%s\n%s' % (ordre.ID, ordre.tekst,  ordre.firma, ordre.firma.vilkar))
        self.leggVedFil.clicked.connect(self.lagVedlegg)
        self.vedlegg.hide()
        self.gui.show()

    def lagVedlegg(self):
        f = QtWidgets.QFileDialog.getOpenFileName(self.gui,
            "Velg en fil å legge ved",
            os.getenv('HOME', '.'))
        if len(f) > 0:
            self.vedlegg.show()
            ff = str(f).encode(sys.getfilesystemencoding())
            logging.debug("Legger ved fil: %s", ff)
            self._vedlegg.append(ff)
            mime = mimetypes.guess_type(ff)
            mtype = ''
            if mime is not None:
                mtype = mime[0]
            size = os.stat(ff)[stat.ST_SIZE]
            i = QtWidgets.QTreeWidgetItem([f, mtype, prettySize(size)])
            self.vedlegg.addTopLevelItem(i)

    def exec_(self):
        res = self.gui.exec_()
        return res, str(self.tekst.toPlainText())


def prettySize(size):
    suffixes = [("B",2**10), ("K",2**20), ("M",2**30), ("G",2**40), ("T",2**50)]
    for suf, lim in suffixes:
        if size > lim:
            continue
        else:
            return "%s%s" % (round(size/float(lim/2**10),2), suf)

# kate: indent-width 4;
