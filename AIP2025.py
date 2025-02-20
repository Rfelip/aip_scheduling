# -*- coding: utf-8 -*-
"""
Created on Mon Feb 17 13:43:10 2025

@author: Edmilson Domingues
"""

import pandas as pd
import gurobipy as gp
from gurobipy import GRB
import sys

def le_arquivo_pessoas():
    # Leitura completa do arquivo de pessoas (organizadores e palestrantes):
    print('Realizando o processo de Leitura.')
    df = pd.read_excel('./AIP2025 - pessoas.xlsx')
    df['Palestra 1'] = df['Palestra 1'].astype('int64')
    return df
    

def le_arquivo_ms():
    # Leitura completa do arquivo de pessoas (organizadores e palestrantes):
    print('Realizando o processo de Leitura.')
    df = pd.read_excel('./AIP2025 - minissimpósios.xlsx')
    df['Blocos'] = df['Blocos'].astype('int64')
    return df

def le_arquivo_pesos_sessoes():
    # Leitura completa do arquivo de pessoas (organizadores e palestrantes):
    print('Realizando o processo de Leitura.')
    df = pd.read_excel('./AIP2025 - pesos sessões.xlsx')
    df['sessão 1'] = df['sessão 1'].astype('int64')
    df['sessão 2'] = df['sessão 2'].astype('int64')
    df['sessão 3'] = df['sessão 3'].astype('int64')
    df['sessão 4'] = df['sessão 4'].astype('int64')
    df['sessão 5'] = df['sessão 5'].astype('int64')
    df['sessão 6'] = df['sessão 6'].astype('int64')
    df['sessão 7'] = df['sessão 7'].astype('int64')
    df['sessão 8'] = df['sessão 8'].astype('int64')
    df['sessão 9'] = df['sessão 9'].astype('int64')
    return df

def le_arquivo_pesos_paralelas():
    # Leitura completa do arquivo de pessoas (organizadores e palestrantes):
    print('Realizando o processo de Leitura.')
    df = pd.read_excel('./AIP2025 - pesos paralelas.xlsx')
    df['paralela 1'] = df['paralela 1'].astype('int64')
    df['paralela 2'] = df['paralela 2'].astype('int64')
    df['paralela 3'] = df['paralela 3'].astype('int64')
    df['paralela 4'] = df['paralela 4'].astype('int64')
    df['paralela 5'] = df['paralela 5'].astype('int64')
    df['paralela 6'] = df['paralela 6'].astype('int64')
    df['paralela 7'] = df['paralela 7'].astype('int64')
    df['paralela 8'] = df['paralela 8'].astype('int64')
    df['paralela 9'] = df['paralela 9'].astype('int64')
    df['paralela 10'] = df['paralela 10'].astype('int64')
    return df

# Leitura do arquivo de pessoas - sua identidade, MS's que palestra e MS's
# que organiza.
dataframe_pessoas= le_arquivo_pessoas()
'''
print("Informações:")
print(dataframe_pessoas.info())
print()

print("Dtypes:")
print(dataframe_pessoas.dtypes)
'''
lista_pessoas = []
for indice, valor in dataframe_pessoas.iterrows():
    linha = [valor[0], valor[1], [valor[4], valor[5]], [valor[6], valor[7]]]
    lista_pessoas.append(linha)
for i in range(len(lista_pessoas)):
    if 9999 in lista_pessoas[i][2]:
        lista_pessoas[i][2].remove(9999)
    if 9999 in lista_pessoas[i][2]:
        lista_pessoas[i][2].remove(9999)
    if 9999 in lista_pessoas[i][3]:
        lista_pessoas[i][3].remove(9999)
    if 9999 in lista_pessoas[i][3]:
        lista_pessoas[i][3].remove(9999)
    print(lista_pessoas[i])
    
# Leitura do arquivo de MS - sua identidade e quantidade de blocos.
dataframe_ms= le_arquivo_ms()
lista_ms = []
for indice, valor in dataframe_ms.iterrows():
    linha = [valor[0], valor[1], valor[2]]
    lista_ms.append(linha)
for i in range(len(lista_ms)):
    print(lista_ms[i])

# Leitura do arquivo de pesos sessões.
dataframe_pesos_sessoes= le_arquivo_pesos_sessoes()
lista_pesos_sessoes = []
for indice, valor in dataframe_pesos_sessoes.iterrows():
    linha = [valor[0], valor[1], valor[2], valor[3], valor[4], valor[5], 
             valor[6], valor[7], valor[8], valor[9]]
    lista_pesos_sessoes.append(linha)
for i in range(len(lista_pesos_sessoes)):
    del lista_pesos_sessoes[i][0]
for i in range(len(lista_pesos_sessoes)):
    print(lista_pesos_sessoes[i])

# Leitura do arquivo de pesos paralelas.
dataframe_pesos_paralelas= le_arquivo_pesos_paralelas()
lista_pesos_paralelas = []
for indice, valor in dataframe_pesos_paralelas.iterrows():
    linha = [valor[0], valor[1], valor[2], valor[3], valor[4], valor[5], 
             valor[6], valor[7], valor[8], valor[9], valor[10]]
    lista_pesos_paralelas.append(linha)
for i in range(len(lista_pesos_paralelas)):
    del lista_pesos_paralelas[i][0]
for i in range(len(lista_pesos_paralelas)):
    print(lista_pesos_paralelas[i])

# Implementação do modelo matemático.
# Cria o ambiente e o modelo
model = gp.Model("AIP2025")
ms = 30
blocos = 3
sessoes = 9
paralelas = 10

# Defining the variables to the model
x = [[[[model.addVar(vtype=GRB.BINARY, name='x') for p in range(paralelas)] 
       for s in range(sessoes)] for b in range(blocos)] 
     for m in range(ms)]    # x[m][b][s][p]
y = [[[[[model.addVar(vtype=GRB.BINARY, name='y') 
         for s2 in range(sessoes)] for s1 in range(sessoes)] 
       for b2 in range(blocos)] for b1 in range(blocos)] 
     for m in range(ms)]    # y[m][b1][b2][s1][s2]
z = [[[[[model.addVar(vtype=GRB.BINARY, name='z') 
         for p2 in range(paralelas)] for p1 in range(paralelas)] 
       for b2 in range(blocos)] for b1 in range(blocos)] 
     for m in range(ms)]    # z[m][b1][b2][p1][p2]

# Defining the constraints
# C1) Each session can only include a single minisymposium (MS) block:
for s in range (sessoes):
    for p in range(paralelas):
        model.addConstr(gp.quicksum(x[m][b][s][p] for b in range(blocos) for m in range(ms)) <= 1, name = "C1: s_" + str(s)+ " p_" + str(p))
     
# C2) Every MS must be composed for all its blocks, that is, each block must have a garanteed allocation:
# Verificar posteriormente: Por que esta implementação leva 73 seg e a de baixo 537 seg? 
for m in range(ms):
    model.addConstr(gp.quicksum(x[m][b][s][p] for p in range(paralelas) for s in range(sessoes) for b in range(blocos)) == lista_ms[m][2], name = "C2_a: m_" + str(m))
    if lista_ms[m][2] == 2:
        model.addConstr(gp.quicksum(x[m][2][s][p] for p in range(paralelas) for s in range(sessoes)) == 0, name = "C2_b: m_" + str(m))
    else:
        if lista_ms[m][2] == 1:
            model.addConstr(gp.quicksum(x[m][1][s][p] for p in range(paralelas) for s in range(sessoes)) == 0, name = "C2_c: m_" + str(m))
            model.addConstr(gp.quicksum(x[m][2][s][p] for p in range(paralelas) for s in range(sessoes)) == 0, name = "C2_d: m_" + str(m))
for m in range(ms):
    for b in range(blocos):
        if b < lista_ms[m][2]:
            model.addConstr(gp.quicksum(x[m][b][s][p] for p in range(paralelas) for s in range(sessoes)) == 1, name = "C2: m_" + str(m) + " b_" + str(b))
'''
for m in range(ms):
    for b in range(lista_ms[m][2]):
        model.addConstr(gp.quicksum(x[m][b][s][p] for p in range(paralelas) for s in range(sessoes)) == 1, name = "C2_a: m_" + str(m) + " b_" + str(b))
for m in range(ms):
    if lista_ms[m][2] == 2:
        model.addConstr(gp.quicksum(x[m][2][s][p] for p in range(paralelas) for s in range(sessoes)) == 0, name = "C2_b: m_" + str(m))
    else:
        if lista_ms[m][2] == 1:
            model.addConstr(gp.quicksum(x[m][1][s][p] for p in range(paralelas) for s in range(sessoes)) == 0, name = "C2_c: m_" + str(m))
            model.addConstr(gp.quicksum(x[m][2][s][p] for p in range(paralelas) for s in range(sessoes)) == 0, name = "C2_d: m_" + str(m))
'''
      
# C3) Each visiting participant must be able to watch an MS in its entirely, that is, there can be no temporal intersection between blocks:
# Generating Gmini. Example: Gmini[29]: [[29, 0], [29, 1]]
Gmini = []
for m in range(ms):
    if lista_ms[m][2] == 1:
        Gmini.append([[m, 0]])
    else:
        if lista_ms[m][2] == 2:
            Gmini.append([[m, 0], [m, 1]])
        else:
            Gmini.append([[m, 0], [m, 1], [m, 2]])
for m in range(ms):
    for s in range(sessoes):
        model.addConstr(gp.quicksum(x[mm][b][s][p] for p in range(paralelas) for mm, b in Gmini[m]) <= 1, name = "C3: m_" + str(m) + " s_" + str(s))
        
# C4) Every speaker who presents in more than one MS must have their participation guarantee in them, and there cannot be a temporal overlap that prevents them from giving their lectures:
# Generating Gspeaker. All speakers are in Gspeaker.
Gspeaker = []
for k in range(len(lista_pessoas)):
    #if len(lista_pessoas[k][2]) > 1 and len(lista_pessoas[k][3]) == 0:
    if len(lista_pessoas[k][2]) > 1:
        temp = []
        for j in range(len(lista_pessoas[k][2])):
            m = lista_pessoas[k][2][j] - 1
            if lista_ms[m][2] == 1:
                temp.append([m, 0])
            else:
                if lista_ms[m][2] == 2:
                    temp.append([m, 0])
                    temp.append([m, 1])
                else:
                    temp.append([m, 0])
                    temp.append([m, 1])
                    temp.append([m, 2])
        Gspeaker.append(temp)
print("Total speakers: ", len(Gspeaker))
print(Gspeaker)
for k in range(len(Gspeaker)):
    for s in range(sessoes):
        model.addConstr(gp.quicksum(x[mm][b][s][p] for p in range(paralelas) for mm, b in Gspeaker[k]) <= 1, name = "C4: k_" + str(k))


# C5) Every participation of the organizer there cannot be a temporal overlap between MS that he organizes or speaks at:
Gorganizer = []
#for o in range(len(lista_pessoas)):
for o in range(len(lista_pessoas)):
    if o != 140:
        if len(lista_pessoas[o][3]) != 0:
            temp1 = []
            if len(lista_pessoas[o][2]) != 0:
                for j in range(len(lista_pessoas[o][2])):
                   temp1.append(lista_pessoas[o][2][j])
                for j in range(len(lista_pessoas[o][3])):
                    temp1.append(lista_pessoas[o][3][j])
            # eliminate duplications
            temp1 = list(set(temp1))
            if len(temp1) > 1:
                temp = []
                for j in range(len(temp1)):
                    m = temp1[j] - 1
                    if lista_ms[m][2] == 1:
                        temp.append([m, 0])
                    else:
                        if lista_ms[m][2] == 2:
                            temp.append([m, 0])
                            temp.append([m, 1])
                        else:
                            temp.append([m, 0])
                            temp.append([m, 1])
                            temp.append([m, 2])
                Gorganizer.append(temp)
print("Gorganizer: ")
print(Gorganizer)
if len(Gorganizer) > 0:
    for o in range(len(Gorganizer)):
        for s in range(sessoes):
            model.addConstr(gp.quicksum(x[mm][b][s][p] for p in range(paralelas) for mm, b in Gorganizer[o]) <= 1, name = "C1: o_" + str(o)) 


# C6) There is a special set with fixed allocation.
# Example: Gspecial = [[1,2,3,4], [3,2,5,6]]
Gspecial = []
if len(Gspecial) > 0:
    for (m, b, s, p) in Gspecial:
        print(m, b, s, p)
        model.addConstr(x[m][b][s][p] == 1, name = "C6: m_" + str(m) + " b_" + str(b) + " s_" + str(s)+ " p_" + str(p))

# C7) The connection between blocks of the same MS is characterized by the sequence of sessions occupied by these blocks:
for m in range(ms):
    b2 = lista_ms[m][2]
    if b2 > 1:
        b2 = 1
        b1 = 0
        while b2 < lista_ms[m][2]:
            for s1 in range(sessoes):
                for s2 in range(sessoes):
                    model.addConstr(y[m][b1][b2][s1][s2] <= gp.quicksum(x[m][b1][s1][p] for p in range(paralelas)))
                    model.addConstr(y[m][b1][b2][s1][s2] <= gp.quicksum(x[m][b2][s2][p] for p in range(paralelas)))
                    model.addConstr(y[m][b1][b2][s1][s2] + 1 >= gp.quicksum(x[m][b1][s1][p] for p in range(paralelas)) + 
                                                                gp.quicksum(x[m][b2][s2][p] for p in range(paralelas)))
            b2 += 1
            b1 += 1


# C8) The connection between blocks of the same MS is also characterized by the sequence of parallels occupied by these blocks:
for m in range(ms):
    b2 = lista_ms[m][2]
    if b2 > 1:
        b2 = 1
        b1 = 0
        while b2 < lista_ms[m][2]:
            for p1 in range(paralelas):
                for p2 in range(paralelas):
                    model.addConstr(z[m][b1][b2][p1][p2] <= gp.quicksum(x[m][b1][s][p1] for s in range(sessoes)))
                    model.addConstr(z[m][b1][b2][p1][p2] <= gp.quicksum(x[m][b2][s][p2] for s in range(sessoes)))
                    model.addConstr(z[m][b1][b2][p1][p2] + 1 >= gp.quicksum(x[m][b1][s][p1] for s in range(sessoes)) + 
                                                                gp.quicksum(x[m][b2][s][p2] for s in range(sessoes)))
            b2 += 1
            b1 += 1

# Defining the objective function
lexpr = gp.LinExpr(0)
for m in range(ms):
    for b2 in range(1, lista_ms[m][2]):
        b1 = b2 - 1
        for s1 in range(sessoes):
            for s2 in range(sessoes):
                lexpr.add(y[m][b1][b2][s1][s2], lista_pesos_sessoes[s1][s2])
for m in range(ms):
    for b2 in range(1, lista_ms[m][2]):
        b1 = b2 - 1
        for p1 in range(paralelas):
            for p2 in range(paralelas):
                lexpr.add(z[m][b1][b2][p1][p2], lista_pesos_paralelas[p1][p2])   
model.setObjective(lexpr, GRB.MINIMIZE)

# Programming a limit time for Gurobi:
model.setParam('TimeLimit', 1*60)

# Optimizing the model
model.optimize()

'''
#print(model.display())
# From "https://www.gurobi.com/documentation/10.0/examples/workforce2_py.html#subsubsection:workforce2.py":
status = model.Status
if status == gp.GRB.UNBOUNDED:
    print('The model cannot be solved because it is unbounded')
    sys.exit(0)
if status == gp.GRB.OPTIMAL:
    print('The optimal objective is %g' % model.ObjVal)
    sys.exit(0)
if status != gp.GRB.INF_OR_UNBD and status != gp.GRB.INFEASIBLE:
    print('Optimization was stopped with status %d' % status)
    sys.exit(0)

# do IIS
print('The model is infeasible; computing IIS')
removed = []
# Loop until we reduce to a model that can be solved
while True:

    model.computeIIS()
    print('\nThe following constraint cannot be satisfied:')
    for c in model.getConstrs():
        if c.IISConstr:
            print('%s' % c.ConstrName)
            sys.exit(0)
            # Remove a single constraint from the model
            removed.append(str(c.ConstrName))
            model.remove(c)
            break
    print('')
'''

# Retorna a solução
sol_x = [[[[x[m][b][s][p].x for m in range(ms)] for b in range(blocos)] for s in range(sessoes)] for p in range(paralelas)]
conta = 0
for m in range(ms):
    novo = True
    for b in range(lista_ms[m][2]):
        for s in range(sessoes):
            for p in range(paralelas):
                if x[m][b][s][p].x > 0.99:
                    if novo:
                        print()
                    print("ms: ", m + 1,"bloco: ", b + 1, "    sessão:", s + 1, "paralela: ", p + 1)
                    novo = False
                    conta += 1
print(conta)

sol_y = [[[[[y[m][b1][b2][s1][s2].x for m in range(ms)] for b1 in range(blocos)] for b2 in range(blocos)] for s1 in range(sessoes)] for s2 in range(sessoes)]
conta = 0
for m in range(ms):
    b2 = lista_ms[m][2]
    if b2 > 1:
        b2 = 1
        b1 = 0
        while b2 < lista_ms[m][2]:
            for s1 in range(sessoes):
                for s2 in range(sessoes):
                    if y[m][b1][b2][s1][s2].x > 0.99:
                        conta += 1
            b2 += 1
            b1 += 1
print(conta)

sol_z = [[[[[z[m][b1][b2][p1][p2].x for m in range(ms)] for b1 in range(blocos)] for b2 in range(blocos)] for p1 in range(paralelas)] for p2 in range(paralelas)]
conta = 0
for m in range(ms):
    b2 = lista_ms[m][2]
    if b2 > 1:
        b2 = 1
        b1 = 0
        while b2 < lista_ms[m][2]:
            for p1 in range(paralelas):
                for p2 in range(paralelas):
                    if z[m][b1][b2][p1][p2].x > 0.99:
                        conta += 1
            b2 += 1
            b1 += 1
print(conta)