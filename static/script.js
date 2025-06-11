document.addEventListener("DOMContentLoaded", () => {
    let atual = "Lagoa Thermas Clube";
    const container = document.getElementById("impressoras");

    function carregarDados() {
        fetch("/api/impressoras")
            .then(response => response.json())
            .then(data => {
                container.innerHTML = "";
                // Filtra as impressoras pelo local selecionado
                const impressorasFiltradas = data.filter(imp => imp.local === atual);

                impressorasFiltradas.forEach(imp => {
                    let tonerValue = imp.toner;
                    let tonerHTML = "";

                    if (tonerValue === -1) {
                        tonerHTML = '<span>Desconhecido</span>';
                    } else {
                        tonerHTML = `
                        <div class="progress" style="height: 20px;">
                            <div class="progress-bar ${tonerValue > 20 ? 'bg-success' : 'bg-danger'}" role="progressbar" 
                                style="width: ${tonerValue}%" aria-valuenow="${tonerValue}" aria-valuemin="0" aria-valuemax="100">
                                ${tonerValue}%
                            </div>
                        </div>`;
                    }

                    container.innerHTML += `
                        <div class="col-md-3">
                            <div class="card border-${imp.status === 'online' ? 'success' : 'danger'}">
                                <div class="card-body">
                                    <h5 class="card-title">${imp.nome}</h5>
                                    <p class="card-text">IP: ${imp.ip}</p>
                                    <p class="card-text">Status: <span class="text-${imp.status === 'online' ? 'success' : 'danger'}">${imp.status}</span></p>
                                    <p class="card-text">Toner: ${tonerHTML}</p>
                                </div>
                            </div>
                        </div>
                    `;
                });
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
