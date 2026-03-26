"""
Script: remove.py
Finalidade: Filtrar estações por distância epicentral e exportar coordenadas SAC para CSV.
Autor: JP.Souza
Data: Março de 2026
Projeto: Inversão de Mecanismo Focal pelo Método CAP
"""
import os
import shutil
import csv
from obspy import read

os.makedirs('/home/joao/Documentos/IC/IC/INV/DATA/DATA/OUTSIDE', exist_ok=True)
pasta = '/home/joao/Documentos/IC/IC/INV/DATA/DATA/'

arquivos = os.listdir(pasta)

with open('coordenads.csv', 'w', newline='') as arquivo_csv:
	escritor_csv = csv.writer(arquivo_csv)
	escritor_csv.writerow(['nome', 'Latitude', 'Longitude'])

	for arquivo in arquivos:
		if arquivo.endswith(('.z','.t','.r')):
			st = read(os.path.join(pasta, arquivo), debug_headers=True)
			distancia = st[0].stats.sac.dist

			if distancia > 1110:
                
				if arquivo in ('br_guaj_dsp.r', 'br_guaj_dsp.t', 'br_guaj_dsp.z'):
					dados = st[0].stats.sac.knetwk, st[0].stats.sac.stla, st[0].stats.sac.stlo
					escritor_csv.writerow(dados)
				else:
					shutil.move(os.path.join(pasta, arquivo), '/home/joao/Documentos/IC/IC/INV/DATA/DATA/OUTSIDE')
			else: 
				dados = st[0].stats.sac.knetwk, st[0].stats.sac.stla, st[0].stats.sac.stlo
				escritor_csv.writerow(dados)
