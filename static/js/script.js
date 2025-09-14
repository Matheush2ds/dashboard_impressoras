$(document).ready(function () {
    const themeToggleBtn = $('#theme-toggle');
    const refreshBtn = $('#refresh-data');
    const body = $('body');
    const empreendimentoTabs = $('#empreendimentoTabs');
    const tabContent = $('#empreendimentoTabContent');
    const dateTimeElement = $('#current-datetime');

    // --- LÓGICA DO HEADER (DATA/HORA E ATUALIZAÇÃO) ---
    function updateDateTime() {
        const now = new Date();
        const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' };
        dateTimeElement.text(now.toLocaleDateString('pt-BR', options));
    }
    updateDateTime();
    setInterval(updateDateTime, 1000); // Atualiza a cada segundo

    refreshBtn.on('click', () => {
        refreshBtn.find('i').addClass('fa-spin');
        fetchPrinterData().always(() => {
            // Remove a animação após um pequeno atraso para o efeito ser visível
            setTimeout(() => refreshBtn.find('i').removeClass('fa-spin'), 500);
        });
    });

    // --- Gerenciamento de Tema ---
    function applySavedTheme() {
        const savedTheme = localStorage.getItem('theme');
        const isDarkMode = savedTheme === 'dark';
        body.toggleClass('dark-mode', isDarkMode);
        updateThemeIcon(isDarkMode);
    }
    function updateThemeIcon(isDarkMode) {
        themeToggleBtn.find('i').attr('class', isDarkMode ? 'fas fa-sun' : 'fas fa-moon');
    }
    themeToggleBtn.on('click', () => {
        const isDarkMode = body.toggleClass('dark-mode').hasClass('dark-mode');
        localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
        updateThemeIcon(isDarkMode);
    });
    applySavedTheme();

    // --- Lógica Principal do Dashboard ---
    const showLoading = () => $('#loading-spinner').show();
    const hideLoading = () => $('#loading-spinner').hide();

    function fetchPrinterData() {
        showLoading();
        // Retorna a promessa do AJAX para o botão de refresh saber quando terminou
        return $.ajax({
            url: '/api/impressoras',
            method: 'GET',
            dataType: 'json',
        }).done(data => {
            if (Array.isArray(data)) updateDashboard(data);
        }).fail(() => {
            // Mostrar erro
        }).always(() => {
            hideLoading();
        });
    }

    function getPrinterVisualState(p) {
        const state = { cardClass: 'status-offline', tonerClass: 'empty' };
        const detail = (p.printer_detailed_status || '').toLowerCase();
        if (p.status === 'online') {
            state.cardClass = 'status-online';
            if (detail.includes('inacessível') || detail.includes('erro') || detail.includes('atolamento')) {
                state.cardClass = 'status-error';
            } else if (p.toner >= 0 && p.toner <= 15) {
                state.cardClass = 'status-toner-low';
            }
        }
        if (p.toner >= 0) {
            if (p.toner > 60) state.tonerClass = 'high';
            else if (p.toner > 20) state.tonerClass = 'medium';
            else state.tonerClass = 'low';
        }
        return state;
    }

    function createPrinterCardHtml(p) {
        const state = getPrinterVisualState(p);
        const tonerWidth = p.toner >= 0 ? p.toner : 0;
        const tonerText = p.toner >= 0 ? `${p.toner}%` : 'N/A';

        return `
            <div class="col-xl-3 col-lg-4 col-md-6 col-sm-12 mb-4">
                <div class="card ${state.cardClass}">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <span>${p.nome || 'Desconhecido'}</span>
                        <span class="badge-status">
                            <i class="status-indicator"></i>
                            ${p.printer_detailed_status}
                        </span>
                    </div>
                    <div class="card-body">
                        <p class="card-text text-muted"><strong>IP:</strong> ${p.ip || 'N/A'}</p>
                        <p class="card-text mb-1"><strong>Nível de Toner:</strong> <span class="font-weight-bold">${tonerText}</span></p>
                        <div class="toner-bar mt-1">
                            <div class="toner-fill ${state.tonerClass}" style="width: ${tonerWidth}%;"></div>
                        </div>
                    </div>
                </div>
            </div>`;
    }

    function updateSummaryCounters(printers) {
        // ... (A lógica desta função continua a mesma)
        const counts = printers.reduce((acc, p) => {
            acc.total++;
            const detail = (p.printer_detailed_status || '').toLowerCase();
            if (p.status === 'online') {
                acc.online++;
                if (p.toner >= 0 && p.toner <= 15) acc.lowToner++;
                if (detail.includes('erro') || detail.includes('atolamento') || detail.includes('inacessível')) {
                    acc.error++;
                }
            } else {
                acc.offline++;
            }
            return acc;
        }, { total: 0, online: 0, offline: 0, lowToner: 0, error: 0 });

        $('#total-impressoras').text(counts.total);
        $('#online-impressoras').text(counts.online);
        $('#offline-impressoras').text(counts.offline);
        $('#low-toner-impressoras').text(counts.lowToner);
        $('#error-impressoras').text(counts.error);
    }
    
    function updateDashboard(printers) {
        const grouped = printers.reduce((acc, p) => {
            const local = p.local || 'Outros';
            if (!acc[local]) acc[local] = [];
            acc[local].push(p);
            return acc;
        }, {});

        updateSummaryCounters(printers);
        empreendimentoTabs.empty();
        tabContent.empty();
        let isFirstTab = true;

        for (const local in grouped) {
            const localId = local.replace(/\s+/g, '-').toLowerCase();
            empreendimentoTabs.append(`<li class="nav-item"><a class="nav-link ${isFirstTab ? 'active' : ''}" data-toggle="pill" href="#${localId}" role="tab">${local}</a></li>`);
            
            const cardsHtml = grouped[local].map(createPrinterCardHtml).join('');
            tabContent.append(`<div class="tab-pane fade ${isFirstTab ? 'show active' : ''}" id="${localId}" role="tabpanel"><div class="row">${cardsHtml}</div></div>`);
            
            isFirstTab = false;
        }
    }

    // --- Inicialização ---
    fetchPrinterData();
    setInterval(fetchPrinterData, 60000);
});