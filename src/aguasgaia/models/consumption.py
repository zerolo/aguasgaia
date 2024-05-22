from dataclasses import dataclass
from typing import Any


@dataclass(repr=True)
class Consumption:
    consumption_attributes: dict[str, Any]
    consumption_value: str

    def __init__(self, consumption_payload):
        self.consumption_value = 0
        self.consumption_attributes = {}
        if len(consumption_payload) > 0:
            if len(consumption_payload[0].get("funcoesContador", None)) > 0:
                self.consumption_value = consumption_payload[0].get("funcoesContador", None)[0].get("ultimaLeitura",
                                                                                                    None)
                meter = consumption_payload[0].get("chaveContador", None)
                self.consumption_attributes = {
                    "Meter Nr": meter.get("numeroContador", None) if meter is not None else None,
                    "Reading Date": consumption_payload[0].get("funcoesContador", None)[0].get("dataUltimaLeitura",
                                                                                               None),
                    "Meter Brand": consumption_payload[0].get("descMarca", None),
                    "Meter Model": consumption_payload[0].get("descModelo", None)
                }
