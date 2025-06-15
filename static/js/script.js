$(document).ready(function() {
    const themeToggleBtn = $('#theme-toggle');
    const body = $('body');

    if (localStorage.getItem('theme') === 'dark') {
        body.addClass('dark-mode');
        themeToggleBtn.html('<i class="fas fa-sun"></i> Modo Claro');
    } else {
        themeToggleBtn.html('<i class="fas fa-moon"></i> Modo Escuro');
    }

    themeToggleBtn.on('click', function() {
        body.toggleClass('dark-mode');
        if (body.hasClass('dark-mode')) {
            localStorage.setItem('theme', 'dark');
            themeToggleBtn.html('<i class="fas fa-sun"></i> Modo Claro');
        } else {
            localStorage.setItem('theme', 'light');
            themeToggleBtn.html('<i class="fas fa-moon"></i> Modo Escuro');
        }
    });

    function showLoadingSpinner() {
        $('#loading-spinner').show();
        $('.tab-content').hide();
    }

    function hideLoadingSpinner() {
        $('#loading-spinner').hide();
        $('.tab-content').show();
    }

    function fetchPrinterData() {
        showLoadingSpinner();
        $.ajax({
            url: '/api/impressoras',
            method: 'GET',
            dataType: 'json',
            success: function(data) {
                console.log("Dados recebidos da API:", data);
                updateDashboard(data);
                hideLoadingSpinner();
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.error("Erro ao buscar dados das impressoras:", textStatus, errorThrown);
                hideLoadingSpinner();
            }
        });
    }

    function updateDashboard(printerArray) {
        let totalPrinters = 0;
        let onlinePrinters = 0;
        let offlinePrinters = 0;
        let lowTonerPrinters = 0;
        let errorPrinters = 0;

        const organizedData = {};
        printerArray.forEach(printer => {
            if (!organizedData[printer.local]) {
                organizedData[printer.local] = [];
            }
            organizedData[printer.local].push(printer);
        });

        $('.tab-pane .row').empty();

        for (const local in organizedData) {
            const printers = organizedData[local];
            totalPrinters += printers.length;

            const targetTabLink = $(`[data-empreendimento="${local}"]`);
            const targetDivId = targetTabLink.attr('href');
            const $targetDiv = $(`${targetDivId} .row`);

            printers.forEach(printer => {
                let statusClass = '';
                let statusBadge = '';
                let tonerLevelClass = '';
                let tonerBlinkClass = '';
                let cardHeaderStatusClass = '';
                let detailedStatusText = printer.printer_detailed_status || 'Desconhecido';

                switch (printer.status) {
                    case 'online':
                        onlinePrinters++;
                        statusClass = 'status-online';
                        statusBadge = 'badge-online';
                        cardHeaderStatusClass = 'status-online';
                        
                        if (detailedStatusText.includes("Toner Baixo")) {
                            lowTonerPrinters++;
                            tonerBlinkClass = 'blinking';
                            cardHeaderStatusClass = 'status-toner-low';
                            statusBadge = 'badge-toner-low';
                        } else if (detailedStatusText.includes("Erro Geral") || detailedStatusText.includes("Atolamento de Papel") || detailedStatusText.includes("Porta Aberta") || detailedStatusText.includes("Sem Papel")) {
                            errorPrinters++;
                            cardHeaderStatusClass = 'status-error';
                            statusBadge = 'badge-error';
                        }
                        break;
                    case 'offline':
                        offlinePrinters++;
                        statusClass = 'status-offline';
                        statusBadge = 'badge-offline';
                        cardHeaderStatusClass = 'status-offline';
                        break;
                    default:
                        offlinePrinters++;
                        statusClass = 'status-unknown';
                        statusBadge = 'badge-unknown';
                        cardHeaderStatusClass = '';
                        break;
                }

                if (printer.toner !== -1 && printer.toner !== null && printer.toner !== undefined) {
                    if (printer.toner > 60) {
                        tonerLevelClass = 'high';
                    } else if (printer.toner > 20) {
                        tonerLevelClass = 'medium';
                    } else if (printer.toner >= 0 && printer.toner <= 20) {
                        tonerLevelClass = 'low';
                        if (!tonerBlinkClass) {
                            tonerBlinkClass = 'blinking';
                        }
                    } else {
                        tonerLevelClass = 'empty';
                    }
                } else {
                    tonerLevelClass = 'empty';
                }
                
                if (detailedStatusText.includes("SNMP Inacessível") || printer.toner === -1 || printer.toner === undefined || printer.toner === null) {
                    tonerLevelClass = 'empty';
                    printer.toner = 'N/A'; 
                }

                const printerCard = `
                    <div class="col-md-3 col-sm-6 mb-4"> 
                        <div class="card">
                            <div class="card-header ${cardHeaderStatusClass}">
                                <span>${printer.nome}</span>
                                <span class="badge badge-status ${statusBadge}">
                                    ${detailedStatusText.toUpperCase()}
                                </span>
                            </div>
                            <div class="card-body">
                                <p class="card-text"><strong>IP:</strong> ${printer.ip}</p>
                                <p class="card-text"><strong>Local:</strong> ${printer.local}</p>
                                <div class="toner-container">
                                    <p class="card-text mb-0"><strong>Toner:</strong></p>
                                    <div class="toner-bar ${tonerBlinkClass}">
                                        <div class="toner-fill ${tonerLevelClass}" style="width: ${printer.toner !== 'N/A' ? printer.toner : 0}%;">
                                            ${printer.toner !== 'N/A' ? printer.toner + '%' : 'N/A'}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                $targetDiv.append(printerCard);
            });
        }

        $('#total-impressoras').text(totalPrinters);
        $('#online-impressoras').text(onlinePrinters);
        $('#offline-impressoras').text(offlinePrinters);
        $('#low-toner-impressoras').text(lowTonerPrinters);
        $('#error-impressoras').text(errorPrinters);
    }

    fetchPrinterData();
    $('.refresh-icon').on('click', function() {
        fetchPrinterData();
    });
    setInterval(fetchPrinterData, 30000);
    $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
    });
});