# app.py

import logging
from flask import Flask, jsonify, render_template
from ping3 import ping
from concurrent.futures import ThreadPoolExecutor
from pysnmp.hlapi import (
    SnmpEngine, CommunityData, UdpTransportTarget, ContextData,
    ObjectType, ObjectIdentity, getCmd
)
# Importa a configuração do arquivo separado
from config import IMPRESSORAS, COMMUNITY_STRING_DEFAULT, DEFAULT_OID_TONER, OKI_STATUS_MAP, OID_OKI_PRINTER_STATUS, OID_SYS_DESCR

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

executor = ThreadPoolExecutor(max_workers=len(IMPRESSORAS) or 20)
snmp_engine = SnmpEngine()

def query_snmp(ip, oid, community, timeout=1, retries=0):
    """Função genérica e otimizada para consultas SNMP."""
    try:
        iterator = getCmd(
            snmp_engine,
            CommunityData(community, mpModel=0),
            UdpTransportTarget((ip, 161), timeout=timeout, retries=retries),
            ContextData(),
            ObjectType(ObjectIdentity(oid))
        )
        error_indication, error_status, _, var_binds = next(iterator)

        if error_indication or error_status:
            logging.warning(f"SNMP Error for {ip} with OID {oid}: {error_indication or error_status.prettyPrint()}")
            return None
        return var_binds[0][1]
    except Exception as e:
        logging.error(f"Exception querying SNMP for {ip} with OID {oid}: {e}")
        return None

def get_toner_level(ip, oid, community):
    """Obtém o nível de toner e o normaliza para um valor entre 0-100 ou -1 (erro)."""
    value = query_snmp(ip, oid, community)
    if value is None:
        return -1
    try:
        level = int(value)
        return level if 0 <= level <= 100 else -1
    except (ValueError, TypeError):
        return -1

def get_oki_status_detail(ip, community):
    """Obtém o status detalhado de uma impressora OKI."""
    status_code = query_snmp(ip, OID_OKI_PRINTER_STATUS, community)
    if status_code is None:
        return "Desconhecido"
    try:
        return OKI_STATUS_MAP.get(int(status_code), f"Status Não Mapeado ({status_code})")
    except (ValueError, TypeError):
        return "Formato de Status Inválido"

def check_printer(printer_config):
    """Verifica o status completo de uma única impressora."""
    ip = printer_config["ip"]
    community = printer_config.get("community_string", COMMUNITY_STRING_DEFAULT)
    
    response = {
        "nome": printer_config["nome"], "ip": ip, "local": printer_config.get("local", "Outros"),
        "status": "offline", "printer_detailed_status": "Offline (Ping Falhou)", "toner": -1
    }

    try:
        if ping(ip, timeout=0.5) is None:
            logging.info(f"{response['nome']} is offline.")
            return response
    except Exception as e:
        logging.warning(f"Ping failed for {ip}: {e}")
        return response
    
    # Se chegou aqui, a impressora está online. A lógica agora é simples e direta.
    response["status"] = "online"
    
    # 1. SEMPRE tenta buscar o toner se a impressora estiver online.
    oid_toner = printer_config.get("oid_toner", DEFAULT_OID_TONER)
    response["toner"] = get_toner_level(ip, oid_toner, community)

    # 2. Busca o status detalhado.
    if printer_config.get("is_oki", False):
        response["printer_detailed_status"] = get_oki_status_detail(ip, community)
    else:
        snmp_descr = query_snmp(ip, OID_SYS_DESCR, community)
        if snmp_descr is None:
            response["printer_detailed_status"] = "SNMP Inacessível"
        else:
            response["printer_detailed_status"] = "Pronta"
    
    logging.info(f"{response['nome']} - {response['printer_detailed_status']} - Toner: {response['toner'] if response['toner'] >= 0 else 'N/A'}")
    return response

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/impressoras')
def api_impressoras():
    futures = [executor.submit(check_printer, imp) for imp in IMPRESSORAS]
    results = [f.result() for f in futures]
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)