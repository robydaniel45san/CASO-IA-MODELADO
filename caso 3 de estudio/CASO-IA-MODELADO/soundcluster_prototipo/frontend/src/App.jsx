import { useState } from "react";

const API_URL = "http://localhost:8000";

// Perfil inicial de ejemplo (un usuario nocturno)
const PERFIL_INICIAL = {
  horas_semana: 24,
  pct_rock: 18,
  pct_pop: 14,
  pct_electronica: 46,
  pct_clasica: 22,
  pct_artistas_nuevos: 40,
  pct_playlists_propias: 52,
  horario_predominante: 2,
  me_gusta_semana: 28,
  pct_saltadas: 35,
  playlists_creadas: 12,
};

const CAMPOS = [
  { key: "horas_semana", label: "Horas de escucha por semana", min: 0, max: 80 },
  { key: "pct_rock", label: "% Rock", min: 0, max: 100 },
  { key: "pct_pop", label: "% Pop", min: 0, max: 100 },
  { key: "pct_electronica", label: "% Electrónica", min: 0, max: 100 },
  { key: "pct_clasica", label: "% Clásica", min: 0, max: 100 },
  { key: "pct_artistas_nuevos", label: "% Artistas nuevos", min: 0, max: 100 },
  { key: "pct_playlists_propias", label: "% Playlists propias", min: 0, max: 100 },
  { key: "me_gusta_semana", label: "Me gusta por semana", min: 0, max: 100 },
  { key: "pct_saltadas", label: "% Canciones saltadas", min: 0, max: 100 },
  { key: "playlists_creadas", label: "Playlists creadas", min: 0, max: 40 },
];

const HORARIOS = [
  { value: 0, label: "Mañana" },
  { value: 1, label: "Tarde" },
  { value: 2, label: "Noche" },
];

export default function App() {
  const [perfil, setPerfil] = useState(PERFIL_INICIAL);
  const [resultado, setResultado] = useState(null);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState(null);

  const sumaGeneros =
    Number(perfil.pct_rock) +
    Number(perfil.pct_pop) +
    Number(perfil.pct_electronica) +
    Number(perfil.pct_clasica);

  function actualizar(key, valor) {
    setPerfil((p) => ({ ...p, [key]: valor === "" ? "" : Number(valor) }));
  }

  async function segmentar() {
    setCargando(true);
    setError(null);
    setResultado(null);
    try {
      const resp = await fetch(`${API_URL}/segment`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(perfil),
      });
      if (!resp.ok) throw new Error(`Error ${resp.status}`);
      setResultado(await resp.json());
    } catch (e) {
      setError("No se pudo contactar la API. ¿Está corriendo en el puerto 8000?");
    } finally {
      setCargando(false);
    }
  }

  return (
    <div className="app">
      <header>
        <h1>SoundCluster</h1>
        <p>Segmentador de usuarios de streaming musical</p>
      </header>

      <div className="grid">
        <section className="card">
          <h2>Perfil de comportamiento</h2>
          <div className="campos">
            {CAMPOS.map((c) => (
              <label key={c.key} className="campo">
                <span>{c.label}</span>
                <input
                  type="number"
                  min={c.min}
                  max={c.max}
                  value={perfil[c.key]}
                  onChange={(e) => actualizar(c.key, e.target.value)}
                />
              </label>
            ))}
            <label className="campo">
              <span>Horario predominante</span>
              <select
                value={perfil.horario_predominante}
                onChange={(e) => actualizar("horario_predominante", e.target.value)}
              >
                {HORARIOS.map((h) => (
                  <option key={h.value} value={h.value}>
                    {h.label}
                  </option>
                ))}
              </select>
            </label>
          </div>

          <p className={`suma ${Math.abs(sumaGeneros - 100) > 5 ? "warn" : ""}`}>
            Suma de géneros: {sumaGeneros.toFixed(0)}% (idealmente ≈ 100%)
          </p>

          <button onClick={segmentar} disabled={cargando}>
            {cargando ? "Analizando..." : "Segmentar usuario"}
          </button>
        </section>

        <section className="card resultado">
          <h2>Resultado</h2>
          {error && <p className="error">{error}</p>}
          {!resultado && !error && (
            <p className="placeholder">
              Ajusta el perfil y presiona “Segmentar usuario” para ver a qué segmento
              pertenece y su estrategia de personalización.
            </p>
          )}
          {resultado && (
            <div className="detalle">
              <div className="badge">Cluster {resultado.cluster}</div>
              <h3>{resultado.segmento}</h3>
              <ul>
                <li>
                  <strong>Playlists:</strong> {resultado.estrategia.playlists}
                </li>
                <li>
                  <strong>Oferta:</strong> {resultado.estrategia.oferta}
                </li>
                <li>
                  <strong>Notificación:</strong> {resultado.estrategia.notificacion}
                </li>
              </ul>
            </div>
          )}
        </section>
      </div>

      <footer>
        <span>Caso de estudio 3 · K-Means · FastAPI + React</span>
      </footer>
    </div>
  );
}
