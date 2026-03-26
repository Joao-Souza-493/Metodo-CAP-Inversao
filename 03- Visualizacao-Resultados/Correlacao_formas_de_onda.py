# -*- coding: utf-8 -*-
"""
Created on Wed Mar 26 10:57:20 2026
@author: JP.Souza
"""

from matplotlib import axes
import glob
import matplotlib.pyplot as plt
import os
from obspy import read # type: ignore
from matplotlib.backends.backend_pdf import PdfPages
from obspy.signal.cross_correlation import correlate, xcorr_max

# --- AUXILIARY FUNCTION
def ler_e_etiquetar(caminho, nome_da_componente):
	if not os.path.exists(caminho):
		return None
	try:
		tr = read(caminho)[0]
		tr.stats.component = nome_da_componente
		return tr
	except Exception as e:
		print(f"Erro ao ler {caminho}: {e}")
		return None

def calcular_cc_max(tr_obs, tr_sin):
	cc_func = correlate(tr_obs.data, tr_sin.data, 50)
	valor_cc = xcorr_max(cc_func)
	return valor_cc

# --- INITIAL SETINGS ---
input_dir = "/home/joao/Documentos/IC/IC/INV/SRCGRD/SRCGRD2_80"
output_file = "comparacao_obs_sint.pdf"

#Search for all Z-component files to list the stations
lista_arquivos_z = sorted(glob.glob(os.path.join(input_dir, "b*_*_dsp.z")))

if not lista_arquivos_z:
	print("Nenhum arquivo encontrado. Verifique o caminho do diretório.")
	exit()

print(f"Encontrados {len(lista_arquivos_z)} arquivos. Gerando PDF...")

with PdfPages(output_file) as pdf:
	#Creating a loop that goes through the file list, skipping every 4 files.
	for i in range (0, len(lista_arquivos_z),4):
		fig, axes = plt.subplots(6, 2, figsize = (15,20))
		grupo_estacoes = lista_arquivos_z[i: i + 4]
		print(f"Processando a página comenaod com o índice {i}...")

		for j, caminho_obs_z in enumerate(grupo_estacoes):
			col = j % 2               # Even numbers (0,2) go on the left. Odd numbers (1,3) go on the right
			row_offset = (j//2) * 3   # For stations 0 and 1 (Top) / For stations 2 and 3 (Bottom)

			#Station identification
			nome_z = os.path.basename(caminho_obs_z)
			estacao = nome_z.split("_")[1]

			#Name of the other components
			nome_obs_r = nome_z.replace(".z", ".r")
			nome_obs_t = nome_z.replace(".z", ".t")

			#Building the full paths
			c_obs_r = os.path.join(input_dir, nome_obs_r)
			c_obs_t = os.path.join(input_dir, nome_obs_t)
			c_sin_z = os.path.join(input_dir, "gs2_" + nome_z)
			c_sin_r = os.path.join(input_dir, "gs2_" + nome_obs_r)
			c_sin_t = os.path.join(input_dir, "gs2_" + nome_obs_t)

			#Labeling
			tr_obs_z = ler_e_etiquetar(caminho_obs_z, "Z")
			tr_obs_r = ler_e_etiquetar(c_obs_r, "R")
			tr_obs_t = ler_e_etiquetar(c_obs_t, "T")
			
			tr_sin_z = ler_e_etiquetar(c_sin_z, "Z")
			tr_sin_r = ler_e_etiquetar(c_sin_r, "R")
			tr_sin_t = ler_e_etiquetar(c_sin_t, "T")
			
			#Organization for the plot
			pares = [
				(tr_obs_z, tr_sin_z, "Z"),
				(tr_obs_r, tr_sin_r, "R"),
				(tr_obs_t, tr_sin_t, "T")
			]

			#Loop to the plot the 3 components (Z,R,T) of the current station
			for k, (obs, sin, comp_nome) in enumerate(pares):
				#Here 'k' define the row(0,1,2) within the station block
				ax = axes[row_offset + k, col]
				coef_cc = calcular_cc_max(obs, sin)

				ax.plot(obs.times(), obs.data, color='black', lw=1.5, label="Observado")
				ax.plot(sin.times(), sin.data, color='red', lw=1, ls='--', label="Sintético")
				ax.set_title(f"Estação: {estacao} | Comp: {comp_nome}| Correlação:{coef_cc[1]:.4f}", fontsize=9)
				ax.set_ylabel("Amplitude")
				ax.legend(loc = "upper right", fontsize = 7)

				if k == 2:
					ax.set_xlabel("Tempo (s)", fontsize = 8)
				
				ax.tick_params(axis='both', which='major', labelsize=8)


		plt.tight_layout()

		pdf.savefig(fig)
		plt.close(fig)

print(f"\nPronto! Relatório salvo em: {output_file}")
