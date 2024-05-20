from dataclasses import dataclass
from typing import Any


@dataclass(repr=True)
class Invoice:
    invoice_value: float
    invoice_attributes: dict[str, Any]

    def __init__(self, invoice_payload):
        if len(invoice_payload) > 0:
            self.invoice_value = invoice_payload[0].get("dadosPagamento", None).get("valor", None)
            self.invoice_attributes = {
                "Payed": invoice_payload[0].get("liquidada", None),
                "Invoice Created": invoice_payload[0].get("dataEmissao", None),
                "Invoice Due": invoice_payload[0].get("dataLimite", None),
                "Invoice Nr": invoice_payload[0].get("numeroFatura", None),
                "Invoice Reference": invoice_payload[0].get("referenciaFatura", None),
                "Sanitation Value": invoice_payload[0].get("saneamento", None),
                "Residues Value": invoice_payload[0].get("residuos", None),
                "Consumption Value": invoice_payload[0].get("consumo", None),
                "Taxes": invoice_payload[0].get("taxas", None),
                "VAT/IVA": invoice_payload[0].get("iva", None)
            }
