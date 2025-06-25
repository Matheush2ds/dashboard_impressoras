$(document).ready(function () {
    const themeToggleBtn = $('#theme-toggle');
    const body = $('body');

    function applySavedTheme() {
        const savedTheme = localStorage.getItem('theme');
        body.toggleClass('dark-mode', savedTheme === 'dark');
        updateThemeIcon();
    }

    function updateThemeIcon() {
        const icon = body.hasClass('dark-mode') ? 'fas fa-sun' : 'fas fa-moon';
        const label = body.hasClass('dark-mode') ? 'Modo Claro' : 'Modo Escuro';
        themeToggleBtn.html(`<i class="${icon}"></i> <span class="ml-2">${label}</span>`);
    }

    themeToggleBtn.on('click', () => {
        body.toggleClass('dark-mode');
        localStorage.setItem('theme', body.hasClass('dark-mode') ? 'dark' : 'light');
        updateThemeIcon();
    });

    applySavedTheme();

    const showLoading = () => $('#loading-spinner').show();
    const hideLoading = () => $('#loading-spinner').hide();

    function showError(msg) {
        $('.dashboard-bg').prepend(`
            <div class="alert alert-danger alert-dismissible fade show" role="alert">
                ${msg}
                <button type="button" class="close" data-dismiss="alert" aria-label="Fechar">
                    <span aria-hidden="true">&times;</span>
                </button>
            </div>
        `);
    }

    function fetchPrinterData() {
        showLoading();
        $.ajax({
            url: '/api/impressoras',
            method: 'GET',
            dataType: 'json',
            success: data => {
                if (Array.isArray(data)) {
                    updateDashboard(data);
                } else {
                    showError('Formato de dados inesperado da API.');
                }
                hideLoading();
            },
            error: () => {
                hideLoading();
                showError('Erro ao buscar dados das impressoras.');
            }
        });
    }

    function updateDashboard(printerArray) {
        let total = 0, online = 0, offline = 0, lowToner = 0, errorCount = 0;

        const grouped = printerArray.reduce((acc, p) => {
            const local = p.local || 'Outros';
            if (!acc[local]) acc[local] = [];
            acc[local].push(p);
            return acc;
        }, {});

        $('.tab-pane .row').empty();

        for (const local in grouped) {
            const printers = grouped[local];
            total += printers.length;
            const target = $(`[data-empreendimento="${local}"]`).attr('href');
            const $targetDiv = $(`${target} .row`);
            if ($targetDiv.length === 0) continue;

            printers.forEach(p => {
                const status = (p.status || 'unknown').toLowerCase();
                const detail = p.printer_detailed_status || 'Desconhecido';
                const toner = p.toner !== undefined && p.toner !== null ? parseInt(p.toner) : -1;

                let statusBadge = '', cardHeaderClass = '', tonerClass = '', blink = '', tonerText = 'N/A';

                if (status === 'online') {
                    online++;
                    cardHeaderClass = 'status-online';
                    statusBadge = 'badge-online';
                    if (detail.includes('Toner Baixo')) {
                        lowToner++;
                        blink = 'blinking';
                        cardHeaderClass = 'status-toner-low';
                        statusBadge = 'badge-toner-low';
                    } else if (
                        detail.includes('Erro Geral') ||
                        detail.includes('Atolamento de Papel') ||
                        detail.includes('Porta Aberta') ||
                        detail.includes('Sem Papel')
                    ) {
                        errorCount++;
                        cardHeaderClass = 'status-error';
                        statusBadge = 'badge-error';
                    }
                } else if (status === 'offline') {
                    offline++;
                    cardHeaderClass = 'status-offline';
                    statusBadge = 'badge-offline';
                } else {
                    offline++;
                    cardHeaderClass = '';
                    statusBadge = 'badge-unknown';
                }

                if (toner >= 0) {
                    tonerText = toner + '%';
                    if (toner > 60) {
                        tonerClass = 'high';
                    } else if (toner > 20) {
                        tonerClass = 'medium';
                    } else {
                        tonerClass = 'low';
                        if (!blink) blink = 'blinking';
                    }
                } else {
                    tonerClass = 'empty';
                    tonerText = 'N/A';
                }

                if (detail.includes('SNMP Inacessível')) {
                    tonerClass = 'empty';
                    tonerText = 'N/A';
                    if (status === 'online') {
                        cardHeaderClass = 'status-error';
                        statusBadge = 'badge-error';
                    }
                }

                const card = `
                    <div class="col-md-3 col-sm-6 mb-4">
                        <div class="card">
                            <div class="card-header ${cardHeaderClass}">
                                <span>${p.nome || 'Nome Desconhecido'}</span>
                                <span class="badge badge-status ${statusBadge}">
                                    ${detail.toUpperCase()}
                                </span>
                            </div>
                            <div class="card-body">
                                <p class="card-text"><strong>IP:</strong> ${p.ip || 'N/A'}</p>
                                <p class="card-text"><strong>Local:</strong> ${p.local || 'N/A'}</p>
                                <div class="toner-container">
                                    <p class="card-text mb-0"><strong>Toner:</strong></p>
                                    <div class="toner-bar ${blink}">
                                        <div class="toner-fill ${tonerClass}" style="width: ${toner >= 0 ? toner : 0}%;">
                                            ${tonerText}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                $targetDiv.append(card);
            });

            if (printers.length === 0) {
                $targetDiv.html('<p class="col-12 text-muted text-center py-5">Nenhuma impressora encontrada neste empreendimento.</p>');
            }
        }

        $('#total-impressoras').text(total);
        $('#online-impressoras').text(online);
        $('#offline-impressoras').text(offline);
        $('#low-toner-impressoras').text(lowToner);
        $('#error-impressoras').text(errorCount);

        $('.tab-pane .row').each(function () {
            if ($(this).is(':empty')) {
                $(this).html('<p class="col-12 text-muted text-center py-5">Nenhuma impressora encontrada neste empreendimento.</p>');
            }
        });
    }

    fetchPrinterData();
    $('.refresh-icon').on('click', fetchPrinterData);
    setInterval(fetchPrinterData, 60000);
});
