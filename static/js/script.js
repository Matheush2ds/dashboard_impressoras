document.addEventListener("DOMContentLoaded", () => {
    let atual = "Lagoa Thermas Clube"; 
    const container = document.getElementById("impressoras");
    
    const totalImpressorasEl = document.getElementById("total-impressoras");
    const onlineImpressorasEl = document.getElementById("online-impressoras");
    const offlineImpressorasEl = document.getElementById("offline-impressoras");

    const themeToggleBtn = document.getElementById("theme-toggle");
    const body = document.body;

    const loadingSpinner = document.getElementById("loading-spinner");

    function applySavedTheme() {
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme === 'dark') {
            body.classList.add('dark-mode');
            themeToggleBtn.innerHTML = '<i class="fas fa-sun"></i> Modo Claro'; 
        } else {
            body.classList.remove('dark-mode');
            themeToggleBtn.innerHTML = '<i class="fas fa-moon"></i> Modo Escuro'; 
        }
    }

    applySavedTheme();

    themeToggleBtn.addEventListener('click', () => {
        if (body.classList.contains('dark-mode')) {
            body.classList.remove('dark-mode');
            localStorage.setItem('theme', 'light');
            themeToggleBtn.innerHTML = '<i class="fas fa-moon"></i> Modo Escuro';
        } else {
            body.classList.add('dark-mode');
            localStorage.setItem('theme', 'dark');
            themeToggleBtn.innerHTML = '<i class="fas fa-sun"></i> Modo Claro';
        }
    });

    function calculateOkiTonerBar(tonerValue) {
        let ktoner = 0;
        let kbarsize = 0;
        let tonerFillClass = '';

        if (tonerValue === -1) {
            ktoner = 0;
            kbarsize = 1;
            tonerFillClass = 'low';
        } else {
            ktoner = tonerValue;
            if (ktoner === 0) {
                kbarsize = 1;
                tonerFillClass = 'low';
            } else if (ktoner < 10) {
                ktoner = 10;
                kbarsize = ktoner;
                tonerFillClass = 'low';
            } else {
                ktoner = Math.round(ktoner / 10) * 10;
                kbarsize = ktoner;

                if (ktoner >= 60) {
                    tonerFillClass = 'high';
                } else if (ktoner >= 20) {
                    tonerFillClass = 'medium';
                } else {
                    tonerFillClass = 'low';
                }
            }
        }
        return { displayValue: ktoner, barWidth: kbarsize, className: tonerFillClass };
    }

    function carregarDados() {
        loadingSpinner.style.display = 'block';
        container.innerHTML = "";

        fetch("/api/impressoras") 
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                loadingSpinner.style.display = 'none';

                const total = data.length;
                const online = data.filter(imp => imp.status === 'online').length;
                const offline = total - online;

                totalImpressorasEl.textContent = total;
                onlineImpressorasEl.textContent = online;
                offlineImpressorasEl.textContent = offline;

                const impressorasFiltradas = data.filter(imp => imp.local === atual);

                if (impressorasFiltradas.length === 0) {
                    container.innerHTML = `
                        <div class="col-12 text-center text-white-50">
                            <p>Nenhuma impressora encontrada para esta localização.</p>
                        </div>
                    `;
                    return;
                }

                impressorasFiltradas.forEach(imp => {
                    let tonerInfo = calculateOkiTonerBar(imp.toner);
                    let tonerHTML = "";

                    if (imp.toner === -1) {
                        tonerHTML = '<span>Desconhecido</span>';
                    } else {
                        tonerHTML = `
                        <div class="toner-container">
                            <span>Black:</span>
                            <div class="toner-bar">
                                <div class="toner-fill ${tonerInfo.className}" style="width: ${tonerInfo.barWidth}%;"></div>
                            </div>
                            <span>${tonerInfo.displayValue}%</span>
                        </div>`;
                    }

                    const statusClass = imp.status === 'online' ? 'status-online' : 'status-offline';
                    const statusBadgeClass = imp.status === 'online' ? 'badge-online' : 'badge-offline';

                    let okiStatusBadgeClass = 'badge-error'; 
                    if (imp.oki_status === 'Online') {
                        okiStatusBadgeClass = 'badge-online';
                    } else if (imp.oki_status === 'Toner Baixo' || imp.oki_status === 'Sem Papel' || imp.oki_status === 'Porta Aberta') {
                        okiStatusBadgeClass = 'badge-toner-low'; 
                    } else if (imp.oki_status === 'Offline' || imp.oki_status === 'Offline (Ping Falhou)' || imp.oki_status === 'Atolamento de Papel' || imp.oki_status === 'Erro Geral da Impressora') {
                        okiStatusBadgeClass = 'badge-offline'; 
                    }

                    container.innerHTML += `
                        <div class="col-lg-4 col-md-6 mb-4">
                            <div class="card h-100 shadow ${statusClass}">
                                <div class="card-header">
                                    ${imp.nome}
                                </div>
                                <div class="card-body">
                                    <p class="card-text"><strong>IP:</strong> ${imp.ip}</p>
                                    <p class="card-text">
                                        <strong>Status Geral:</strong> 
                                        <span class="badge ${statusBadgeClass} badge-status">${imp.status.toUpperCase()}</span>
                                    </p>
                                    <p class="card-text">
                                        <strong>Status Oki:</strong> 
                                        <span class="badge ${okiStatusBadgeClass} badge-status">${imp.oki_status}</span>
                                    </p>
                                    <p class="card-text"><strong>Toner:</strong> ${tonerHTML}</p>
                                </div>
                            </div>
                        </div>
                    `;
                });
            })
            .catch(error => {
                loadingSpinner.style.display = 'none';
                container.innerHTML = `
                    <div class="col-12 text-center text-danger">
                        <p>Erro ao carregar dados das impressoras: ${error.message}</p>
                        <p>Verifique o servidor Flask e a conexão de rede.</p>
                    </div>
                `;
                console.error('Erro na requisição da API:', error);
            });
    }
    
    carregarDados();

    document.querySelectorAll(".nav-link").forEach(link => {
        link.addEventListener("click", (e) => {
            e.preventDefault(); 
            document.querySelectorAll(".nav-link").forEach(l => l.classList.remove("active"));
            link.classList.add("active");
            atual = link.getAttribute("data-empreendimento");
            carregarDados();
        });
    });
});