document.addEventListener("DOMContentLoaded", () => {
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
            if (themeToggleBtn) {
                themeToggleBtn.innerHTML = '<i class="fas fa-sun"></i> Modo Claro'; 
            }
        } else {
            body.classList.remove('dark-mode');
            if (themeToggleBtn) {
                themeToggleBtn.innerHTML = '<i class="fas fa-moon"></i> Modo Escuro'; 
            }
        }
    }

    applySavedTheme();

    if (themeToggleBtn) {
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
    }

    function calculateOkiTonerBar(tonerValue) {
        let ktoner = 0;
        let kbarsize = 0;
        let tonerFillClass = '';

        if (tonerValue === -1) {
            ktoner = "N/A";
            kbarsize = 0;
            tonerFillClass = 'unknown';
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

    function carregarImpressoras() {
        $('#impressoras-lagoa-thermas').html('<p>Carregando impressoras...</p>');
        $('#impressoras-ecotowers').html('<p>Carregando impressoras...</p>');
        $('#impressoras-lagoa-jardins').html('<p>Carregando impressoras...</p>');
        $('#impressoras-sala-de-vendas').html('<p>Carregando impressoras...</p>');

        if (loadingSpinner) {
            loadingSpinner.style.display = 'block';
        }

        fetch("/api/impressoras")
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (loadingSpinner) {
                    loadingSpinner.style.display = 'none';
                }

                const total = data.length;
                const online = data.filter(imp => imp.status === 'online').length;
                const offline = total - online;

                if (totalImpressorasEl) totalImpressorasEl.textContent = total;
                if (onlineImpressorasEl) onlineImpressorasEl.textContent = online;
                if (offlineImpressorasEl) offlineImpressorasEl.textContent = offline;

                const impressorasPorLocal = {
                    "Lagoa Thermas Clube": [],
                    "Ecotowers": [],
                    "Lagoa Jardins": [],
                    "Sala de Vendas": []
                };

                data.forEach(imp => {
                    if (impressorasPorLocal[imp.local]) {
                        impressorasPorLocal[imp.local].push(imp);
                    }
                });

                renderizarImpressoras(impressorasPorLocal["Lagoa Thermas Clube"], 'impressoras-lagoa-thermas');
                renderizarImpressoras(impressorasPorLocal["Ecotowers"], 'impressoras-ecotowers');
                renderizarImpressoras(impressorasPorLocal["Lagoa Jardins"], 'impressoras-lagoa-jardins');
                renderizarImpressoras(impressorasPorLocal["Sala de Vendas"], 'impressoras-sala-de-vendas');
            })
            .catch(error => {
                if (loadingSpinner) {
                    loadingSpinner.style.display = 'none';
                }
                console.error('Erro na requisição da API:', error);

                const errorMessage = `
                    <div class="col-12 text-center text-danger">
                        <p>Erro ao carregar dados das impressoras: ${error.message}</p>
                        <p>Verifique o servidor Flask e a conexão de rede.</p>
                    </div>
                `;
                $('#impressoras-lagoa-thermas').html(errorMessage);
                $('#impressoras-ecotowers').html(errorMessage);
                $('#impressoras-lagoa-jardins').html(errorMessage);
                $('#impressoras-sala-de-vendas').html(errorMessage);
            });
    }

    function renderizarImpressoras(impressorasArray, elementId) {
        const container = document.getElementById(elementId);
        container.innerHTML = '';

        if (impressorasArray.length === 0) {
            container.innerHTML = `
                <div class="col-12 text-center text-secondary">
                    <p>Nenhuma impressora encontrada para este local.</p>
                </div>
            `;
            return;
        }

        impressorasArray.forEach(imp => {
            let headerStatusClass = '';
            let statusTextClass = '';
            let okiStatusTextClass = 'text-muted';
            let okiStatusBadgeClass = 'badge-secondary';
            let cardBlinkingClass = '';

            if (imp.status === 'online') {
                statusTextClass = 'status-online';
                headerStatusClass = 'status-online';
                
                if (imp.oki_status && imp.oki_status !== "Desconhecido") {
                    if (imp.oki_status === 'Online') {
                        okiStatusTextClass = 'status-online';
                        okiStatusBadgeClass = 'badge-online';
                    } else if (imp.oki_status === 'Toner Baixo' || imp.oki_status === 'Sem Papel' || imp.oki_status === 'Porta Aberta') {
                        headerStatusClass = 'status-toner-low';
                        okiStatusTextClass = 'status-toner-low';
                        okiStatusBadgeClass = 'badge-toner-low';
                    } else if (imp.oki_status === 'Offline' || imp.oki_status === 'Atolamento de Papel' || imp.oki_status === 'Erro Geral da Impressora') {
                        headerStatusClass = 'status-offline';
                        okiStatusTextClass = 'status-offline';
                        okiStatusBadgeClass = 'badge-offline';
                    } else {
                        okiStatusTextClass = 'status-unknown';
                        okiStatusBadgeClass = 'badge-secondary';
                    }
                } else {
                     okiStatusTextClass = 'status-unknown';
                     okiStatusBadgeClass = 'badge-secondary';
                }

                if (imp.toner !== -1 && imp.toner <= 10) {
                    headerStatusClass = 'status-toner-low';
                    cardBlinkingClass = 'blinking';
                } else if (imp.toner !== -1 && imp.toner <= 20 && headerStatusClass === 'status-online') {
                    headerStatusClass = 'status-toner-low'; 
                }

            } else {
                statusTextClass = 'status-offline';
                headerStatusClass = 'status-offline';
                okiStatusTextClass = 'status-offline';
                okiStatusBadgeClass = 'badge-offline';
            }


            let tonerInfo = calculateOkiTonerBar(imp.toner);
            let tonerHTML = "";
            let tonerBarBlinkingClass = '';

            if (imp.toner !== -1 && imp.toner <= 10) {
                tonerBarBlinkingClass = 'blinking';
            }

            if (tonerInfo.displayValue === "N/A") {
                tonerHTML = `<span><span class="status-unknown">N/A</span></span>`;
            } else {
                tonerHTML = `
                    <div class="toner-container">
                        <span>Black:</span>
                        <div class="toner-bar ${tonerBarBlinkingClass}">
                            <div class="toner-fill ${tonerInfo.className}" style="width: ${tonerInfo.barWidth}%;"></div>
                        </div>
                        <span>${tonerInfo.displayValue}%</span>
                    </div>`;
            }
            
            const cardHtml = `
                <div class="col-12 col-sm-6 col-md-3 mb-4">
                    <div class="card h-100 shadow ${headerStatusClass} ${cardBlinkingClass}">
                        <div class="card-header">
                            ${imp.nome}
                        </div>
                        <div class="card-body">
                            <p class="card-text"><strong>IP:</strong> ${imp.ip}</p>
                            <p class="card-text">
                                <strong>Status Geral:</strong> 
                                <span class="${statusTextClass}">${imp.status.toUpperCase()}</span>
                            </p>
                            <p class="card-text">
                                <strong>Status Oki:</strong> 
                                <span class="${okiStatusTextClass}">${imp.oki_status}</span>
                            </p>
                            <p class="card-text"><strong>Toner:</strong> ${tonerHTML}</p>
                        </div>
                    </div>
                </div>
            `;
            container.innerHTML += cardHtml;
        });
    }

    carregarImpressoras();
    setInterval(carregarImpressoras, 30000);

    $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
        carregarImpressoras();
    });
});