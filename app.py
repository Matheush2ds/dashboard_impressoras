from flask import Flask, jsonify, render_template
from ping3 import ping
from pysnmp.hlapi import *

app = Flask(__name__)

impressoras = [
    {"nome": "Impressora TI Parque", "ip": "172.30.0.224", "local": "Lagoa Thermas Clube"},
    {"nome": "Impressora Bilheteria", "ip": "172.30.0.223", "local": "Lagoa Thermas Clube"},
    {"nome": "Impressora Eco 1", "ip": "172.30.1.100", "local": "Ecotowers"},
    {"nome": "Impressora Eco 2", "ip": "172.30.1.101", "local": "Ecotowers"},
    {"nome": "Impressora Jardins A", "ip": "172.30.2.10", "local": "Jardins da Lagoa"},
    {"nome": "Impressora Jardins B", "ip": "172.30.2.11", "local": "Jardins da Lagoa"}
]

OID_TONER = '1.3.6.1.2.1.43.11.1.1.9.1.1'

def consulta_toner(ip):
    try:
        iterator = getCmd(
            SnmpEngine(),
            CommunityData('public', mpModel=0),
            UdpTransportTarget((ip, 161), timeout=1, retries=0),
            ContextData(),
            ObjectType(ObjectIdentity(OID_TONER))
        )
        errorIndication, errorStatus, errorIndex, varBinds = next(iterator)

        if errorIndication or errorStatus:
            return -1
        for varBind in varBinds:
            valor = int(varBind[1])
            return valor
    except:
        return -1

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

        ping_result = ping(ip, timeout=1)
        status = "online" if ping_result else "offline"
        toner = consulta_toner(ip) if status == "online" else -1

        resultado.append({
            "nome": nome,
            "ip": ip,
            "status": status,
            "toner": toner,
            "local": local
        })
    return jsonify(resultado)

if __name__ == '__main__':
    app.run(debug=True)
