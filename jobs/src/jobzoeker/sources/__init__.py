"""Bron-adapters. Elke adapter geeft een lijst ruwe vacatures (dicts) terug.

Velden van een ruwe vacature:
    titel, organisatie, url, locatie, publicatiedatum, deadline, contract_hint, regime_hint,
    categorie_hint, beschrijving, extra_bronnen (lijst urls)
Alles behalve titel en url is optioneel. Datums als ISO-string, alleen als de bron ze expliciet geeft.
"""

from __future__ import annotations

from collections.abc import Callable

ADAPTERS: dict[str, Callable[[dict, dict], list[dict]]] = {}


def adapter(name: str):
    def deco(fn):
        ADAPTERS[name] = fn
        return fn

    return deco


from . import aggregators, generiek, overheid, venues  # noqa: E402,F401
