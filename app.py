import logging
from flask import Flask, jsonify, render_template
from ping3 import ping
from concurrent.futures import ThreadPoolExecutor
from pysnmp.hlapi import (
    SnmpEngine, CommunityData, UdpTransportTarget, ContextData,
    ObjectType, ObjectIdentity, getCmd
)

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

OID_SYS_DESCR = '1.3.6.1.2.1.1.1.0'
DEFAULT_OID_TONER = '1.3.6.1.2.1.43.11.1.1.9.1.1'
OID_OKI_PRINTER_STATUS = '1.3.6.1.4.1.258.1.1.1.1.1.2'
OKI_SPECIFIC_TONER_OID = '1.3.6.1.4.1.258.1.1.1.1.1.18'

OKI_STATUS_MAP = {
    1: "Online", 2: "Offline", 3: "Nenhuma Impressora Conectada",
    4: "Toner Baixo", 5: "Sem Papel", 6: "Atolamento de Papel",
    7: "Porta Aberta", 16: "Erro Geral da Impressora"
}

impressoras = [
    {"nome": "Impressora TI Parque", "ip": "172.30.0.224", "local": "Lagoa Thermas Clube", "community_string": "public"},
    {"nome": "Impressora Bilheteria", "ip": "172.30.0.223", "local": "Lagoa Thermas Clube", "community_string": "public"},
    {"nome": "Impressora RH", "ip": "172.24.0.61", "local": "Lagoa Thermas Clube", "community_string": "public"},
    {"nome": "Impressora AeB", "ip": "172.30.0.227", "local": "Lagoa Thermas Clube", "community_string": "public"},
    {"nome": "Almoxarifado Parque", "ip": "172.30.0.221", "local": "Lagoa Thermas Clube", "community_string": "public"},
    {"nome": "Ambulatório Parque", "ip": "172.30.0.222", "local": "Lagoa Thermas Clube", "community_string": "public"},
    {"nome": "Impressora Diretoria", "ip": "172.24.0.15", "local": "Lagoa Thermas Clube", "community_string": "public"},
    {"nome": "AeB Hotel Vermelho", "ip": "172.50.0.30", "local": "Lagoa Thermas Clube", "community_string": "public"},
    {"nome": "Impressora Financeiro 1", "ip": "172.24.0.11", "local": "Lagoa Thermas Clube", "community_string": "public"},
    {"nome": "Impressora Financeiro 2", "ip": "172.24.0.12", "local": "Lagoa Thermas Clube", "community_string": "public"},
    {"nome": "Impressora AeB Vermelho", "ip": "172.50.0.10", "local": "Lagoa Thermas Clube", "community_string": "public"},
    {"nome": "IMP Marketing", "ip": "172.24.0.17", "local": "Lagoa Thermas Clube", "community_string": "public"},
    {"nome": "Contabilidade", "ip": "172.24.0.10", "local": "Lagoa Thermas Clube", "community_string": "public"},
    {"nome": "Central de Títulos", "ip": "172.24.0.19", "local": "Lagoa Thermas Clube", "community_string": "public"},
    {"nome": "Almoxarifado Hotel", "ip": "172.50.0.31", "local": "Lagoa Thermas Clube", "community_string": "public"},
    {"nome": "Impressora Adm Principal", "ip": "172.30.0.201", "local": "Lagoa Thermas Clube", "community_string": "public"},
    {"nome": "Impressora Contabilidade", "ip": "172.30.0.202", "local": "Lagoa Thermas Clube", "community_string": "public"},
    {"nome": "Impressora Financeiro", "ip": "172.30.0.203", "local": "Lagoa Thermas Clube", "community_string": "public"},
    {"nome": "Impressora Compras", "ip": "192.168.200.89", "local": "Ecotowers", "community_string": "public"},
    {"nome": "Impressora Almoxarifado Principal", "ip": "192.168.200.87", "local": "Ecotowers", "community_string": "public"},
    {"nome": "Sala de vendas Eco", "ip": "192.168.200.91", "local": "Sala de Vendas", "community_string": "public"},
    {"nome": "Sala de vendas Lagoa Quente", "ip": "172.30.0.228", "local": "Sala de Vendas", "community_string": "public"},
    {"nome": "Imp Vendas Jardins", "ip": "192.168.3.231", "local": "Sala de Vendas", "community_string": "public"},
    {"nome": "Sala de venda parque", "ip": "172.30.0.225", "local": "Sala de Vendas", "community_string": "public"},
]

executor = ThreadPoolExecutor(max_workers=20)

def consulta_snmp_oid(ip, oid, community_string='public', timeout=1, retries=0):
    try:
        errorIndication, errorStatus, _, varBinds = next(
            getCmd(
                SnmpEngine(),
                CommunityData(community_string, mpModel=0),
                UdpTransportTarget((ip, 161), timeout=timeout, retries=retries),
                ContextData(),
                ObjectType(ObjectIdentity(oid))
            )
        )
        if errorIndication or errorStatus:
            return None
        return varBinds[0][1]
    except:
        return None

def consulta_toner(ip, oid_toner, community_string='public'):
    valor = consulta_snmp_oid(ip, oid_toner, community_string)
    if valor is None:
        return -1
    try:
        val = int(valor)
        return val if 0 <= val <= 100 else -1
    except:
        return -1

def consulta_oki_status(ip, community_string='public'):
    valor = consulta_snmp_oid(ip, OID_OKI_PRINTER_STATUS, community_string)
    if valor is None:
        return "N/A"
    try:
        return OKI_STATUS_MAP.get(int(valor), f"Status Não Mapeado ({valor})")
    except:
        return "Desconhecido"

def check_printer_status(imp):
    ip = imp["ip"]
    nome = imp["nome"]
    local = imp["local"]
    community = imp.get("community_string", "public")
    oid_toner = imp.get("oid_toner", DEFAULT_OID_TONER)
    is_oki = (oid_toner == OKI_SPECIFIC_TONER_OID)
    status_ping = ping(ip, timeout=0.5)
    status = "online" if status_ping else "offline"
    descr = consulta_snmp_oid(ip, OID_SYS_DESCR, community) if status == "online" else None
    toner = -1
    detalhado = "Offline (Ping Falhou)"

    if status == "online":
        if descr is None:
            detalhado = "Online (SNMP Inacessível)"
        else:
            if is_oki:
                detalhado = consulta_oki_status(ip, community)
                toner = consulta_toner(ip, oid_toner, community)
                if toner == -1:
                    detalhado += " (Toner OID Não Encontrado)"
            else:
                detalhado = "Online (SNMP OK)"
                toner = consulta_toner(ip, oid_toner, community)
                if toner == -1:
                    detalhado += " (Toner OID Não Encontrado)"

    return {
        "nome": nome,
        "ip": ip,
        "status": status,
        "printer_detailed_status": detalhado,
        "toner": toner,
        "local": local
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/impressoras')
def api_impressoras():
    resultado = list(executor.map(check_printer_status, impressoras))
    return jsonify(resultado)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
