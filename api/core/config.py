from typing import List, Any
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
import json

# -----------------------------------------------------------------------------
# Clase de configuración de la aplicación
# -----------------------------------------------------------------------------
# Hereda de BaseSettings (pydantic-settings), lo que permite:
# - Mapear variables de entorno (ENV o .env) a atributos de Python.
# - Validar y transformar valores automáticamente.
# -----------------------------------------------------------------------------
class Settings(BaseSettings):
    # Cadena de conexión a la base de datos (Postgres con asyncpg en este proyecto).
    database_url: str

    # Orígenes permitidos para CORS.
    # Por defecto: ["*"] (permite todo).
    # En producción, conviene poner explícitamente los dominios válidos.
    cors_allow_origins: List[str] = ["*"]

    # Bandera de debug (equivale a DEBUG=True/False en el .env).
    # Sirve para habilitar logs más detallados u otras configuraciones.
    debug: bool = False

    # Configuración de pydantic-settings
    model_config = SettingsConfigDict(
        env_file=".env",          # Archivo donde leer variables en local
        case_sensitive=False,     # Permite DEBUG o debug en mayúsculas/minúsculas
        extra="ignore",           # Ignora variables que no están declaradas aquí
    )

    # -------------------------------------------------------------------------
    # Validador de cors_allow_origins
    # -------------------------------------------------------------------------
    # Transforma la variable de entorno CORS_ALLOW_ORIGINS a una lista de strings.
    # Soporta:
    #   - None o cadena vacía → ["*"]
    #   - Lista directa (["dom1","dom2"])
    #   - String en formato JSON (ej: '["dom1","dom2"]')
    #   - String CSV (ej: "dom1, dom2")
    # -------------------------------------------------------------------------
    @field_validator("cors_allow_origins", mode="before")
    @classmethod
    def parse_cors(cls, v: Any) -> List[str]:
        if v is None or (isinstance(v, str) and v.strip() == ""):
            return ["*"]   # Si no hay valor, se permite todo por defecto
        if isinstance(v, list):
            return v       # Ya viene como lista
        if isinstance(v, str):
            s = v.strip()
            if s.startswith("["):  # Detecta formato JSON
                return json.loads(s)
            # Caso CSV: "http://localhost:5173,https://front.vercel.app"
            return [item.strip() for item in s.split(",") if item.strip()]
        return v

# Instancia única de Settings (singleton).
# Accedes a settings.database_url, settings.debug, settings.cors_allow_origins, etc.
settings = Settings()
