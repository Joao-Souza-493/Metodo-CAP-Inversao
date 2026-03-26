"""
Script: mapa_estacoes_evento.py
Finalidade: Gera mapa mostrando a localização do evento sísmico 
            a distribuição das estações receptoras e o raio de 
            distância epicentral (10°).
Autor: JP.Souza
Data: Dezembro de 2026
Projeto: Inversão de Mecanismo Focal (Método CAP)
"""
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import geopandas as gpd
import pandas as pd
import numpy as np
from cartopy.geodesic import Geodesic
import cartopy.io.shapereader as shpreader

# --- dados de entrada ---
Latitude = -17.19667
Longitude = -56.69356
R = np.deg2rad(10.0) * 6378000.0
pts = Geodesic().circle(lon=Longitude, lat=Latitude, radius=R, n_samples=180, endpoint=True)

# --- Leitura e Limpeza dos Dados ---
df = pd.read_csv("coordenadas.csv")
df['nome'] = df['nome'].str.strip()
df = df.drop_duplicates()

# Criar GeoDataFrame
gdf = gpd.GeoDataFrame(
    df, geometry=gpd.points_from_xy(df.Longitude, df.Latitude), crs="EPSG:4326"
)

# Criar figura
fig = plt.figure(figsize=(10, 10))
ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
ax.set_extent([-74, -34, -34, 6], crs=ccrs.PlateCarree())

# --- Desenho do Mapa (Brasil, estados, etc.) ---
shapefile = shpreader.natural_earth(resolution='50m',
                                    category='cultural',
                                    name='admin_0_countries')
reader = shpreader.Reader(shapefile)
countries = reader.records()
for country in countries:
    if country.attributes['NAME_LONG'] == 'Brazil':
        ax.add_geometries([country.geometry], crs=ccrs.PlateCarree(),
                          facecolor='antiquewhite', edgecolor='black', linewidth=0.5)
    else:
        ax.add_geometries([country.geometry], crs=ccrs.PlateCarree(),
                          facecolor='linen', edgecolor='black', linewidth=0.2)
demarcacao_estados = cfeature.NaturalEarthFeature(
    category='cultural', name='admin_1_states_provinces_lines',
    scale='50m', facecolor='none'
)
ax.add_feature(demarcacao_estados, edgecolor='gray', linewidth=0.2)

# --- Plot dos Elementos Principais ---

# Evento
ax.plot(
    Longitude, Latitude,
    marker='*', color='red', markersize=20,
    markeredgecolor='black', transform=ccrs.PlateCarree(), label='Evento Sísmico'
)

# Círculo em torno do evento
circle_lons, circle_lats = pts[:, 0], pts[:, 1]
ax.plot(
    circle_lons, circle_lats,
    color="black",
    linewidth=1,
    linestyle='--',
    transform=ccrs.Geodetic()
)

# Função Seta Norte
def add_north_arrow(ax, location=(0.95, 0.95), size=18):
    x, y = location
    ax.text(x, y, u'\u25B2\nN', transform=ax.transAxes,
            ha='center', va='bottom', fontsize=size, fontweight='bold',
            color='black', zorder=10)

add_north_arrow(ax, location=(0.90, 0.90))

color_map = {'BR': 'blue', 'BL': 'green'}
gdf["Rede"] = gdf["nome"].str.split("-").str[1]

# Plotar estações e nomes
for rede, color in color_map.items():
    gdf_rede = gdf[gdf['Rede'] == rede]
    if not gdf_rede.empty:
        ax.scatter(
            gdf_rede.geometry.x, gdf_rede.geometry.y, color=color, marker='^', s=80,
            edgecolor='black', transform=ccrs.PlateCarree(), zorder=3, label=rede
        )
for idx, row in gdf.iterrows():
    ax.text(
        row.geometry.x + 0.2, row.geometry.y, row['nome'],
        transform=ccrs.PlateCarree(), fontsize=8, zorder=4
    )

# --- Finalização do Gráfico ---
ax.legend(title="Legenda")
gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                  linewidth=0, color='none', alpha=0, linestyle='--')
gl.top_labels = True
gl.left_labels = True
gl.bottom_labels = False
gl.right_labels = False
gl.xlabel_style = {'size': 8}
gl.ylabel_style = {'size': 8}

plt.show()
