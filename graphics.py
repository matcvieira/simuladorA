#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PySide import QtCore, QtGui
import math
import sys
from rede import Chave
from rede import BusBarSection
from rede import Transformador
from DialogRecloser import RecloserDialog
from DialogLine import LineDialog
from DialogBarra import BarraDialog
from DialogSubstation import SubstationDialog


class Edge(QtGui.QGraphicsLineItem):
    '''
        Classe que implementa o objeto Edge que liga dois objetos Node um ao
        outro
    '''
    def __init__(self, w1, w2, edge_menu):
        '''
            Metodo inicial da classe Edge
            Recebe como parâmetros os objetos Node Inicial e Final
            Define o objeto QtCore.QLineF que define a linha que
            representa o objeto QtGui.QGraphicsLineItem
        '''
        super(Edge, self).__init__()
        self.w1 = w1
        self.w2 = w2
        self.w1.add_edge(self)  # adiciona o objeto Edge a lista de Edges do
# objeto w1
        self.w2.add_edge(self)  # adiciona o objeto Edge a lista de Edges do
# objeto w2

        self.myEdgeMenu = edge_menu
        line = QtCore.QLineF(self.w1.pos(), self.w2.pos())
        self.setLine(line)
        self.setZValue(-1)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True)
        self.isFixed = False
        self.fixFlag = False
        self.isPermanent = False
        if w1.myItemType == Node.Barra or w2.myItemType == Node.Barra:
            print "hey!"
            self.isPermanent = True
            if w1.myItemType == Node.Barra:
                w1.bar_busy = True
            if w2.myItemType == Node.Barra:
                w2.bar_busy = True

    def get_fraction(self, pos):
        deltaX = math.fabs(self.line().p2().x() - self.line().p1().x())
        deltaY = math.fabs(self.line().p2().y() - self.line().p1().y())

        dist = math.sqrt(pow(pos.x() - self.line().p1().x(), 2) + pow(pos.y() - self.line().p1().y(), 2))
        fraction = dist / self.line().length()
        print "fraction:"
        print fraction
        if 0.75 < fraction < 1:
            fraction = 0.75
        if 0.5 < fraction < 0.75:
            fraction = 0.5
        if 0.25 < fraction < 0.5:
            fraction = 0.25
        if 0 < fraction < 0.25:
            fraction = 0.25
        if self.line().p1().x() > self.line().p2().x():
            posf_x = self.line().p1().x() - fraction * deltaX
        else:
            posf_x = self.line().p1().x() + fraction * deltaX
        if self.line().p1().y() > self.line().p2().y():
            posf_y = self.line().p1().y() - fraction * deltaY
        else:
            posf_y = self.line().p1().y() + fraction * deltaY
        posf = QtCore.QPointF(posf_x, posf_y)

        return posf

    def update_position(self):
        '''
            Metodo de atualizacao da posicao do objeto edge implementado pela
            classe Edge. Sempre que um dos objetos Nodes w1 ou w2 modifica sua
            posicao este método é chamado para que o objeto edge possa
            acompanhar o movimento dos Objetos Node.
        '''
        if not self.w1 or not self.w2:
            return

        line = QtCore.QLineF(self.w1.pos(), self.w2.pos())
        length = line.length()

        if length == 0.0:
            return

        self.prepareGeometryChange()
        self.setLine(line)
        # self.update_ret()

    def set_color(self, color):
        self.setPen(QtGui.QPen(color))

    # def drawRec(self):
    #   self.ret = QtCore.QRectF(0,0,self.line().p2.x() - self.line().p1.x())
    #   self.ret.setCoords()

    def boundingRect(self):
        '''
            Metodo de definicao da borda do objeto edge implementado pela
            classe Edge.
        '''
        extra = (self.pen().width() + 100)
        p1 = self.line().p1()  # ponto inicial do objeto QtCore.QLineF
        # associado ao objeto QtGui.QGraphicsLine
        p2 = self.line().p2()  # ponto final do objeto QtCore.QLineF associado
        # ao objeto QtGui.QGraphicsLine

        rec = QtCore.QRectF(p1,
                            QtCore.QSizeF(p2.x() - p1.x(),
                                          p2.y() - p1.y())).normalized()
        rec.adjust(-extra, -extra, extra, extra)
        return rec

    def paint(self, painter, option, widget):
        '''
            Metodo de desenho do objeto edge implementado pela classe Edge
        '''
        if (self.w1.collidesWithItem(self.w2)):
            return

        # if self.w1.myItemType == Node.NoConectivo or self.w2.myItemType == Node.NoConectivo:
        #     return

        # Esta é a logica de distribuicao e alinhamento das linhas conectadas
        # ao item grafico Barra

        # Se o item self.w1 for do tipo barra deve-se alinhar o item self.w2
        if self.w1.myItemType == Node.Barra and self.w2.myItemType != Node.Subestacao:
            self.fixFlag = True
            self.w2.Fixed = True
            # se o numero de linhas conectas a barra for maior que 1 deve-se
            # proceder a logica de distribuicao e alinhamento
            if len(self.w1.edges) > 1:
                # insere a linha em seu local de distribuicao calculado pelo
                # item grafico barra
                line = QtCore.QLineF(self.mapFromItem(
                    self.w1, self.w1.rect().center().x(),
                    self.w1.edge_position(
                        self)), self.mapFromItem(
                    self.w2, self.w2.rect().center()))
                # alinha o item religador conectado ao item Barra com alinha
                # que conecta esses dois items
                self.w2.setY(self.mapFromItem(
                    self.w1, self.w1.rect().center().x(),
                    self.w1.edge_position(
                        self)).y() - 20.0)
                if self.w2.myItemType == Node.NoConectivo:
                    self.w2.setY(self.mapFromItem(
                    self.w1, self.w1.rect().center().x(),
                    self.w1.edge_position(
                        self)).y() -5)
                self.w2.fix_item()
            # se não os items são apenas conectados
            else:
                line = QtCore.QLineF(self.mapFromItem(
                    self.w1, self.w1.rect().center()), self.mapFromItem(
                    self.w2, self.w2.rect().center()))

        # Se o item self.w2 for do tipo barra deve-se alinhar o item self.w1
        elif self.w2.myItemType == Node.Barra and self.w1.myItemType != Node.Subestacao:
            self.fixFlag = True
            self.w1.Fixed = True
            # se o numero de linhas conectas a barra for maior que 1 deve-se
            # proceder a logica de distribuicao e alinhamento
            if len(self.w2.edges) > 1:
                # insere a linha em seu local de distribuicao calculado pelo
                # item grafico barra
                line = QtCore.QLineF(self.mapFromItem(
                    self.w1, self.w1.rect().center()), self.mapFromItem(
                    self.w2, self.w2.rect().center().x(),
                    self.w2.edge_position(
                        self)))
                # alinha o item religador conectado ao item Barra com alinha
                # que conecta esses dois items
                self.w1.setY(self.mapFromItem(
                    self.w2, self.w2.rect().center().x(),
                    self.w2.edge_position(
                        self)).y() - 20.0)
                self.w1.fix_item()
            # se não os items são apenas conectados
            else:
                line = QtCore.QLineF(self.mapFromItem(
                    self.w1, self.w1.rect().center()), self.mapFromItem(
                    self.w2, self.w2.rect().center()))
        # se nenhum dos items for do tipo Barra então os items são apenas
        # conectados
        else:
            line = QtCore.QLineF(self.mapFromItem(
                self.w1, self.w1.rect().center()), self.mapFromItem(
                self.w2, self.w2.rect().center()))

        # line = QtCore.QLineF(self.mapFromItem(
            # self.w1, self.w1.rect().center()) , self.mapFromItem(
            # self.w2, self.w2.rect().center()))

        self.setLine(line)
        if self.fixFlag:
            self.isFixed = True

        painter.setPen(QtGui.QPen(QtCore.Qt.black,  # QPen Brush
                                                    2,  # QPen width
                                                    QtCore.Qt.SolidLine,
                                                    # QPen style
                                                    QtCore.Qt.SquareCap,
                                                    # QPen cap style
                                                    QtCore.Qt.RoundJoin)
                       # QPen join style
                       )
        painter.setBrush(QtCore.Qt.black)
        painter.drawLine(self.line())

        if self.isSelected():
            painter.setPen(QtGui.QPen(QtCore.Qt.red, 2, QtCore.Qt.DashLine))
            my_line = QtCore.QLineF(line)
            my_line.translate(0, 4.0)
            painter.drawLine(my_line)
            my_line.translate(0, -8.0)
            painter.drawLine(my_line)

    def mousePressEvent(self, mouse_event):
        self.setSelected(True)
        super(Edge, self).mousePressEvent(mouse_event)
        return

    def contextMenuEvent(self, event):
        self.scene().clearSelection()
        self.setSelected(True)
        self.myEdgeMenu.exec_(event.screenPos() + QtCore.QPointF(20,20))


class Text(QtGui.QGraphicsTextItem):
    '''
        Classe que implementa o objeto Text Generico
    '''

    selectedChange = QtCore.Signal(QtGui.QGraphicsItem)
    lostFocus = QtCore.Signal(QtGui.QGraphicsTextItem)

    def __init__(self, text, parent=None, scene=None):

        super(Text, self).__init__(parent, scene)
        self.setPlainText(text)
        self.setZValue(100)
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, False)
        #self.setTextInteractionFlags(
            #QtCore.Qt.TextInteractionFlag.TextEditorInteraction)
        # self.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextSelectableByMouse)
        # self.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextSelectableByKeyboard)

    #def mouseDoubleClickEvent(self, event):
       # '''
          #  Metodo que trata o evento de duplo click no item grafico texto
         #   para edicao de seu conteudo
        #'''
     #   if self.textInteractionFlags() == QtCore.Qt.NoTextInteraction:
       #     self.setTextInteractionFlags(QtCore.Qt.TextEditorInteraction)
      #  super(Text, self).mouseDoubleClickEvent(event)

    def itemChange(self, change, value):
        if change == QtGui.QGraphicsItem.ItemSelectedChange:
            self.selectedChange.emit(self)
        return value

    def focusOutEvent(self, event):
        # self.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.lostFocus.emit(self)
        super(Text, self).focusOutEvent(event)


class Node(QtGui.QGraphicsRectItem):
    '''
       Classe que implementa o objeto Node Genérico.
    '''
    # tipos de itens possiveis
    Subestacao, Religador, Barra, Agent, NoDeCarga, NoConectivo = range(6)

    def __init__(self, item_type, node_menu, parent=None, scene=None):
        '''
            Método inicial da classe Node
            Recebe como parâmetros os objetos myItemType que define o tipo de
            Node desejado e x, y a posicao do objeto Node. Define o objeto
            QtCore.QRectF que define o retangulo que representa o objeto
            QtGui.QGraphicsRectItem.
        '''
        super(Node, self).__init__()
        self.id = id(self)
        self.edges = {}
        self.l0 = None
        self.edges_no_sub = {}
        self.myItemType = item_type
        self.Fixed = False
        self.edge_counter = 0
        self.bar_busy = False
        self.mean_pos = None
        self.semiFixed = False
        self.dict_prop = {}
        # caso o item a ser inserido seja do tipo subestacao
        if self.myItemType == self.Subestacao:
            rect = QtCore.QRectF(0, 0, 50.0, 50.0)
            # definine e ajusta a posicao do label do item grafico
            self.substation = Transformador("Identificador", 0.0, 0.0, 0.0, complex(0,0))
            self.text = Text('Subestacao', self, self.scene())
            self.text.setPos(self.mapFromItem(self.text, 0, rect.height()))
        # caso o item a ser inserido seja do tipo religador
        elif self.myItemType == self.Religador:
            rect = QtCore.QRectF(0, 0, 40.0, 40.0)
            # Cria o objeto abstrato chave referente ao religador
            self.chave = Chave("Identificador")
            # definine e ajusta a posicao do label do item grafico
            self.text = Text('Religador', self, self.scene())
            self.text.setPos(self.mapFromItem(self.text, 0, rect.height()))
            self.create_dict(10,15,4,'ABB')
            self.create_dict(12,10,3,'SEL')
            self.create_dict(9,11,2,'BOSCH')
        # caso o item a ser inserido seja do tipo barra
        elif self.myItemType == self.Barra:
            rect = QtCore.QRectF(0, 0, 10.0, 100.0)
            self.barra = BusBarSection("Identificador")
            # definine e ajusta a posicao do label do item grafico
            self.text = Text('Barra', self, self.scene())
            self.text.setPos(self.mapFromItem(self.text, 0, rect.height()))
        # caso o item a ser inserido seja do tipo agent
        elif self.myItemType == self.Agent:
            rect = QtCore.QRectF(0, 0, 50.0, 50.0)
            # definine e ajusta a posicao do label do item grafico
            self.text = Text('Agente', self, self.scene())
            self.text.setPos(self.mapFromItem(self.text, 0, rect.height()))
        # caso o item a ser inserido seja do tipo nó conectivo
        elif self.myItemType == self.NoConectivo:
            rect = QtCore.QRectF(0, 0, 7, 7)

        elif self.myItemType == self.NoDeCarga:
            rect = QtCore.QRectF(0, 0, 12, 12)
            self.text = Text('Carga', self, self.scene())
            self.text.setPos(self.mapFromItem(self.text, 0, rect.height()))

        self.setRect(rect)
        self.myNodeMenu = node_menu

        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QtGui.QGraphicsItem.ItemIsFocusable, True)
        self.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setZValue(0)


    def create_dict(self, corrente, capacidade, num_rel, padrao):
        prop = {'Corrente Nominal': corrente, 'Capacidade de Interrupcao': capacidade, 'Sequencia':num_rel}
        self.dict_prop[padrao] = prop

    def fix_item(self):
        self.Fixed = True

    def update_count(self):
        self.edge_counter = len(self.edges)
    def remove_edges(self):
        '''
            Metodo de remocao de todos objetos edge associados ao objeto node
        '''
        deleted_list = []
        for edge in self.edges:
            deleted_list.append(edge)
            # self.scene().removeItem(edge.GhostRetItem)
            self.scene().removeItem(edge)

        for edge in deleted_list:
            if edge.w1 is not None:
                edge.w1.remove_edge(edge)
            if edge.w2 is not None:
                edge.w2.remove_edge(edge)

        self.edges.clear()
        self.edges_no_sub.clear()
        self.update_count()

    def remove_edge(self, edge):
        scene = self.scene()
        self.edges.pop(edge)
        # scene.removeItem(edge)
        self.update_count()

    def add_edge(self, edge):
        '''
            Metodo de adicao de objetos edge associados ao objeto node
        '''
        if self.myItemType == self.Religador:
            if self.edge_counter > 2:
                return
            self.edge_counter += 1
        self.edges[edge] = len(self.edges)

        if edge.w1.myItemType != Node.Subestacao and edge.w2.myItemType != Node.Subestacao:
            self.edges_no_sub[edge] = len(self.edges_no_sub)
        self.update_count()

    def edge_position(self, edge):

        height = self.rect().height()
        height = height - 2.0 * height / 8.0

        num_edges = len(self.edges_no_sub)

        num_edges -= 1

        if num_edges <= 0:
            num_edges = 1

        dw = height / float(num_edges)

        pos = height / 8.0 + self.edges_no_sub[edge] * dw

        return pos

    def center(self):
        point = QtCore.QPointF(self.rect().width(), self.rect().height())
        return (self.pos() + point / 2)

    def setCenter(self, pos):
        w = self.rect().width()
        h = self.rect().height()
        point = QtCore.QPointF(w / 2, h / 2)
        self.setPos(pos - point)

    def boundingRect(self):
        '''
            Metodo que especifica a borda do objeto node
        '''
        extra = 5.0
        return self.rect().adjusted(-extra, -extra, extra, extra)

    def paint(self, painter, option, widget):
        '''
            Metodo de desenho do objeto node implementado pela classe Node
        '''

        # self.text.setPos(0, self.rect().height())
        # caso o item a ser inserido seja do tipo subestacao
        if self.myItemType == self.Subestacao:
            painter.setPen(QtGui.QPen(QtCore.Qt.black, 2))
            painter.setBrush(QtCore.Qt.white)
            painter.drawEllipse(self.rect())
        # caso o item a ser inserido seja do tipo religador1
        elif self.myItemType == self.Religador:
            painter.setPen(QtGui.QPen(QtCore.Qt.black, 2))
            painter.setBrush(QtCore.Qt.white)
            painter.drawRoundedRect(self.rect(), 5, 5)
        # caso o item a ser inserido seja do tipo barra
        elif self.myItemType == self.Barra:
            painter.setPen(QtGui.QPen(QtCore.Qt.black, 2))
            painter.setBrush(QtCore.Qt.black)
            painter.drawRoundedRect(self.rect(), 2, 2)
        # caso o item a ser inserido seja do tipo agent
        elif self.myItemType == self.Agent:
            painter.setPen(QtGui.QPen(QtCore.Qt.black, 2))
            painter.setBrush(QtCore.Qt.white)
            painter.drawRect(self.rect())
        # caso o item a ser inserido seja do tipo nó conectivo
        elif self.myItemType == self.NoConectivo:
            painter.setPen(QtGui.QPen(QtCore.Qt.black, 2))
            painter.setBrush(QtCore.Qt.black)
            painter.drawEllipse(self.rect())

        elif self.myItemType == self.NoDeCarga:
            painter.setPen(QtGui.QPen(QtCore.Qt.black, 2))
            painter.setBrush(QtCore.Qt.black)
            painter.drawRect(self.rect())

        if self.isSelected():
            painter.setPen(QtGui.QPen(QtCore.Qt.red, 2, QtCore.Qt.DashLine))
            painter.setBrush(QtCore.Qt.NoBrush)
            adjust = 2
            rect = self.rect().adjusted(-adjust, -adjust, adjust, adjust)
            painter.drawRect(rect)

    def itemChange(self, change, value):
        '''
            Metodo que detecta mudancas na posicao do objeto node
        '''
        if change == QtGui.QGraphicsItem.ItemPositionChange:
            for edge in self.edges:
                edge.update_position()
        return QtGui.QGraphicsItem.itemChange(self, change, value)

    def mousePressEvent(self, mouse_event):
        self.scene().clearSelection()
        # print "Id:", self.chave.nome, ",", "Corrente Nominal:", self.chave.ratedCurrent, ",", "Breaking Capacity:", self.chave.breakingCapacity, ",", "Seq de Religamento", self.chave.recloseSequences
        self.setSelected(True)
        print self.dict_prop
        super(Node, self).mousePressEvent(mouse_event)
        return

    def mouseMoveEvent(self, mouse_event):
        super(Node, self).mouseMoveEvent(mouse_event)
        return

    def mouseReleaseEvent(self, mouse_event):
        print "=================RELEASE EVENT======================="
        super(Node, self).mouseReleaseEvent(mouse_event)
        new_edge = None
        scene = self.scene()
        ell = QtGui.QGraphicsEllipseItem()
        ell.setRect(QtCore.QRectF(mouse_event.scenePos() - QtCore.QPointF(10,10), QtCore.QSizeF(30,30)))
        scene.addItem(ell)
        if self.myItemType == Node.NoConectivo and len(self.edges) == 1:
            for item in scene.items():
                if ell.collidesWithItem(item):
                    if isinstance(item, Node):
                        if item.myItemType != Node.NoConectivo:
                            if item.myItemType == Node.Barra:
                                scene.removeItem(ell)
                                return
                            for edge in self.edges:
                                edge.scene().removeItem(edge)
                                if edge.w1.myItemType != Node.NoConectivo:
                                    w1 = edge.w1
                                else:
                                    w1 = edge.w2
                                new_edge = Edge(w1, item, scene.myLineMenu)
                                scene.addItem(new_edge)
                                new_edge.update_position()
                                scene.removeItem(self)


        if self.myItemType == Node.NoDeCarga:
            for item in scene.items():
                if self.collidesWithItem(item):
                    if isinstance(item, Edge) and not item.isUnderMouse():
                        if item.line().length() < 130:
                            return
                        break_mode = 3
                        pos = item.get_fraction(mouse_event.scenePos())
                        self.setPos(pos.x()-5, pos.y()-5)
                        scene.break_edge(item, break_mode, self)
        scene.removeItem(ell)
        print "=================END OF RELEASE EVENT======================="
        return

    def contextMenuEvent(self, event):
            self.scene().clearSelection()
            self.setSelected(True)
            self.myNodeMenu.exec_(event.screenPos())


class command(QtGui.QUndoCommand):

    def __init__(self, comando, scene, item, pos):
        super(command, self).__init__(comando)
        self.comando = comando
        self.item = item
        self.scene = scene
        self.pos = pos
        self.count = 0

    def redo(self):
        print "oiiii"
        self.count += 1
        if self.count <=1:
            return
        if self.comando == "Add Item":
            self.scene.addItem(self.item)
        elif self.comando == "Add Line":
            
            if self.item.w1.myItemType == Node.NoConectivo and len(self.item.w1.edges) <= 1:
                self.scene.addItem(self.item.w1)
            if self.item.w2.myItemType == Node.NoConectivo and len(self.item.w2.edges) <= 1:
                self.scene.addItem(self.item.w2)
            self.scene.addItem(self.item)
            # self.scene.addItem(self.item.GhostRetItem)
            self.item.update_position()
        elif self.comando == "Increase Bus":
            self.item.setSelected(True)
            self.scene.increase_bus()




    def undo(self):
        if self.comando == "Add Item":
            self.scene.removeItem(self.item)
        elif self.comando == "Add Line":
            
            if self.item.w1.myItemType == Node.NoConectivo and len(self.item.w1.edges) <= 1:
                self.scene.removeItem(self.item.w1)
            if self.item.w2.myItemType == Node.NoConectivo and len(self.item.w2.edges) <= 1:
                self.scene.removeItem(self.item.w2)
            # self.item.w1.edge_counter -= 1
            # self.item.w2.edge_counter -= 1
            self.scene.removeItem(self.item)
            # self.scene.removeItem(self.item.GhostRetItem)
        elif self.comando == "Increase Bus":
            self.item.setSelected(True)
            self.scene.decrease_bus()
            


class SceneWidget(QtGui.QGraphicsScene):
    '''
        Classe que implementa o container Grafico onde os
        widgets residirão
    '''

    # tipos de modos de iteracao com o diagrama grafico
    InsertItem, InsertLine, InsertText, MoveItem, SelectItems = range(5)

    # tipos de estilos para o background do diagrama grafico
    GridStyle, NoStyle = range(2)
    # signal definido para a classe SceneWidget enviado quando um item é
    # inserido no diagrama grafico
    itemInserted = QtCore.Signal(int)

    def __init__(self):

        super(SceneWidget, self).__init__()
        self.setSceneRect(0, 0, 800, 800)
        self.myMode = self.MoveItem
        self.myItemType = Node.Subestacao
        self.myBackgroundSytle = self.NoStyle
        self.keyControlIsPressed = False
        self.line = None
        self.no = None
        self.ghost = None
        self.selectRect = None
        self.start_item_is_ghost = False
        self.end_item_is_ghost = False
        self.text_item = None
        self.create_actions()
        self.create_menus()
        self.undoStack = QtGui.QUndoStack()


    def mousePressEvent(self, mouse_event):
        '''
            Este metodo define as acoes realizadas quando um evento do tipo
            mousePress e detectado no diagrama grafico
        '''
        super(SceneWidget, self).mousePressEvent(mouse_event)
        self.pressPos = mouse_event.scenePos()
        self.break_mode = 2
        self.edge_broken = None

        if (mouse_event.button() != QtCore.Qt.LeftButton):
            node_priority = False
            self.clearSelection()
            ell = QtGui.QGraphicsEllipseItem()
            ell.setRect(QtCore.QRectF(mouse_event.scenePos() - QtCore.QPointF(10,10), QtCore.QSizeF(30,30)))
            self.addItem(ell)

            for item in self.items():
                if ell.collidesWithItem(item):
                    if isinstance(item, Node):
                        node_priority = True

            for item in self.items():
                if ell.collidesWithItem(item) and isinstance(item, Edge) and not node_priority:
                    self.removeItem(ell)
                    item.setSelected(True)
                    item.myEdgeMenu.exec_(mouse_event.screenPos())
                    item.setSelected(False)
                    return
            self.removeItem(ell)
            return
        item_oculto = None
        for item in self.items():
            if not item.isVisible():
                item_oculto = item
        if item_oculto == None:
            pass
        else:
            self.removeItem(item_oculto)
        if self.myMode == self.InsertItem:
            if self.myItemType == Node.Religador:
                item = Node(self.myItemType, self.myRecloserMenu)
            elif self.myItemType == Node.Barra:
                item = Node(self.myItemType, self.myBusMenu)
            elif self.myItemType == Node.Subestacao:
                item = Node(self.myItemType, self.mySubstationMenu)
            elif self.myItemType == Node.NoDeCarga:
                item = Node(self.myItemType, self.mySubstationMenu)

            self.addItem(item)
            item.setPos(mouse_event.scenePos())
            comando = command("Add Item", self, item, item.scenePos())
            self.undoStack.push(comando)
            self.itemInserted.emit(self.myItemType)

        elif self.myMode == self.InsertLine:
            ell = QtGui.QGraphicsEllipseItem()
            ell.setRect(QtCore.QRectF(mouse_event.scenePos() - QtCore.QPointF(10,10), QtCore.QSizeF(30,30)))
            self.addItem(ell)
            node_priority = False
            edge_collision, node_collision, ellipse_collision = range(3)
            collision = None
            for item in self.items(mouse_event.scenePos()):
                if isinstance(item, Node):
                    node_priority = True
            for item in self.items():
                if ell.collidesWithItem(item):
                    if isinstance(item, Edge) and not node_priority:

                        self.c_pos = (
                            item.line().p1() + item.line().p2()) / 2
                        collision = edge_collision
                        self.break_mode = 0
                        self.edge_broken = item

                    elif isinstance(item, Node):
                        collision = node_collision
                        self.start_item = item
                    elif isinstance(item, QtGui.QGraphicsEllipseItem):
                        collision = ellipse_collision
            self.l0 = mouse_event.scenePos()
            if collision == edge_collision:
                self.no = Node(Node.NoConectivo, self.myLineMenu)
                self.addItem(self.no)
                self.no.setPos(self.c_pos - QtCore.QPointF(3.5, 3.5))
                self.start_item = self.no
                self.l0 = self.c_pos

            elif collision == ellipse_collision:
                self.no = Node(Node.NoConectivo, self.myLineMenu)
                self.addItem(self.no)
                self.no.setPos(mouse_event.scenePos())
                self.start_item = self.no
            self.line = QtGui.QGraphicsLineItem(
                QtCore.QLineF(
                    self.l0,
                    self.l0))
            self.line.setPen(
                QtGui.QPen(QtCore.Qt.black, 2))
            self.addItem(self.line)
            self.removeItem(ell)
            print "start item:"
            print self.start_item

        elif self.myMode == self.InsertText:
            text_item = Text()
            text_item.setFont(self.myFont)
            text_item.setTextInteractionFlags(QtCore.Qt.TextEditorInteraction)
            text_item.setZValue(1000.0)
            text_item.lostFocus.connect(self.editorLostFocus)
            text_item.selectedChange.connect(self.itemSelected)
            self.addItem(text_item)
            text_item.setDefaultTextColor(self.myTextColor)
            text_item.setPos(mouse_event.scenePos())
            self.textInserted.emit(text_item)
        elif self.myMode == self.SelectItems:
            selection = True
            # for item in self.items():
            #     if item.isUnderMouse():
            #         if isinstance(item,GhostR):
            #             selection = True
            #         else:
            #             selection = False
            if selection:
                init_point = mouse_event.scenePos()
                self.selectRect = QtGui.QGraphicsRectItem(
                    QtCore.QRectF(init_point, init_point))
                self.selectRect.setPen(
                    QtGui.QPen(QtCore.Qt.red, 2, QtCore.Qt.DashLine))
                self.addItem(self.selectRect)

        else:
            super(SceneWidget, self).mousePressEvent(mouse_event)
            priority_on = False
            priority_node = False
            ell = QtGui.QGraphicsEllipseItem()
            ell.setRect(QtCore.QRectF(mouse_event.scenePos() - QtCore.QPointF(10,10), QtCore.QSizeF(30,30)))
            self.addItem(ell)
            for item in self.items():
                if ell.collidesWithItem(item):
                    if isinstance(item, Node) or isinstance(item, Edge):
                        if isinstance(item, Node):
                            priority_node = True
                        priority_on = True
                        print priority_on
            for item in self.items():
                if ell.collidesWithItem(item):
                    if isinstance(item, QtGui.QGraphicsEllipseItem) and not priority_on:
                        self.clearSelection()
                    elif isinstance(item, Node):
                        self.removeItem(ell)
                        self.clearSelection()
                        item.setSelected(True)
                        print "lets check"
                    elif isinstance(item, Edge) and not priority_node:
                        self.removeItem(ell)
                        self.clearSelection()
                        item.setSelected(True)
                        print "lets check"                        
                        return
            self.removeItem(ell)
            print "opa"
        

        return

    def mouseMoveEvent(self, mouse_event):
        '''
            Este método define as acoes realizadas quando um evento do tipo
            mouseMove é detectado no diagrama grafico. Neste caso desenha uma
            linha quando o modo self.InsertLine está ativado
        '''
        if self.myMode == self.InsertLine and self.line:
            new_line = QtCore.QLineF(
                self.line.line().p1(), mouse_event.scenePos())
            self.line.setLine(new_line)
        elif self.myMode == self.MoveItem:
            super(SceneWidget, self).mouseMoveEvent(mouse_event)
        elif self.myMode == self.SelectItems and self.selectRect:
            new_rect = QtCore.QRectF(
                self.selectRect.rect().topLeft(), mouse_event.scenePos())
            self.selectRect.setRect(new_rect)

    def mouseReleaseEvent(self, mouse_event):
        '''
            Este método define as acoes realizadas quando um evento do tipo
            mouseRelease e detectado no diagrama grafico. Neste caso conecta
            os dois elementos que estão ligados pela linha criada no evento
            mousePress.
        '''

        if self.myMode == self.InsertLine and self.line:
            node_priority = False
            edge_priority = False
            block_on = False
            self.removeItem(self.no)
            # if self.start_item.myItemType == Node.NoConectivo:
            #     self.addItem(self.start_item)
            ell = QtGui.QGraphicsEllipseItem()
            ell.setRect(QtCore.QRectF(mouse_event.scenePos() - QtCore.QPointF(10,10), QtCore.QSizeF(30,30)))
            self.addItem(ell)

            # Testes preliminares do start_item
            if self.start_item.myItemType == Node.Barra:
                block_on = True
            if self.start_item.myItemType == Node.Religador:
                if len(self.start_item.edges) >= 2:
                    self.removeItem(self.line)
                    self.line = None
                    self.removeItem(ell)
                    return

            # Estabelecimento do end_item
            for item in self.items():
                if item.isUnderMouse():
                    if isinstance(item, Node):
                        node_priority = True

            for item in self.items():
                if ell.collidesWithItem(item):
                    if isinstance(item, Edge):
                        edge_priority = True

            for item in self.items():
                if ell.collidesWithItem(item):

                    if isinstance(item, Node):
                        if item.myItemType == Node.Religador:
                            if len(item.edges) >= 2:
                                self.removeItem(self.line)
                                self.line = None
                                self.removeItem(ell)
                                return
                        if block_on is True:
                            for edge in item.edges:
                                if edge.w1.myItemType == Node.Barra or edge.w2.myItemType == Node.Barra:
                                    self.removeItem(self.line)
                                    self.line = None
                                    self.removeItem(ell)
                                    return
                        self.end_item = item
                        print "checkpoint 1"

                    elif isinstance(item, Edge) and not node_priority:
                        if block_on is True:
                            self.removeItem(self.line)
                            self.line = None
                            self.removeItem(ell)
                            return
                        c_pos = (item.line().p1() + item.line().p2()) / 2
                        self.end_item = Node(Node.NoConectivo, self.myLineMenu)
                        self.end_item.setPos(c_pos + QtCore.QPointF(-3.5, -3.5))
                        self.break_mode = 1
                        self.edge_broken = item
                        print "checkpoint 2"
                    elif isinstance(item, QtGui.QGraphicsEllipseItem) and not node_priority and not edge_priority:
                        self.end_item = Node(Node.NoConectivo, self.myLineMenu)
                        self.end_item.setPos(mouse_event.scenePos())
                        print "checkpoint 3"

            self.removeItem(self.line)
            self.line = None
            self.removeItem(ell)

            # Testes posteriores do start_item e end_item
            if self.start_item.myItemType == Node.Barra:
                if self.end_item.myItemType == Node.NoConectivo:
                    self.removeItem(self.end_item)
                    self.end_item = Node(Node.Religador, self.myRecloserMenu)
                    self.addItem(self.end_item)
                    self.end_item.setPos(mouse_event.scenePos())

            if self.end_item.myItemType == Node.Barra:
                if self.start_item.myItemType == Node.NoConectivo:
                    self.removeItem(self.start_item)
                    self.start_item = Node(Node.Religador, self.myRecloserMenu)
                    self.addItem(self.start_item)
                    self.start_item.setPos(self.pressPos)


            # Teste de comprimento de linha
            dist = math.sqrt(
                math.pow(
                    self.start_item.pos().x() -
                    self.end_item.pos().x(), 2) + math.pow(
                    self.start_item.pos().y() - self.end_item.pos().y(), 2))
            if dist < 115:
                print "Erro: Comprimento da ligação muito pequeno!"
                return
            if self.edge_broken is not None and self.edge_broken.isPermanent:
                return

            self.addItem(self.start_item)
            self.addItem(self.end_item)

            edge = Edge(self.start_item, self.end_item, self.myLineMenu)
            self.addItem(edge)
            print "scene:"
            print edge.scene()
            edge.set_color(QtCore.Qt.black)
            # self.addItem(edge.GhostRetItem)
            edge.update_position()
            print "b mode"
            print self.break_mode
            #Teste de quebra de linha
            self.break_edge(self.edge_broken, self.break_mode)


            # comando = command("Add Line", self, edge, None)
            # self.undoStack.push(comando)

            if edge.w1.myItemType == Node.NoConectivo:
                aux = edge.w1
                edge.w1 = edge.w2
                edge.w2 = aux

            for item in self.selectedItems():
                item.setSelected(False)

            self.no = None

        elif self.myMode == self.SelectItems and self.selectRect:
            path = QtGui.QPainterPath()
            path.addRect(self.selectRect.rect())
            self.setSelectionArea(path)
            self.removeItem(self.selectRect)
            self.selectRect = None
            for item in self.selectedItems():
                if isinstance(item, Edge):
                    if item.w1.myItemType == Node.NoConectivo or item.w1.myItemType == Node.Barra:
                        item.w1.setSelected(True)
                    if item.w2.myItemType == Node.NoConectivo or item.w2.myItemType == Node.Barra:
                        item.w2.setSelected(True)
        self.line = None
        self.itemInserted.emit(3)
        self.ghost = None
        super(SceneWidget, self).mouseReleaseEvent(mouse_event)
        print "END SCENE"

        #     Problema quando tenta-se modificar o texto dos componentes
    def keyPressEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_Up:
            for item in self.selectedItems():
                item.moveBy(0, -5)
        elif key == QtCore.Qt.Key_Down:
            for item in self.selectedItems():
                item.moveBy(0, 5)
        elif key == QtCore.Qt.Key_Left:
            for item in self.selectedItems():
                item.moveBy(-5, 0)
            self.undoStack.undo()
            print self.undoStack.index()
        elif key == QtCore.Qt.Key_Right:
            for item in self.selectedItems():
                item.moveBy(5, 0)
            self.undoStack.redo()
            print self.undoStack.index()
        elif key == QtCore.Qt.Key_Space or key == QtCore.Qt.Key_Enter:
            pass
        elif key == QtCore.Qt.Key_Control:
            self.keyControlIsPressed = True
            print 'Ctrl pressed'
        elif key == QtCore.Qt.Key_Delete:
            self.delete_item()
        elif key == QtCore.Qt.Key_Escape:
            for item in self.items():
                item.setSelected(False)
        else:
            pass
            super(SceneWidget, self).keyPressEvent(event)
        return

    def break_edge(self, edge, mode, insert = None):
        if mode == 3:
            break_point = insert 
        if mode == 2:
            return
        if mode == 0:
            break_point = self.start_item
        if mode == 1:
            break_point = self.end_item
        self.removeItem(edge)
        new_edge_1 = Edge(edge.w1, break_point, self.myLineMenu)
        new_edge_2 = Edge(break_point, edge.w2, self.myLineMenu)
        self.addItem(new_edge_1)
        self.addItem(new_edge_2)
        new_edge_1.update_position()
        new_edge_2.update_position()

    def recover_edge(self, item):
        w = []

        for edge in item.edges:
            if edge.w1 == item:
                w.append(edge.w2)
            elif edge.w2 == item:
                w.append(edge.w1)
            print w
        item.remove_edges()
        new_edge = Edge(w[0], w[1], self.myLineMenu)
        self.addItem(new_edge)
        self.addItem(new_edge.GhostRetItem)
        new_edge.update_position()

    def set_item_type(self, type):
        '''
            Define em qual tipo de item sera inserido no diagrama grafico assim
            que um evento do tipo mousePress for detectado, podendo ser:
            Node.Subestacao
            Node.Religador
            Node.Barra
            Node.Agent
        '''
        self.myItemType = type

    def set_mode(self, mode):
        '''
            Define em qual modo
        '''
        self.myMode = mode

    def create_actions(self):
        '''
            Este metodo cria as ações que serão utilizadas nos menus dos itens
            gráficos.
        '''
        self.propertysAction = QtGui.QAction(
            'Propriedades', self, shortcut='Enter',
            triggered=self.launch_dialog)
        self.deleteAction = QtGui.QAction(
            'Excluir Item', self, shortcut='Delete',
            triggered=self.delete_item)
        self.increaseBusAction = QtGui.QAction(
            'Aumentar Barra', self, shortcut='Ctrl + a',
            triggered=self.increase_bus)
        self.decreaseBusAction = QtGui.QAction(
            'Diminuir Barra', self, shortcut='Ctrl + d',
            triggered=self.decrease_bus)
        self.alignHLineAction = QtGui.QAction(
            'Alinha Linha H', self, shortcut='Ctrl + h',
            triggered=self.align_line_h)
        self.alignVLineAction = QtGui.QAction(
            'Alinhar Linha V', self, shortcut='Ctrl + v',
            triggered=self.align_line_v)

    def create_menus(self):
        '''
            Este metodo cria os menus de cada um dos itens gráficos: religador,
            subestação, barra e linha.
        '''
        self.myBusMenu = QtGui.QMenu('Menu Bus')
        self.myBusMenu.addAction(self.increaseBusAction)
        self.myBusMenu.addAction(self.decreaseBusAction)
        self.myBusMenu.addAction(self.deleteAction)
        self.myBusMenu.addAction(self.propertysAction)

        self.myRecloserMenu = QtGui.QMenu('Menu Recloser')
        self.myRecloserMenu.addAction(self.propertysAction)
        self.myRecloserMenu.addAction(self.deleteAction)

        self.mySubstationMenu = QtGui.QMenu('Menu Subestacao')
        self.mySubstationMenu.addAction(self.propertysAction)
        self.mySubstationMenu.addAction(self.deleteAction)

        self.myLineMenu = QtGui.QMenu('Menu Linha')
        self.myLineMenu.addAction(self.alignHLineAction)
        self.myLineMenu.addAction(self.alignVLineAction)
        self.myLineMenu.addAction(self.propertysAction)
        self.myLineMenu.addAction(self.deleteAction)

    def delete_item(self):
        '''
            Este método implementa a ação de exclusão de um item gráfico do
            diagrama.
        '''
        for item in self.selectedItems():
            if isinstance(item, Node):
                if len(item.edges) > 2 or len(item.edges) < 2:
                    item.remove_edges()
                else:
                    self.recover_edge(item)
            if isinstance(item, Edge):
                item.w1.remove_edge(item)
                item.w2.remove_edge(item)
                if item.w1.myItemType == Node.NoConectivo:
                    item.w1.remove_edges()
                    self.removeItem(item.w1)
                if item.w2.myItemType == Node.NoConectivo:
                    item.w2.remove_edges()
                    self.removeItem(item.w2)
                # self.removeItem(item.GhostRetItem)
            self.removeItem(item)


    def launch_dialog(self):
        '''
            Este método inicia os diálogos de configuração de cada um dos itens
            gráficos do diagrama.
        '''
        for item in self.selectedItems():
            if isinstance(item, Node):
                if item.myItemType == Node.Religador:
                    dialog = RecloserDialog(item)
                    if dialog.dialog.result() == 1:
                        if dialog.identificaOLineEdit.text() == "":
                            pass
                        else:
                            item.chave.nome = dialog.identificaOLineEdit.text()
                        if dialog.correnteNominalLineEdit.text() == "":
                            pass
                        else:
                            item.chave.ratedCurrent = dialog.correnteNominalLineEdit.text()
                        if dialog.capacidadeDeInterrupOLineEdit.text() == "":
                            pass
                        else:
                            item.chave.breakingCapacity = dialog.capacidadeDeInterrupOLineEdit.text()
                        if dialog.nDeSequNciasDeReligamentoLineEdit.text() == "":
                            pass
                        else:
                            item.chave.recloseSequences = dialog.nDeSequNciasDeReligamentoLineEdit.text()
                
            if isinstance(item, Node):
                if item.myItemType == Node.Barra:
                    dialog = BarraDialog(item)
                    if dialog.dialog.result() == 1:
                        if dialog.nomeLineEdit.text() == "":
                            pass
                        else:
                            item.barra.nome = dialog.nomeLineEdit.text()
                        if dialog.fasesLineEdit.text() == "":
                            pass
                        else:
                            item.barra.phases = dialog.fasesLineEdit.text()

            if isinstance(item, Node):
                if item.myItemType == Node.Subestacao:
                    dialog = SubstationDialog(item)
                    if dialog.dialog.result() == 1:
                        if dialog.nomeLineEdit.text() == "":
                            pass
                        else:
                            item.substation.nome = dialog.nomeLineEdit.text()
                        if dialog.tpLineEdit.text() == "":
                            pass
                        else:
                            item.substation.tensao_primario = dialog.tpLineEdit.text()

    def increase_bus(self):
        '''
            Este método implementa a açao de aumentar o tamanho do item gráfico
            barra.
        '''

        for item in self.selectedItems():
            if isinstance(item, Node):
                item.prepareGeometryChange()
                item.setRect(
                    item.rect().x(), item.rect().y(), item.rect().width(),
                    item.rect().height() * 1.25)
                comando = command("Increase Bus", self, item, None)
                self.undoStack.push(comando)

    def decrease_bus(self):
        '''
            Este método implementa a ação de diminuir o tamanho do item gráfico
            barra.
        '''
        for item in self.selectedItems():
            if isinstance(item, Node):
                item.prepareGeometryChange()
                item.setRect(
                    item.rect().x(), item.rect().y(), item.rect().width(),
                    item.rect().height() / 1.25)

    def align_line_h(self):
        w1_is_locked = False
        w2_is_locked = False
        for item in self.selectedItems():
            if isinstance(item, Edge):
                for edge in item.w1.edges:
                    if edge.w1.myItemType == Node.Barra or edge.w2.myItemType == Node.Barra:
                        w1_is_locked = True
                for edge in item.w2.edges:
                    if edge.w1.myItemType == Node.Barra or edge.w2.myItemType == Node.Barra:
                        w2_is_locked = True
                if w1_is_locked and not w2_is_locked:
                    pos = QtCore.QPointF(item.w2.center().x(), item.w1.center().y())
                    item.w2.setCenter(pos)
                    item.update_position()
                if w2_is_locked and not w1_is_locked:
                    pos = QtCore.QPointF(item.w1.center().x(), item.w2.center().y())
                    item.w1.setCenter(pos)
                    item.update_position()

                else:
                    pos = QtCore.QPointF(item.w2.center().x(), item.w1.center().y())
                    item.w2.setCenter(pos)
                    item.update_position()
        for item in self.items():
            if isinstance(item, Edge):
                item.update_position()

    def align_line_v(self):
        for item in self.selectedItems():
            if isinstance(item, Edge):
                if item.w1.x() < item.w2.x():
                    pos = QtCore.QPointF(item.w1.center().x(), item.w2.center().y())
                    item.w2.setCenter(pos)
                else:
                    pos = QtCore.QPointF(item.w2.center().x(), item.w1.center().y())
                    item.w1.setCenter(pos)
                item.update_position()
                item.update_ret()

    def h_align(self):
        fix = False
        fixed_items = []
        first_priority = False
        has_pos_priority = False
        has_bar_priority = False
        y_pos_list = []
        for item in self.selectedItems():
            if isinstance(item, Node):
                if item.myItemType == Node.Religador:
                    has_pos_priority = True
                    pos_item = item.pos().y()
                if item.myItemType == Node.Barra and item.bar_busy is True:
                    has_bar_priority = True
                    pos_barra = item.pos().y()

        for item in self.selectedItems():
            if isinstance(item, Node):
                if item.myItemType != Node.Barra:
                    if has_bar_priority:
                        continue
                else:
                    y_pos_list.append(item.pos().y())
                    continue

                if item.myItemType == Node.NoConectivo:
                    if has_pos_priority:
                        continue
                    else:
                        y_pos_list.append(item.pos().y())
                else:
                    y_pos_list.append(item.pos().y())

        print len(y_pos_list)
        print y_pos_list
        max_pos = max(y_pos_list)
        min_pos = min(y_pos_list)
        mean_pos = max_pos - abs(max_pos - min_pos) / 2.0

        for item in self.selectedItems():
            if isinstance(item, Node):
                if item.Fixed is True:
                        mean_pos = item.pos().y()
                        item.mean_pos = mean_pos
                        first_priority = True



        print "mean_pos"
        print mean_pos

        for item in self.selectedItems():
            if isinstance(item, Node):
                pos = mean_pos
                print "===========COMEÇO LOOP=================="
                print has_bar_priority, has_pos_priority, first_priority

                if item.Fixed is True:
                    continue

                # for edge in item.edges:
                #     if edge.w1.Fixed:
                #         pos = edge.w1.mean_pos
                #         item.mean_pos = pos
                #         item.semiFixed = True

                #     if edge.w1.semiFixed:
                #         pos = edge.w1.mean_pos
                #         item.mean_pos = pos
                #         item.semiFixed = True
                        
                #     if edge.w2.Fixed:
                #         pos = edge.w2.mean_pos
                #         item.mean_pos = pos
                #         item.semiFixed = True

                #     if edge.w2.semiFixed:
                #         pos = edge.w2.mean_pos
                #         item.mean_pos = pos
                #         item.semiFixed = True

                if has_bar_priority is True and item.myItemType == Node.Subestacao:
                    pos = pos_barra + 25

                elif has_pos_priority:
                    pos = pos_item

                if item.myItemType == Node.NoConectivo:
                    print "no conectivo"
                    pos = pos + 17

                if item.myItemType == Node.NoDeCarga:
                    pos = pos + 15

                if item.myItemType == Node.Barra:
                    print "Node Barra"
                    pos = pos_barra

                item.setY(pos)
                print "===========FIM LOOP=================="
        print mean_pos




        for item in self.selectedItems():
            if isinstance(item, Edge):
                item.update_position()

    def v_align(self):
        x_pos_list = []
        for item in self.selectedItems():
            if isinstance(item, Node):
                x_pos_list.append(item.pos().x())
        max_pos = max(x_pos_list)
        min_pos = min(x_pos_list)
        mean_pos = max_pos - abs(max_pos - min_pos) / 2.0

        for item in self.selectedItems():
            if isinstance(item, Node):
                item.setX(mean_pos)

        for item in self.selectedItems():
            if isinstance(item, Edge):
                item.update_position()

    def set_grid(self):
        if self.myBackgroundSytle == self.GridStyle:
            self.setBackgroundBrush(QtGui.QBrush(
                QtCore.Qt.white, QtCore.Qt.NoBrush))
            self.myBackgroundSytle = self.NoStyle
        elif self.myBackgroundSytle == self.NoStyle:
            self.setBackgroundBrush(QtGui.QBrush(
                QtCore.Qt.lightGray, QtCore.Qt.CrossPattern))
            self.myBackgroundSytle = self.GridStyle


class ViewWidget(QtGui.QGraphicsView):
    '''
        Esta classe implementa o container QGraphicsView
        onde residirá o objeto QGraphicsScene.
    '''
    def __init__(self, scene):

        super(ViewWidget, self).__init__(scene)
        self.setCacheMode(QtGui.QGraphicsView.CacheBackground)
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtGui.QGraphicsView.AnchorViewCenter)

    def wheelEvent(self, event):
        self.scale_view(math.pow(2.0, -event.delta() / 240.0))

    def scale_view(self, scale_factor):
        factor = self.matrix().scale(scale_factor, scale_factor).mapRect(
            QtCore.QRectF(0, 0, 1, 1)).width()
        if factor < 0.5 or factor > 3:
            return
        self.scale(scale_factor, scale_factor)

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    scene = SceneWidget()
    widget = ViewWidget(scene)
    widget.show()
    sys.exit(app.exec_())
