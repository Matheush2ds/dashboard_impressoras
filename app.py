import logging
from flask import Flask, jsonify, render_template
from ping3 import ping
from pysnmp.hlapi import *

app = Flask(__name__)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

impressoras = [
    {"nome": "Impressora TI Parque", "ip": "172.30.0.224", "local": "Lagoa Thermas Clube"},
    {"nome": "Impressora Bilheteria", "ip": "172.30.0.223", "local": "Lagoa Thermas Clube"},
    
    {"nome": "Impressora Compras", "ip": "192.168.200.89", "local": "Ecotowers"},
    {"nome": "Impressora Almoxarifado Principal", "ip": "192.168.200.87", "local": "Ecotowers"},
    
    {"nome": "Impressora Recepção J. Lagoa", "ip": "172.40.0.30", "local": "Lagoa Jardins"},
    {"nome": "Impressora Sala de Vendas J. Lagoa", "ip": "192.168.3.231", "local": "Lagoa Jardins"},
    
    {"nome": "Impressora Adm Principal", "ip": "172.30.0.201", "local": "Centro de Negócios"},
    {"nome": "Impressora Contabilidade", "ip": "172.30.0.202", "local": "Centro de Negócios"},
    {"nome": "Impressora Financeiro", "ip": "172.30.0.203", "local": "Centro de Negócios"},
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

def consulta_toner(ip):
    try:
        app.logger.info(f"Consultando toner para IP: {ip}")
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
                app.logger.info(f"Toner para {ip}: {valor}%")
                return valor
            else:
                app.logger.warning(f"Valor de toner inválido para {ip}: {valor}")
                return -1 
    except Exception as e:
        app.logger.error(f"Exceção durante a consulta SNMP de toner para {ip}: {e}")
        return -1 

def consulta_oki_status(ip):
    try:
        app.logger.info(f"Consultando status Oki para IP: {ip}")
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
            app.logger.info(f"Status Oki para {ip}: {status_desc} (código: {status_code})")
            return status_desc
    except Exception as e:
        app.logger.error(f"Exceção durante a consulta SNMP de status Oki para {ip}: {e}")
        return "Desconhecido" 

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/impressoras')
def api_impressoras():
    resultado = []
    for imp in impressoras:
        ip = imp["ip"]
        nome = imp["nome"]
        local = imp["local"]

        app.logger.info(f"Verificando impressora: {nome} ({ip})")
        ping_result = ping(ip, timeout=1) 
        status_geral = "online" if ping_result else "offline"

        oki_status_detalhado = "N/A" 
        toner = -1 

        if status_geral == "online":
            oki_status_detalhado = consulta_oki_status(ip)
            toner = consulta_toner(ip)
        else:
            oki_status_detalhado = "Offline (Ping Falhou)" 
            app.logger.info(f"Impressora {nome} ({ip}) está offline.")

        resultado.append({
            "nome": nome,
            "ip": ip,
            "status": status_geral,       
            "oki_status": oki_status_detalhado, 
            "toner": toner,
            "local": local
        })
    return jsonify(resultado)

if __name__ == '__main__':
    app.run(debug=True)