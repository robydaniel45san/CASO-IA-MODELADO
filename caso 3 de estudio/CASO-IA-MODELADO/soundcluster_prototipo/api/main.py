"""API REST de SoundCluster.

Expone el modelo de segmentacion entrenado: recibe el perfil de comportamiento de un
usuario y devuelve su segmento y la estrategia de personalizacion recomendada.

Ejecutar:  uvicorn main:app --reload --port 8000
Docs:      http://localhost:8000/docs
"""
import os

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")

# Si faltan los artefactos, se entrenan al vuelo (autocontenido).
if not os.path.exists(os.path.join(MODELS_DIR, "kmeans_soundcluster.pkl")):
    import train_model
    train_model.entrenar()

scaler = joblib.load(os.path.join(MODELS_DIR, "scaler.pkl"))
kmeans = joblib.load(os.path.join(MODELS_DIR, "kmeans_soundcluster.pkl"))
mapa_segmentos = joblib.load(os.path.join(MODELS_DIR, "mapa_segmentos.pkl"))
VARIABLES = joblib.load(os.path.join(MODELS_DIR, "variables.pkl"))

ESTRATEGIAS = {
    "Descubridores nocturnos": {
        "playlists": "Novedades semanales y mixes de descubrimiento (electronica/indie)",
        "oferta": "Plan Audiofilo con audio de alta fidelidad",
        "notificacion": "22:00 - 01:00 (pico nocturno)",
    },
    "Clasicos de fin de semana": {
        "playlists": "Colecciones curadas de clasica y jazz para fin de semana",
        "oferta": "Plan Familia (escucha compartida en el hogar)",
        "notificacion": "Sabado y domingo por la tarde",
    },
    "Usuario de fondo": {
        "playlists": "Playlists largas de fondo (focus, lo-fi, pop suave)",
        "oferta": "Plan Free con ads o Premium basico anti-interrupciones",
        "notificacion": "09:00 (inicio de jornada laboral)",
    },
    "Fans del pop diurno": {
        "playlists": "Top hits y pop del momento, actualizado a diario",
        "oferta": "Plan Estudiante con descuento",
        "notificacion": "12:00 - 15:00 (mediodia)",
    },
    "Rockeros intensos": {
        "playlists": "Rock clasico y alternativo, esenciales por decada",
        "oferta": "Plan Premium individual + entradas a conciertos de rock",
        "notificacion": "18:00 - 20:00 (fin de jornada)",
    },
}


class PerfilUsuario(BaseModel):
    horas_semana: float = Field(..., ge=0, le=80, description="Horas de escucha por semana")
    pct_rock: float = Field(..., ge=0, le=100)
    pct_pop: float = Field(..., ge=0, le=100)
    pct_electronica: float = Field(..., ge=0, le=100)
    pct_clasica: float = Field(..., ge=0, le=100)
    pct_artistas_nuevos: float = Field(..., ge=0, le=100)
    pct_playlists_propias: float = Field(..., ge=0, le=100)
    horario_predominante: int = Field(..., ge=0, le=2, description="0=manana, 1=tarde, 2=noche")
    me_gusta_semana: int = Field(..., ge=0)
    pct_saltadas: float = Field(..., ge=0, le=100)
    playlists_creadas: int = Field(..., ge=0)

    model_config = {
        "json_schema_extra": {
            "example": {
                "horas_semana": 24, "pct_rock": 18, "pct_pop": 14,
                "pct_electronica": 46, "pct_clasica": 22, "pct_artistas_nuevos": 40,
                "pct_playlists_propias": 52, "horario_predominante": 2,
                "me_gusta_semana": 28, "pct_saltadas": 35, "playlists_creadas": 12,
            }
        }
    }


class RespuestaSegmento(BaseModel):
    cluster: int
    segmento: str
    estrategia: dict


app = FastAPI(title="SoundCluster API", version="1.0",
              description="Segmentacion de usuarios de streaming musical (K-Means)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # en produccion, restringir al dominio del frontend
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok", "segmentos": list(ESTRATEGIAS.keys())}


@app.post("/segment", response_model=RespuestaSegmento)
def segmentar(perfil: PerfilUsuario):
    """Asigna el perfil recibido a un segmento y devuelve su estrategia."""
    x = pd.DataFrame([perfil.model_dump()]).reindex(columns=VARIABLES)
    x_scaled = scaler.transform(x)
    cluster = int(kmeans.predict(x_scaled)[0])
    segmento = mapa_segmentos[cluster]
    return {
        "cluster": cluster,
        "segmento": segmento,
        "estrategia": ESTRATEGIAS[segmento],
    }
