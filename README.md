# 📡 Dashboard de Monitoramento de Impressoras

Este projeto foi desenvolvido com o objetivo de **monitorar o status online/offline das impressoras** e **acompanhar o nível de toner**, permitindo realizar a troca preventiva antes que o suprimento se esgote por completo. Isso garante que **nenhum setor tenha suas operações interrompidas** por falta de impressão.

## 🚀 Funcionalidades

- Verifica a conectividade de cada impressora na rede.
- Exibe o nível atual do toner.
- Organiza as impressoras por empreendimento:
  - Lagoa Thermas Clube
  - Ecotowers
  - Jardins da Lagoa
- Interface responsiva e clara com Bootstrap.
- Atualização periódica automática dos dados.

## 🛠 Tecnologias Utilizadas

- **Python** (Flask) – Backend
- **JavaScript** – Atualização dinâmica dos dados
- **HTML + Bootstrap** – Interface responsiva
- **CSS** – Estilo personalizado
- **ping3 / pysnmp** – Comunicação com as impressoras

## 📁 Estrutura do Projeto

dashboard_impressoras/
├── app.py # Servidor Flask
├── impressoras.json # Lista de impressoras e seus dados
├── status.json # Status atualizado das impressoras
├── templates/
│ └── index.html # Página principal
└── static/
├── script.js # Atualização de dados via fetch
└── style.css # Estilização personalizada

✅ Objetivo
Evitar a paralisação das atividades de setores dependentes de impressão, garantindo visibilidade em tempo real do estado das impressoras e antecipação na reposição dos toners.

🧠 Projeto ideal para ambientes corporativos que utilizam diversas impressoras e precisam manter o controle e a eficiência da infraestrutura de impressão.

