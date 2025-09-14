COMMUNITY_STRING_DEFAULT = "public"
OID_SYS_DESCR = '1.3.6.1.2.1.1.1.0'
DEFAULT_OID_TONER = '1.3.6.1.2.1.43.11.1.1.9.1.1'
OID_OKI_PRINTER_STATUS = '1.3.6.1.4.1.258.1.1.1.1.1.2'
OKI_SPECIFIC_TONER_OID = '1.3.6.1.4.1.258.1.1.1.1.1.18'

# Mapeamento de status da OKI para textos legíveis
OKI_STATUS_MAP = {
    1: "Online", 2: "Offline", 3: "Nenhuma Impressora Conectada",
    4: "Toner Baixo", 5: "Sem Papel", 6: "Atolamento de Papel",
    7: "Porta Aberta", 16: "Erro Geral da Impressora"
}

IMPRESSORAS = [
    # === Lagoa Thermas Clube ===
    {"nome": "Impressora TI Parque", "ip": "172.30.0.224", "local": "Lagoa Thermas Clube"},
    {"nome": "Impressora Bilheteria", "ip": "172.30.0.223", "local": "Lagoa Thermas Clube"},
    {"nome": "Impressora RH", "ip": "172.24.0.61", "local": "Lagoa Thermas Clube"},
    {"nome": "Impressora AeB", "ip": "172.30.0.227", "local": "Lagoa Thermas Clube"},
    {"nome": "Almoxarifado Parque", "ip": "172.30.0.221", "local": "Lagoa Thermas Clube"},
    {"nome": "Ambulatório Parque", "ip": "172.30.0.222", "local": "Lagoa Thermas Clube"},
    {"nome": "Impressora Diretoria", "ip": "172.24.0.15", "local": "Lagoa Thermas Clube"},
    {"nome": "AeB Hotel Vermelho", "ip": "172.50.0.30", "local": "Lagoa Thermas Clube"},
    {"nome": "Governança Hotel Vermelho", "ip": "172.50.0.200", "local": "Lagoa Thermas Clube"},
    {"nome": "Almoxarifado Hotel Vermelho", "ip": "172.50.0.31", "local": "Lagoa Thermas Clube"},
    {"nome": "IMP Financeiro 1", "ip": "172.24.0.11", "local": "Lagoa Thermas Clube"},
    {"nome": "IMP Financeiro 2", "ip": "172.24.0.12", "local": "Lagoa Thermas Clube"},
    {"nome": "IMP AeB Vermelho", "ip": "172.50.0.10", "local": "Lagoa Thermas Clube"},
    {"nome": "IMP Marketing", "ip": "172.24.0.17", "local": "Lagoa Thermas Clube"},
    {"nome": "Contabilidade", "ip": "172.24.0.10", "local": "Lagoa Thermas Clube"},
    {"nome": "Central de Títulos", "ip": "172.24.0.19", "local": "Lagoa Thermas Clube"},
    {"nome": "Recreação", "ip": "172.30.0.226", "local": "Lagoa Thermas Clube"},
    {"nome": "Imp Sr Ari", "ip": "172.24.0.14", "local": "Lagoa Thermas Clube"},
    {"nome": "Recepção Hotel Vermelho", "ip": "192.168.5.39", "local": "Lagoa Thermas Clube"},

    # === Ecotowers ===
    {"nome": "Impressora Compras", "ip": "192.168.200.89", "local": "Ecotowers"},
    {"nome": "Impressora Almoxarifado Principal", "ip": "192.168.200.87", "local": "Ecotowers"},
    {"nome": "IMP Governança", "ip": "192.168.200.60", "local": "Ecotowers"},
    {"nome": "AEB Ecotowers", "ip": "192.168.200.92", "local": "Ecotowers"},
    {"nome": "IMP Recepção 1 Samsung", "ip": "192.168.200.74", "local": "Ecotowers"},
    {"nome": "IMP Recepção 2 Samsung", "ip": "192.168.200.75", "local": "Ecotowers"},

    # === Sala de Vendas ===
    {"nome": "Sala de vendas Eco", "ip": "192.168.200.91", "local": "Sala de Vendas"},
    {"nome": "Sala de vendas Lagoa Quente", "ip": "172.30.0.228", "local": "Sala de Vendas"},
    {"nome": "Imp Vendas Jardins", "ip": "192.168.3.231", "local": "Sala de Vendas"},
    {"nome": "Sala de venda parque", "ip": "172.30.0.225", "local": "Sala de Vendas"},

    # === Jardins ===
    {"nome": "IMP-JDL-Recepção 1", "ip": "172.40.0.30", "local": "Jardins"},
    {"nome": "IMP-JDL-Recepção 2", "ip": "172.40.0.31", "local": "Jardins"},

    # === CN ===
    {"nome": "IMP-BACK-OFFICE", "ip": "192.168.10.29", "local": "CN"},
    {"nome": "LOJA CENTRO", "ip": "192.168.20.231", "local": "CN"},
    {"nome": "Financeiro CN", "ip": "192.168.10.26", "local": "CN"},
    {"nome": "IMP-SERRA-VERDE", "ip": "192.168.10.27", "local": "CN"},
    {"nome": "Pos Venda IMP-POS-Vendas", "ip": "192.168.10.27", "local": "CN"},
]