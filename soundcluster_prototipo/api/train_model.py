"""Entrena el pipeline de SoundCluster y serializa los artefactos que consume la API.

Reutiliza el mismo generador sintético y preprocesamiento del notebook CRISP-DM,
de modo que la API quede autocontenida: si faltan los .pkl, se ejecuta este script.
Uso: python train_model.py
"""
import os
from dataclasses import dataclass

import numpy as np
import pandas as pd
import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

RANDOM_STATE = 42
MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")

VARIABLES = [
    "horas_semana", "pct_rock", "pct_pop", "pct_electronica", "pct_clasica",
    "pct_artistas_nuevos", "pct_playlists_propias", "horario_predominante",
    "me_gusta_semana", "pct_saltadas", "playlists_creadas",
]


@dataclass
class PerfilLatente:
    nombre: str
    peso: float
    horas_semana: float
    mezcla_genero: tuple
    pct_artistas_nuevos: float
    pct_playlists_propias: float
    horario: tuple
    me_gusta_semana: float
    pct_saltadas: float
    playlists_creadas: float


PERFILES = [
    PerfilLatente("Descubridores nocturnos", 0.20, 25.0, (0.20, 0.15, 0.45, 0.20),
                  34.8, 48.2, (0.10, 0.25, 0.65), 26, 33.9, 11),
    PerfilLatente("Clasicos de fin de semana", 0.18, 16.6, (0.10, 0.15, 0.05, 0.70),
                  12.6, 33.2, (0.20, 0.55, 0.25), 14, 15.9, 5),
    PerfilLatente("Usuario de fondo", 0.24, 29.8, (0.25, 0.45, 0.20, 0.10),
                  11.4, 24.2, (0.45, 0.40, 0.15), 10, 44.1, 4),
    PerfilLatente("Fans del pop diurno", 0.22, 20.2, (0.15, 0.60, 0.15, 0.10),
                  19.8, 39.2, (0.50, 0.40, 0.10), 23, 23.1, 8),
    PerfilLatente("Rockeros intensos", 0.16, 26.2, (0.65, 0.15, 0.15, 0.05),
                  18.6, 45.2, (0.30, 0.45, 0.25), 25, 21.9, 9),
]


def generar_dataset(n=10_000, seed=RANDOM_STATE):
    rng = np.random.default_rng(seed)
    pesos = np.array([p.peso for p in PERFILES]); pesos = pesos / pesos.sum()
    asign = rng.choice(len(PERFILES), size=n, p=pesos)
    filas = []
    for i in asign:
        p = PERFILES[i]
        mezcla = rng.dirichlet(np.array(p.mezcla_genero) * 14 + 0.5) * 100
        filas.append({
            "horas_semana": round(float(np.clip(rng.normal(p.horas_semana, 6), 1, 60)), 1),
            "pct_rock": round(mezcla[0], 1), "pct_pop": round(mezcla[1], 1),
            "pct_electronica": round(mezcla[2], 1), "pct_clasica": round(mezcla[3], 1),
            "pct_artistas_nuevos": round(float(np.clip(rng.normal(p.pct_artistas_nuevos, 10), 0, 100)), 1),
            "pct_playlists_propias": round(float(np.clip(rng.normal(p.pct_playlists_propias, 12), 0, 100)), 1),
            "horario_predominante": int(rng.choice([0, 1, 2], p=p.horario)),
            "me_gusta_semana": int(np.clip(rng.normal(p.me_gusta_semana, 7), 0, None)),
            "pct_saltadas": round(float(np.clip(rng.normal(p.pct_saltadas, 9), 0, 100)), 1),
            "playlists_creadas": int(np.clip(rng.normal(p.playlists_creadas, 4), 0, None)),
            "segmento_real": p.nombre,
        })
    return pd.DataFrame(filas)


def entrenar():
    os.makedirs(MODELS_DIR, exist_ok=True)
    df = generar_dataset()

    X = df[VARIABLES]
    scaler = StandardScaler().fit(X)
    X_scaled = scaler.transform(X)

    kmeans = KMeans(n_clusters=5, random_state=RANDOM_STATE, n_init=10).fit(X_scaled)
    df["cluster"] = kmeans.labels_

    # Nombre por segmento latente mayoritario (dataset sintetico -> uso legitimo)
    mapa = (df.groupby("cluster")["segmento_real"]
            .agg(lambda s: s.value_counts().idxmax()).to_dict())

    joblib.dump(scaler, os.path.join(MODELS_DIR, "scaler.pkl"))
    joblib.dump(kmeans, os.path.join(MODELS_DIR, "kmeans_soundcluster.pkl"))
    joblib.dump(mapa, os.path.join(MODELS_DIR, "mapa_segmentos.pkl"))
    joblib.dump(VARIABLES, os.path.join(MODELS_DIR, "variables.pkl"))
    print("Artefactos generados en", MODELS_DIR)
    print("Mapa de segmentos:", mapa)


if __name__ == "__main__":
    entrenar()
