#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PySide import QtCore, QtGui
import math
import sys
# Importa os módulos necessários para implementação do diagrama gráfico
from elementos import Religador, BusBarSection, Substation, Condutor
from elementos import EnergyConsumer
from DialogRecloser import RecloserDialog
from DialogBarra import BarraDialog
from DialogConductor import ConductorDialog
from DialogSubstation import SubstationDialog
from DialogEnergyConsumer import EnergyConsumerDialog
from aviso_conexao import AvisoConexaoDialog
from avisoReligador import AvisoReligador


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
            representa o objeto QtGui.QGraphicsLineItem.
        '''
        # A class edge representará graficamente os condutores no diagrama.
        # Nesta classe está presente a sua definição, assim como suas funções
        # necessárias para alinhamento e ligação.
        # NOTA IMPORTANTE: A Edge representa gráficamente uma linha. Sendo
        # assim, ela possui uma linha virtual em que a classe se baseia para
        # desenhar a linha de fato. Edge é um objeto do tipo
        # QtGui.QGraphicsLineItem. Sua linha é definida por um objeto do tipo
        # QtCore.QLineF. (Ver esta duas funções na biblioteca PySide)
        super(Edge, self).__init__()
        self.id = id(self)
        self.w1 = w1
        self.w2 = w2
        # Adiciona o objeto edge as lista de w1 e w2, respectivamente.
        self.w1.add_edge(self)
        self.w2.add_edge(self)
        # Associa o menu edge a ser passado para abertura de dialog.
        self.myEdgeMenu = edge_menu
        # Cria e configura a linha que liga os itens w1 e w2.
        line = QtCore.QLineF(self.w1.pos(), self.w2.pos())
        self.setLine(line)
        self.setZValue(-1)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True)
        # Cria uma flag que determina se a edge está ou não fixa a uma barra
        self.isFixed = False
        # Cria uma flag que fixa a edge numa barra.
        self.fixFlag = False
        # Cria uma flag que determina se a edge é ou não permanente.
        self.isPermanent = False
        # Cria um atributo "linha", que é um objeto do tipo condutor. Este
        # objeto será utilizado para representar os dados elétricos do
        # condutor. Os dados são iniciados nulos e depois serão setados por
        # meio dos menus. Ver classe "Condutor" em elementos.py.
        self.linha = Condutor(0, 0, 0, 0, 0, 0)

        # Análise: se um item (w1 ou w2) que a linha conecta for uma barra,
        # seta-se um atributo desta barra, denominado "bar_busy", como True,
        # indicando que a barra está "ocupada".
        if w1.myItemType == Node.Barra or w2.myItemType == Node.Barra:
            self.isPermanent = True
            if w1.myItemType == Node.Barra:
                w1.bar_busy = True
            if w2.myItemType == Node.Barra:
                w2.bar_busy = True

    def get_fraction(self, pos):
        '''
            Esta função obtém uma fração da linha e é utilizada durante o
            modelo que denomino "Sticky to Line" de um nó de carga. Pode ser
            usado para outros fins em futuras expansões.
        '''
        # Define os limites (horizontal e vertical) da linha, ou seja, a
        # diferença entre os pontos x2 e x1 e os pontos y2 e y1 da linha
        # (supondo uma linha que liga (x1,y1) a (x2,y2)).
        delta_x = math.fabs(self.line().p2().x() - self.line().p1().x())
        delta_y = math.fabs(self.line().p2().y() - self.line().p1().y())

        # "dist" representa a distância entre o ponto presente na posição
        # "pos", passada na chamada da função, e o ponto inicial da linha.
        # Esta distância é dada pela relação matemática que descreve a
        # distância entre dois pontos:
        # L = ((x1 - x2)² + (y1 - y2)²)^(1/2)
        dist = math.sqrt(pow(pos.x() - self.line().p1().x(), 2)
                         + pow(pos.y() - self.line().p1().y(), 2))
        # Este é um método de aproximação para uma fração definida. Compara-se
        # "dist" com o comprimento total da linha. Dependendo da fração obtida
        # arredonda-se esta fração para os valores definidos de 0.25, 0.5 e
        # 0.75
        fraction = dist / self.line().length()
        if 0.75 < fraction < 1:
            fraction = 0.75
        if 0.5 < fraction < 0.75:
            fraction = 0.5
        if 0.25 < fraction < 0.5:
            fraction = 0.25
        if 0 < fraction < 0.25:
            fraction = 0.25
        # Resta analisar uma possível inconsistência: Se o ponto p1 analisado
        # acima está abaixo ou acima, à esquerda ou à direita, do ponto p2.
        # Se estiver à direita:
        if self.line().p1().x() > self.line().p2().x():
            # A posição final x é x1 - fração_obtida * delta_x. Ou seja, x1
            # será o ponto referência e a posição final x estará a esquerda
            # deste ponto
            posf_x = self.line().p1().x() - fraction * delta_x
        # Se estiver à esquerda:
        else:
            # A posição final x é x1 + fração_obtida * delta_x. Ou seja, x1
            # será o ponto referência e a posição final x estará à direita
            # deste ponto.
            posf_x = self.line().p1().x() + fraction * delta_x
        # O mesmo é feito para y, sabendo que nos módulos do PySide, o eixo y
        # incrementa seu valor quando é percorrido para BAIXO. Assim:
        # Se estiver ABAIXO:
        if self.line().p1().y() > self.line().p2().y():
            # A posição final y é y1 - fração_obtida * delta_y. Ou seja, y1
            # será o ponto referência e a posição final y estará ACIMA deste
            # ponto.
            posf_y = self.line().p1().y() - fraction * delta_y
        # Se estiver ACIMA:
        else:
            # A posição final y é y1 + fração_obtida * delta_y. Ou seja, y1
            # será o ponto de referência e a posição final y estará ABAIXO
            # deste ponto.
            posf_y = self.line().p1().y() + fraction * delta_y
        # Finalmente, define e retorna a posição final. Explicando: Se
        # passarmos uma posição que esteja entre o começo e a metade da linha,
        # a função retornará a posição que está exatamente em 0.25 da linha.
        # Caso passemos uma posição que esteja no terceiro quarto da linha,
        # a função retornará a posição que esteja exatamente na metade da
        # linha. Passando uma posição que esteja no último quarto da linha, a
        # função retornará a posição que esteja exatamente em 0.75 da linha.
        posf = QtCore.QPointF(posf_x, posf_y)

        return posf

    def update_position(self):
        '''
            Método de atualização da posição do objeto edge implementado pela
            classe Edge. Sempre que um dos objetos Nodes w1 ou w2 modifica sua
            posição este método é chamado para que o objeto edge possa
            acompanhar o movimento dos Objetos Node.
        '''
        # Simplesmente cria uma nova linha ligando os itens w1 e w2.
        line = QtCore.QLineF(self.w1.pos(), self.w2.pos())
        length = line.length()
        # Se o comprimento obtido for nulo, retorna a função e a linha não
        # será atualizada
        if length == 0.0:
            return
        # Esta função virtual é necessária para realizar mudanças de geometria
        # em tempo real nos objetos da biblioteca PySide.
        self.prepareGeometryChange()
        # Seta a linha obtida como linha da Edge.
        self.setLine(line)

    def set_color(self, color):
        '''
            Esta classe simplesmente seta a cor da Edge
        '''
        # Com a cor passada na chamada da função, seta a cor desejada.
        self.setPen(QtGui.QPen(color))

    def paint(self, painter, option, widget):
        '''
            Metodo de desenho do objeto edge implementado pela classe Edge.
            A classe executa esta função constantemente.
        '''
        # Se os itens colidirem graficamente, a linha não é desenhada.
        if (self.w1.collidesWithItem(self.w2)):
            return

        # Temos abaixo a lógica de distribuição de linhas quando elas são
        # conectadas a uma barra.

        # Se o item self.w1 for do tipo barra deve-se alinhar o item self.w2.
        # Note que este alinhamento não se aplica ao elemento Subestação:
        if (self.w1.myItemType == Node.Barra
                and self.w2.myItemType != Node.Subestacao):
            # Seta a flag indicando fixação da linha na Barra.
            self.fixFlag = True
            # Seta flag de w2, indicando que este item está fixo na barra.
            self.w2.Fixed = True
            # Se o número de linhas conectas a barra for maior que 1 deve-se
            # proceder a lógica de distribuição e alinhamento.
            if len(self.w1.edges) > 1:
                # Insere a linha em seu local de distribuição calculado pelo
                # item gráfico barra. Este local é determinado pela função
                # edge_position (Ver classe Node).
                line = QtCore.QLineF(self.mapFromItem(
                    self.w1, self.w1.rect().center().x(),
                    self.w1.edge_position(
                        self)), self.mapFromItem(
                    self.w2, self.w2.rect().center()))
                # Ajusta o item w2 na grade invisível presente no diagrama.
                # (Ver classe Node, função "adjust_in_grid")
                pos = self.w2.adjust_in_grid(
                    QtCore.QPointF(self.w2.scenePos().x(), line.y1()))
                self.w2.setPos(pos)

                # Ajusta a linha finalde acordo com o local de distribuição
                # com a correção do ajuste na grade.
                line.setLine(line.x1(), self.w2.y() + 10, line.x2(), line.y2())
                # Fixa o item w2.
                self.w2.fix_item()
            # Se esta é a primeira ligação da linha, realiza-se uma ligação
            # normal.
            else:
                line = QtCore.QLineF(self.mapFromItem(
                    self.w1, self.w1.rect().center()), self.mapFromItem(
                    self.w2, self.w2.rect().center()))

        # Se o item self.w2 for do tipo barra deve-se alinhar o item self.w1.
        # O procedimento é análogo ao exposto acima.
        elif (self.w2.myItemType == Node.Barra
                and self.w1.myItemType != Node.Subestacao):
            self.fixFlag = True
            self.w1.Fixed = True
            if len(self.w2.edges) > 1:
                line = QtCore.QLineF(self.mapFromItem(
                    self.w1, self.w1.rect().center()), self.mapFromItem(
                    self.w2, self.w2.rect().center().x(),
                    self.w2.edge_position(
                        self)))
                self.w1.setY(self.mapFromItem(
                    self.w2, self.w2.rect().center().x(),
                    self.w2.edge_position(
                        self)).y() - 12.5)
                self.w1.fix_item()
            else:
                line = QtCore.QLineF(self.mapFromItem(
                    self.w1, self.w1.rect().center()), self.mapFromItem(
                    self.w2, self.w2.rect().center()))
        else:
            line = QtCore.QLineF(self.mapFromItem(
                self.w1, self.w1.rect().center()), self.mapFromItem(
                self.w2, self.w2.rect().center()))
        self.setLine(line)
        if self.fixFlag:
            self.isFixed = True

        # Define a caneta e o preenchimento da linha.

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

        # Se a linha for selecionado, desenha uma linha tracejada ao redor
        # da linha selecionada.
        if self.isSelected():
            painter.setPen(QtGui.QPen(QtCore.Qt.red, 2, QtCore.Qt.DashLine))
            my_line = QtCore.QLineF(line)
            my_line.translate(0, 4.0)
            painter.drawLine(my_line)
            my_line.translate(0, -8.0)
            painter.drawLine(my_line)

    def mousePressEvent(self, mouse_event):
        '''
            Metodo que reimplementa a função de press do Mouse (ver biblioteca
            PySide, mouse events)
        '''
        # Se a linha for pressionada, seta a mesma como selecionada, para que
        # a linha tracejada seja desenhada.
        self.setSelected(True)
        super(Edge, self).mousePressEvent(mouse_event)
        return

    def contextMenuEvent(self, event):
        '''
            Reimplementação da função virtual contextMenuEvent, que define menu
            que aparece com o clique direito do mouse (ver biblioteca Pyside,
            contextMenuEvent)
        '''
        self.scene().clearSelection()
        self.setSelected(True)
        self.myEdgeMenu.exec_(event.screenPos() + QtCore.QPointF(20, 20))


class Text(QtGui.QGraphicsTextItem):
    '''
        Classe que implementa o objeto Text Genérico
    '''

    # Cria dois sinais, um relacionado à mudança de posição/geometria do item
    # e outro a quando o item perde o foco, ou deixa de estar selecionado.
    # (ver PySide, QtCore.Signal)
    selectedChange = QtCore.Signal(QtGui.QGraphicsItem)
    lostFocus = QtCore.Signal(QtGui.QGraphicsTextItem)

    def __init__(self, text, parent=None, scene=None):
        '''
            Configurações do texto (ver PySide, QtGui.QGraphicsTextItem)
        '''
        super(Text, self).__init__(parent, scene)
        self.setPlainText(text)
        self.setZValue(100)
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable, False)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, False)

    def itemChange(self, change, value):
        '''
            Função virtual reimplementada para emitir sinal de mudança (ver
            Pyside, QGraphicsTextItem)
        '''
        if change == QtGui.QGraphicsItem.ItemSelectedChange:
            self.selectedChange.emit(self)
        return value

    def focusOutEvent(self, event):
        '''
            Função virtual reimplementada para emitir sinal de perda de foco
            (ver Pyside, QGraphicsTextItem)
        '''
        self.lostFocus.emit(self)
        super(Text, self).focusOutEvent(event)


class Node(QtGui.QGraphicsRectItem):
    '''
       Classe que implementa o objeto Node Genérico. Este elemento gráfico irá
       representar religadores, barras, subestações e nós de carga
    '''
    # tipos de itens possiveis
    Subestacao, Religador, Barra, Agent, NoDeCarga, NoConectivo = range(6)

    def __init__(self, item_type, node_menu, parent=None, scene=None):
        '''
            Método inicial da classe Node
            Recebe como parâmetros os objetos myItemType (que define o tipo de
            Node desejado) e o menu desejado (menu que abre com clique direito)
            Analogamente ao que acontece com a Edge, este item é apenas a
            representação de um retângulo do tipo QtCore.QRectF.
        '''
        super(Node, self).__init__()
        # Definição de atributos do tipo flag
        self.con_lock = False
        self.adjusted = False
        self.bar_busy = False
        self.Fixed = False
        self.semiFixed = False
        # Definição de diversos atributos que serão usados posteriormente
        self.id = id(self)              # Atributo que guarda id única do item
        self.edges = {}                 # Dicionário contendo edges do item
        self.l0 = None                  # Variável auxiliar de posição
        self.edges_no_sub = {}          # Falta perguntar ao lucas o que é isso
        self.myItemType = item_type     # Define o tipo de item
        self.edge_counter = 0           # Contador que acompanha o nº de edges
        self.mean_pos = None            # Atributo de posição média
        self.text_config = 'Custom'     # Atributo da configuração de relé
        self.pos_ref = 0                # Atributo de posição referência
        # Se o item a ser inserido for do tipo subestação:
        if self.myItemType == self.Subestacao:
            # Define o retângulo.
            rect = QtCore.QRectF(0, 0, 50.0, 50.0)
            # Define e ajusta a posição do label do item gráfico. Começa com
            # um texto vazio.
            self.text = Text('', self, self.scene())
            self.substation = Substation(
                self.text.toPlainText(), 0.0, 0.0, 0.0, complex(0, 0))
            self.text.setPos(self.mapFromItem(self.text, 0, rect.height()))
        # Se o item a ser inserido for do tipo religador:
        elif self.myItemType == self.Religador:
            rect = QtCore.QRectF(0, 0, 20, 20)
            # Define e ajusta a posição do label do item gráfico. Começa com
            # um texto vazio.
            self.text = Text('', self, self.scene())
            self.text.setPos(self.mapFromItem(self.text, 10, rect.height()))
            # Cria o objeto chave que contém os dados elétricos do elemento
            # religador.
            self.chave = Religador(self.text.toPlainText(), 0, 0, 0, 0, 1)
        # Se o item a ser inserido for do tipo barra:
        elif self.myItemType == self.Barra:
            rect = QtCore.QRectF(0, 0, 10.0, 100.0)
            # Define e ajusta a posição do label do item gráfico. Começa com
            # um texto vazio.
            self.text = Text('Barra', self, self.scene())
            self.text.setPos(self.mapFromItem(self.text, 0, rect.height()))
            # Cria o objeto barra que contém os dados elétricos do elemento
            # barra.
            self.barra = BusBarSection("Identificador")
            # Define uma lista vazia com os terminais que possivelmente a barra
            # terá
            self.terminals = []
        # Se o item a ser inserido for do tipo agente:
        # OBS: PERGUNTAR PRO LUCAS SE O ABAIXO É NECESSÁRIO
        elif self.myItemType == self.Agent:
            rect = QtCore.QRectF(0, 0, 50.0, 50.0)
            # Define e ajusta a posição do label do item gráfico. Começa com
            # o texto Agente.
            self.text = Text('Agente', self, self.scene())
            self.text.setPos(self.mapFromItem(self.text, 0, rect.height()))

        # OBS: PERGUNTAR SE AINDA É NECESSÁRIO A PRESENÇA DE UM NÓ CONECTIVO
        # Se o item a ser inserido for do tipo nó conectivo:
        elif self.myItemType == self.NoConectivo:
            rect = QtCore.QRectF(0, 0, 7, 7)

        # Se o item a ser inserido for do tipo nó de carga:
        elif self.myItemType == self.NoDeCarga:
            rect = QtCore.QRectF(0, 0, 8, 8)
            # Define e ajusta a posição do label do item gráfico. Começa com
            # um texto vazio.
            self.text = Text('', self, self.scene())
            self.text.setPos(self.mapFromItem(self.text, 0, rect.height()))
            # Define uma lista vazia com os terminais que possivelmente o nó
            # de carga terá
            self.terminals = []
            # Cria o objeto barra que contém os dados elétricos do elemento
            # barra.
            self.no_de_carga = EnergyConsumer('', 0, 0)
        # Estabelece o retângulo do item gráfico como o rect obtido, dependendo
        # do item.
        self.setRect(rect)
        # Estabelece o menu (aberto via clique direito) dependendo do tipo de
        # item.
        self.myNodeMenu = node_menu

        # Seta as flags do QGraphicsItem (ver QtGui.QGraphicsItem.setFlag)
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QtGui.QGraphicsItem.ItemIsFocusable, True)
        self.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setZValue(0)

    def fix_item(self):
        '''
            Seta a flag de fixação do item.
        '''
        self.Fixed = True

    def update_count(self):
        '''
            Atualiza o contador que acompanha o número de Edges do item.
        '''
        self.edge_counter = len(self.edges)

    def remove_edges(self):
        '''
            Método de remoção de todos objetos Edge associados ao objeto node.
        '''
        # Cria uma lista vazia que irá receber as Edges removidas.
        deleted_list = []
        # Varre as edges do Node.
        for edge in self.edges:
            # Como todas as edges serão removidas, adiciona cada uma à
            # "deleted_list".
            deleted_list.append(edge)
            # Remove a Edge da cena em que o Node se encontra.
            self.scene().removeItem(edge)

        for edge in deleted_list:
            # Como cada edge removida possui um outro item conectado além do
            # Node presente, precisamos removê-la também da lista de edges.
            # deste outro item.
            if edge.w1 is not None:
                edge.w1.remove_edge(edge)
            if edge.w2 is not None:
                edge.w2.remove_edge(edge)

        # Limpa a lista de edges do presente Node, assim como a lista de edges
        # que não são conectadas à subestações.
        self.edges.clear()
        self.edges_no_sub.clear()
        # Atualiza o contador que acompanha o número de edges associadas ao
        # item.
        self.update_count()

    def remove_edge(self, edge):
        '''
            Esta função remove a edge passada na chamada do item presente.
        '''
        self.edges.pop(edge)
        self.update_count()

    def add_edge(self, edge):
        '''
            Método de adição de objetos edge associados ao objeto node
        '''
        # Se o Node for um religador, este só pode ter no máximo 2 ligações.
        # Ou seja, se o contador que acompanha o número de edges do Node for
        # maior que 2, a função retorna.
        if self.myItemType == self.Religador:
            if self.edge_counter > 2:
                return
        # Incrementa o contador.
            self.edge_counter += 1
        # Adiciona a Edge passada na chamada da função para o dicionário de
        # Edges do Node.
        self.edges[edge] = len(self.edges)
        # Se o presente Node não for uma subestação, adiciona a Edge no
        # dicionário de edges que não se conectam a subestações.
        if (edge.w1.myItemType != Node.Subestacao
                and edge.w2.myItemType != Node.Subestacao):
            self.edges_no_sub[edge] = len(self.edges_no_sub)
        self.update_count()

    def edge_position(self, edge):
        '''
            Este método é utilizado da distribuição das Edges ligadas numa
            barra, seguindo uma lógica de alinhamento.
        '''
        # PEDIR PARA O LUCAS EXPLICAR
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
        '''
            Método que retorna o centro do objeto passado.
        '''
        point = QtCore.QPointF(self.rect().width(), self.rect().height())
        return (self.pos() + point / 2)

    def set_center(self, pos):
        w = self.rect().width()
        h = self.rect().height()
        point = QtCore.QPointF(w / 2, h / 2)
        self.setPos(pos - point)

    def boundingRect(self):
        '''
            Reimplementação da função virtual que especifica a borda do objeto
            node (ver biblioteca Pyside, QtGui.QGraphicsRectItem.boundingRect)
        '''
        extra = 5.0
        return self.rect().adjusted(-extra, -extra, extra, extra)

    def paint(self, painter, option, widget):
        '''
            Método de desenho do objeto node implementado pela classe Node.
            Aqui se diferencia os objetos pela sua forma. Todos eram definidos
            por um retângulo QtCore.QRectF. Neste método, serão desenhadas
            suas formas baseadas em seus retângulos.
            Ver método paint em PySide.
        '''
        # Caso o item a ser inserido seja do tipo subestacão:
        if self.myItemType == self.Subestacao:
            painter.setPen(QtGui.QPen(QtCore.Qt.black, 2))
            painter.setBrush(QtCore.Qt.white)
            painter.drawEllipse(self.rect())
        # Caso o item a ser inserido seja do tipo religador:
        elif self.myItemType == self.Religador:
            painter.setPen(QtGui.QPen(QtCore.Qt.black, 2))
            # Faz-se aqui importante observação: se a chave associada ao
            # elemento gráfico religador estiver fechada, desenha-se o
            # religador preenchido de preto. Caso contrário, ele é vazado
            # (branco)
            if self.chave.normalOpen == 1:
                painter.setBrush(QtCore.Qt.white)
            else:
                painter.setBrush(QtCore.Qt.black)
            painter.drawRoundedRect(self.rect(), 5, 5)
        # Caso o item a ser inserido seja do tipo barra:
        elif self.myItemType == self.Barra:
            painter.setPen(QtGui.QPen(QtCore.Qt.black, 2))
            painter.setBrush(QtCore.Qt.black)
            painter.drawRoundedRect(self.rect(), 2, 2)
        # Caso o item a ser inserido seja do tipo agente:
        elif self.myItemType == self.Agent:
            painter.setPen(QtGui.QPen(QtCore.Qt.black, 2))
            painter.setBrush(QtCore.Qt.white)
            painter.drawRect(self.rect())
        # Caso o item a ser inserido seja do tipo nó conectivo:
        elif self.myItemType == self.NoConectivo:
            painter.setPen(QtGui.QPen(QtCore.Qt.black, 2))
            painter.setBrush(QtCore.Qt.black)
            painter.drawEllipse(self.rect())

        # Caso o item a ser inserido seja do tipo nó de carga:
        elif self.myItemType == self.NoDeCarga:
            painter.setPen(QtGui.QPen(QtCore.Qt.black, 2))
            painter.setBrush(QtCore.Qt.black)
            painter.drawRect(self.rect())

        # Se o item estiver selecionado, desenha uma caixa pontilhada de
        # seleção em seu redor.
        if self.isSelected():
            painter.setPen(QtGui.QPen(QtCore.Qt.red, 2, QtCore.Qt.DashLine))
            painter.setBrush(QtCore.Qt.NoBrush)
            adjust = 2
            rect = self.rect().adjusted(-adjust, -adjust, adjust, adjust)
            painter.drawRect(rect)

    def itemChange(self, change, value):
        '''
            Método que detecta mudancas na posição do objeto Node
        '''
        # Se a mudança for posição (ver QtGui.QGraphicsItem.ItemPositionChange)
        # é preciso atualizar as edges deste Node uma a uma:
        if change == QtGui.QGraphicsItem.ItemPositionChange:
            for edge in self.edges:
                edge.update_position()
        # Condição interna de retorno necessária.
        return QtGui.QGraphicsItem.itemChange(self, change, value)

    def mousePressEvent(self, mouse_event):
        '''
            Reimplementação da função virtual que define o evento referente
            ao aperto de botão do mouse.
        '''
        # Armazena a cena do item
        self.cena = self.scene()
        # "Deseleciona" os outros itens que por ventura estejam selecionados.
        self.scene().clearSelection()
        # Aciona a flag interna do item que indica que o item está selecionado.
        self.setSelected(True)
        super(Node, self).mousePressEvent(mouse_event)
        return

    def mouseMoveEvent(self, mouse_event):
        '''
            Reimplementação da função virtual que define o evento referente
            ao movimento do mouse durante o aperto.
        '''
        super(Node, self).mouseMoveEvent(mouse_event)
        # Chama a função "adjust_in_grid", que limita o movimento dos itens
        # numa grade invisível presente no diagrama (ver adjust_in_grid na
        # class node).
        self.setPos(self.adjust_in_grid(self.scenePos()))

    def mouseReleaseEvent(self, mouse_event):
        '''
            Reimplementação da função virtual que define o evento referente
            ao soltar do botão mouse após aperto.
        '''
        super(Node, self).mouseReleaseEvent(mouse_event)
        # Cria uma edge None para auxílio na execução.
        new_edge = None
        scene = self.scene()
        # Cria um elemento gráfico do tipo elipse, com tamanho definido pelo
        # retângulo QtCore.QRectF. Este elipse é adicionado na posição em que o
        # botão foi solto. Este elipse precisa ser removido ao final da função,
        # caso contrário ele ficará visível na cena.
        ell = QtGui.QGraphicsEllipseItem()
        ell.setRect(
            QtCore.QRectF(
                mouse_event.scenePos() - QtCore.QPointF(10, 10),
                QtCore.QSizeF(30, 30)))
        scene.addItem(ell)

        # O trecho a seguir implementa o caráter "Sticky" do nó conectivo.
        # Explicando: Se o nó só tiver uma extremidade ocupada e colidir com
        # um node que não seja outro nó conectivo, a linha "gruda" no item
        # colidido, estabelecendo uma ligação.
        if self.myItemType == Node.NoConectivo and len(self.edges) == 1:
            # Varre todos os itens que foram colididos com o elipse criado.
            # Isto permite que haja uma margem de colisão ao redor do nó.
            for item in scene.items():
                if ell.collidesWithItem(item):
                    if isinstance(item, Node):
                        if item.myItemType != Node.NoConectivo:
                            # Se o item for uma barra, ainda é preciso tratar
                            # o algoritmo! PENDÊNCIA.
                            if item.myItemType == Node.Barra:
                                scene.removeItem(ell)
                                return
                            # Não sendo o item uma barra, remove-se a linha
                            # do nó conectivo, e cria uma nova linha se liga
                            # diretamente ao item colidido.
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
        # Caso o item seja um Nó de Carga e não esteja conectado ainda, este
        # trecho do método implementa a característica "Sticky" do Nó de Carga
        # quando ele colide com uma linha.
        if self.myItemType == Node.NoDeCarga:
            # Se o Nó de Carga já estiver conectado, a função retorna.
            if len(self.edges) != 0:
                scene.removeItem(ell)
                return
            scene.removeItem(ell)
            if self.scene().myMode == 1:
                return
                # Se algum item da cena colidir com o elipse e este item não
                # for o próprio nó de carga, quebra a linha e adiciona o nó
                # de carga. Se o comprimento da linha for muito pequeno, isto
                # não é feito.
            for item in scene.items():
                if ell.collidesWithItem(item):
                    if isinstance(item, Edge) and not item.isUnderMouse():
                        if item.line().length() < 20:
                            return
                        break_mode = 3
                        pos = item.get_fraction(mouse_event.scenePos())
                        self.setPos(pos.x() - 5, pos.y() - 5)
                        scene.break_edge(item, break_mode, None, self)

        scene.removeItem(ell)
        return

    def mouseDoubleClickEvent(self, event):
        '''
            Reimplementação da função de duplo clique do mouse.
        '''
        # Limpa a seleção de qualquer objeto na cena.
        self.scene().clearSelection()
        # Seta o item como selecionado.
        self.setSelected(True)
        super(Node, self).mouseDoubleClickEvent(event)
        # Executa o Dialog de configuração dos elementos do Node.
        self.scene().launch_dialog()

    def adjust_in_grid(self, pos):
        '''
            Este método implementa uma grade invisível na cena, que limita o
            movimento dos Nodes para posições bem definidas.
        '''
        # Seta uma flag que indica que este item foi ajustado.
        self.adjusted = True
        # Ajuste de posição empírico
        item_x = pos.x() - 5
        item_y = pos.y() - 5
        if item_x == 0 or item_y == 0:
            return
        # Isola a centena da posição x e y do item, e.g se a posição x for
        # 384, centena_x = int(384/100) * 100 = 3 * 100. Todo o exemplo é aná-
        # logo para a posição y.
        centena_x = int(item_x / 100) * 100
        centena_y = int(item_y / 100) * 100
        # Calcula os residuais, que é a dezena+unidade. No nosso exemplo,
        # residual_x = 384 - 300 = 84
        residual_x = item_x - centena_x
        residual_y = item_y - centena_y
        # A posição de referência para a grade é a 0,0. Assim, definiu-se que
        # cada quadrado da grade possui 20x20 pixels. Sendo assim, o residual
        # calculado irá nos mostrar em que quadrado o item precisa ser
        # ajustado. No nosso exemplo, temos x = 384. Então a posição x deve
        # ser ajustada para 380, que se encontra no quadrado que compreende
        # 380 -> 400. Segue-se a seguinte regra:
        #  0 < residual < 10  -> Posição final = centena
        # 10 < residual < 20  -> Posição final = centena + 20
        # 20 < residual < 30  -> Posição final = centena + 20
        # 30 < residual < 40  -> Posição final = centena + 40
        # 40 < residual < 50  -> Posição final = centena + 40
        # 50 < residual < 60  -> Posição final = centena + 60
        # 60 < residual < 70  -> Posição final = centena + 60
        # 70 < residual < 80  -> Posição final = centena + 80
        # 80 < residual < 90  -> Posição final = centena + 80
        #      residual > 90  -> Posição final = centena + 100

        if residual_x > 10:
            if residual_x > 20:
                if residual_x > 30:
                    new_pos_x = centena_x + 40
                else:
                    new_pos_x = centena_x + 20
            else:
                new_pos_x = centena_x + 20
        else:
            new_pos_x = centena_x

        if residual_x > 40:
            if residual_x > 50:
                new_pos_x = centena_x + 60
            else:
                new_pos_x = centena_x + 40
        if residual_x > 60:
            if residual_x > 70:
                new_pos_x = centena_x + 80
            else:
                new_pos_x = centena_x + 60
        if residual_x > 80:
            if residual_x > 90:
                new_pos_x = centena_x + 100
            else:
                new_pos_x = centena_x + 80

        if residual_y > 10:
            if residual_y > 20:
                if residual_y > 30:
                    new_pos_y = centena_y + 40
                else:
                    new_pos_y = centena_y + 20
            else:
                new_pos_y = centena_y + 20
        else:
            new_pos_y = centena_y

        if residual_y > 40:
            if residual_y > 50:
                new_pos_y = centena_y + 60
            else:
                new_pos_y = centena_y + 40
        if residual_y > 60:
            if residual_y > 70:
                new_pos_y = centena_y + 80
            else:
                new_pos_y = centena_y + 60
        if residual_y > 80:
            if residual_y > 90:
                new_pos_y = centena_y + 100
            else:
                new_pos_y = centena_y + 80
        # Ajuste de posição devido à diferença de geometria.
        if self.myItemType == Node.NoDeCarga:
            new_pos_x += 6
            new_pos_y += 6
        return QtCore.QPointF(new_pos_x, new_pos_y)

    def contextMenuEvent(self, event):
        '''
            Método que reimplementa a função virtual do menu aberto pelo clique
            com botão direito.
        '''
        # Limpa a seleção dos itens da cena.
        self.scene().clearSelection()
        # Seta a flag do item como selecionado.
        self.setSelected(True)
        # Executa o menu, dependendo do tipo de item.
        self.myNodeMenu.exec_(event.screenPos())


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
        self.custom_dict = {'Corrente Nominal': 0, 'Capacidade de Interrupcao': 0, 'Sequencia':0}
        self.dict_prop = {}
        self.create_dict(100,4,4,'ABB')
        self.create_dict(150,5,3,'SEL')
        self.create_dict(200,6,3,'BOSCH')
        self.lista_no_conectivo = []


    def create_dict(self, corrente, capacidade, num_rel, padrao):
        prop = {'Corrente Nominal': corrente, 'Capacidade de Interrupcao': capacidade, 'Sequencia':num_rel}
        self.dict_prop[padrao] = prop


    def mousePressEvent(self, mouse_event):
        '''
            Este metodo define as acoes realizadas quando um evento do tipo
            mousePress e detectado no diagrama grafico
        '''
        super(SceneWidget, self).mousePressEvent(mouse_event)
        #print mouse_event.scenePos()
        self.pressPos = mouse_event.scenePos()
        self.break_mode = 2
        self.edge_broken = None
        # print "=========================Lista de Nós Conectivos=========================\n\n"
        # for no in self.lista_no_conectivo:
        #     print str(id(no)) + "\n"
        # print "=========================================================================\n\n"
        # for no in self.lista_no_conectivo:
        #     print "===============================NÓ CONECTIVO - " + str(id(no)) + "============\n\n"
        #     for no2 in no.terminal_list:
        #         print "terminal: " + str(id(no2)) + "\n" + "objeto: " + str(id(no2.parent)) + "\n" + "Posição: " + str(no2.parent.scenePos()) + "\n"
        #     print "=====================================================================\n\n"

        # print "--------------------------------------------------------------------------"



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

            
            

            item.setPos(item.adjust_in_grid(mouse_event.scenePos()))
            self.addItem(item)

            if self.myItemType == Node.Religador:
                item.setSelected(True)
                result = self.launch_dialog()
                item.setSelected(False)
                if result == 0:
                    self.removeItem(item)

            elif self.myItemType == Node.Barra:
                item.setSelected(True)
                result = self.launch_dialog()
                item.setSelected(False)
                if result == 0:
                    self.removeItem(item)
            elif self.myItemType == Node.Subestacao:
                item.setSelected(True)
                result = self.launch_dialog()
                item.setSelected(False)
                if result == 0:
                    self.removeItem(item)
                
            elif self.myItemType == Node.NoDeCarga:
                item.setSelected(True)
                result = self.launch_dialog()
                item.setSelected(False)
                if result == 0:
                    self.removeItem(item)

            #item.setPos(mouse_event.scenePos())
            comando = add_remove_command("Add", self, item)
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
            for item in self.items():
                if ell.collidesWithItem(item):
                    if isinstance(item, QtGui.QGraphicsEllipseItem) and not priority_on:
                        self.clearSelection()
                    elif isinstance(item, Node):
                        self.removeItem(ell)
                        self.clearSelection()
                        item.setSelected(True)
                    elif isinstance(item, Edge) and not priority_node:
                        self.removeItem(ell)
                        self.clearSelection()
                        item.setSelected(True)                    
                        return
            if ell.scene() == self:
                self.removeItem(ell)

        return

    def mouseMoveEvent(self, mouse_event):
        '''
            Este método define as acoes realizadas quando um evento do tipo
            mouseMove é detectado no diagrama grafico. Neste caso desenha uma
            linha quando o modo self.InsertLine está ativado
        '''
        if self.myMode == self.InsertLine and self.line:
            self.clearSelection()
            new_line = QtCore.QLineF(
                self.line.line().p1(), mouse_event.scenePos())
            self.line.setLine(new_line)
        elif self.myMode == self.MoveItem:
            super(SceneWidget, self).mouseMoveEvent(mouse_event)
            return
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
            if self.no != None:
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
                    elif isinstance(item, QtGui.QGraphicsEllipseItem) and not node_priority and not edge_priority:
                        self.end_item = Node(Node.NoConectivo, self.myLineMenu)
                        self.end_item.setPos(mouse_event.scenePos())
            self.removeItem(self.line)
            self.line = None
            self.removeItem(ell)
            print "checkpoint"

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
            if dist < 15:
                print "Erro: Comprimento da ligação muito pequeno!"
                return
            if self.edge_broken is not None and self.edge_broken.isPermanent:
                return

            if self.start_item.scene() == None:
                self.addItem(self.start_item)
            if self.end_item.scene() == None:
                self.addItem(self.end_item)

            edge = Edge(self.start_item, self.end_item, self.myLineMenu)
            self.addItem(edge)


            # # Adição de terminais e nós conectivos virtuais
            # no_conectivo_1 = NoConect([])
            # no_conectivo_2 = NoConect([])
            
            # if edge.w1.myItemType != Node.NoConectivo:

            #     if edge.w1.terminal1.connected:
            #         if edge.w1.terminal2.connected:
            #             pass
            #         else:
            #             no_conectivo_1.terminal_list.append(edge.w1.terminal2)
            #             edge.w1.terminal2.connect()
            #             no_conectivo_1.terminal_list.append(edge.terminal1)
            #             edge.terminal1.connect()
            #             self.lista_no_conectivo.append(no_conectivo_1)
            #             no_conectivo_1.define_no()
            #     else:
            #         no_conectivo_1.terminal_list.append(edge.w1.terminal1)
            #         edge.w1.terminal1.connect()
            #         no_conectivo_1.terminal_list.append(edge.terminal1)
            #         edge.terminal1.connect()
            #         self.lista_no_conectivo.append(no_conectivo_1)
            #         no_conectivo_1.define_no()

            # if edge.w2.myItemType != Node.NoConectivo:

            #     if edge.w2.terminal1.connected:
            #         if edge.w2.terminal2.connected:
            #             pass
            #         else:
            #             no_conectivo_2.terminal_list.append(edge.w2.terminal2)
            #             edge.w2.terminal2.connect()
            #             no_conectivo_2.terminal_list.append(edge.terminal2)
            #             edge.terminal2.connect()
            #             self.lista_no_conectivo.append(no_conectivo_2)
            #             no_conectivo_2.define_no()
            #     else:
            #         no_conectivo_2.terminal_list.append(edge.w2.terminal1)
            #         edge.w2.terminal1.connect()
            #         no_conectivo_2.terminal_list.append(edge.terminal2)
            #         edge.terminal2.connect()
            #         self.lista_no_conectivo.append(no_conectivo_2)
            #         no_conectivo_2.define_no()


            edge.set_color(QtCore.Qt.black)
            # self.addItem(edge.GhostRetItem)
            edge.update_position()
            #Teste de quebra de linha
            self.break_edge(self.edge_broken, self.break_mode, edge)


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
            # for item in self.selectedItems():
            #     if isinstance(item, Edge):
            #         # if item.w1.myItemType == Node.NoConectivo or item.w1.myItemType == Node.Barra:
            #         #     item.w1.setSelected(True)
            #         if item.w2.myItemType == Node.NoConectivo or item.w2.myItemType == Node.Barra:
            #             item.w2.setSelected(True)
        self.line = None
        self.itemInserted.emit(3)
        self.ghost = None
        super(SceneWidget, self).mouseReleaseEvent(mouse_event)

    def mouseDoubleClickEvent(self, mouse_event):
        
        for item in self.selectedItems():
            if isinstance(item, Node):
                item.setSelected(True)
                self.launch_dialog()
                item.setSelected(False)
                return
        ell = QtGui.QGraphicsEllipseItem()
        ell.setRect(QtCore.QRectF(mouse_event.scenePos() - QtCore.QPointF(10,10), QtCore.QSizeF(30,30)))
        self.addItem(ell)
        for item in self.items():
            if item.collidesWithItem(ell) and isinstance(item, Edge):
                if ell.scene() != None:
                    self.removeItem(ell)
                item.setSelected(True)
                self.launch_dialog()
                item.setSelected(False)
                return
            else:
                if ell.scene() != None:
                    self.removeItem(ell)

        #     Problema quando tenta-se modificar o texto dos componentes
    def keyPressEvent(self, event):
        key = event.key()
        if self.keyControlIsPressed == True:
            if key == QtCore.Qt.Key_Z:
                self.undoStack.undo()
            if key == QtCore.Qt.Key_Y:
                self.undoStack.redo()
        if key == QtCore.Qt.Key_Space:
            self.change_state()
        if key == QtCore.Qt.Key_Up:
            for item in self.selectedItems():
                item.moveBy(0, -5)
        elif key == QtCore.Qt.Key_Down:
            for item in self.selectedItems():
                item.moveBy(0, 5)
        elif key == QtCore.Qt.Key_Left:
            for item in self.selectedItems():
                item.moveBy(-5, 0)
        elif key == QtCore.Qt.Key_Right:
            for item in self.selectedItems():
                item.moveBy(5, 0)
        elif key == QtCore.Qt.Key_Space or key == QtCore.Qt.Key_Enter:
            pass
        elif key == QtCore.Qt.Key_Control:
            self.keyControlIsPressed = True
        elif key == QtCore.Qt.Key_Delete:
            self.delete_item()
        elif key == QtCore.Qt.Key_Escape:
            self.clearSelection()
        else:
            pass
            super(SceneWidget, self).keyPressEvent(event)
        return

    def keyReleaseEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_Control:
            self.keyControlIsPressed = False

    def break_edge(self, edge, mode, original_edge, insert = None):
        if mode == 3:
            break_point = insert 
        if mode == 2:
            command = add_remove_command("Add", self, original_edge)
            self.undoStack.push(command)
            return
        if mode == 0:
            break_point = self.start_item
        if mode == 1:
            break_point = self.end_item
        edge.w1.remove_edge(edge)
        edge.w2.remove_edge(edge)
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
        item.remove_edges()
        new_edge = Edge(w[0], w[1], self.myLineMenu)
        self.addItem(new_edge)
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

    def change_state(self):
        print "entrou"
        
        for item in self.selectedItems():
            if item.myItemType == Node.Religador:
                aviso = AvisoReligador(item.chave.normalOpen, item.chave.nome)
                if aviso.dialog.result() == 1: 
                    print item.chave.normalOpen
                    if item.chave.normalOpen == 1:               
                        item.chave.normalOpen = 0

                    elif item.chave.normalOpen == 0:
                        item.chave.normalOpen = 1
                    item.setSelected(False)
                    item.setSelected(True)
                    print item.chave.normalOpen
                else:
                    continue

    def create_actions(self):
        '''
            Este metodo cria as ações que serão utilizadas nos menus dos itens
            gráficos.
        '''
        self.propertysAction = QtGui.QAction(
            'Abrir/Fechar', self, shortcut='Enter',
            triggered=self.change_state)
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
            item.Noc = None
            if isinstance(item, Node):
                if item.myItemType != Node.NoConectivo:
                    lista = item.edges
                    if len(item.edges) >= 1:
                        item.Noc = Node(Node.NoConectivo, self.myLineMenu)
                        self.addItem(item.Noc)
                        item.Noc.setPos(item.scenePos() + QtCore.QPointF(20, 20))
                        for edge in lista:
                            if edge.w1 == item:
                                new_edge = Edge(item.Noc, edge.w2, self.myLineMenu)
                            else:
                                new_edge = Edge(item.Noc, edge.w1, self.myLineMenu)
                            self.addItem(new_edge)
                    item.remove_edges()
                if len(item.edges) > 2:
                    dialog = AvisoConexaoDialog()
                    return
                elif len(item.edges) == 2 and item.myItemType == Node.NoConectivo:
                    self.recover_edge(item)
            if isinstance(item, Edge):
                if item.w1.myItemType == Node.NoConectivo and len(item.w1.edges) <= 1:
                    self.removeItem(item.w1)
                if item.w2.myItemType == Node.NoConectivo and len(item.w2.edges) <= 1:
                    self.removeItem(item.w2)
                item.w1.remove_edge(item)
                item.w2.remove_edge(item)
                # self.removeItem(item.GhostRetItem)
            self.removeItem(item)
            command = add_remove_command("Remove", self, item)
            
            self.undoStack.push(command)



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
                        item.text_config = unicode(dialog.testeLineEdit.currentText())
                        if dialog.identificaOLineEdit.text() == "":
                            pass
                        else:
                            item.chave.nome = dialog.identificaOLineEdit.text()
                            item.text.setPlainText(dialog.identificaOLineEdit.text())
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
                    else:
                        return dialog.dialog.result()
                
            if isinstance(item, Node):
                if item.myItemType == Node.Barra:
                    dialog = BarraDialog(item)
                    if dialog.dialog.result() == 1:
                        
                        if dialog.nomeLineEdit.text() == "":
                            pass
                        else:
                            item.text.setPlainText(dialog.nomeLineEdit.text())
                            item.barra.nome = dialog.nomeLineEdit.text()
                        if dialog.fasesLineEdit.text() == "":
                            pass
                        else:
                            item.barra.phases = dialog.fasesLineEdit.text()
                    else:
                        return dialog.dialog.result()

            if isinstance(item, Node):
                if item.myItemType == Node.Subestacao:
                    dialog = SubstationDialog(item)
                    if dialog.dialog.result() == 1:
                        
                        if dialog.nomeLineEdit.text() == "":
                            pass
                        else:
                            item.text.setPlainText(dialog.nomeLineEdit.text())
                            item.substation.nome = dialog.nomeLineEdit.text()
                        if dialog.tpLineEdit.text() == "":
                            pass
                        else:
                            item.substation.tensao_primario = dialog.tpLineEdit.text()
                    else:
                        return dialog.dialog.result()

            if isinstance(item, Edge):
                print str(item.linha.id)
                dialog = ConductorDialog(item)
                if dialog.dialog.result() == 1:
                        if dialog.comprimentoLineEdit.text() == "":
                            pass
                        else:
                            item.linha.comprimento = dialog.comprimentoLineEdit.text()
                        if dialog.resistenciaLineEdit.text() == "":
                            pass
                        else:
                            item.linha.resistencia = dialog.resistenciaLineEdit.text()
                        if dialog.resistenciaZeroLineEdit.text() == "":
                            pass
                        else:
                            item.linha.resistencia_zero = dialog.resistenciaZeroLineEdit.text()
                        if dialog.reatanciaLineEdit.text() == "":
                            pass
                        else:
                            item.linha.reatancia = dialog.reatanciaLineEdit.text()
                        if dialog.reatanciaZeroLineEdit.text() == "":
                            pass
                        else:
                            item.linha.reatancia_zero = dialog.reatanciaZeroLineEdit.text()
                        if dialog.ampacidadeLineEdit.text() == "":
                            pass
                        else:
                            item.linha.ampacidade = dialog.ampacidadeLineEdit.text()
                else:
                        return dialog.dialog.result()
        
            if isinstance(item, Node):
                if item.myItemType == Node.NoDeCarga:
                    dialog = EnergyConsumerDialog(item)
                    if dialog.dialog.result() == 1:
                        
                        if dialog.identificaOLineEdit.text() == "":
                            pass
                        else:
                            item.text.setPlainText(dialog.identificaOLineEdit.text())
                            item.no_de_carga.nome = dialog.identificaOLineEdit.text()
                        if dialog.potNciaAtivaLineEdit.text() == "":
                            pass
                        else:
                            item.no_de_carga.potencia_ativa = dialog.potNciaAtivaLineEdit.text() 
                        if dialog.potNciaReativaLineEdit.text() == "":
                            pass
                        else:
                            item.no_de_carga.potencia_reativa = dialog.potNciaReativaLineEdit.text()
                    else:
                        return dialog.dialog.result()

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
                    item.w2.set_center(pos)
                    item.update_position()
                if w2_is_locked and not w1_is_locked:
                    pos = QtCore.QPointF(item.w1.center().x(), item.w2.center().y())
                    item.w1.set_center(pos)
                    item.update_position()

                else:
                    pos = QtCore.QPointF(item.w2.center().x(), item.w1.center().y())
                    item.w2.set_center(pos)
                    item.update_position()
        for item in self.items():
            if isinstance(item, Edge):
                item.update_position()

    def align_line_v(self):
        for item in self.selectedItems():
            if isinstance(item, Edge):
                if item.w1.x() < item.w2.x():
                    pos = QtCore.QPointF(item.w1.center().x(), item.w2.center().y())
                    item.w2.set_center(pos)
                else:
                    pos = QtCore.QPointF(item.w2.center().x(), item.w1.center().y())
                    item.w1.set_center(pos)
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

        max_pos = max(y_pos_list)
        min_pos = min(y_pos_list)
        mean_pos = max_pos - abs(max_pos - min_pos) / 2.0

        for item in self.selectedItems():
            if isinstance(item, Node):
                if item.Fixed is True:
                        mean_pos = item.pos().y()
                        item.mean_pos = mean_pos
                        first_priority = True


        for item in self.selectedItems():
            if isinstance(item, Node):
                pos = mean_pos

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
                    pos = pos + 17

                if item.myItemType == Node.NoDeCarga:
                    pos = pos + 15

                if item.myItemType == Node.Barra:
                    pos = pos_barra

                item.setY(pos)




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

class add_remove_command(QtGui.QUndoCommand):

    def __init__(self, mode, scene, item):
        super(add_remove_command, self).__init__(mode)
        self.mode = mode
        self.item = item
        self.scene = scene
        self.count = 0

    def redo(self):
        self.count += 1
        if self.count <= 1:
            return
        if self.mode == "Add":
            self.scene.addItem(self.item)
            self.scene.addItem(self.item.text)
        if self.mode == "Remove":
            self.scene.removeItem(self.item)

    def undo(self):
        if self.mode == "Add":
            self.scene.removeItem(self.item)


        if self.mode == "Remove":
            self.scene.addItem(self.item)
            if self.item.Noc != None:
                lista = self.item.Noc.edges    
                for edge in lista:
                    if edge.w1 == self.item.Noc:
                        new_edge = Edge(self.item, edge.w2, self.scene.myLineMenu)
                    else:
                        new_edge = Edge(self.item, edge.w1, self.scene.myLineMenu)
                    self.scene.addItem(new_edge)
                self.item.Noc.remove_edges()
                self.scene.removeItem(self.item.Noc)


                

# class add_remove_edge_break_command(QtGui.QUndoCommand):

#     def __init__(self, mode, scene, edge, edge_broken, break_mode):
#         super(add_remove_command,self).__init__(mode)
#         self.mode = mode
#         self.edge = edge
#         self.scene = scene
#         self.count = 0

#     def redo(self):
#         self.count += 1
#         if self.count <= 1:
#             return
#         if self.mode == "Add":
#             self.scene.addItem(edge)
#             self.scene.break_edge(edge_broken, break_mode, edge)

#     def undo(self):
#         if self.mode == "Add":
#             self.scene.removeItem(edge)
#             self.scene.reco

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    scene = SceneWidget()
    widget = ViewWidget(scene)
    widget.show()
    sys.exit(app.exec_())
