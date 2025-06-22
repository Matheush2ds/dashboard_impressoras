import logging
from flask import Flask, jsonify, render_template
from ping3 import ping
from pysnmp.hlapi import *
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

OID_SYS_DESCR = '1.3.6.1.2.1.1.1.0'
DEFAULT_OID_TONER = '1.3.6.1.2.1.43.11.1.1.9.1.1' 
OID_OKI_PRINTER_STATUS = '1.3.6.1.4.1.258.1.1.1.1.1.2' 
OKI_SPECIFIC_TONER_OID = "1.3.6.1.4.1.258.1.1.1.1.1.18"

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
    
    {"nome": "Recepção Jardin1", "ip": "172.40.0.30", "local": "Lagoa Jardins", "community_string": "public", "oid_toner": OKI_SPECIFIC_TONER_OID}, 
    {"nome": "Recepção Jardin2", "ip": "172.40.0.31", "local": "Lagoa Jardins", "community_string": "public", "oid_toner": OKI_SPECIFIC_TONER_OID}, 
    
    {"nome": "Sala de vendas Eco", "ip": "192.168.200.91", "local": "Sala de Vendas", "community_string": "public"},
    {"nome": "Sala de vendas Lagoa Quente", "ip": "172.30.0.228", "local": "Sala de Vendas", "community_string": "public"},
    {"nome": "Imp Vendas Jardins", "ip": "192.168.3.231", "local": "Sala de Vendas", "community_string": "public"},
    {"nome": "Sala de venda parque", "ip": "172.30.0.225", "local": "Sala de Vendas", "community_string": "public"},
]

OKI_STATUS_MAP = {
    1: "Online",
    2: "Offline",
    3: "Nenhuma Impressora Conectada",
    4: "Toner Baixo",
    5: "Sem Papel",
    6: "Atolamento de Papel",
    7: "Porta Aberta",
    16: "Erro Geral da Impressora",
}

executor = ThreadPoolExecutor(max_workers=20)

def consulta_snmp_oid(ip, oid_to_query, community_string='public', timeout=1, retries=0):
    try:
        errorIndication, errorStatus, errorIndex, varBinds = next(
            getCmd(
                SnmpEngine(),
                CommunityData(community_string, mpModel=0),
                UdpTransportTarget((ip, 161), timeout=timeout, retries=retries),
                ContextData(),
                ObjectType(ObjectIdentity(oid_to_query))
            )
        )
        if errorIndication:
            app.logger.warning(f"Erro SNMP para {ip} ({oid_to_query}): {errorIndication}")
            return None
        if errorStatus:
            if errorStatus == 2:
                app.logger.info(f"OID {oid_to_query} não encontrado na impressora {ip}.")
                return None
            app.logger.warning(f"Erro de status SNMP para {ip} ({oid_to_query}): {errorStatus.prettyPrint()}")
            return None
        for varBind in varBinds:
            return varBind[1]
    except Exception as e:
        app.logger.error(f"Exceção SNMP para {ip} ({oid_to_query}): {e}")
        return None

def consulta_toner(ip, oid_toner, community_string='public'):
    raw_value = consulta_snmp_oid(ip, oid_toner, community_string)
    if raw_value is not None:
        try:
            valor = int(raw_value)
            if 0 <= valor <= 100:
                return valor
            else:
                app.logger.warning(f"Valor toner fora da faixa 0-100 para {ip} (OID {oid_toner}): {valor}")
                return -1
        except ValueError:
            app.logger.warning(f"Valor toner não numérico para {ip} (OID {oid_toner}): {raw_value}")
            return -1
    return -1

def consulta_oki_status(ip, community_string='public'):
    raw_value = consulta_snmp_oid(ip, OID_OKI_PRINTER_STATUS, community_string)
    if raw_value is not None:
        try:
            status_code = int(raw_value)
            return OKI_STATUS_MAP.get(status_code, f"Status Não Mapeado ({status_code})")
        except ValueError:
            app.logger.warning(f"Valor status OKI não numérico para {ip}: {raw_value}")
            return "Desconhecido"
    return "N/A"

def check_printer_status(imp):
    ip = imp["ip"]
    nome = imp["nome"]
    local = imp["local"]
    community_string = imp.get("community_string", "public")
    oid_toner_effective = imp.get("oid_toner", DEFAULT_OID_TONER)
    is_oki_printer = (oid_toner_effective == OKI_SPECIFIC_TONER_OID)

    app.logger.info(f"Verificando impressora: {nome} ({ip})")
    ping_result = ping(ip, timeout=0.5)
    status_geral = "online" if ping_result else "offline"
    printer_detailed_status = "Desconhecido"
    toner = -1

    if status_geral == "online":
        sys_descr = consulta_snmp_oid(ip, OID_SYS_DESCR, community_string)
        if sys_descr is None:
            printer_detailed_status = "Online (SNMP Inacessível)"
        else:
            if is_oki_printer:
                printer_detailed_status = consulta_oki_status(ip, community_string)
                toner = consulta_toner(ip, oid_toner_effective, community_string)
                if toner == -1 and "SNMP Inacessível" not in printer_detailed_status:
                    printer_detailed_status += " (Toner OID Inválido/Não Encontrado)"
            else:
                printer_detailed_status = "Online (SNMP OK)"
                toner = consulta_toner(ip, oid_toner_effective, community_string)
                if toner == -1:
                    printer_detailed_status += " (Toner OID Inválido/Não Encontrado)"
    else:
        printer_detailed_status = "Offline (Ping Falhou)"
        app.logger.info(f"Impressora {nome} ({ip}) está offline.")

    return {
        "nome": nome,
        "ip": ip,
        "status": status_geral,
        "printer_detailed_status": printer_detailed_status,
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