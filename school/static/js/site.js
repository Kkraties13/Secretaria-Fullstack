/* =========================================
ARQUIVO JS PRINCIPAL (site.js)
Funções de integração com a API Django e gráficos.
=========================================
*/

// Variáveis Globais de API (Ajustar para o seu ambiente)
const API_BASE_URL = '/api/';

/**
 * Função genérica para buscar dados da API.
 * Adiciona o token de autenticação (se disponível).
 * @param {string} url - O endpoint completo da API (ex: 'notas/').
 */
async function fetchData(endpoint) {
    const url = `${API_BASE_URL}${endpoint}`;
    // Simulação de token de autenticação
    const authToken = localStorage.getItem('authToken') || ''; 

    try {
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Token ${authToken}` // Ajustar para o tipo de autenticação do Django (Token ou JWT)
            }
        });

        if (!response.ok) {
            console.error(`Erro ao buscar dados de ${endpoint}: ${response.statusText}`);
            return null;
        }

        return response.json();

    } catch (error) {
        console.error('Erro de rede ao buscar dados:', error);
        return null;
    }
}

/**
 * Função para iniciar o dashboard com uma saudação dinâmica.
 */
function initDashboard() {
    const greetingElement = document.getElementById('user-greeting');
    const dateElement = document.getElementById('current-date');
    const now = new Date();
    const hours = now.getHours();
    
    // Saudação (Bom dia, Boa tarde, Boa noite)
    let greeting = "Olá";
    if (hours >= 5 && hours < 12) {
        greeting = "Bom dia";
    } else if (hours >= 12 && hours < 18) {
        greeting = "Boa tarde";
    } else {
        greeting = "Boa noite";
    }

    // Tenta obter o nome do usuário (simulação)
    const userName = "Aluno(a) Exemplo"; 
    
    if (greetingElement) {
        greetingElement.textContent = `${greeting}, ${userName} 👋`;
    }

    // Data Atual
    if (dateElement) {
        const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
        dateElement.textContent = now.toLocaleDateString('pt-BR', options);
    }
}

/**
 * Função para baixar relatórios, recebendo o URL do backend.
 * @param {string} url - URL do endpoint que gera o PDF/Blob.
 * @param {string} filename - Nome do arquivo para download.
 */
function downloadReport(url, filename) {
    // Simulação: o Django deve retornar um blob (PDF)
    fetch(url, {
        headers: {
            'Authorization': `Token ${localStorage.getItem('authToken') || ''}`
        }
    })
    .then(r => {
        if (!r.ok) throw new Error("Erro ao gerar relatório. Verifique permissões.");
        return r.blob();
    })
    .then(blob => {
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = filename;
        // Adiciona e remove o link rapidamente para acionar o download
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    })
    .catch(error => {
        console.error('Erro no download:', error.message);
        // Exibir mensagem de erro no modal ou console
    });
}


/**
 * Inicializa o gráfico de desempenho na página Notas Acadêmicas.
 */
function initializeNotasChart() {
    const ctx = document.getElementById('desempenhoChart');
    if (!ctx) return; // Sai se o elemento não existir na página

    // Exemplo de dados simulados (seriam obtidos via fetchData('notas/'))
    const notasSimuladas = [8.5, 7.0, 9.2, 6.5, 7.8, 9.5];
    const materias = ['Português', 'Matemática', 'História', 'Geografia', 'Ciências', 'Arte'];

    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: materias,
            datasets: [{
                label: 'Média por Disciplina',
                data: notasSimuladas,
                borderColor: '#007bff',
                backgroundColor: 'rgba(0, 123, 255, 0.1)',
                borderWidth: 2,
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 10,
                    title: {
                        display: true,
                        text: 'Nota (0-10)'
                    }
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                },
                title: {
                    display: true,
                    text: 'Desempenho Geral por Matéria'
                }
            }
        }
    });
}

// Inicializa o dashboard e o gráfico quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
    initDashboard();
    initializeNotasChart();

    // Lógica para toggle da sidebar no mobile
    const toggleButton = document.getElementById('sidebarToggle');
    const wrapper = document.getElementById('wrapper');
    if (toggleButton && wrapper) {
        toggleButton.addEventListener('click', () => {
            wrapper.classList.toggle('toggled');
        });
    }
});