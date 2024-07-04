import math
#DESCRIÇÃO: Cálculo de vigas retangulares em concreto

#ENTRADA DE DADOS DA VIGA P/ CÁLCULO DAS ARMADURAS
#Nome da viga
nome = "V101"
#Altura total da viga: 
h = 50 #cm
#Largura da viga:
bw = 25 #cm
#Cobrimento
c = 3 #cm
#Diâmetro da armadura escolhida (5/6.3/8/10/12.5/16/20/25/32)
diam = 12.5 #mm
#Momento fletor solicitante de cálculo
msd = 40000 #kN*cm

#ENTRADA DE DADOS DOS MATERIAIS
fck = 20 #MPa
fyk = 500 #MPa

#ENTRADA DE DADOS DA VIGA PARA CÁLCULO DA CORTANTE
#Tipo de modelo de cálculo:
#1 p/ Treliça clássica (ângulo de inclinação das bielas fixo em 45°)
#2 p/ Treliça generalizada (ângulo de inclinação das bielas entre 30º e 45º)
tipo = 1
#Cortante solicitante de cálculo
vsd = 500 #kN

#ENTRADA DE DADOS DA VIGA PARA CÁLCULO DA FLECHA
#Momento fletor na seção mais solicitada em serviço (ELS-QP)
mat = 32200 #kN*cm 
#Vão da viga
l_viga = 700 #cm
#Fator que considera deformação por fluência
fl = 2.5
#Carga uniformemente distribuída
q = 8 #kN/m
#Armadura calculada
as_calc = 9.47 #cm2

#ITENS QUE DEVEM SER CALCULADOS (s = sim/ n = nao)
calcular_as_elu = "s"
calcular_cortante = "n"
els_deslocamento = "s"

#ALGORITMO----------------------------------------------------------------------------------------------------------------------
def add_resultado(resultado):
    # Open a file in write mode
    with open('resultados.txt', 'a') as file:
        file.write(resultado)

#Variáveis globais
res_elu = ""

#Função para escolher o que será calculado
def o_que_calcular(calcular_as_elu, calcular_cortante, els_deslocamento, h, c, diam, msd,bw, fck, fyk, as_calc, mat, q, l_viga, fl, nome):
    global res_elu
    #CONVERSÃO DE VALORES E DEFINIÇÃO DE VARIÁVEIS
    fcd = fck / (1.4*10) #kN/cm2
    fyd = fyk / (1.15*10) #kN/cm2
    d = h - c - 2 #cm
    res_elu = f"Viga: {nome} \n" \
    f"Altura (h): {h} cm \n" \
    f"Base (bw): {bw} cm \n \n"
    with open('resultados.txt', 'w') as file:
        file.write(res_elu)
    if calcular_as_elu == "s":
        calcular_viga(d, h, msd, bw, fck, fcd, fyd, diam)
    if calcular_cortante == "s":
        calc_vsd()
    if els_deslocamento == "s":
        els_desl(h, d, bw, fck, msd, as_calc, mat, q, l_viga, fl)

def calcular_viga(d, h, msd, bw, fck, fcd, fyd, diam):
    global res_elu
    res_elu += f"Resultados para ELU:\n"
    #As mínimo
    as_min = calc_as_min(fck, bw, h)
    as_max = 0.04 * h * bw
    res_elu += f"Área de aço máxima: {as_max:.2f} cm2 \n"
    #Armadura de pele
    if h >= 60:
        as_pele = (0.10 / 100) * (bw * h) #cm2
        res_elu += f'Armadura de pele: {as_pele:.2f} cm2 por face lateral \n'
    #Define se é armadura simples ou dupla
    if (math.pow(0.68*d, 2) - 4*0.272*(msd/(bw*fcd))) < 0 :
        calc_as_dupla(h, bw, d, fcd, fyd, msd, diam, as_max)
    else:
        x_1 = (0.68*d + math.sqrt(math.pow(0.68*d, 2) - 4*0.272*(msd/(bw*fcd))))/0.544
        x_2 = (0.68*d - math.sqrt(math.pow(0.68*d, 2) - 4*0.272*(msd/(bw*fcd))))/0.544
        if x_1 > 0 and x_1 <= h:
            x = x_1
        else:
            x = x_2
        if x/d <= 0.45:
            calc_as_simples(msd, fyd,  d, x, as_min, as_max)
        else:   
            calc_as_dupla(h, bw, d, fcd, fyd, msd, diam, as_max)
    
def calc_as_simples(msd, fyd,  d, x, as_min, as_max):
    global res_elu
    res_elu += "Cálculo da armadura: Armadura simples\n"
    res_elu += f"Profundidade da linha neutra: {x:.2f} cm \n"
    as_calc = msd / (fyd*(d - 0.4*x)) #cm2
    res_elu += f'Área de aço calculada: {as_calc:.2f} cm2 \n'
    #Checa as armaduras mínimas e máximas
    if as_calc < as_min:
        as_calc = as_min
    if as_calc > as_max:
        res_elu += f"ATENÇÃO: As calculado ({as_calc:.2f} cm2) acima do As Máximo ({as_max:.2f} cm2) permitido!"
    add_resultado(res_elu)
    
def calc_as_dupla(h, bw, d, fcd, fyd, msd, diam, as_max):
    global res_elu
    res_elu += "Cálculo da armadura: Armadura dupla \n"
    #Momento limite p/ x = 0,45
    mom_lim = 0.251*bw*math.pow(d,2)*fcd
    #Armadura tracionada - As1
    xlim = 0.45*d
    res_elu += f'Relação x/d acima de 0,45 - Calculado momento fletor limite M1: {mom_lim:.2f} kN*cm \n'
    as1 = mom_lim / ((d - 0.4*xlim)*fyd)
    #Armadura tracionada - As2
    m2 = msd - mom_lim
    dlinha = h - d #cm 
    as2 = m2 / ((d - dlinha)*fyd)
    as_tot = as1 + as2
    #qtd barras totais incluindo as barras comprimidas, para o cálculo do As máx
    as_tot_max = as1 + 2* as2
    if as_tot_max > as_max:
        res_elu += f"ATENÇÃO: As calculado ({as_tot_max:.2f} cm2) acima do As Máximo ({as_max:.2f} cm2) permitido!"
    res_elu += f'Área de aço p/ armadura tracionada: {as_tot:.2f} cm2 \n'\
             f'Área de aço p/ armadura comprimida: {as2:.2f} cm2 \n'
    res_elu += f'Quant. barras adotadas p/ armadura tracionada: \n' 
    qtd_barras(diam, as_tot)
    res_elu += f'Quant. barras adotadas p/ armadura comprimida: \n' 
    qtd_barras(diam, as2)
    add_resultado(res_elu)

def calc_vsd(bw,d,fck, fcd):

    fctm = 0.3*math.pow(fck, (2/3))
    #Calculo da cortante pelo modelo de treliça clássica (ângulo de inclinação das bielas fixo em 45°)
    #Verificação de compressão nas bielas
    Vrd2 = 0.27*( 1 - (fck/250))*fcd*bw*d
    #Calculo da armadura transversal
    #as_sw_min = 20*

def els_desl(h, d, bw, fck, msd, as_calc, mat, q, l_viga, fl):
    res_els = "\nResultados para deslocamento da viga (ELS) \n"
    res_els += "Propriedades da seção bruta: \n"
    yt = h /2 #cm
    ic = (bw * math.pow(h, 3)) /12 #cm4
    res_els += f"Inércia da seção bruta: {ic:.0f} cm4 \n"
    fctm = (0.3*math.pow(fck, (2/3))) / 10 #kN/cm2
    res_els += f"Fctm: {fctm:.2f} kN/cm2 \n"
    mr = (1.5 * fctm * ic) / yt
    res_els += f"Momento de fissuração (Mr): {mr:.0f} kN*cm \n"
    q = q/100 #kN/cm
    if mr < msd:
        res_els += 'Ocorre fissuração! \n'
        res_els += 'Propriedades da viga no Estádio 2:\n'
        alpha_e = 210000/(4760*math.sqrt(fck))
        res_els += f'Ae: {alpha_e:.2f} \n'
        a1 = bw / 2
        a2 = alpha_e * as_calc
        a3 = - d * alpha_e * as_calc
        res_els += f'a1: {a1:.2f} cm \n'
        res_els += f'a2: {a2:.2f} cm2 \n'
        res_els += f'a3: {a3:.2f} cm3 \n'
        x_1 = (- a2 + math.sqrt(a2 * a2 - 4 * a1 * a3)) / (2 * a1)
        x_2 = (- a2 - math.sqrt(a2 * a2 - 4 * a1 * a3)) / (2 * a1)
        if x_1 > 0 and x_1 <= h:
            x = x_1
        else:
            x = x_2
        res_els += f'Profundidade da LN: {x:.2f} cm \n'
        iII = ((bw * math.pow(x,3)) / 3) + alpha_e * as_calc * math.pow((x - d), 2)
        res_els += f'Inércia da viga fissurada: {iII:.0f} cm4 \n'
        im = (math.pow((mr / mat),3))*ic + (1 - math.pow((mr / mat),3))*iII
        res_els += f'Inércia média entre Estádios I e II (Branson): {im:.0f} cm4 \n'
        i = im
    else:
        res_els += 'Não ocorre fissuração! \n'
        i = ic

    #Deslocamento máximo da viga
    res_els += "Deslocamento máximo da viga: \n"
    eci = 5600*math.sqrt(fck) #MPa
    res_els += f'Módulo de deformação tangente inicial (Eci): {eci:.0f} MPa \n'
    ecs = (0.8 + (0.2*fck)/80) * eci #MPa
    res_els += f'Módulo de deformação secante (Ecs): {ecs:.0f} MPa \n'
    ecs = ecs /10 #kN/cm2
    desl = ((5 * q * math.pow(l_viga, 4)) / (384*ecs*i)) * fl
    res_els += f'Deslocamento máximo da viga: {desl:.2f} cm\n'
    desl_lim = l_viga / 250
    res_els += f'Deslocamento limite da viga: {desl_lim:.2f} cm\n'
    if desl > desl_lim:
        res_els += 'Não passou!'
    else:
        res_els += 'Passou !'
    
    # Open a file in append mode
    file_path = 'resultados.txt'

    # Using 'with' statement ensures the file is properly closed
    with open(file_path, 'a') as file:
        # Perform operations on the file
        file.write(res_els)

def calc_as_min(fck, bw, h):
    global res_elu
    #AS Mínimo-----------------------------
    if fck == 20 or fck == 25 or fck == 30:
        p = 0.15 / 100
    elif fck == 35:
        p = 0.164 /100
    elif fck == 40:
        p = 0.179/100
    elif fck == 45:
        p = 0.194/100
    elif fck == 50:
        p = 0.208/100
    as_min = p*bw*h
    res_elu += f'Armadura mínima: {as_min:.2f} cm2 \n'
    return as_min

def qtd_barras(diam, as_calc):
    global res_elu
    #Areas de aço por barra (cm2)
    if diam == 5:
        b5 = 0.20
        n_barras = math.ceil(as_calc / b5)
    elif diam == 6.3:
        b63 = 0.315
        n_barras = math.ceil(as_calc / b63)
    elif diam == 8:
        b8 = 0.50
        n_barras = math.ceil(as_calc / b8)
    elif diam == 10:
        b10 = 0.80
        n_barras = math.ceil(as_calc / b10)
    elif diam == 12.5:
        b125 = 1.25
        n_barras = math.ceil(as_calc / b125)
    elif diam == 16:
        b16 = 2
        n_barras = math.ceil(as_calc / b16)
    elif diam == 20:
        b20 = 3.15
        n_barras = math.ceil(as_calc / b20)
    elif diam == 25:
        b25 = 5
        n_barras = math.ceil(as_calc / b25)
    elif diam == 32:
        b32 = 8
        n_barras = math.ceil(as_calc / b32)
    res_elu += f'Qtd de barras de {diam:.2f} mm: {n_barras:.2f} \n'

o_que_calcular(calcular_as_elu, calcular_cortante, els_deslocamento, h, c, diam, msd,bw, fck, fyk, as_calc, mat, q, l_viga, fl, nome)









