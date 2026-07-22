# SoundCluster — Prototipo web (paso 5)

Prototipo funcional que expone el modelo K-Means de segmentación: ingresas el perfil de
comportamiento de un usuario y la app te dice a qué segmento pertenece y qué estrategia de
personalización aplicarle. Arquitectura de tres capas (React → FastAPI → modelo serializado),
el mismo patrón del proyecto de referencia VerifiNews.

## Estructura

```
soundcluster_prototipo/
├── api/                       # Backend (capa de negocio + modelo)
│   ├── main.py                # API FastAPI, endpoint /segment
│   ├── train_model.py         # genera los .pkl (se ejecuta solo si faltan)
│   ├── requirements.txt
│   └── models/                # scaler.pkl, kmeans_soundcluster.pkl, ...
└── frontend/                  # Capa de presentación
    ├── src/App.jsx            # formulario de perfil + panel de resultado
    └── ...
```

## 1. Backend (FastAPI)

```bash
cd api
python -m venv venv && source venv/bin/activate      # opcional
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

- API: http://localhost:8000
- Documentación interactiva (Swagger): http://localhost:8000/docs
- Si la carpeta `models/` está vacía, la API entrena el modelo automáticamente al arrancar.

Prueba rápida:

```bash
curl -X POST http://localhost:8000/segment \
  -H "Content-Type: application/json" \
  -d '{"horas_semana":24,"pct_rock":18,"pct_pop":14,"pct_electronica":46,"pct_clasica":22,"pct_artistas_nuevos":40,"pct_playlists_propias":52,"horario_predominante":2,"me_gusta_semana":28,"pct_saltadas":35,"playlists_creadas":12}'
```

## 2. Frontend (React + Vite)

En otra terminal:

```bash
cd frontend
npm install
npm run dev
```

- App: http://localhost:5173

El frontend espera la API en `http://localhost:8000` (configurable en `src/App.jsx`).

## Flujo

1. El usuario ajusta el perfil de comportamiento en el formulario React.
2. El frontend envía un `POST /segment` con los 11 valores en JSON.
3. La API valida con Pydantic, escala con `scaler.pkl` y predice el cluster con `kmeans_soundcluster.pkl`.
4. La API devuelve el segmento y su estrategia; el frontend lo renderiza.

/COMENZANDO 
