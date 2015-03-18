# -*- encoding: utf-8 -*-
from xml.etree import ElementTree
from xml.dom import minidom
from PySide import QtCore, QtGui
from graphics import Node, Edge
from bs4 import BeautifulSoup
from elementos import NoConect, Terminal



class DiagramToXML(ElementTree.Element):
    '''
        Esta classe possui as funções que armazenam as informações
        necessárias à reconstrução do diagrama grafico em um
        arquivo XML
    '''
    def __init__(self, scene):
        '''
            Função que inicializa o objeto criado pela classe DiagramToXML
        '''
        super(DiagramToXML, self).__init__('items')

        self.scene = scene
        lista = self.scene.items()
        lista.reverse()
        for item in self.scene.items():
            if isinstance(item, Node):
                CE = ElementTree.Element(
                    'CE', attrib={'type': str(item.myItemType)})
                id = ElementTree.Element('id')
                id.text = str(item.id)
                CE.append(id)

                x = ElementTree.Element('x')
                x.text = str(item.scenePos().x())
                CE.append(x)

                y = ElementTree.Element('y')
                y.text = str(item.scenePos().y())
                CE.append(y)

                width = ElementTree.Element('width')
                width.text = str(item.rect().width())
                CE.append(width)

                height = ElementTree.Element('height')
                height.text = str(item.rect().height())
                CE.append(height)

                self.append(CE)
        for item in lista:

            if isinstance(item, Edge):
                edge = ElementTree.Element('edge')
                w1 = ElementTree.Element('w1')
                w1.text = str(item.w1.id)

                w2 = ElementTree.Element('w2')
                w2.text = str(item.w2.id)

                edge.append(w1)
                edge.append(w2)
                self.append(edge)

    def write_xml(self, path):
        '''
            Função que cria o arquivo XML na localização indicada pelo
            argumento path
        '''
        xml_string = ElementTree.tostring(self)
        dom_element = (minidom.parseString(xml_string))
        f = open(path, 'w')
        f.write(dom_element.toprettyxml())
        f.close()



class XMLToDiagram():
    '''
        Classe que realiza a conversão do arquivo XML com as informações do 
        diagrama em um diagrama gráfico interativo.
    '''

    def __init__(self, scene, file_path):
        self.scene = scene
        self.file_path = file_path

        xml_tree = ElementTree.parse(self.file_path)
        xml_element = xml_tree.getroot()
        self.scene.clear()
        for child in xml_element:

            if child.tag == 'CE':

                if child.attrib['type'] == '0':
                    item = Node(
                        int(child.attrib['type']), self.scene.mySubstationMenu)
                    self.scene.addItem(item)
                    item.setPos(
                        float(child.find('x').text), float(
                            child.find('y').text))
                    item.id = int(child.find('id').text)

                elif child.attrib['type'] == '1':
                    item = Node(
                        int(child.attrib['type']), self.scene.myRecloserMenu)
                    item.id = int(child.find('id').text)
                    item.setPos(float(child.find('x').text), float(
                        child.find('y').text))
                    self.scene.addItem(item)
                elif child.attrib['type'] == '2':
                    item = Node(int(
                        child.attrib['type']), self.scene.myBusMenu)
                    item.setPos(float(child.find('x').text), float(
                        child.find('y').text))
                    item.id = int(child.find('id').text)
                    item.setRect(
                        0, 0, float(child.find('width').text), float(
                            child.find('height').text))
                    self.scene.addItem(item)

                elif child.attrib['type'] == '3':
                    item = Node(int(child.attrib['type']), None)
                    item.setPos(
                        float(child.find('x').text), float(
                            child.find('y').text))
                    item.id = int(child.find('id').text)
                    self.scene.addItem(item)

                elif child.attrib['type'] == '4':
                    item = Node(int(child.attrib['type']), None)
                    item.setPos(
                        float(child.find('x').text), float(
                            child.find('y').text))
                    item.id = int(child.find('id').text)
                    self.scene.addItem(item)

                elif child.attrib['type'] == '5':
                    item = Node(int(child.attrib['type']), None)
                    item.setPos(
                        float(child.find('x').text), float(
                            child.find('y').text))
                    item.id = int(child.find('id').text)
                    self.scene.addItem(item)

            elif child.tag == 'edge':
                for item in self.scene.items():
                    if isinstance(item, Node) and item.id == int(child.find('w1').text):
                        w1 = item
                    elif isinstance(item, Node) and item.id == int(child.find('w2').text):
                        w2 = item
                edge = Edge(w1, w2, self.scene.myLineMenu)
                self.scene.addItem(edge)
                edge.update_position()
                print "opa"


class CimXML():

    '''Classe que representa os dados dos componentes em padrão CIM'''

    def __init__(self, scene):
        self.scene = scene
        self.lista_no_conectivo = []
        self.lista_terminais = []
        self.montar_rede(scene)

        self.cim_xml = BeautifulSoup()

        for item in scene.items():
            if isinstance(item, Node):

                if item.myItemType == item.Religador:

                    tag_CE = self.cim_xml.new_tag("ConductingEquipment")
                    self.cim_xml.append(tag_CE)

                    tag_breaker = self.cim_xml.new_tag("Breaker")
                    tag_CE.append(tag_breaker)

                    tag_id = self.cim_xml.new_tag("mRID")
                    tag_id.append(str(item.id))
                    tag_breaker.append(tag_id)

                    tag_rc = self.cim_xml.new_tag("ratedCurrent")
                    tag_rc.append(str(item.chave.ratedCurrent))
                    tag_breaker.append(tag_rc)

                    tag_itt = self.cim_xml.new_tag("inTransitTime")
                    tag_itt.append(str(item.chave.inTransitTime))
                    tag_breaker.append(tag_itt)

                    tag_bc = self.cim_xml.new_tag("breakingCapacity")
                    tag_bc.append(str(item.chave.breakingCapacity))
                    tag_breaker.append(tag_bc)

                    tag_rs = self.cim_xml.new_tag("recloseSequences")
                    tag_rs.append(str(item.chave.recloseSequences))
                    tag_breaker.append(tag_rs)

                    tag_NO = self.cim_xml.new_tag("normalOpen")
                    tag_NO.append(str(item.chave.normalOpen))
                    tag_breaker.append(tag_NO)

                    tag_terminal1 = self.cim_xml.new_tag("terminal1")
                    tag_terminal1.append(str(item.terminal1.mRID))
                    tag_breaker.append(tag_terminal1)

                    tag_terminal2 = self.cim_xml.new_tag("terminal2")
                    tag_terminal2.append(str(item.terminal2.mRID))
                    tag_breaker.append(tag_terminal2)
                    
                    # tag_CE = self.cim_xml.new_tag("ConductingEquipment")
                    # self.cim_xml.append(tag_CE)

                    # tag_terminal = self.cim_xml.new_tag("terminal")
                    # tag_terminal.append(str(item.terminal1.mRID))
                    # tag_CE.append(tag_terminal)

                    # tag_CE = self.cim_xml.new_tag("ConductingEquipment")
                    # self.cim_xml.append(tag_CE)

                    # tag_terminal = self.cim_xml.new_tag("terminal")
                    # tag_terminal.append(str(item.terminal2.mRID))
                    # tag_CE.append(tag_terminal)
                    

        for item in scene.items():
            if isinstance(item, Node):

                if item.myItemType == item.Barra:

                    tag_CE = self.cim_xml.new_tag("ConductingEquipment")
                    self.cim_xml.append(tag_CE)

                    tag_barra = self.cim_xml.new_tag("busBarSection")
                    tag_CE.append(tag_barra)

                    tag_id = self.cim_xml.new_tag("mRID")
                    tag_id.append(str(item.id))
                    self.cim_xml.find("busBarSection").append(tag_id)

                    tag_phases = self.cim_xml.new_tag("phases")
                    tag_phases.append(str(item.barra.phases))
                    tag_barra.append(tag_phases)

                    tag_terminal1 = self.cim_xml.new_tag("terminal1")
                    tag_terminal1.append(str(item.terminal1.mRID))
                    tag_barra.append(tag_terminal1)

                    tag_terminal2 = self.cim_xml.new_tag("terminal2")
                    tag_terminal2.append(str(item.terminal2.mRID))
                    tag_barra.append(tag_terminal2)

                    # tag_CE = self.cim_xml.new_tag("ConductingEquipment")
                    # self.cim_xml.append(tag_CE)
                    
                    # tag_terminal = self.cim_xml.new_tag("terminal")
                    # tag_terminal.append(str(item.terminal1.mRID))
                    # tag_CE.append(tag_terminal)

                    # tag_CE = self.cim_xml.new_tag("ConductingEquipment")
                    # self.cim_xml.append(tag_CE)

                    # tag_terminal = self.cim_xml.new_tag("terminal")
                    # tag_terminal.append(str(item.terminal2.mRID))
                    # tag_CE.append(tag_terminal)
                    

        
        for item in scene.items():
            if isinstance(item, Node):

                if item.myItemType == item.Subestacao:

                    tag_CE = self.cim_xml.new_tag("ConductingEquipment")
                    self.cim_xml.append(tag_CE)

                    tag_substation = self.cim_xml.new_tag("Substation")
                    tag_CE.append(tag_substation)

                    tag_id = self.cim_xml.new_tag("mRID")
                    tag_id.append(str(item.id))
                    self.cim_xml.find("Substation").append(tag_id)

                    tag_terminal1 = self.cim_xml.new_tag("terminal1")
                    tag_terminal1.append(str(item.terminal1.mRID))
                    tag_substation.append(tag_terminal1)

                    tag_terminal2 = self.cim_xml.new_tag("terminal2")
                    tag_terminal2.append(str(item.terminal2.mRID))
                    tag_substation.append(tag_terminal2)

                    # tag_CE = self.cim_xml.new_tag("ConductingEquipment")
                    # self.cim_xml.append(tag_CE)
                    
                    # tag_terminal = self.cim_xml.new_tag("terminal")
                    # tag_terminal.append(str(item.terminal1.mRID))
                    # tag_CE.append(tag_terminal)

                    # tag_CE = self.cim_xml.new_tag("ConductingEquipment")
                    # self.cim_xml.append(tag_CE)

                    # tag_terminal = self.cim_xml.new_tag("terminal")
                    # tag_terminal.append(str(item.terminal2.mRID))
                    # tag_CE.append(tag_terminal)    

        for item in scene.items():
            if isinstance(item, Node):

                if item.myItemType == item.NoDeCarga:

                    tag_CE = self.cim_xml.new_tag("ConductingEquipment")
                    self.cim_xml.append(tag_CE)

                    tag_energyConsumer = self.cim_xml.new_tag("EnergyConsumer")
                    tag_CE.append(tag_energyConsumer)
                    
                    tag_id = self.cim_xml.new_tag("mRID")
                    tag_id.append(str(item.id))
                    self.cim_xml.find("EnergyConsumer").append(tag_id)

                    tag_terminal1 = self.cim_xml.new_tag("terminal1")
                    tag_terminal1.append(str(item.terminal1.mRID))
                    tag_energyConsumer.append(tag_terminal1)

                    tag_terminal2 = self.cim_xml.new_tag("terminal2")
                    tag_terminal2.append(str(item.terminal2.mRID))
                    tag_energyConsumer.append(tag_terminal2)

                    # tag_CE = self.cim_xml.new_tag("ConductingEquipment")
                    # self.cim_xml.append(tag_CE)
                    
                    # # tag_terminal = self.cim_xml.new_tag("terminal")
                    # # tag_terminal.append(str(item.terminal1.mRID))
                    # # tag_CE.append(tag_terminal)

                    # tag_CE = self.cim_xml.new_tag("ConductingEquipment")
                    # self.cim_xml.append(tag_CE)

                    # tag_terminal = self.cim_xml.new_tag("terminal")
                    # tag_terminal.append(str(item.terminal2.mRID))
                    # tag_CE.append(tag_terminal)

        for item in scene.items():
            if isinstance(item, Edge):

                    tag_CE = self.cim_xml.new_tag("ConductingEquipment")
                    self.cim_xml.append(tag_CE)

                    tag_conductor = self.cim_xml.new_tag("Conductor")
                    tag_CE.append(tag_conductor)
                    
                    tag_id = self.cim_xml.new_tag("mRID")
                    tag_id.append(str(item.linha.id))
                    self.cim_xml.find("Conductor").append(tag_id)

                    tag_length = self.cim_xml.new_tag("length")
                    tag_length.append(str(item.linha.comprimento))
                    self.cim_xml.find("Conductor").append(tag_length)

                    tag_r = self.cim_xml.new_tag("r")
                    tag_r.append(str(item.linha.resistencia))
                    self.cim_xml.find("Conductor").append(tag_r)

                    tag_r0 = self.cim_xml.new_tag("r0")
                    tag_r0.append(str(item.linha.resistencia_zero))
                    self.cim_xml.find("Conductor").append(tag_r0)

                    tag_x = self.cim_xml.new_tag("x")
                    tag_x.append(str(item.linha.reatancia))
                    self.cim_xml.find("Conductor").append(tag_x) 

                    tag_x0 = self.cim_xml.new_tag("x0")
                    tag_x0.append(str(item.linha.reatancia_zero))
                    self.cim_xml.find("Conductor").append(tag_x0)

                    tag_currentLimit = self.cim_xml.new_tag("currentLimit")
                    tag_currentLimit.append(str(item.linha.ampacidade))
                    self.cim_xml.find("Conductor").append(tag_currentLimit)                   

                    tag_terminal1 = self.cim_xml.new_tag("terminal1")
                    tag_terminal1.append(str(item.terminal1.mRID))
                    tag_conductor.append(tag_terminal1)

                    tag_terminal2 = self.cim_xml.new_tag("terminal2")
                    tag_terminal2.append(str(item.terminal2.mRID))
                    tag_conductor.append(tag_terminal2)

                    # tag_CE = self.cim_xml.new_tag("ConductingEquipment")
                    # self.cim_xml.append(tag_CE)
                    
                    # tag_terminal = self.cim_xml.new_tag("terminal")
                    # tag_terminal.append(str(item.terminal1.mRID))
                    # tag_CE.append(tag_terminal)

                    # tag_CE = self.cim_xml.new_tag("ConductingEquipment")
                    # self.cim_xml.append(tag_CE)

                    # tag_terminal = self.cim_xml.new_tag("terminal")
                    # tag_terminal.append(str(item.terminal2.mRID))
                    # tag_CE.append(tag_terminal)

        # for terminal in self.lista_terminais:            
        #     tag_CE = self.cim_xml.new_tag("ConductingEquipment")
        #     self.cim_xml.append(tag_CE)

        #     tag_mRID = self.cim_xml.new_tag("mRID")
        #     tag_mRID.append(str(terminal.mRID))

        #     tag_terminal = self.cim_xml.new_tag("terminal")
        #     tag_terminal.append(tag_mRID)
        #     tag_CE.append(tag_terminal)

        for no in self.lista_no_conectivo:
            tag_mRID = self.cim_xml.new_tag("mRID")
            tag_mRID.append(str(id(no)))

            tag_no_conectivo = self.cim_xml.new_tag("ConnectivityNode")
            tag_no_conectivo.append(tag_mRID)

            self.cim_xml.append(tag_no_conectivo)

            
            for terminal in no.terminal_list:
                tag_terminal = self.cim_xml.new_tag("terminal")
                tag_mRID_terminal = self.cim_xml.new_tag("mRID")
                tag_mRID_terminal.append(str(terminal.mRID))
                tag_terminal.append(tag_mRID_terminal)
                tag_no_conectivo.append(tag_terminal)  



            




    def write_xml(self, path):
        '''
            Função que cria o arquivo XML na localização indicada pelo
            argumento path
        '''
        f = open(path, 'w')
        f.write(self.cim_xml.prettify())
        f.close()


    def montar_rede(self, scene):

        for item in self.scene.items():
            if isinstance(item, Node):
                if item.myItemType != Node.NoConectivo and item.myItemType != Node.Barra:
                    item.terminal1 = Terminal(item)
                    item.terminal2 = Terminal(item)
                    self.lista_terminais.append(item.terminal1)
                    self.lista_terminais.append(item.terminal2)

                if item.myItemType == Node.Barra:
                    for i in range(len(item.edges)):
                        terminal = Terminal(item)
                        item.terminals.append(terminal)
                        self.lista_terminais.append(terminal)
            if isinstance(item, Edge):
                item.terminal1 = Terminal(item)
                item.terminal2 = Terminal(item)
                self.lista_terminais.append(item.terminal1)
                self.lista_terminais.append(item.terminal1)

        for edge in self.scene.items():
            if isinstance(edge, Edge):
                no_conectivo_1 = NoConect([])
                no_conectivo_2 = NoConect([])
                print "start"

                # Ligação do Nó Conectivo relativo à ligação do terminal de w1 com o terminal 1 da linha - CONVENÇÃO!
                if edge.w1.myItemType != Node.NoConectivo and edge.w1.myItemType != Node.Barra and edge.w2.myItemType != Node.Barra:

                    print "w1 is not NoC"
                    if edge.w1.terminal1.connected:
                        if edge.w1.terminal2.connected:
                            pass
                        else:
                            no_conectivo_1.terminal_list.append(edge.w1.terminal2)
                            edge.w1.terminal2.connect()
                            no_conectivo_1.terminal_list.append(edge.terminal1)
                            edge.terminal1.connect()
                            self.lista_no_conectivo.append(no_conectivo_1)
                    else:
                        no_conectivo_1.terminal_list.append(edge.w1.terminal1)
                        edge.w1.terminal1.connect()
                        no_conectivo_1.terminal_list.append(edge.terminal1)
                        edge.terminal1.connect()
                        self.lista_no_conectivo.append(no_conectivo_1)
                elif edge.w1.myItemType == Node.NoConectivo and edge.w1.con_lock is False:
                    print "w1 is noC"
                    edge.w1.con_lock = True

                    
                    print len(edge.w1.edges)
                    no_conectivo = NoConect([])  
                    print id(no_conectivo.terminal_list)                 
                    for derivation in edge.w1.edges:
                        
                        if derivation.terminal1.connected:
                            print "cp1"
                            if derivation.terminal2.connected:
                                pass
                            else:
                                no_conectivo.terminal_list.append(derivation.terminal2)
                                derivation.terminal2.connect()
                        else:
                            print "cp2"
                            no_conectivo.terminal_list.append(derivation.terminal1)
                            derivation.terminal1.connect()
                    self.lista_no_conectivo.append(no_conectivo)

                elif edge.w1.myItemType == Node.Barra:
                    for terminal in edge.w1.terminals:
                        no_conectivo = NoConect([])
                        if terminal.connected:
                            continue
                        else:
                            no_conectivo.terminal_list.append(terminal)
                            terminal.connect()
                            if edge.w2.terminal1.connected:
                                if edge.w2.terminal2.connected:
                                    pass
                                else:
                                    no_conectivo.terminal_list.append(edge.w2.terminal2)
                                    edge.w2.terminal2.connect()
                            else:
                                no_conectivo.terminal_list.append(edge.w2.terminal1)
                                edge.w2.terminal1.connect()
                            self.lista_no_conectivo.append(no_conectivo)
                            break


                # Ligação do Nó Conectivo relativo à ligação do terminal de w2 com o terminal 2 da linha - CONVENÇÃO!
                if edge.w2.myItemType != Node.NoConectivo and edge.w2.myItemType != Node.Barra and edge.w1.myItemType != Node.Barra:
                    print "w2 is not NoC"
                    if edge.w2.terminal1.connected:
                        if edge.w2.terminal2.connected:
                            pass
                        else:
                            no_conectivo_2.terminal_list.append(edge.w2.terminal2)
                            edge.w2.terminal2.connect()
                            no_conectivo_2.terminal_list.append(edge.terminal2)
                            edge.terminal2.connect()
                            self.lista_no_conectivo.append(no_conectivo_2)
                    else:
                        no_conectivo_2.terminal_list.append(edge.w2.terminal1)
                        edge.w2.terminal1.connect()
                        no_conectivo_2.terminal_list.append(edge.terminal2)
                        edge.terminal1.connect()
                        self.lista_no_conectivo.append(no_conectivo_2)

                elif edge.w2.myItemType == Node.NoConectivo and edge.w2.con_lock is False:
                    print "w2 is noC"
                    edge.w2.con_lock = True
                    no_conectivo = NoConect([])
                    print id(no_conectivo.terminal_list)  
                    
                    for derivation in edge.w2.edges:
                        
                        if derivation.terminal1.connected:
                            if derivation.terminal2.connected:
                                pass
                            else:
                                no_conectivo.terminal_list.append(derivation.terminal2)
                                derivation.terminal2.connect()
                        else:
                            no_conectivo.terminal_list.append(derivation.terminal1)
                            derivation.terminal1.connect()
                            
                    self.lista_no_conectivo.append(no_conectivo)

                elif edge.w2.myItemType == Node.Barra:
                    for terminal in edge.w2.terminals:
                        no_conectivo = NoConect([])
                        if terminal.connected:
                            continue
                        else:
                            no_conectivo.terminal_list.append(terminal)
                            terminal.connect()
                            if edge.w1.terminal1.connected:
                                if edge.w1.terminal2.connected:
                                    pass
                                else:
                                    no_conectivo.terminal_list.append(edge.w1.terminal2)
                                    edge.w1.terminal2.connect()
                            else:
                                no_conectivo.terminal_list.append(edge.w1.terminal1)
                                edge.w1.terminal1.connect()
                            self.lista_no_conectivo.append(no_conectivo)
                            break

                print "end"


        print "=========================Lista de Nós Conectivos=========================\n\n"
        for no in self.lista_no_conectivo:
            print str(id(no)) + "\n"
        print "=========================================================================\n\n"
        for no in self.lista_no_conectivo:
            print "===============================NÓ CONECTIVO - " + str(id(no)) + "============\n\n"
            for no2 in no.terminal_list:
                print "terminal: " + str(id(no2)) + "\n" + "objeto: " + str(id(no2.parent)) + "\n" + "Posição: " + str(no2.parent.scenePos()) + "\n"
            print "=====================================================================\n\n"

        print "--------------------------------------------------------------------------"




