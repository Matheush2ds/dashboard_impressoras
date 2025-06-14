import logging
from flask import Flask, jsonify, render_template
from ping3 import ping
from pysnmp.hlapi import *
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

impressoras = [
    {"nome": "Impressora TI Parque", "ip": "172.30.0.224", "local": "Lagoa Thermas Clube"},
    {"nome": "Impressora Bilheteria", "ip": "172.30.0.223", "local": "Lagoa Thermas Clube"},
    {"nome": "Impressora RH", "ip": "172.24.0.61", "local": "Lagoa Thermas Clube"},
    {"nome": "Impressora AeB", "ip": "172.30.0.227", "local": "Lagoa Thermas Clube"},
    {"nome": "Almoxarifado Parque", "ip": "172.30.0.221", "local": "Lagoa Thermas Clube"},
    {"nome": "Ambulatório Parque", "ip": "172.30.0.222", "local": "Lagoa Thermas Clube"},
    {"nome": "Impressora Diretoria", "ip": "172.24.0.15", "local": "Lagoa Thermas Clube"},
    {"nome": "AeB Hotel Vermelho", "ip": "172.50.0.30", "local": "Lagoa Thermas Clube"},
    {"nome": "Impressora Financeiro 1", "ip": "172.24.0.11", "local": "Lagoa Thermas Clube"},
    {"nome": "Impressora Financeiro 2", "ip": "172.24.0.12", "local": "Lagoa Thermas Clube"},
    {"nome": "Impressora AeB Vermelho", "ip": "172.50.0.10", "local": "Lagoa Thermas Clube"},
    {"nome": "IMP Marketing", "ip": "172.24.0.17", "local": "Lagoa Thermas Clube"},
    {"nome": "Contabilidade", "ip": "172.24.0.10", "local": "Lagoa Thermas Clube"},
    {"nome": "Central de Títulos", "ip": "172.24.0.19", "local": "Lagoa Thermas Clube"},
    {"nome": "Almoxarifado Hotel", "ip": "172.50.0.31", "local": "Lagoa Thermas Clube"},

    {"nome": "Impressora Compras", "ip": "192.168.200.89", "local": "Ecotowers"},
    {"nome": "Impressora Almoxarifado Principal", "ip": "192.168.200.87", "local": "Ecotowers"},
    
    {"nome": "Impressora Recepção J. Lagoa", "ip": "172.40.0.30", "local": "Lagoa Jardins"},
    
    {"nome": "Sala de vendas Eco", "ip": "192.168.200.91", "local": "Sala de Vendas"},
    {"nome": "Sala de vendas Lagoa Quente", "ip": "172.30.0.228", "local": "Sala de Vendas"},
    {"nome": "Imp Vendas Jardins", "ip": "192.168.3.231", "local": "Sala de Vendas"},
    {"nome": "Sala de venda parque", "ip": "172.30.0.225", "local": "Sala de Vendas"},
]

OID_TONER = '1.3.6.1.2.1.43.11.1.1.9.1.1' 
OID_OKI_PRINTER_STATUS = '1.3.6.1.4.1.258.1.1.1.1.1.2'

OKI_STATUS_MAP = {
    1: "Online",
    2: "Offline",
    3: "Nenhuma Impressora Conectada",
    4: "Toner Baixo",
    5: "Sem Papel",
    6: "Atolamento de Papel",
    7: "Porta Aberta",
    16: "Erro Geral da Impressora"
}

executor = ThreadPoolExecutor(max_workers=20) 

def consulta_toner(ip):
    try:
        errorIndication, errorStatus, errorIndex, varBinds = next(
            getCmd(
                SnmpEngine(),
                CommunityData('public', mpModel=0),
                UdpTransportTarget((ip, 161), timeout=1, retries=0),
                ContextData(),
                ObjectType(ObjectIdentity(OID_TONER))
            )
        )

        if errorIndication or errorStatus:
            app.logger.warning(f"Erro SNMP ou indicação de erro para toner em {ip}: {errorIndication or errorStatus}")
            return -1 
        
        for varBind in varBinds:
            valor = int(varBind[1])
            if 0 <= valor <= 100:
                return valor
            else:
                app.logger.warning(f"Valor de toner inválido para {ip}: {valor}")
                return -1 
    except Exception as e:
        app.logger.error(f"Exceção durante a consulta SNMP de toner para {ip}: {e}")
        return -1 

def consulta_oki_status(ip):
    try:
        errorIndication, errorStatus, errorIndex, varBinds = next(
            getCmd(
                SnmpEngine(),
                CommunityData('public', mpModel=0),
                UdpTransportTarget((ip, 161), timeout=1, retries=0),
                ContextData(),
                ObjectType(ObjectIdentity(OID_OKI_PRINTER_STATUS))
            )
        )

        if errorIndication or errorStatus:
            app.logger.warning(f"Erro SNMP ou indicação de erro para status Oki em {ip}: {errorIndication or errorStatus}")
            return "Desconhecido" 
        
        for varBind in varBinds:
            status_code = int(varBind[1])
            status_desc = OKI_STATUS_MAP.get(status_code, "Status Não Mapeado")
            return status_desc
    except Exception as e:
        app.logger.error(f"Exceção durante a consulta SNMP de status Oki para {ip}: {e}")
        return "Desconhecido" 

def check_printer_status(imp):
    ip = imp["ip"]
    nome = imp["nome"]
    local = imp["local"]

    app.logger.info(f"Verificando impressora (thread): {nome} ({ip})")
    ping_result = ping(ip, timeout=0.5)

    status_geral = "online" if ping_result else "offline"
    oki_status_detalhado = "N/A" 
    toner = -1 

    if status_geral == "online":
        oki_status_detalhado = consulta_oki_status(ip)
        toner = consulta_toner(ip)
    else:
        oki_status_detalhado = "Offline (Ping Falhou)" 
        app.logger.info(f"Impressora {nome} ({ip}) está offline.")

    return {
        "nome": nome,
        "ip": ip,
        "status": status_geral,       
        "oki_status": oki_status_detalhado, 
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
    app.run(debug=True)