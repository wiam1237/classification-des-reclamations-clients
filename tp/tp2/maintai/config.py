
"""Configuration du projet : chemins et paramètres lus depuis l'environnement."""

import os
from dataclasses import dataclass
from pathlib import Path

# Définir le répertoire racine du projet.
ROOT = Path(__file__).resolve().parent.parent

# Contrat d'entrée du modèle : noms et ordre des variables utilisées.
FEATURES = ["temperature_c", "vibration_mm_s", "load_pct", "runtime_hours"]
TARGET = "failure"
SEED = 42


@dataclass(frozen=True)
class Settings:
    """Regroupe les paramètres nécessaires au fonctionnement de MaintAI."""

    data_path: Path
    models_dir: Path
    threshold: float

    # Clé secrète utilisée pour authentifier les requêtes API.
    api_key: str | None = None

    # Liste des origines autorisées à accéder à l'API.
    cors_origins: tuple[str, ...] = ()

    @property
    def model_path(self) -> Path:
        """Retourne le chemin du fichier contenant le modèle entraîné."""
        return self.models_dir / "model.joblib"

    @property
    def info_path(self) -> Path:
        """Retourne le chemin des informations sur le modèle."""
        return self.models_dir / "model_info.json"

    @property
    def metrics_path(self) -> Path:
        """Retourne le chemin des métriques d'évaluation du modèle."""
        return self.models_dir / "metrics.json"


def get_settings() -> Settings:
    """Charge la configuration depuis les variables d'environnement."""

    return Settings(
        # Chemin du jeu de données.
        data_path=Path(
            os.getenv("MAINTAI_DATA_PATH", str(ROOT / "data" / "sensors.csv"))
        ),

        # Répertoire contenant les fichiers du modèle.
        models_dir=Path(os.getenv("MAINTAI_MODELS_DIR", str(ROOT / "models"))),

        # Seuil utilisé pour la prédiction.
        threshold=float(os.getenv("MAINTAI_THRESHOLD", "0.3")),

        # Récupérer la clé API depuis l'environnement.
        api_key=os.getenv("MAINTAI_API_KEY") or None,

        # Récupérer les origines autorisées et les convertir en tuple.
        cors_origins=tuple(
            origin.strip()
            for origin in os.getenv(
                "MAINTAI_CORS_ORIGINS",
                "http://localhost:5500,http://127.0.0.1:5500",
            ).split(",")
            if origin.strip()
        ),
    )
