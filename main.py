import cv2
import collections

import numpy as np

from arvore_huffman.ListaNos import ListaNos
from arvore_huffman.HuffmanTree import HuffmanTree

from scipy.fftpack import dct, idct

def dct2 (bloco):
    return dct(dct(bloco.T,norm="ortho").T, norm="ortho")

def idct2(bloco):
    return abs(idct(idct(bloco.T, norm="ortho").T, norm="ortho"))

def conversorDeEspaco(imagem, modo='ycrcb'):
    if modo == 'ycrcb':
        YCrCb = cv2.cvtColor(imagem, cv2.COLOR_BGR2YCR_CB)
        return YCrCb
    elif modo == 'bgr':
        bgr = cv2.cvtColor(imagem, cv2.COLOR_YCR_CB2BGR)
        return bgr
    elif modo == 'gray':
        gray = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
        return gray

def separarImagemBlocos(imagem, tamMasc=8):
    # Lista com todos os blocos possiveis na imagem
    # media = np.mean(imagem)
    listaDct2Blocos = list()

    # Tamanho das componentes da imagem e da bloco
    rows, cols = imagem.shape

    '''Calculo de quantos blocos 8x8 caberao na imagem'''
    linhas = int(rows/tamMasc)
    colunas = int(cols/tamMasc)

    '''Criando uma lista com os k blocos possiveis'''
    contLinhas = contColunas = 0
    for cordX in range(linhas):
        for cordY in range(colunas):
            if cordX == cordY == 0: # primeiro elemento
                bloco = imagem[contLinhas:contLinhas+tamMasc, contColunas:contColunas+tamMasc]
            else: 
                contLinhas = contLinhas + tamMasc

                if contLinhas >= linhas*tamMasc:
                    contLinhas = 0
                    contLinhas = contLinhas + tamMasc
                
                    contColunas = contColunas + tamMasc
                    if contColunas == colunas*tamMasc:
                        contColunas = colunas*tamMasc - 1

                bloco = imagem[contLinhas:contLinhas+tamMasc, contColunas:contColunas+tamMasc]

            '''Calculo da dct2 e quantização com fator de escala = 1/sqrt(1/2N)'''
            dct = np.round(dct2(bloco))
            dct[dct==-0] = 0 # -0 é igual a 0, mas na codificação tem diferença
            listaDct2Blocos.append(dct)
            
    return listaDct2Blocos

def algoritmoZigZag(bloco):
    lenBloco=len(bloco)
    return sum([list(bloco[::-1,:].diagonal(i)[::(i+lenBloco+1)%2*-2+1])for i in range(-lenBloco,lenBloco+len(bloco[0]))],[])

def openFile(nomeArquivo):	# pega o texto incial	
		try:
			file = open(nomeArquivo, "r")
			text = file.read()
			file.close()
		except IOError:
			print ("Erro ao abrir o arquivo")
		return text

def creatFile(nomeArquivo, listaBlocos):		# escreve um arquivo com o texto em binário
    with open(nomeArquivo, 'w') as file:
        for bloco in listaBlocos:
            file.write(bloco+' ')

def frequenciaRelativa(freqElementos, freqTotal):
    # dicionarioFreqRelativa = dict()

    # for freq in freqElementos:
    #     dicionarioFreqRelativa[freq.conteudo] = freq.freq/freqTotal

    # return dicionarioFreqRelativa
    
    listaFreqRelativa = list()

    for freq in freqElementos:
        listaFreqRelativa.append(freq.freq/freqTotal)

    return listaFreqRelativa

def huffmanBloco(saidaLZ78bloco):
    listaNos = ListaNos(saidaLZ78bloco)
    listaNos.criaArv()
    
    ht = HuffmanTree()
    ht.codifica(listaNos.raiz[0])

    codificacaoHuffman = ht.getTextBin(listaNos.raiz[0],listaNos.texto)
    
    freqElementos = listaNos.frequenciasPorElemento
    freqTotal = listaNos.raiz[0].freq

    listaFrequencia = frequenciaRelativa(freqElementos, freqTotal)

    return codificacaoHuffman, listaFrequencia

def calcH(listaFreq):
    
    '''
        FIXME - Calculo da entropia H

        [Parametro]:
                    - Uma lista de entrada contendo listas com as probabilidades de ocorrencia
                      de cada caractere para cada bloco de tamanho (NxN)
        [Saida]: 
                - O resultado do calculo da entropia, dada a lista de listas 'listaFreq'

    '''
        
    # ----------------------------------
    # Definição de variaveis
    listaValoresH = list()
    # ----------------------------------
    
    for lista in listaFreq:
        H = 0 # Entropia
        for freq in lista:
            H += abs(freq * np.log2(freq))
        listaValoresH.append(round(H, 4))
        
    return listaValoresH

def calcHImagemFull(listaFreq):
    # ----------------------------------
    # Definição de variaveis
    H = 0 # Entropia
    # ----------------------------------
    for freq in listaFreq:
        H += abs(freq * np.log2(freq))
        
    return round(H, 4)

def calcL(listvetProbs):
    '''
        FIXME - Calculo do comprimento medio, considerando o codigo ótimo

        [Parametros]:
                    - Um vetor contendo as probabilidades de ocorrencia
                      de cada caractere
        [Saida]: 
                - O resultado do calculo do comprimento médio, dado o vetor de probabilidades 'listvetProbs'

    '''
    
    # ----------------------------------
    # Definição de variaveis
    listaCompL = list()
    # ----------------------------------

    for bloco in listvetProbs:
        L = 0 # Comprimento medio
        for freq in bloco:
            L += abs(freq * round(abs(np.log2(freq)), 0))
        listaCompL.append(round(L, 4))
    return listaCompL

def codificacaoLZ_78(listaBlocos, mostrarBlocos=False):
    
    listaSaidaLZ78Blocos = list()
    listaSaidaHuffmanBlocos = list()
    listaDeListasFrequencia = list()

    for index, bloco in enumerate(listaBlocos):
        vetorizacaoZigZag = algoritmoZigZag(bloco) # aplicação do algoritmo zip-zag

        vetorZigZagString = [str(int(elemento)) for elemento in vetorizacaoZigZag]
        
        saidaLZ78bloco = lz78(vetorZigZagString)
        listaSaidaLZ78Blocos.append(saidaLZ78bloco)

        decodificacaoHuffman, listaFrequencias = huffmanBloco(saidaLZ78bloco)
        listaDeListasFrequencia.append(listaFrequencias)
        listaSaidaHuffmanBlocos.append(decodificacaoHuffman)

        if mostrarBlocos:
            cv2.imshow('Bloco {}'.format(bloco.shape), np.asarray(idct2(bloco), np.uint8))
            # cv2.imwrite('blocos(NxN)/bloco_{}.jpg'.format(index), np.asarray(idct2(bloco), np.uint8))
            cv2.waitKey()
    
    return listaSaidaLZ78Blocos, listaSaidaHuffmanBlocos, listaDeListasFrequencia

def lz78(vetorZigZag):
    texto = vetorZigZag

    listaArmazenamento = list()
    listaPosicao = list()
 
    variavelTemp = ''
    variavelTemp2 = ''
    for index in range(len(texto)):
        if index == 0: # primeiro elemento
            variavelTemp = texto[index]
            listaArmazenamento.append(variavelTemp)
            listaPosicao.append((index, texto[index]))
            variavelTemp = texto[index+1]
        else:
            if variavelTemp in listaArmazenamento:
                try:
                    variavelTemp2 += texto[index]
                    variavelTemp += texto[index+1]
                except Exception:
                    listaArmazenamento.append(variavelTemp)
            else:
                listaArmazenamento.append(variavelTemp)
                try:
                    variavelTemp = texto[index+1]
                    variavelTemp2 = texto[index+1]
                except Exception as e:
                    pass
    # print(listaArmazenamento)
    # time.sleep(1)
    # string = None
    # print(string.join(texto))
    return listaArmazenamento

def remove_repetidos(lista):
    # Cantagem dos elementos remetidos
    l = list()
    for i in lista:
        if i not in l:
            l.append(i)
    l.sort()
   
    return l

def calcCompressao(lenListaBlocos, tamBlocos, image):
    return round(1 - ((lenListaBlocos*tamBlocos)/(image.shape[0] * image.shape[1])), 4)

def calculosPedidos(imagem, listaSaidaLZ78Blocos, listaDicionariosFrequencia, lenMediaBlocos):
    # ===================================================================================================
    # Salvando os elementos repetidos dos dados brutos, ou seja, da imagem original em tons de cinza
    dicionarioRepetidosImagemFull = collections.Counter(algoritmoZigZag(imagem)) 
    arrayValuesImagemFull = np.array(list(dicionarioRepetidosImagemFull.values()))
    listaFreq = list(arrayValuesImagemFull/sum(arrayValuesImagemFull))

    # Calculo da entropia H de LZ78
    entropiaImagemFull = calcHImagemFull(listaFreq)
    print('Entropia H da imagem completa em tons de cinza:', round(np.mean(entropiaImagemFull), 4))
    # ===================================================================================================

    # ===================================================================================================
    '''Calculo da entropia H da saida gerada pelo LZ78 gerado para cada bloco (NxN)'''
    # Tratamento dos dados do LZ78
    # Montagem da lista de dicionarios cotendo as frequencias relativas a cada caractere
    listaDicionariosReticoes = list()
    listaFrequenciaLZ78 = list()

    # Salvando os elementos repetidos do LZ78
    for bloco in listaSaidaLZ78Blocos:
        dicionarioRepetidos = collections.Counter(bloco)
        listaDicionariosReticoes.append(dicionarioRepetidos)
    
    for bloco in listaDicionariosReticoes:
        arrayValues = np.array(list(bloco.values()))
        freq = arrayValues/sum(arrayValues)
        listaFrequenciaLZ78.append(freq)

    # Calculo da entropia H de LZ78
    listaValoresEntropLZ78 = calcH(listaFrequenciaLZ78)
    print('Media de todos os blocos da entropia H do codigo de LZ78:', round(np.mean(listaValoresEntropLZ78), 4))
    # ===================================================================================================

    # ===================================================================================================
    '''Calculo da entropia H do codigo de Huffman gerado para cada bloco (NxN)'''
    listaValoresEntropHuffman = calcH(listaDicionariosFrequencia)
    print('Media de todos os blocos da entropia H do codigo de Huffman:', round(np.mean(listaValoresEntropHuffman), 4))
    # ===================================================================================================
    
    # ===================================================================================================
    '''Calculo do comprimento medio dos codigos gerados por Huffman'''
    compMedioHuffman = calcL(listaDicionariosFrequencia)
    print('Media do calculo do comprimento de codigo de todos os blocos (NxN):', round(np.mean(compMedioHuffman), 4))
    # ===================================================================================================
   
    # ===================================================================================================
    '''Calculo da compressao final dos dados'''
    # ===================================================================================================
    compressao = calcCompressao(len(listaDicionariosFrequencia), lenMediaBlocos, imagem)
    print('Compessao final da imagens: {}'.format(compressao))

def main():
    # -----------------------------------------------------
    # Configurações basicas
    resize = False
    mostrarImagens = False

    tamBlocos = 8
    fatoResize = 0.5
    # -----------------------------------------------------

    '''Abrindo a imagem com OpenCV'''
    # pathImg = 'input.png'
    pathImg = 'teste.jpg'
    imagem = cv2.imread(pathImg)

    if mostrarImagens:
        cv2.imshow('{}'.format(pathImg.split('.')[0]), imagem)

    '''Conversao da imagem'''
    gray = conversorDeEspaco(imagem, modo='gray')

    # with open('imagem_tons_cinza.txt', 'w') as file:
    #     rows, cols = gray.shape
    #     for row in range(rows):
    #         for col in range(cols):
    #             file.write(str(gray[row, col])+' ')

    if resize:
        imagem = cv2.resize(imagem, None, fx=fatoResize, fy=fatoResize)

    if mostrarImagens:
        cv2.imshow('BGR para Gray', gray)

    '''Separando cada canal da imagens em blocos de tamanho 8x8'''
    listaBlocosgray = separarImagemBlocos(gray, tamMasc=tamBlocos)

    '''Aplicação do LZ-78 para codificação'''
    listaSaidaLZ78Blocos, listaSaidaHuffmanBlocos, listaDicionariosFrequencia = codificacaoLZ_78(listaBlocosgray, mostrarBlocos=mostrarImagens)
    calculosPedidos(gray, listaSaidaLZ78Blocos, listaDicionariosFrequencia, tamBlocos)

    # creatFile('codificacao_huffman.txt', listaSaidaHuffmanBlocos)

    if cv2.waitKey() or  0xFFF == ord('q'):
        cv2.destroyAllWindows()
        exit()

if __name__ == '__main__':
    main()
