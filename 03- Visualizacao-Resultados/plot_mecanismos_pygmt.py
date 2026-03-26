"""
Script: analise_profundidade_rms.py
Finalidade: Realizar a varredura de resultados de inversão (SRCGRD), calcular magnitudes Mw, 
            identificar a profundidade de menor erro (RMS) e gerar gráfico de sensibilidade 
            com mecanismos focais com a sensabilidade usando PyGMT.
Autor: JP.Souza
Data: Dezembro de 2025
Projeto: Inversão de Mecanismo Focal (Método CAP)
"""
import os
import glob
import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt
from obspy.imaging.beachball import beach
import pygmt

print("Iniciando varredura de diretórios...")

dirs = sorted(glob.glob('/home/joao/Documentos/IC/IC/INV/SRCGRD/SRCGRD2_*'), key=lambda d: int(d.split('_')[-1]))
m0_base = 1e20 #Reference seismic moment for magnitude calculation 

#Criando Listas vazias 
profundidades = []
strikes = []
dips = []
rakes = []
rms_valores = []
escalares = []
magnitude = []

#Iterating over directories 
for d in dirs:
    srcout = os.path.join(d, 'srcgrd.out')
    if not os.path.isfile(srcout):
        print(f'[AVISO] {srcout} não encontrado. Pulando diretório.')
        continue
    try:
        with open(srcout, 'r') as f_in:
            lines = f_in.readlines() 

        #Gets the second-to-last line of the file
        best_l2_line = lines[-2]
        parte = best_l2_line.split()
        valores_extraidos = parte[2:]

        #Coverts string values to float
        if len(valores_extraidos) >= 5:
            strike = float(valores_extraidos[0])
            dip = float(valores_extraidos[1])
            rake = float(valores_extraidos[2])
            scalar = float(valores_extraidos[3])
            rms = float(valores_extraidos[4])
        
            #Gets the depth from the directory name
            profundidade_str = d.split('_')[-1]
            profundidade = float(profundidade_str) / 10.0

            #Calculates the moment magnitude 
            m0_final = m0_base * scalar
            Mw = (2/3) * np.log10(m0_final) - 10.7

            # adds the calculated values to the list
            profundidades.append(profundidade)
            strikes.append(strike)
            dips.append(dip)
            rakes.append(rake)
            rms_valores.append(rms)
            escalares.append(scalar)
            magnitude.append(Mw)
            
            print(f'[SUCESSO] Dados extraídos de {d} para profundidade {profundidade} km.')

        else:

            print(f'[ERRO] Não foi possível extrair valores da linha "bestl2" em {srcout}')

    except Exception as e:
        print(f'[ERRO GERAL] Falha ao processar o arquivo {srcout}. Erro: {e}')

print("\n--- Processo de Coleta Finalizado ---")
if profundidades:
    print(f"Total de {len(profundidades)} resultados coletados com sucesso.")
else:
    print("Nenhum dado foi coletado. Verifique os erros acima.")

#Create and organize the DataFrame bt the 'Depth' column and redefine the index
df = pd.DataFrame({
    'profundidade': profundidades,
    'rms': rms_valores,
    'Mw': magnitude,
    'strike': strikes,
    'dip': dips,
    'rake': rakes
})
df = df.sort_values('profundidade').reset_index(drop=True)

print("\nTabela: profundidade (km) e Magnitude Mw")
print(df[['profundidade', 'Mw']])


print("\n--- Iniciando a fase de plotagem ---")


fig = pygmt.Figure()

#Define automatic data limits
x_min, x_max = df.profundidade.min(), df.profundidade.max()
y_min, y_max = df.rms.min(), df.rms.max()

#adds spacing on the axes
espaco_x = 0.9  
espaco_y = (y_max - y_min) * 0.04 

region = [x_min - espaco_x, x_max + espaco_x, y_min - espaco_y, y_max + espaco_y]

#Drawing the base of the graph
fig.basemap(
    region = region,
    projection = "X20c/10c",
    frame = [
        'xaf+l Profundidade (km)', 
        'yaf+l RMS',
        'WSen+glightgray'              
    ]
)

#Drawing the dashed line 
fig.plot(
    x = df.profundidade,
    y = df.rms,
    pen = "1p,black,dashed"
)

#Found the best solution
melhor_solucao = df['rms'].idxmin()
print(f'\n [INFO] Melhor solução encontrada no índice: {melhor_solucao}')
print('Detalhes da melhor solução:')
print(df.loc[melhor_solucao])

#Creates a 'Translator' dataFrame for the fig.emca() function
df_meca = pd.DataFrame({
    'longitude': df.profundidade,
    'latitude': df.rms,
    'depth': df.profundidade,
    'strike': df.strike,
    'dip': df.dip,
    'rake': df.rake,
    'magnitude': df.Mw
})

Dividing the Mecca DataFrame into 'Best' and 'other'
df_meca_melhor = df_meca.loc[[melhor_solucao]]
df_meca_outros = df_meca.drop(melhor_solucao)

#Plot the Focal Mechanisms
fig.meca(
    spec = df_meca_outros,
    convention = "aki",
    scale = "0.5c",
)

#Plot the focal mechanism with the lowest RMS value. 
fig.meca(
    spec = df_meca_melhor,
    convention = "aki",
    scale = "0.5c",
    compressionfill = "red"
)
fig.show()

try:
    fig.savefig("grafico_mecanismos_focais.png") 
    print("\n--- Gráficos 'grafico_mecanismos_focais.pdf' salvos com sucesso! ---")
    
except Exception as e:
    print(f"\n ---[ERRO] não foi possível'salvar ou mostrar o gráfico ---")
    print(f"\Detalhe do erro: {e}")
