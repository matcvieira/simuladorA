# -*- encoding: utf-8 -*-
from bs4 import BeautifulSoup
from xml.etree import ElementTree
from xml.dom import minidom



class Bridge(object):
    def __init__(self, cim_path):

        cim_path = cim_path
        xml_cim = BeautifulSoup(open(cim_path))
        #print xml_cim.prettify()
        xml_rnp = BeautifulSoup()
        tag_rede = xml_rnp.new_tag("rede")
        tag_elementos = xml_rnp.new_tag("elementos")
        tag_rede.append(tag_elementos)
        xml_rnp.append(tag_rede)

        # Representação de todos os religadores

        for breaker in xml_cim.findAll('breaker'):
            mrid = breaker.find('mrid').text
            nome = str(mrid)[10:18]
            estado = breaker.find('normalopen').text
            if estado == True:
                estado = "fechado"
            else:
                estado = "aberto"
            chave = xml_rnp.new_tag("chave")
            chave["nome"] = nome
            chave["estado"] = estado
            tag_elementos.append(chave)

        # Representação de todos os nós de carga

        for no_carga in xml_cim.findAll('energyconsumer'):
            nome = no_carga.find('mrid').text
            potencia_ativa = no_carga.find('pfixed').text
            potencia_reativa = no_carga.find('qfixed').text

            no = xml_rnp.new_tag("no")
            no["nome"] = nome[10:18]

            potencia_ativa_tag = xml_rnp.new_tag("potencia")
            potencia_ativa_tag["tipo"] = "ativa"
            potencia_ativa_tag["multip"] = "k"
            potencia_ativa_tag["unid"] = "W"
            potencia_ativa_tag.append(str(potencia_ativa))

            potencia_reativa_tag = xml_rnp.new_tag("potencia")
            potencia_reativa_tag["tipo"] = "reativa"
            potencia_reativa_tag["multip"] = "k"
            potencia_reativa_tag["unid"] = "VAr"
            potencia_reativa_tag.append(str(potencia_reativa))

            no.append(potencia_ativa_tag)
            no.append(potencia_reativa_tag)

            tag_elementos.append(no)

        # Representação de todos os trechos

        for trecho in xml_cim.findAll("conductor"):
            trecho_tag = xml_rnp.new_tag("trecho")
            nome = no_carga.find('mrid').text

            trecho_tag["nome"] = nome[10:18]

            comprimento = xml_rnp.new_tag('comprimento')
            comprimento["multip"] = "k"
            comprimento ["unid"] = "m"
            comprimento.append(trecho.find('length').text)

            trecho_tag.append(comprimento)
            tag_elementos.append(trecho_tag)

        # Definição dos setores

        # Definir lista geral de todos os terminais com seus mrid's
        self.lista_terminais = xml_cim.findAll("terminal")
        for terminal in self.lista_terminais:
            terminal.marcado = False
        # Definir lista geral de todos os nós conectivos com seus mrid's
        self.lista_nosconect = xml_cim.findAll("connectivitynode")
        # Definir a lista de barras
        lista_barras = xml_cim.findAll("busbarsection")
        # Começar um caminho a partir de uma barra
        terminais_0 = xml_cim.find("busbarsection").findAll('terminal')
        count = 0
        setores = []
        fim = False
        







           


        self.xml_final = xml_rnp
        self.save_file('home/mateus/Desktop/xml_rnp')

    def achar_terminal_noc(self, terminal):
        lista = []
        for noc in self.lista_nosconect:
            lista_terminais = noc.findAll('terminal')
            for terminal_eq in lista_terminais:
                if terminal.find('mrid') == terminal_eq.find('mrid'):
                    print "igual"
                else:
                    lista.append(terminal_eq)
        return lista

    def achar_parent(self, terminal):
        for item in self.lista_terminais:
            if terminal.find('mrid') == item.find('mrid') and item.parent.name != 'connectivitynode':
                parent = item.parent
        return parent


    def save_file(self, path):
        f = open('/home/mateus/Desktop/xml_rnp', 'w')
        f.write(self.xml_final.prettify(formatter = "xml"))

        

bridge = Bridge("/home/mateus/Desktop/rede2CIM")
#print bridge.xml_final.prettify()
            

        


