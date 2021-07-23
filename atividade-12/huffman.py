import numpy as np
import collections
from copy import deepcopy


def ordenaDict(dicionario, reverse=False):
    '''

    '''

    dictTemp = dict()
    for i in sorted(dicionario, key=dicionario.get, reverse=reverse):
        dictTemp[i] = dicionario[i]

    return dictTemp


def menores2valores(dicionario):
    '''

    '''

    dictCopy = deepcopy(dicionario)
    listMenores2valores = list()
    listMenores2keys = list()
    cont = 0
    for key in dictCopy.keys():
        if cont < 2:
            try:
                if dicionario[key] == dicionario[min(dicionario, key=dicionario.get)]:
                    listMenores2valores.append(dicionario[min(dicionario, key=dicionario.get)])
                    listMenores2keys.append(key)
                    dicionario.pop(key)
            except KeyError:
                pass
            cont += 1
    if len(listMenores2keys) == 2:
        dicionario['{}, {}'.format(listMenores2keys[0], listMenores2keys[1])] = round(sum(listMenores2valores), 4)


def defCodeWorde(listCodeWordIncompleta):
    '''

    '''

    codeWorde = ''
    dictCodeWord = dict()
    for index1 in range(len(listCodeWordIncompleta)):
        for index2 in range(len(listCodeWordIncompleta)):
            if listCodeWordIncompleta[index1][0] in listCodeWordIncompleta[index2][0] and len(listCodeWordIncompleta[index2][0].split(', ')) == 1:
                codeWorde = '{} | {}'.format(listCodeWordIncompleta[index2][1], listCodeWordIncompleta[index2][3])
                dictCodeWord[listCodeWordIncompleta[index1][0]] = codeWorde
            elif listCodeWordIncompleta[index1][0] in listCodeWordIncompleta[index2][0] and len(listCodeWordIncompleta[index1][0].split(', ')) > 1:
                codeWorde = '{} | {}'.format(listCodeWordIncompleta[index2][1], listCodeWordIncompleta[index2][3])
                dictCodeWord[listCodeWordIncompleta[index1][0]] = codeWorde
    
    return dictCodeWord


def montCod(dictCode):
    '''

    '''

    dictToList = list(dictCode.items())
    listSimbolos = list()
    listBits = list()
    listFolhas = list()
    for key in dictToList:
        listSimbolos.append([key[0].split(', '), key[1].split(' | ')[0]])
        listBits.append(key[1].split(' | ')[0])
    for lista in listSimbolos:
        if len(lista[0]) == 1:
            listFolhas.append(lista)

    dictWord = dict()
    for folha in zip(listFolhas):
        cont = ''
        for listSimbolo in listSimbolos:
            if listSimbolo[0].count(folha[0][0][0]) > 0:
                cont += listSimbolo[1].split('bit')[1]
                dictWord[folha[0][0][0]] = cont 
    
    return dictWord


def remove_repetidos(lista):
    '''

    '''

    l = list()
    for i in lista:
        if i not in l:
            l.append(i)
    l.sort()
   
    return l


def formDict():
    '''

    '''

    # TODO - Resolver problema de simbolos iguais no dicionario (NAO ACEITA KEYS IGUAIS)
    # # Frequencia de ocorrencia das letras do alfabeto
    # dictProbs = [
    #     'A': 0.1463, 'B': 0.104, 'C': 0.388, 'D': 0.499, 'E': 0.1257,
    #     'F': 0.102, 'G': 0.130, 'H': 0.128, 'I': 0.618, 'J': 0.040, 
    #     'K': 0.002, 'L': 0.278, 'M': 0.474, 'N': 0.505, 'O': 0.1073,
    #     'P': 0.252, 'Q': 0.120, 'R': 0.653, 'S': 0.781, 'T': 0.434, 
    #     'U': 0.463, 'V': 0.167, 'W': 0.001, 'X': 0.021, 'Y': 0.001, 
    #     'Z': 0.047
    # ]

    with open('texto.txt', 'r') as files:

        listSimbolos = list()
        dictSimbolos = dict()
        for file in files:
            for simbolo in file:
                listSimbolos.append(simbolo)

        freq = 0
        repetidos = collections.Counter(listSimbolos)
        for key in repetidos.keys():
            freq = round(int(repetidos[key])/len(listSimbolos), 8)
            dictSimbolos[key] = freq

    return dictSimbolos

def main():
    # dictProbs = formDict()
    dictProbs = {'1': 0.18, '2': 0.16, '3': 0.14, '4': 0.12, '5': 0.1, 'A': 0.1, 'B': 0.08, 'c': 0.06, 'd': 0.04, 'E': 0.02}
    # dictProbs = {'1': 0.25, '2': 0.25, '3': 0.2, '4': 0.15, '5': 0.15}
    # dictProbs = {'L': 0.25, 'u': 0.25, 'c': 0.2, 'a': 0.15, 's': 0.02, 'd': 0.08, 'e': 0.05}
    print('Dicionario de simbolos:\n', dictProbs)
    print('-------------------------------------------------------------------------------------------------------------')
    dictProbsOdernado = ordenaDict(dictProbs)
    print('Dicionario de simbolos ordenado:\n', dictProbsOdernado)
    print('-------------------------------------------------------------------------------------------------------------')


    dictCopy = deepcopy(dictProbsOdernado)

    listaDicionarios = list()
    for index in dictCopy.keys():
        newDict = deepcopy(dictProbsOdernado)
        listaDicionarios.append(newDict)
        menores2valores(dictProbsOdernado)
        dictProbsOdernado = ordenaDict(dictProbsOdernado)

    print('Dicionario com os elementos somados:\n')
    for dicionario in listaDicionarios:
        print(dicionario)
    print('-------------------------------------------------------------------------------------------------------------')

    dicionarioAuxiliar = dict()
    for index in range(len(listaDicionarios), -1, -1):
        if index + 1 <= len(listaDicionarios) - 1: # Tirando a ultima posição, pois é o elemento principal que ira dividir os bits
            bit = 1
            for key in listaDicionarios[index].keys():
                
                if bit == 1:
                    dicionarioAuxiliar[key + '| bit{} | {} | left'.format(bit, listaDicionarios[index][key])] = listaDicionarios[index][key]
                elif bit == 0:
                    dicionarioAuxiliar[key + '| bit{} | {} | rigth'.format(bit, listaDicionarios[index][key])] = listaDicionarios[index][key]
                
                if bit > 0:
                    bit -= 1
                else:
                    bit = 1

    listCodeWordIncompleta = list()
    for element in dicionarioAuxiliar:
        if 'bit' in element:
            listCodeWordIncompleta.append(element.split('| '))
    
    dictCodeWord = defCodeWorde(listCodeWordIncompleta)
    print('Atribuição dos bits e da posição para cada simbolo:\n')
    for key in dictCodeWord: # Nós e folhas da arvore
        print('({}): {}'.format(key, dictCodeWord[key]))
    print('-------------------------------------------------------------------------------------------------------------')

    dictCodSimb = montCod(dictCodeWord)

    setKeys = sorted(set(dictCodSimb)) # Ordenando as keys para printar em ordem os codigos
    print('Formação do codigo de cada simbolo:\n')
    aux = ''
    for key in setKeys:
        aux += dictCodSimb[key]
        print('C({}): {}'.format(key, dictCodSimb[key]))
    print('-------------------------------------------------------------------------------------------------------------')
    print(aux)
if __name__ == '__main__':

    main()
