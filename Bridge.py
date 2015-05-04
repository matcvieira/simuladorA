# -*- encoding: utf-8 -*-
from bs4 import BeautifulSoup
from xml.etree import ElementTree
from xml.dom import minidom

class Setor(object):
    def __init__(self):
        self.vizinhos = []
        self.nos = []



class Bridge(object):
    def __init__(self, cim_path):

        cim_path = cim_path
        self.xml_cim = BeautifulSoup(open(cim_path))
        #print self.xml_cim.prettify()
        xml_rnp = BeautifulSoup()
        tag_rede = xml_rnp.new_tag("rede")
        tag_elementos = xml_rnp.new_tag("elementos")
        tag_topologia = xml_rnp.new_tag("topologia")
        tag_rede.append(tag_elementos)
        tag_rede.append(tag_topologia)
        xml_rnp.append(tag_rede)

        # Representação de todos os religadores

        for breaker in self.xml_cim.findAll('breaker'):
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
        for no_carga in self.xml_cim.findAll('energyconsumer'):
            no = xml_rnp.new_tag("no")
            nome = no_carga.find('mrid').text
            potencia_ativa = no_carga.find('pfixed').text
            potencia_reativa = no_carga.find('qfixed').text

            
            no["nome"] = str(no_carga.find('label').text)[3:5]

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

        for trecho in self.xml_cim.findAll("conductor"):
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
        self.lista_terminais = self.xml_cim.findAll("terminal")
        # Definir lista geral de todos os nós conectivos com seus mrid's
        self.lista_nosconect = self.xml_cim.findAll("connectivitynode")
        # Definir a lista de barras
        # lista_barras = self.xml_cim.findAll("busbarsection")
        
        

        for substation in self.xml_cim.findAll('substation'):
            substation_tag = xml_rnp.new_tag('subestacao')
            substation_tag["nome"] = str(substation.find('mrid').text)[10:18]
            tag_elementos.append(substation_tag)
        print "--------------------------------------------------------------------------------"
        print "VIZINHANÇAS"
        self.lista_barras = []
        self.lista_nos_de_carga = self.xml_cim.findAll('energyconsumer')
        
        print "VIZINHOS: "
        for no in self.lista_nos_de_carga:
            (vizinhos, chaves) = self.definir_vizinhos(no, 0)
            no.vizinhos = vizinhos
            no.chaves = chaves


        for no in self.lista_barras:
            (vizinhos, chaves) = self.definir_vizinhos(no, 1)
            no.vizinhos = vizinhos
            no.chaves = chaves

        for no in self.lista_barras:
            tag_elemento_no = xml_rnp.new_tag("elemento")
            tag_elemento_no["nome"] = str(no.find('label').text)[3:5]
            tag_elemento_no["tipo"] = "no"            
            tag_vizinhos = xml_rnp.new_tag("vizinhos")
            tag_chaves = xml_rnp.new_tag("chaves")
            tag_elemento_no.append(tag_vizinhos)
            tag_elemento_no.append(tag_chaves)
            for vizinho in no.vizinhos:
                tag_vizinho_no = xml_rnp.new_tag("no")
                tag_vizinho_no["nome"] = str(vizinho.find('label').text)[3:5]
                tag_vizinhos.append(tag_vizinho_no)
            for chave in no.chaves:
                tag_chave = xml_rnp.new_tag("chave")
                tag_chave["nome"] = str(chave.find('mrid').text)[10:18]
                tag_chaves.append(tag_chave)
            tag_topologia.append(tag_elemento_no)

        # for no in self.lista_nos_de_carga:
        #     # print "VIZINHOS DE " + str(no.find('label').text)
        #     for vizinho in no.vizinhos:
        #         print str(vizinho.find('label').text)
        #     print "CHAVES: "
        #     for chave in no.chaves:
        #         print str(chave.find('mrid').text)
        for no in self.lista_nos_de_carga:
            tag_elemento_no = xml_rnp.new_tag("elemento")
            tag_elemento_no["nome"] = str(no.find('label').text)[3:5]
            tag_elemento_no["tipo"] = "no"            
            tag_vizinhos = xml_rnp.new_tag("vizinhos")
            tag_chaves = xml_rnp.new_tag("chaves")
            tag_elemento_no.append(tag_vizinhos)
            tag_elemento_no.append(tag_chaves)
            for vizinho in no.vizinhos:
                tag_vizinho_no = xml_rnp.new_tag("no")
                tag_vizinho_no["nome"] = str(vizinho.find('label').text)[3:5]
                tag_vizinhos.append(tag_vizinho_no)
            for chave in no.chaves:
                tag_chave = xml_rnp.new_tag("chave")
                tag_chave["nome"] = str(chave.find('mrid').text)[10:18]
                tag_chaves.append(tag_chave)
            tag_topologia.append(tag_elemento_no)

        setores = self.definir_setores()

        for barra in self.lista_barras:
            setor = Setor()
            setor.nos.append(barra)
            barra.setor = setor
            barra.setor.nome = str(barra.find('label').text)[3:5]
            print barra.setor.nome
            setores.append(setor)


        for setor in setores:

            setor.vizinhos =[]

            setor_tag = xml_rnp.new_tag("setor")
            if setor.nos[0].name == "busbarsection":
                setor_tag["nome"] = str(setor.nos[0].find('label').text)[3:5]
            else:
                setor_tag["nome"] = setor.nome
            tag_elementos.append(setor_tag)

        lista_chaves = self.xml_cim.findAll('breaker')

        for no in self.lista_nos_de_carga:
            for no2 in no.vizinhos:
                # print str(no2.find('label').text)[3:5]
                if no.setor != no2.setor:
                    no.setor.vizinhos.append(no2.setor)

        for no in self.lista_barras:
            for no2 in no.vizinhos:
                if no.setor != no2.setor:
                    no.setor.vizinhos.append(no2.setor)

        for setor in setores:
            tag_elemento_setor = xml_rnp.new_tag("elemento")
            tag_elemento_setor["tipo"] = "setor"
            tag_elemento_setor["nome"] = setor.nome
            tag_vizinhos = xml_rnp.new_tag("vizinhos")
            tag_nos = xml_rnp.new_tag("nos")
            tag_elemento_setor.append(tag_vizinhos)
            tag_elemento_setor.append(tag_nos)
            for vizinho in setor.vizinhos:
                tag_setor = xml_rnp.new_tag("setor")
                tag_setor["nome"] = vizinho.nome
                tag_vizinhos.append(tag_setor)
            for no in setor.nos:
                tag_no = xml_rnp.new_tag("no")
                tag_no["nome"] = str(no.find('label').text)[3:5]
                tag_nos.append(tag_no)
            tag_topologia.append(tag_elemento_setor)



        

        

        
        















        



                    


        







           


        self.xml_final = xml_rnp
        self.save_file('home/mateus/Desktop/rede2CIM')

    def no_percorrido(self, no):
        for item in self.nos_percorridos:
            if no == item:
                return True
        return False

    def religador_usado(self, religador):
        for item in self.lista_religadores_usados:
            if religador == item:
                return True
        return False

    def no_raiz(self, no):
        for item in self.nos_raiz:
            if no == item:
                return True
        return False

    def no_setor(self, no, setor):
        if setor.nos == []:
            print "False"
            return False
        for item in setor.nos:
            if no == item:
                return True
        return False

    def achar_terminal_noc(self, terminal):
        lista = []
        for noc in self.lista_nosconect:
            lista_terminais = noc.findAll('terminal')
            for elemento in lista_terminais:
                if elemento.find('mrid') == terminal.find('mrid'):
                    no_achado = noc
                    return no_achado

    def achar_parent(self, terminal):
        for item in self.lista_terminais:
            if terminal.find('mrid') == item.find('mrid') and item.parent.name != 'connectivitynode':
                parent = item.parent
                return parent

    def is_vizinho(self, no, no_vizinho):
        for item in no.vizinhos:
            if item == no_vizinho:
                return True
        return False

    def is_chave(self, no, chave):
        for item in no.chaves:
            if item == chave:
                return True
        return False

    def is_lista_barras(self, barra):
        for item in self.lista_barras:
            if item == barra:
                return True
        return False

    def setor_pertence(self, breaker, setor):
        for item in breaker.setores:
            if item == setor:
                return True
        return False


    def definir_vizinhos(self, no, mode):
         # Começar um caminho a partir de uma barra
        no_original = no
        no_raiz_encontrado = False
        no_rot = no
        no_original.vizinhos = []
        no_original.chaves = []
        fim = False
        terminal_counter = 0

        for item in self.xml_cim.findAll('energyconsumer'):
            item.counter = 0
            count = 0
            for item2 in item.findAll('terminal'):
                count += 1
            item.number = count

        for item in self.xml_cim.findAll('busbarsection'):
            item.counter = 0
            count = 0
            for item2 in item.findAll('terminal'):
                count += 1
            item.number = count
        count = 0
        # reset_counter = 0
        
        reset_counter = 0
        while terminal_counter < no_original.number:
            print "Nó Inicial: " + str(no_rot.name)
            print no_rot.number
            if no_rot.name == "energyconsumer":
                print "Label: " + str(no_rot.find('label'))
            if no_rot.name == "breaker":
                terminal_counter += 1
                print "ID: " + str(no_rot.find('mrid'))
            # Loop geral: Varre todos os terminais do nó
            lista_base = no_rot.findAll('terminal')
            for terminal in lista_base:
                print "Contador Interno: " + str(count)
                count = count + 1

                # Chama a função que acha o nó conectivo a que este terminal está associado
                no_conectivo = self.achar_terminal_noc(terminal)
                # Lista todos os terminais que o nó conectivo achado possui
                lista_conexoes = no_conectivo.findAll('terminal')
                # Loop interno: varre todos os terminais do referido nó conectivo, excetuando
                # o próprio terminal analisado, obviamente. Ou seja, o objetivo é descobrir com
                # que terminais o terminal em questão se conecta.
                

                for conexao in lista_conexoes:
                    if conexao.find('mrid') != terminal.find('mrid'):
                        # print conexao
                        # Chama a função que acha a que tipo de nó pertence o terminal conectado
                        # e.g Religador, Barra, Nó de Carga.
                        parent_conexao = self.achar_parent(conexao)
                        print "Nó Vizinho: " + str(parent_conexao.name)
                        # print parent_conexao
                        # Analisa os casos possíveis

                        # if parent_conexao.name == 'breaker':
                        #     setores.append(setor)
                        #     setor = Setor()

                        # Se o item conectado ao nó raiz for um condutor, obviamente existe um nó
                        # em seguida. Precisa-se achar e identificar este nó.
                        if parent_conexao.name == 'conductor':
                            print "Condutor ID:" + str(parent_conexao.find('mrid'))
                        # Varre todos os terminais (2) do condutor, excetuando-se o próprio terminal
                        # analisado (primeiro extremo do condutor). O objetivo é encontrar o terminal
                        # referente ao segundo extremo do condutor.
                            for no in parent_conexao.findAll('terminal'):
                                
                                if no.find('mrid') != conexao.find('mrid'):
                                    # print "Terminal:"
                                    # print no
                        # Acha o nó conectivo referente a este terminal
                                    no_conectivo_2 = self.achar_terminal_noc(no)
                                    # print "No conectivo:"
                                    # print no_conectivo_2
                        # Lista todos terminais deste nó conectivo. O objetivo é encontrar qual nó
                        # está conectado na outra extremidade do condutor.
                                    lista_conexoes_2 = no_conectivo_2.findAll('terminal')
                        # Varre todos os terminais deste nó conectivo, excetuando-se o próprio terminal
                        # analisado, obviamente.
                                    for conexao2 in lista_conexoes_2:
                                        # print "Terminal do No:" + str(conexao2.find('mrid'))
                                        if conexao2.find('mrid') != no.find('mrid'):
                                            parent_conexao2 = self.achar_parent(conexao2)
                                            print "Nó Final: " + str(parent_conexao2.name)

                if parent_conexao.name == "substation":
                    terminal_counter += 1
                    continue
                if parent_conexao.name == "breaker":
                    if self.is_chave(no_original, parent_conexao) == False:
                        no_original.chaves.append(parent_conexao)
                        no_rot = parent_conexao
                        break
                    else:
                        continue
                if parent_conexao.name == 'busbarsection':
                    if mode == 1:
                        continue
                    no_original.vizinhos.append(parent_conexao)
                    if self.is_lista_barras(parent_conexao) == False:
                        self.lista_barras.append(parent_conexao)
                        no_rot = no_original
                        continue
                    else:
                        break
                
                if parent_conexao2.name == "breaker":
                    print "ID: " + str(parent_conexao2.find('mrid'))
                    if no_rot.name == "breaker":
                        continue
                    if self.is_chave(no_original, parent_conexao2) == True:
                        print "Já é chave"
                        continue
                    else:
                        print "Nova chave!"
                        no_original.chaves.append(parent_conexao2)
                        no_rot = parent_conexao2
                        break
                
                if parent_conexao2.name == "energyconsumer":
                    print "Label: " + str(parent_conexao2.find('label'))
                    if no_rot.name == "breaker":
                        if parent_conexao2 == no_original:                            
                            continue
                        else:
                            print "Novo vizinho depois de um Breaker!"
                            no_original.vizinhos.append(parent_conexao2)
                            no_rot = no_original
                            break

                    if no_rot.name == "energyconsumer":
                        if parent_conexao2 == no_rot:
                            continue
                        if self.is_vizinho(no_original, parent_conexao2) == False:
                            print "Vizinho Adicionado!"
                            no_original.vizinhos.append(parent_conexao2)
                            terminal_counter += 1
            print "--------------------------------------------------------------------------------------------"
        print "FIM"
        return (no_original.vizinhos, no_original.chaves)

    def definir_setores(self):

        for terminal in self.lista_terminais:
            terminal.marcado = False
        for item in self.xml_cim.findAll('breaker'):
            item.setores = []
            item.counter = 0
            count = 0
            for item2 in item.findAll('terminal'):
                count += 1
            item.number = count
        for item in self.xml_cim.findAll('busbarsection'):
            item.counter = 0
            count = 0
            for item2 in item.findAll('terminal'):
                count += 1
            item.number = count
        for item in self.xml_cim.findAll('energyconsumer'):
            item.counter = 0
            count = 0
            for item2 in item.findAll('terminal'):
                count += 1
            item.number = count
        
        
        
        # Começar um caminho a partir de uma barra
        count = 0
        setores = []
        fim = False
        no_raiz_encontrado = False
        self.nos_percorridos = []
        self.nos_raiz = []

        for noconec in self.lista_nosconect:
            lista_terminais_noc = noconec.findAll('terminal')
            for terminal in lista_terminais_noc:
                parent = self.achar_parent(terminal)
                if parent.name == 'busbarsection':
                    no_raiz_encontrado = True
                    break
            for terminal in lista_terminais_noc:
                if no_raiz_encontrado:
                    parent = self.achar_parent(terminal)
                    if parent.name == 'breaker':
                        no_raiz = parent
                        break
        self.lista_religadores_nao_usados = []
        self.lista_religadores_usados = []
        no_raiz_rot = no_raiz
        no_raiz_antigo = no_raiz
        setor = Setor()
        break_sign = False
        counter = 0
        # reset_counter = 0
        while fim is False:
            reset_counter = 0
            if no_raiz_rot.name == "breaker":
                self.nos_percorridos.append(no_raiz_rot)
                if self.religador_usado(no_raiz_rot) == True:
                    print "Religador usado anteriormente, redefinindo..."                    
                    no_raiz = self.lista_religadores_nao_usados.pop(0)
                    no_raiz_rot = no_raiz
                    no_raiz_antigo = no_raiz


            if no_raiz_rot.name != "breaker":
                no_raiz_rot.counter += 1
            print "Nó raiz: " + str(no_raiz_rot.name)
            if no_raiz_rot.name == "breaker":
                print "ID: " + str(no_raiz_rot.find('mrid'))
            if no_raiz_rot.name == "energyconsumer":
                print "Label: " + str(no_raiz_rot.find('label'))
            print "Tracking Number: " + str(no_raiz_rot.counter)
            print "Reference Number: " + str(no_raiz_rot.number)
            #print "Numero de Terminais: "
            count = 1
            # Loop geral: Varre todos os terminais do nó raiz
            for terminal in no_raiz_rot.findAll('terminal'):
                print "Contador Interno: " + str(count)
                count = count + 1
                if no_raiz_rot.counter == no_raiz_rot.number:
                    no_raiz_rot = no_raiz
                    no_raiz_antigo = no_raiz
                    break

                # Chama a função que acha o nó conectivo a que este terminal está associado
                no_conectivo = self.achar_terminal_noc(terminal)
                # Lista todos os terminais que o nó conectivo achado possui
                lista_conexoes = no_conectivo.findAll('terminal')
                # Loop interno: varre todos os terminais do referido nó conectivo, excetuando
                # o próprio terminal analisado, obviamente. Ou seja, o objetivo é descobrir com
                # que terminais o terminal em questão se conecta.
                for conexao in lista_conexoes:
                    if conexao.find('mrid') != terminal.find('mrid'):
                        # print conexao
                        # Chama a função que acha a que tipo de nó pertence o terminal conectado
                        # e.g Religador, Barra, Nó de Carga.
                        parent_conexao = self.achar_parent(conexao)
                        print "Nó Vizinho: " + str(parent_conexao.name)
                        # print parent_conexao
                        # Analisa os casos possíveis
                        if parent_conexao.name == 'busbarsection':
                            continue

                        # if parent_conexao.name == 'breaker':
                        #     setores.append(setor)
                        #     setor = Setor()

                        # Se o item conectado ao nó raiz for um condutor, obviamente existe um nó
                        # em seguida. Precisa-se achar e identificar este nó.
                        if parent_conexao.name == 'conductor':
                            print "Condutor ID:" + str(parent_conexao.find('mrid'))
                        # Varre todos os terminais (2) do condutor, excetuando-se o próprio terminal
                        # analisado (primeiro extremo do condutor). O objetivo é encontrar o terminal
                        # referente ao segundo extremo do condutor.
                            for no in parent_conexao.findAll('terminal'):
                                
                                if no.find('mrid') != conexao.find('mrid'):
                                    # print "Terminal:"
                                    # print no
                        # Acha o nó conectivo referente a este terminal
                                    no_conectivo_2 = self.achar_terminal_noc(no)
                                    # print "No conectivo:"
                                    # print no_conectivo_2
                        # Lista todos terminais deste nó conectivo. O objetivo é encontrar qual nó
                        # está conectado na outra extremidade do condutor.
                                    lista_conexoes_2 = no_conectivo_2.findAll('terminal')
                        # Varre todos os terminais deste nó conectivo, excetuando-se o próprio terminal
                        # analisado, obviamente.
                                    for conexao2 in lista_conexoes_2:
                                        # print "Terminal do No:" + str(conexao2.find('mrid'))
                                        if conexao2.find('mrid') != no.find('mrid'):
                                            parent_conexao2 = self.achar_parent(conexao2)
                                            print "Nó Final: " + str(parent_conexao2.name)
                                            if parent_conexao2.name == "breaker":
                                                print "ID: " + str(parent_conexao2.find('mrid'))
                                            if parent_conexao2.name == "energyconsumer":
                                                print "Label: " + str(parent_conexao2.find('label'))
                                            print "Tracking Number: " + str(parent_conexao2.counter)
                                            print "Reference Number: " + str(parent_conexao2.number)
                if parent_conexao2 == no_raiz_antigo:
                    print "tentou voltar pro nó antigo!!"
                    if no_raiz_rot.counter ==  no_raiz_rot.number:
                        print "e esse era o único nó a qual ele podia voltar!"
                        no_raiz_antigo = no_raiz
                        no_raiz_rot = no_raiz
                        break
                    else:
                        print "vejamos o pŕoximo nó então"
                        continue

                elif parent_conexao2.name == "energyconsumer":

                    if self.no_percorrido(parent_conexao2) == True:
                        print "Energy Consumer pertence a outro setor!"
                        reset_counter += 1
                        continue
                    else:
                        print "Energy Consumer não pertence a nenhum outro setor!"
                        if self.no_setor(parent_conexao2, setor) == False:
                            setor.nos.append(parent_conexao2)
                        if self.no_raiz(parent_conexao2) == True and parent_conexao2.counter == parent_conexao2.number:
                            print "proibido"
                            if no_raiz_rot == no_raiz:
                                print "fim do setor"
                                
                                setores.append(setor)
                                for setor in setores:
                                    print "SETOR: "
                                    for item in setor.nos:
                                        print str(item.find('label').text)
                                        item.setor = setor
                                self.lista_religadores_usados.append(no_raiz)
                                for elemento in setor.nos:
                                    self.nos_percorridos.append(elemento)
                                setor = Setor()


                                break
                            else:
                                continue
                        else:
                            print "Será o novo nó raiz"
                            
                            no_raiz_antigo = no_raiz_rot
                            no_raiz_rot = parent_conexao2
                            self.nos_raiz.append(parent_conexao2)


                            break

                    # no_raiz_rot = parent_conexao2
                elif parent_conexao2.name == "breaker":
                    if self.no_percorrido(parent_conexao2) == True:
                        print "percorrido!"
                        break_sign = False
                        continue
                        
                    else:
                        self.nos_percorridos.append(parent_conexao2)
                        print "marcado como percorrido."
                        self.lista_religadores_nao_usados.append(parent_conexao2)
                        
                        no_counter = no_raiz_rot.counter
                        no_number = no_raiz_rot.number
                        
                        if no_counter == no_number:
                            no_raiz_rot = no_raiz
                            no_raiz_antigo = no_raiz
                            break
                        else:
                            continue
                        
                        # no_raiz_rot.counter += 1
                        break
                                                    
                                                # setores.append(setor)
                                                # setor = Setor()
            if reset_counter == 2:
                if len(self.lista_religadores_nao_usados) > 1:
                    no_raiz = self.lista_religadores_nao_usados.pop(0)
                    no_raiz_rot = no_raiz
                    no_raiz_antigo = no_raiz
                    reset_counter = 0
                else:
                    fim = True

                     
            print "--------------------------------------------------------------------------"


                #print parent.name
        counting = 0
        for item in self.nos_percorridos:
            counting += 1
        print counting
        print self.lista_religadores_nao_usados

        for setor in setores:
            for item in setor.nos:
                #print str(item.find('label').text)
                #print len(str(item.find('label').text))
                setor.nome = str(item.find('label').text)[3]
            print setor.nome

        return setores



            #print len(lista_conexoes)
            # print len(lista_conexoes)
            # for elemento in lista_conexoes:
            #     parent = self.achar_parent(elemento)
            #     print parent.name



    def save_file(self, path):
        f = open('/home/mateus/Desktop/xml_rnp', 'w')
        f.write(self.xml_final.prettify(formatter = "xml"))

        

bridge = Bridge("/home/mateus/Redes de Teste/rede01_CIM")
#print bridge.xml_final.prettify()
            

        


