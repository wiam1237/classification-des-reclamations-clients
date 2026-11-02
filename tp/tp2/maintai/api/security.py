
"""Authentification par clé API transmise dans l'en-tête HTTP X-API-Key."""

import secrets

from fastapi import Header, HTTPException, status

from maintai.config import get_settings


def require_api_key(
    x_api_key: str | None = Header(default=None),
) -> None:
    """Vérifie la présence et la validité de la clé API du client."""

    # Récupérer la clé API configurée côté serveur.
    expected_key = get_settings().api_key

    # Vérifier que le serveur possède bien une clé configurée.
    if not expected_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Clé API non configurée sur le serveur",
        )

    # Refuser la requête si la clé du client est absente ou incorrecte.
    # compare_digest permet une comparaison sécurisée des deux clés.
    if x_api_key is None or not secrets.compare_digest(
        x_api_key, expected_key
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clé API absente ou invalide",
        )
