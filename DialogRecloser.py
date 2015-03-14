# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'DialogRecloser.ui'
#
# Created: Sun Feb  8 22:33:29 2015
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui
import sys
class RecloserDialog(QtGui.QWidget):

    def __init__(self, item):
        super(RecloserDialog, self).__init__()
        self.dialog = QtGui.QDialog(self)
        self.item = item
        self.setupUi(self.dialog)
        self.dialog.exec_()

    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(380, 210)
        #Define o tamanho da caixa dialogo 
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(0, 170, 341, 32))
        #Define o tamanho do layout dos botões do dialogo
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        #self.apply = QtGui.QDialogButtonBox.Apply
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok|QtGui.QDialogButtonBox.Save)
        self.buttonBox.setObjectName("buttonBox")
        # self.buttonBox.clicked.connect(self.update_values)
        print self.buttonBox.buttons
        self.formLayoutWidget = QtGui.QWidget(Dialog)
        self.formLayoutWidget.setGeometry(QtCore.QRect(10, 10, 350, 150))
        #Define a localização do layout das propriedades (coordenada x do ponto, coordenada y do ponto, dimensão em x, dimensão em y)
        self.formLayoutWidget.setObjectName("formLayoutWidget")
        self.formLayout = QtGui.QFormLayout(self.formLayoutWidget)
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.formLayout.setObjectName("formLayout")

        # Definição da COMBOBOX
        self.testeLabel = QtGui.QLabel(self.formLayoutWidget)
        self.testeLabel.setObjectName("testeLabel")
        self.formLayout.setWidget(4, QtGui.QFormLayout.LabelRole, self.testeLabel)
        self.testeLineEdit = QtGui.QComboBox(self.formLayoutWidget)
        self.testeLineEdit.setObjectName("testeEdit")
        print self.item.dict_prop.keys()
        self.testeLineEdit.insertItem(0,'Custom')
        self.testeLineEdit.addItems(self.item.dict_prop.keys())
        self.formLayout.setWidget(4, QtGui.QFormLayout.FieldRole, self.testeLineEdit)
        self.testeLineEdit.currentIndexChanged.connect(self.update_values)


        #definição da propriedade NOME
        self.identificaOLabel = QtGui.QLabel(self.formLayoutWidget)
        self.identificaOLabel.setObjectName("identificaOLabel")
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.identificaOLabel)
        self.identificaOLineEdit = QtGui.QLineEdit(self.formLayoutWidget)
        self.identificaOLineEdit.setObjectName("identificaOLineEdit")
        self.identificaOLineEdit.setText(self.item.chave.nome)
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.identificaOLineEdit)


        #definição da propriedade CORRENTE NOMINAL
        self.correnteNominalLabel = QtGui.QLabel(self.formLayoutWidget)
        self.correnteNominalLabel.setObjectName("correnteNominalLabel")
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.correnteNominalLabel)
        self.correnteNominalLineEdit = QtGui.QLineEdit(self.formLayoutWidget)
        self.correnteNominalLineEdit.setObjectName("correnteNominalLineEdit")
        self.correnteNominalLineEdit.setText(str(self.item.chave.ratedCurrent))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.correnteNominalLineEdit)
        self.correnteNominalLineEdit.textEdited.connect(self.custom)


        #definição da propriedade CAPACIDADE DE INTERRUPÇÃO
        self.capacidadeDeInterrupOLabel = QtGui.QLabel(self.formLayoutWidget)
        self.capacidadeDeInterrupOLabel.setObjectName("capacidadeDeInterrupOLabel")
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.capacidadeDeInterrupOLabel)
        self.capacidadeDeInterrupOLineEdit = QtGui.QLineEdit(self.formLayoutWidget)
        self.capacidadeDeInterrupOLineEdit.setObjectName("capacidadeDeInterrupOLineEdit")
        self.capacidadeDeInterrupOLineEdit.setText(str(self.item.chave.breakingCapacity))
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.capacidadeDeInterrupOLineEdit)
        self.capacidadeDeInterrupOLineEdit.textEdited.connect(self.custom)


        #definição da propriedade Nº DE SEQUENCIA DE RELIGAMENTO
        self.nDeSequNciasDeReligamentoLabel = QtGui.QLabel(self.formLayoutWidget)
        self.nDeSequNciasDeReligamentoLabel.setObjectName("nDeSequNciasDeReligamentoLabel")
        self.formLayout.setWidget(3, QtGui.QFormLayout.LabelRole, self.nDeSequNciasDeReligamentoLabel)
        self.nDeSequNciasDeReligamentoLineEdit = QtGui.QLineEdit(self.formLayoutWidget)
        self.nDeSequNciasDeReligamentoLineEdit.setObjectName("nDeSequNciasDeReligamentoLineEdit")
        self.nDeSequNciasDeReligamentoLineEdit.setText(str(self.item.chave.recloseSequences))
        self.formLayout.setWidget(3, QtGui.QFormLayout.FieldRole, self.nDeSequNciasDeReligamentoLineEdit)
        self.nDeSequNciasDeReligamentoLineEdit.textEdited.connect(self.custom)

        lista_comp = [int(self.capacidadeDeInterrupOLineEdit.text()), int(self.correnteNominalLineEdit.text()), int(self.nDeSequNciasDeReligamentoLineEdit.text())]
        print lista_comp

        # i = 0
        # for value in self.item.dict_prop[self.testeLineEdit.currentText()].values():
        #     if value ==

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)


    def update_values(self,button):

        if self.testeLineEdit.currentIndex == 0:
            self.correnteNominalLineEdit.setText(str(self.item.custom_dict['Corrente Nominal']))
            self.capacidadeDeInterrupOLineEdit.setText(str(self.item.custom_dict['Corrente Nominal']))
            self.nDeSequNciasDeReligamentoLineEdit.setText(str(self.item.custom_dict['Corrente Nominal']))

        self.correnteNominalLineEdit.setText(str(self.item.dict_prop[self.testeLineEdit.currentText()]['Corrente Nominal']))
        self.capacidadeDeInterrupOLineEdit.setText(str(self.item.dict_prop[self.testeLineEdit.currentText()]['Capacidade de Interrupcao']))
        self.nDeSequNciasDeReligamentoLineEdit.setText(str(self.item.dict_prop[self.testeLineEdit.currentText()]['Sequencia']))

    def custom(self):
        self.testeLineEdit.setCurrentIndex(0)



    def teste(self):
        print "teste"


    def retranslateUi(self, Dialog):

        #Tradução dos nomes dados aos objetos para os nomes gráficos do programa
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Religador - Propriedades", None, QtGui.QApplication.UnicodeUTF8))
        self.identificaOLabel.setText(QtGui.QApplication.translate("Dialog", "Identificação:", None, QtGui.QApplication.UnicodeUTF8))
        self.correnteNominalLabel.setText(QtGui.QApplication.translate("Dialog", "Corrente Nominal (A): ", None, QtGui.QApplication.UnicodeUTF8))
        self.capacidadeDeInterrupOLabel.setText(QtGui.QApplication.translate("Dialog", "Capacidade de Interrupção (kA):", None, QtGui.QApplication.UnicodeUTF8))
        self.nDeSequNciasDeReligamentoLabel.setText(QtGui.QApplication.translate("Dialog", "Nº de Sequências de Religamento:", None, QtGui.QApplication.UnicodeUTF8))
        self.testeLabel.setText(QtGui.QApplication.translate("Dialog", "Fabricante:", None, QtGui.QApplication.UnicodeUTF8))

    if __name__ == '__main__':
        app = QtGui.QApplication(sys.argv)
        dialogReligador = RecloserDialog()
        sys.exit(app.exec_())