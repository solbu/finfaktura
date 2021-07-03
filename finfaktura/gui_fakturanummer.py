#!/usr/bin/python3
# -*- coding: utf-8 -*-
# kate: indent-width 2; encoding utf-8
###########################################################################
#    Copyright (C) 2005-2009 Håvard Gulldahl
#    <havard@gulldahl.no>
#
#    Lisens: GPL2
#
# $Id: faktura.py 260 2008-05-11 08:59:23Z havard.gulldahl $
#
###########################################################################

import sys
import os
import os.path
import glob
from time import strftime, localtime
import logging

from stat import ST_MTIME

from PyQt5 import uic, QtWidgets
#from ui import fakturanummer_ui

import sqlite3


class nummersetter(object):
  def lesDBInfo(self, databasenavn):
    if not os.path.exists(databasenavn): return False
    db = sqlite3.connect(databasenavn)

    mtime = os.stat(databasenavn)[ST_MTIME]

    cursor = db.cursor()
    try:
      cursor.execute('SELECT firmanavn FROM Firma')
      fnavn = cursor.fetchone()[0]
      cursor.execute('SELECT * FROM Ordrehode')
      fakturaer = len(cursor.fetchall())
      status = fakturaer == 0
    except sqlite3.Error:
      status = False
      firmanavn = 'Feil'

    ret = {'filnavn':databasenavn,
           'firmanavn':fnavn,
           'fakturaer': fakturaer,
           'endret':mtime,
           'status':status}
    return ret

  def settFakturanummer(self, databasenavn, fakturanummer):
    logging.debug("Skal sette fakturanr %s på db %s", fakturanummer, databasenavn)
    if not os.path.exists(databasenavn): return False
    db = sqlite3.connect(databasenavn)
    cursor = db.cursor()
    try:
      cursor.execute('SELECT * FROM Ordrehode')
      if len(cursor.fetchall()) > 0:
        raise Exception('Det er allerede laget fakturaer i denne databasen. Kan ikke sette fakturanummer.')
      cursor.execute('INSERT INTO Kunde (ID, navn, slettet) VALUES (1, "Tom kunde", 1)')
      cursor.execute('INSERT INTO Ordrehode (ID, tekst, kansellert, kundeID, ordredato, forfall) VALUES (?, "Tom faktura", 1, 1, 1, 1)', (fakturanummer,))
      db.commit()
      db.close()
      return True
    except sqlite3.Error:
      raise


class nummersettergui(object):
  def __init__(self):
    self.help = nummersetter()
    p = os.path.join(os.path.dirname(__file__), 'ui/fakturanummer.ui')
    self.gui = uic.loadUi(p)
    self.gui.databasenavn.activated.connect(self.slotDatabaseValgt)
    self.gui.settFakturanummer.clicked.connect(self.slotSettFakturanummer)
    self.gui.show()
    self.gui.databasenavn.addItems(list(self.listDatabaser()))
    self.visDatabaseStatus()

  def listDatabaser(self):
    if os.path.exists(os.getenv('FAKTURADB', '')):
      yield os.getenv('FAKTURADB')
    for d in (os.path.join(os.getenv('HOME', ''), '.finfaktura'),
              os.path.join(os.getenv('HOME', ''), 'finfaktura'),
              os.getenv('FAKTURADIR'),
              '.'):
      if not d: continue
      if not os.path.exists(d): continue
      for f in glob.glob(os.path.join(d, '*.db')):
        yield f
    yield '...'

  def slotDatabaseValgt(self, i):
    logging.debug('valgte databasenr: %s', i)
    filename = self.gui.databasenavn.currentText()
    logging.debug('valgte database: %s', filename)
    if filename == '...':
      (f, _) = self.velgDatabase()  # ignorer mimetype
      self.gui.databasenavn.insertItem(-1, f)
      filename = f
    self.visDatabaseStatus()

  def visDatabaseStatus(self):
    status = self.help.lesDBInfo(str(self.gui.databasenavn.currentText()))
    logging.debug('status:%s', status)
    if not status:
      return False
    self.gui.detaljerFilnavn.setText(status['filnavn'])
    self.gui.detaljerFirmanavn.setText(status['firmanavn'])
    self.gui.detaljerFakturaer.setText(str(status['fakturaer']))
    self.gui.detaljerEndretDato.setText(strftime('%Y-%m-%d %H:%M:%S', localtime(status['endret'])))
    self.gui.detaljerStatus.setText({True:'<b>Klar til å endres</b>', False:'<b>Kan ikke endres</b>'}[status['status']])
    self.gui.handlingsBoks.setEnabled(status['status'])

  def velgDatabase(self):
    f = QtWidgets.QFileDialog.getOpenFileName(self.gui,
                                          'Velg database',
                                          os.getenv('HOME', '.'),
                                          "Databasefil (*.db)")
    logging.debug('valgte fil: %s', f)
    return f

  def slotSettFakturanummer(self):
    fnr = self.gui.fakturanummer.value()
    logging.debug('Frste fakturanummer skal være %s', repr(fnr))
    if fnr < 1:
      QtWidgets.QMessageBox.critical(self.gui, "Feil fakturanummer", "Du må sette første fakturanummer (nummeret du ønsker at din første faktura skal få)")
      return False
    click = QtWidgets.QMessageBox.warning(self.gui,
                                     "Sette fakturanummer?",
                                     "Advarsel! \nDu er nå i ferd med å endre fakturadatabasen, slik at neste faktura får løpenummer %s. Dette kan ikke endres senere! \n\nEr du sikker? (Hvis du er i tvil, velg 'Nei/No')" % fnr,
                                     QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                     QtWidgets.QMessageBox.No)
    logging.debug('vil gjøre %s', click)
    if click == QtWidgets.QMessageBox.Yes:
      logging.debug('ja')
      if self.help.settFakturanummer(str(self.gui.databasenavn.currentText()), fnr-1):
        QtWidgets.QMessageBox.information(self.gui, "Fakturanummer endret", "Endret fakturanummer. Nå får neste faktura nummer %s" % fnr)

if __name__ == '__main__':
  if '-d' in sys.argv:
    logging.basicConfig(level=logging.DEBUG)
  a = QtWidgets.QApplication(sys.argv)
  p = nummersettergui()
  a.exec_()
