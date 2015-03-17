# coding=utf-8




class Religador(object):
     def __init__(self, nome=None, rated_current=None, in_transit_time=None, breaking_capacity=None, reclose_sequences=None, estado=1, mRID = None):
        assert estado == 1 or estado == 0, 'O parâmetro estado deve ser um inteiro de valor 1 ou 0'
        self.normalOpen = estado
        self.ratedCurrent = rated_current
        self.inTransitTime = in_transit_time
        self.breakingCapacity = breaking_capacity
        self.recloseSequences = reclose_sequences
        self.nome = nome
        self.mRID = mRID


class EnergyConsumer(object):

    def __init__(self, power):
        self.power = power/1000


class Substation(object):
    def __init__(self, nome, tensao_primario, tensao_secundario, potencia, impedancia):
        self.nome = nome
        self.tensao_primario = tensao_primario
        self.tensao_secundario = tensao_secundario
        self.potencia = potencia
        self.impedancia = impedancia
        

class BusBarSection(object):
    def __init__(self,nome=None, phases = None):
        self.nome = nome
        self.phases = phases


class Condutor(object):
    def __init__(self, tipo):
        self.tipo = tipo


class NoConectivo(object):
    def __init__(self, terminal1, terminal2):
        self.terminal1 = terminal1.mRID
        self.terminal2 = terminal2.mRID

