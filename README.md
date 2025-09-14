# ?? Dashboard de Monitoramento de Impressoras v2.0

![Python](https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-2.2-black?style=for-the-badge&logo=flask)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6-yellow?style=for-the-badge&logo=javascript)
![Bootstrap](https://img.shields.io/badge/Bootstrap-4.5-purple?style=for-the-badge&logo=bootstrap)


Este projeto foi desenvolvido com o objetivo de **monitorar em tempo real o status das impressoras** e **acompanhar o nível de toner**, permitindo a troca preventiva de suprimentos. O sistema garante que **nenhum setor tenha suas operações interrompidas** por falta de impressão, otimizando o fluxo de trabalho e a gestão de recursos.

## ? Funcionalidades Principais

-   **??? Monitoramento Real-Time:** Visualização clara do status `Online`, `Offline`, `Com Erro` ou `Toner Baixo`.
-   **?? Nível de Toner:** Barras de progresso visuais indicam o nível de suprimento de cada impressora.
-   **?? Organização por Setor:** Agrupamento dinâmico das impressoras por empreendimento (Lagoa Thermas Clube, Ecotowers, Jardins, etc.).
-   **?? Interface Moderna:** Design "premium" com tema claro e escuro, responsivo para desktop e mobile.
-   **?? Atualização Automática:** Os dados são atualizados periodicamente sem a necessidade de recarregar a página.
-   **?? Suporte a Docker:** A aplicação pode ser facilmente executada em um container isolado.

## ??? Tecnologias Utilizadas

| Backend          | Frontend             | Comunicação de Rede   |
| ---------------- | -------------------- | --------------------- |
| ![Python][Python]| ![HTML5][HTML5]      | `ping3` (ICMP)        |
| ![Flask][Flask]  | ![CSS3][CSS3]        | `pysnmp` (SNMP)       |
|                  | ![JavaScript][JS]    |                       |
|                  | ![jQuery][jQuery]    |                       |
|                  | ![Bootstrap][BS]     |                       |

[Python]: https://img.shields.io/badge/-Python-blue?style=flat&logo=python&logoColor=white
[Flask]: https://img.shields.io/badge/-Flask-black?style=flat&logo=flask&logoColor=white
[HTML5]: https://img.shields.io/badge/-HTML5-E34F26?style=flat&logo=html5&logoColor=white
[CSS3]: https://img.shields.io/badge/-CSS3-1572B6?style=flat&logo=css3&logoColor=white
[JS]: https://img.shields.io/badge/-JavaScript-F7DF1E?style=flat&logo=javascript&logoColor=black
[jQuery]: https://img.shields.io/badge/-jQuery-0769AD?style=flat&logo=jquery&logoColor=white
[BS]: https://img.shields.io/badge/-Bootstrap-7952B3?style=flat&logo=bootstrap&logoColor=white

## ?? Estrutura do Projeto

```
/projeto_monitoramento
+-- app.py              # Servidor Flask (Backend)
+-- config.py           # Lista e configuração das impressoras
+-- Dockerfile          # Instruções para criar a imagem Docker
+-- requirements.txt    # Dependências Python
+-- README.md           # Documentação do projeto
+-- /static
¦   +-- /css/style.css
¦   +-- /images/favicon.ico
¦   +-- /js/script.js
+-- /templates
    +-- index.html
```

## ?? Como Executar

Siga os passos abaixo para configurar e rodar o projeto em sua máquina local.

### Pré-requisitos

-   [Python 3.9+](https://www.python.org/downloads/)
-   [Pip](https://pip.pypa.io/en/stable/installation/) (geralmente já vem com o Python)

### Instalação

1.  **Clone o repositório:**
    ```bash
    git clone <url-do-seu-repositorio>
    cd <pasta-do-projeto>
    ```

2.  **Crie e ative um ambiente virtual (recomendado):**
    ```bash
    # Windows
    python -m venv .venv
    .\.venv\Scripts\activate

    # Linux / macOS
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

### Configuração

-   Abra o arquivo `config.py`.
-   Edite a lista `IMPRESSORAS` para adicionar, remover ou modificar os dados das suas impressoras (nome, IP, local).

### Executando a Aplicação

1.  **Inicie o servidor Flask:**
    ```bash
    python app.py
    ```
2.  **Acesse o dashboard** no seu navegador em `http://127.0.0.1:5000`.

## ?? Executando com Docker

Como alternativa, você pode rodar a aplicação em um container Docker, garantindo um ambiente isolado e de fácil deploy.

1.  **Construa a imagem Docker:**
    ```bash
    docker build -t monitor-impressoras .
    ```

2.  **Execute o container:**
    ```bash
    docker run -p 5000:5000 monitor-impressoras
    ```
3.  **Acesse o dashboard** no seu navegador em `http://localhost:5000`.

## ?? Objetivo do Projeto

Evitar a paralisação das atividades de setores dependentes de impressão, garantindo visibilidade em tempo real do estado da infraestrutura e permitindo a antecipação na reposição de suprimentos. Ideal para ambientes corporativos que precisam maximizar a eficiência e o controle de seus ativos de impressão.
