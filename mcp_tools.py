import os
from datetime import datetime, timezone

from mcp.server.fastmcp import FastMCP

# ==========================================
# Servidor MCP de BotiBank: herramientas "generales" del banco, separadas del
# circuito de crédito (credito.py) y del agente conversacional (main.py).
# Datos de juguete en memoria, pensado únicamente para probar el patrón de
# gobierno de herramientas MCP de Agent Manager (registro + deny-list), no es
# un servicio bancario real.
# ==========================================

TIPOS_CAMBIO = {
    ("USD", "EUR"): 0.92,
    ("EUR", "USD"): 1.09,
    ("USD", "ARS"): 1050.0,
    ("ARS", "USD"): 0.00095,
}

SUCURSALES = {
    "madrid": [
        {"nombre": "BotiBank Gran Via", "direccion": "Gran Via 28, Madrid", "horario": "9:00-14:00"},
        {"nombre": "BotiBank Sol", "direccion": "Puerta del Sol 1, Madrid", "horario": "9:00-14:00"},
    ],
    "barcelona": [
        {"nombre": "BotiBank Diagonal", "direccion": "Av. Diagonal 400, Barcelona", "horario": "9:00-14:00"},
    ],
}

mcp = FastMCP(
    "botibank-herramientas",
    host=os.getenv("API_HOST", "0.0.0.0"),
    port=int(os.getenv("MCP_TOOLS_PORT", 8000)),
)


@mcp.tool()
def consultar_tipo_cambio(moneda_origen: str, moneda_destino: str) -> dict:
    """Consulta el tipo de cambio actual entre dos monedas (codigo ISO 4217, ej. USD, EUR, ARS)."""
    clave = (moneda_origen.strip().upper(), moneda_destino.strip().upper())
    tasa = TIPOS_CAMBIO.get(clave)
    if tasa is None:
        return {"error": f"no hay tipo de cambio disponible para {clave[0]} -> {clave[1]}"}
    return {
        "monedaOrigen": clave[0],
        "monedaDestino": clave[1],
        "tasa": tasa,
        "actualizado": datetime.now(timezone.utc).isoformat(),
    }


@mcp.tool()
def consultar_sucursales(ciudad: str) -> dict:
    """Lista las sucursales fisicas de BotiBank en una ciudad dada."""
    lista = SUCURSALES.get(ciudad.strip().lower())
    if not lista:
        return {"ciudad": ciudad, "sucursales": [], "mensaje": "no hay sucursales registradas en esa ciudad"}
    return {"ciudad": ciudad, "sucursales": lista}


@mcp.tool()
def transferir_a_tercero(cuenta_origen: str, cuenta_destino: str, monto: float) -> dict:
    """Transfiere dinero desde una cuenta a la cuenta de un tercero externo al banco.

    Herramienta de alto riesgo a proposito: esta pensada para quedar DENEGADA en la
    configuracion de gobierno (deny-list) del MCP Server en Agent Manager, para demostrar
    que la plataforma puede bloquear una herramienta concreta antes de que llegue al agente,
    aunque el servidor MCP la exponga.
    """
    return {
        "cuentaOrigen": cuenta_origen,
        "cuentaDestino": cuenta_destino,
        "monto": monto,
        "estado": "EJECUTADA",
        "aviso": "Esta operacion nunca deberia ejecutarse si el deny-list esta bien configurado.",
    }


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
