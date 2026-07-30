// Configuração da API
const API_URL = "http://localhost:5000/api";

// Estado global da aplicação
let currentEditingObra = null;
let currentEditingResponsavel = null;
let currentEditingRelatorio = null;
let obras = [];
let responsaveis = [];
let relatoriosMensais = [];

// Inicialização da aplicação
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

async function initializeApp() {
    showLoading(true);
    
    try {
        await checkApiStatus();
        await loadInitialData();
        setupEventListeners();
        showSection('dashboard');
    } catch (error) {
        console.error('Erro ao inicializar aplicação:', error);
        showNotification('Erro ao conectar com a API', 'error');
    } finally {
        showLoading(false);
    }
}

// Verificar status da API
async function checkApiStatus() {
    try {
        const response = await fetch(`${API_URL}/status`);
        if (response.ok) {
            updateApiStatus(true);
        } else {
            throw new Error('API não respondeu');
        }
    } catch (error) {
        updateApiStatus(false);
        throw error;
    }
}

function updateApiStatus(isOnline) {
    const statusElement = document.getElementById('status-indicator');
    if (isOnline) {
        statusElement.className = 'status-online';
        statusElement.innerHTML = '<i class="fas fa-circle"></i><span>API Online</span>';
    } else {
        statusElement.className = 'status-offline';
        statusElement.innerHTML = '<i class="fas fa-circle"></i><span>API Offline</span>';
    }
}

// Carregar dados iniciais
async function loadInitialData() {
    await Promise.all([
        carregarDashboard(),
        carregarResponsaveis(),
        carregarObras()
    ]);
}

// Setup de event listeners
function setupEventListeners() {
    // Navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const section = this.getAttribute('data-section');
            showSection(section);
        });
    });

    // Forms
    document.getElementById('form-obra').addEventListener('submit', handleObraSubmit);
    document.getElementById('form-responsavel').addEventListener('submit', handleResponsavelSubmit);
    document.getElementById('form-relatorio-mensal').addEventListener('submit', handleRelatorioMensalSubmit);

    // CPF mask
    document.getElementById('cpf-responsavel').addEventListener('input', function(e) {
        e.target.value = formatCPF(e.target.value);
    });

    // Modal close on outside click
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                hideModal(modal.id);
            }
        });
    });
}

// Navegação entre seções
function showSection(sectionName) {
    // Update navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    document.querySelector(`[data-section="${sectionName}"]`).classList.add('active');

    // Update content
    document.querySelectorAll('.content-section').forEach(section => {
        section.classList.remove('active');
    });
    document.getElementById(`${sectionName}-section`).classList.add('active');

    // Load section-specific data
    switch(sectionName) {
        case 'dashboard':
            carregarDashboard();
            break;
        case 'obras':
            carregarObras();
            break;
        case 'responsaveis':
            carregarResponsaveis();
            break;
        case 'relatorios-mensais':
            carregarRelatoriosMensais();
            break;
        case 'relatorios':
            carregarDadosRelatorios();
            break;
    }
}

// =================== DASHBOARD ===================
async function carregarDashboard() {
    try {
        const response = await fetch(`${API_URL}/dashboard`);
        const data = await response.json();

        if (response.ok) {
            document.getElementById('total-obras').textContent = data.total_obras;
            document.getElementById('obras-andamento').textContent = data.obras_em_andamento;
            document.getElementById('obras-concluidas').textContent = data.obras_concluidas;
            document.getElementById('total-responsaveis').textContent = data.total_responsaveis;
            document.getElementById('obras-atrasadas').textContent = data.obras_atrasadas;
            document.getElementById('valor-total').textContent = formatCurrency(data.valor_total_orcamentos);
            document.getElementById('valor-gasto').textContent = formatCurrency(data.valor_total_gasto);
            document.getElementById('evolucao-media').textContent = `${data.evolucao_media}%`;
        }
    } catch (error) {
        console.error('Erro ao carregar dashboard:', error);
        showNotification('Erro ao carregar dados do dashboard', 'error');
    }
}

// =================== RESPONSÁVEIS ===================
async function carregarResponsaveis() {
    try {
        const response = await fetch(`${API_URL}/responsibles`);
        const data = await response.json();

        if (response.ok) {
            responsaveis = data;
            renderResponsaveis(data);
            updateResponsaveisSelects(data);
        } else {
            throw new Error(data.error || 'Erro ao carregar responsáveis');
        }
    } catch (error) {
        console.error('Erro ao carregar responsáveis:', error);
        showNotification('Erro ao carregar responsáveis', 'error');
    }
}

function renderResponsaveis(data) {
    const tbody = document.getElementById('responsaveis-tbody');
    tbody.innerHTML = '';

    data.forEach(responsavel => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${responsavel.nome}</td>
            <td>${responsavel.funcao || 'Não informada'}</td>
            <td>${responsavel.contato || 'Não informado'}</td>
            <td>${responsavel.email || 'Não informado'}</td>
            <td>${responsavel.cpf || 'Não informado'}</td>
            <td>
                <button class="btn btn-sm btn-secondary" onclick="editarResponsavel(${responsavel.id})">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-sm btn-danger" onclick="excluirResponsavel(${responsavel.id})">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

function updateResponsaveisSelects(data) {
    const selects = [
        document.getElementById('responsavel-obra'),
        document.getElementById('filtro-responsavel')
    ];

    selects.forEach(select => {
        if (select) {
            const currentValue = select.value;
            select.innerHTML = select.id === 'filtro-responsavel' 
                ? '<option value="">Todos os Responsáveis</option>'
                : '<option value="">Selecione um responsável</option>';
            
            data.forEach(responsavel => {
                const option = document.createElement('option');
                option.value = responsavel.id;
                option.textContent = responsavel.nome;
                select.appendChild(option);
            });
            
            select.value = currentValue;
        }
    });
}

async function handleResponsavelSubmit(e) {
    e.preventDefault();
    showLoading(true);

    const formData = {
        nome: document.getElementById('nome-responsavel').value,
        funcao: document.getElementById('funcao-responsavel').value,
        contato: document.getElementById('contato-responsavel').value,
        email: document.getElementById('email-responsavel').value,
        cpf: document.getElementById('cpf-responsavel').value
    };

    try {
        const url = currentEditingResponsavel 
            ? `${API_URL}/responsibles/${currentEditingResponsavel}`
            : `${API_URL}/responsibles`;
        
        const method = currentEditingResponsavel ? 'PUT' : 'POST';

        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });

        const data = await response.json();

        if (response.ok) {
            showNotification(
                currentEditingResponsavel ? 'Responsável atualizado com sucesso!' : 'Responsável cadastrado com sucesso!',
                'success'
            );
            hideModal('responsavel-modal');
            resetResponsavelForm();
            await carregarResponsaveis();
            await carregarDashboard();
        } else {
            throw new Error(data.error || 'Erro ao salvar responsável');
        }
    } catch (error) {
        console.error('Erro ao salvar responsável:', error);
        showNotification(error.message, 'error');
    } finally {
        showLoading(false);
    }
}

function editarResponsavel(id) {
    const responsavel = responsaveis.find(r => r.id === id);
    if (responsavel) {
        currentEditingResponsavel = id;
        document.getElementById('responsavel-modal-title').textContent = 'Editar Responsável';
        
        document.getElementById('nome-responsavel').value = responsavel.nome;
        document.getElementById('funcao-responsavel').value = responsavel.funcao || '';
        document.getElementById('contato-responsavel').value = responsavel.contato || '';
        document.getElementById('email-responsavel').value = responsavel.email || '';
        document.getElementById('cpf-responsavel').value = responsavel.cpf || '';
        
        showModal('responsavel-modal');
    }
}

async function excluirResponsavel(id) {
    if (confirm('Tem certeza que deseja excluir este responsável?')) {
        showLoading(true);
        
        try {
            const response = await fetch(`${API_URL}/responsibles/${id}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                showNotification('Responsável excluído com sucesso!', 'success');
                await carregarResponsaveis();
                await carregarDashboard();
            } else {
                const data = await response.json();
                throw new Error(data.error || 'Erro ao excluir responsável');
            }
        } catch (error) {
            console.error('Erro ao excluir responsável:', error);
            showNotification(error.message, 'error');
        } finally {
            showLoading(false);
        }
    }
}

function resetResponsavelForm() {
    currentEditingResponsavel = null;
    document.getElementById('responsavel-modal-title').textContent = 'Novo Responsável';
    document.getElementById('form-responsavel').reset();
}

// =================== OBRAS ===================
async function carregarObras() {
    try {
        const status = document.getElementById('filtro-status')?.value || '';
        const responsavelId = document.getElementById('filtro-responsavel')?.value || '';
        
        let url = `${API_URL}/works`;
        const params = new URLSearchParams();
        
        if (status) params.append('status', status);
        if (responsavelId) params.append('responsavel_id', responsavelId);
        
        if (params.toString()) {
            url += '?' + params.toString();
        }

        const response = await fetch(url);
        const data = await response.json();

        if (response.ok) {
            obras = data;
            renderObras(data);
            updateObrasSelects(data);
        } else {
            throw new Error(data.error || 'Erro ao carregar obras');
        }
    } catch (error) {
        console.error('Erro ao carregar obras:', error);
        showNotification('Erro ao carregar obras', 'error');
    }
}

function renderObras(data) {
    const tbody = document.getElementById('obras-tbody');
    tbody.innerHTML = '';

    data.forEach(obra => {
        const evolucao = obra.ultimo_relatorio ? `${obra.ultimo_relatorio.evolucao_obra_percent}%` : 'N/I';
        
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${obra.numero_projeto || 'N/I'}</td>
            <td>${obra.nome}</td>
            <td><span class="status-badge ${getStatusClass(obra.status)}">${obra.status}</span></td>
            <td>${obra.responsavel ? obra.responsavel.nome : 'N/A'}</td>
            <td>${formatDate(obra.data_inicio)}</td>
            <td><strong>${evolucao}</strong></td>
            <td>${obra.orcamento ? formatCurrency(obra.orcamento) : 'Não informado'}</td>
            <td>
                <button class="btn btn-sm btn-secondary" onclick="editarObra(${obra.id})">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-sm btn-info" onclick="verRelatoriosObra(${obra.id})">
                    <i class="fas fa-calendar-alt"></i>
                </button>
                <button class="btn btn-sm btn-success" onclick="gerarRelatorioObra(${obra.id})">
                    <i class="fas fa-file-pdf"></i>
                </button>
                <button class="btn btn-sm btn-danger" onclick="excluirObra(${obra.id})">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

function updateObrasSelects(data) {
    const selects = [
        document.getElementById('obra-relatorio'),
        document.getElementById('obra-relatorio-mensal'),
        document.getElementById('filtro-obra-relatorio')
    ];

    selects.forEach(select => {
        if (select) {
            const currentValue = select.value;
            let defaultOption = '<option value="">Selecione uma obra</option>';
            
            if (select.id === 'filtro-obra-relatorio') {
                defaultOption = '<option value="">Todas as Obras</option>';
            }
            
            select.innerHTML = defaultOption;
            
            data.forEach(obra => {
                const option = document.createElement('option');
                option.value = obra.id;
                option.textContent = `${obra.numero_projeto || 'S/N'} - ${obra.nome}`;
                select.appendChild(option);
            });
            
            select.value = currentValue;
        }
    });
}

function getStatusClass(status) {
    const statusMap = {
        'Em Planejamento': 'status-planejamento',
        'Em Andamento': 'status-andamento',
        'Concluída': 'status-concluida',
        'Pausada': 'status-pausada'
    };
    return statusMap[status] || 'status-planejamento';
}

async function handleObraSubmit(e) {
    e.preventDefault();
    showLoading(true);

    const formData = {
        numero_projeto: document.getElementById('numero-projeto-obra').value,
        nome: document.getElementById('nome-obra').value,
        descricao: document.getElementById('descricao-obra').value,
        endereco: document.getElementById('endereco-obra').value,
        data_inicio: document.getElementById('data-inicio-obra').value,
        data_inicio_real: document.getElementById('data-inicio-real-obra').value || null,
        data_prevista_fim: document.getElementById('data-prevista-obra').value || null,
        data_termino_dedicacao: document.getElementById('data-termino-dedicacao-obra').value || null,
        orcamento: document.getElementById('orcamento-obra').value ? parseFloat(document.getElementById('orcamento-obra').value) : null,
        status: document.getElementById('status-obra').value,
        responsavel_id: parseInt(document.getElementById('responsavel-obra').value)
    };

    try {
        const url = currentEditingObra 
            ? `${API_URL}/works/${currentEditingObra}`
            : `${API_URL}/works`;
        
        const method = currentEditingObra ? 'PUT' : 'POST';

        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });

        const data = await response.json();

        if (response.ok) {
            showNotification(
                currentEditingObra ? 'Obra atualizada com sucesso!' : 'Obra cadastrada com sucesso!',
                'success'
            );
            hideModal('obra-modal');
            resetObraForm();
            await carregarObras();
            await carregarDashboard();
        } else {
            throw new Error(data.error || 'Erro ao salvar obra');
        }
    } catch (error) {
        console.error('Erro ao salvar obra:', error);
        showNotification(error.message, 'error');
    } finally {
        showLoading(false);
    }
}

function editarObra(id) {
    const obra = obras.find(o => o.id === id);
    if (obra) {
        currentEditingObra = id;
        document.getElementById('obra-modal-title').textContent = 'Editar Obra';
        
        document.getElementById('numero-projeto-obra').value = obra.numero_projeto || '';
        document.getElementById('nome-obra').value = obra.nome;
        document.getElementById('descricao-obra').value = obra.descricao || '';
        document.getElementById('endereco-obra').value = obra.endereco || '';
        document.getElementById('data-inicio-obra').value = obra.data_inicio;
        document.getElementById('data-inicio-real-obra').value = obra.data_inicio_real || '';
        document.getElementById('data-prevista-obra').value = obra.data_prevista_fim || '';
        document.getElementById('data-termino-dedicacao-obra').value = obra.data_termino_dedicacao || '';
        document.getElementById('orcamento-obra').value = obra.orcamento || '';
        document.getElementById('status-obra').value = obra.status;
        document.getElementById('responsavel-obra').value = obra.responsavel_id;
        
        showModal('obra-modal');
    }
}

async function excluirObra(id) {
    if (confirm('Tem certeza que deseja excluir esta obra?')) {
        showLoading(true);
        
        try {
            const response = await fetch(`${API_URL}/works/${id}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                showNotification('Obra excluída com sucesso!', 'success');
                await carregarObras();
                await carregarDashboard();
            } else {
                const data = await response.json();
                throw new Error(data.error || 'Erro ao excluir obra');
            }
        } catch (error) {
            console.error('Erro ao excluir obra:', error);
            showNotification(error.message, 'error');
        } finally {
            showLoading(false);
        }
    }
}

function resetObraForm() {
    currentEditingObra = null;
    document.getElementById('obra-modal-title').textContent = 'Nova Obra';
    document.getElementById('form-obra').reset();
}

function filtrarObras() {
    carregarObras();
}

function verRelatoriosObra(obraId) {
    // Filtrar por obra específica e ir para seção de relatórios mensais
    showSection('relatorios-mensais');
    document.getElementById('filtro-obra-relatorio').value = obraId;
    filtrarRelatoriosMensais();
}

// =================== RELATÓRIOS MENSAIS ===================
async function carregarRelatoriosMensais() {
    try {
        // Carregar todos os relatórios mensais
        const allReports = [];
        
        for (const obra of obras) {
            const response = await fetch(`${API_URL}/works/${obra.id}/reports`);
            if (response.ok) {
                const reports = await response.json();
                reports.forEach(report => {
                    report.obra_nome = obra.nome;
                    report.numero_projeto = obra.numero_projeto;
                });
                allReports.push(...reports);
            }
        }
        
        relatoriosMensais = allReports;
        renderRelatoriosMensais(allReports);
    } catch (error) {
        console.error('Erro ao carregar relatórios mensais:', error);
        showNotification('Erro ao carregar relatórios mensais', 'error');
    }
}

function renderRelatoriosMensais(data) {
    const tbody = document.getElementById('relatorios-mensais-tbody');
    tbody.innerHTML = '';

    data.forEach(relatorio => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${relatorio.numero_projeto || 'S/N'} - ${relatorio.obra_nome}</td>
            <td>${formatDate(relatorio.data_relatorio)}</td>
            <td>${formatCurrency(relatorio.valor_gasto)}</td>
            <td>${formatCurrency(relatorio.valor_comprometido)}</td>
            <td><strong>${relatorio.evolucao_obra_percent}%</strong></td>
            <td><span class="status-badge ${relatorio.aprovado ? 'status-concluida' : 'status-andamento'}">${relatorio.aprovado ? 'Aprovado' : 'Pendente'}</span></td>
            <td>
                <button class="btn btn-sm btn-secondary" onclick="editarRelatorioMensal(${relatorio.id})">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-sm btn-danger" onclick="excluirRelatorioMensal(${relatorio.id})">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

async function handleRelatorioMensalSubmit(e) {
    e.preventDefault();
    showLoading(true);

    const obraId = document.getElementById('obra-relatorio-mensal').value;
    const formData = {
        data_relatorio: document.getElementById('data-relatorio-mensal').value,
        valor_gasto: parseFloat(document.getElementById('valor-gasto-relatorio').value) || 0,
        valor_comprometido: parseFloat(document.getElementById('valor-comprometido-relatorio').value) || 0,
        evolucao_obra_percent: parseFloat(document.getElementById('evolucao-obra-relatorio').value) || 0,
        data_inicio_seguro: document.getElementById('data-inicio-seguro-relatorio').value || null,
        data_vencimento_seguro: document.getElementById('data-vencimento-seguro-relatorio').value || null,
        comentarios: document.getElementById('comentarios-relatorio').value,
        relatos_lideranca: document.getElementById('relatos-lideranca-relatorio').value,
        foto1_url: document.getElementById('foto1-url-relatorio').value,
        foto2_url: document.getElementById('foto2-url-relatorio').value
    };

    try {
        let url, method;
        
        if (currentEditingRelatorio) {
            url = `${API_URL}/reports/${currentEditingRelatorio}`;
            method = 'PUT';
        } else {
            url = `${API_URL}/works/${obraId}/reports`;
            method = 'POST';
        }

        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });

        const data = await response.json();

        if (response.ok) {
            showNotification(
                currentEditingRelatorio ? 'Relatório mensal atualizado com sucesso!' : 'Relatório mensal cadastrado com sucesso!',
                'success'
            );
            hideModal('relatorio-mensal-modal');
            resetRelatorioMensalForm();
            await carregarRelatoriosMensais();
            await carregarDashboard();
        } else {
            throw new Error(data.error || 'Erro ao salvar relatório mensal');
        }
    } catch (error) {
        console.error('Erro ao salvar relatório mensal:', error);
        showNotification(error.message, 'error');
    } finally {
        showLoading(false);
    }
}

function editarRelatorioMensal(id) {
    const relatorio = relatoriosMensais.find(r => r.id === id);
    if (relatorio) {
        currentEditingRelatorio = id;
        document.getElementById('relatorio-mensal-modal-title').textContent = 'Editar Relatório Mensal';
        
        document.getElementById('obra-relatorio-mensal').value = relatorio.obra_id;
        document.getElementById('data-relatorio-mensal').value = relatorio.data_relatorio;
        document.getElementById('valor-gasto-relatorio').value = relatorio.valor_gasto;
        document.getElementById('valor-comprometido-relatorio').value = relatorio.valor_comprometido;
        document.getElementById('evolucao-obra-relatorio').value = relatorio.evolucao_obra_percent;
        document.getElementById('data-inicio-seguro-relatorio').value = relatorio.data_inicio_seguro || '';
        document.getElementById('data-vencimento-seguro-relatorio').value = relatorio.data_vencimento_seguro || '';
        document.getElementById('comentarios-relatorio').value = relatorio.comentarios || '';
        document.getElementById('relatos-lideranca-relatorio').value = relatorio.relatos_lideranca || '';
        document.getElementById('foto1-url-relatorio').value = relatorio.foto1_url || '';
        document.getElementById('foto2-url-relatorio').value = relatorio.foto2_url || '';
        
        showModal('relatorio-mensal-modal');
    }
}

async function excluirRelatorioMensal(id) {
    if (confirm('Tem certeza que deseja excluir este relatório mensal?')) {
        showLoading(true);
        
        try {
            const response = await fetch(`${API_URL}/reports/${id}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                showNotification('Relatório mensal excluído com sucesso!', 'success');
                await carregarRelatoriosMensais();
                await carregarDashboard();
            } else {
                const data = await response.json();
                throw new Error(data.error || 'Erro ao excluir relatório mensal');
            }
        } catch (error) {
            console.error('Erro ao excluir relatório mensal:', error);
            showNotification(error.message, 'error');
        } finally {
            showLoading(false);
        }
    }
}

function resetRelatorioMensalForm() {
    currentEditingRelatorio = null;
    document.getElementById('relatorio-mensal-modal-title').textContent = 'Novo Relatório Mensal';
    document.getElementById('form-relatorio-mensal').reset();
}

function filtrarRelatoriosMensais() {
    const obraId = document.getElementById('filtro-obra-relatorio').value;
    const mesAno = document.getElementById('filtro-mes-relatorio').value;
    
    let filteredReports = relatoriosMensais;
    
    if (obraId) {
        filteredReports = filteredReports.filter(r => r.obra_id == obraId);
    }
    
    if (mesAno) {
        const [ano, mes] = mesAno.split('-');
        filteredReports = filteredReports.filter(r => {
            const dataRelatorio = new Date(r.data_relatorio);
            return dataRelatorio.getFullYear() == ano && (dataRelatorio.getMonth() + 1) == mes;
        });
    }
    
    renderRelatoriosMensais(filteredReports);
}

// =================== RELATÓRIOS ===================
async function carregarDadosRelatorios() {
    const select = document.getElementById('obra-relatorio');
    select.innerHTML = '<option value="">Selecione uma obra</option>';
    
    obras.forEach(obra => {
        const option = document.createElement('option');
        option.value = obra.id;
        option.textContent = `${obra.numero_projeto || 'S/N'} - ${obra.nome}`;
        select.appendChild(option);
    });
}

function gerarRelatorioObra(id = null) {
    const obraId = id || document.getElementById('obra-relatorio').value;
    
    if (!obraId) {
        showNotification('Selecione uma obra para gerar o relatório', 'error');
        return;
    }
    
    showNotification('Gerando relatório da obra...', 'info');
    window.open(`${API_URL}/reports/works/${obraId}`, '_blank');
}

function gerarRelatorioGeral() {
    showNotification('Gerando relatório geral...', 'info');
    window.open(`${API_URL}/reports/general`, '_blank');
}

// =================== MODALS ===================
function showModal(modalId) {
    document.getElementById(modalId).style.display = 'block';
    document.body.style.overflow = 'hidden';
}

function hideModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
    document.body.style.overflow = 'auto';
    
    // Reset forms when closing modals
    if (modalId === 'obra-modal') {
        resetObraForm();
    } else if (modalId === 'responsavel-modal') {
        resetResponsavelForm();
    } else if (modalId === 'relatorio-mensal-modal') {
        resetRelatorioMensalForm();
    }
}

// =================== UTILITIES ===================
function showLoading(show) {
    document.getElementById('loading-overlay').style.display = show ? 'flex' : 'none';
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${getNotificationIcon(type)}"></i>
        <span>${message}</span>
    `;
    
    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        border-radius: 0.5rem;
        color: white;
        font-weight: 600;
        z-index: 10000;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        min-width: 300px;
        box-shadow: 0 10px 25px -3px rgba(0, 0, 0, 0.1);
        transform: translateX(100%);
        transition: transform 0.3s ease;
    `;
    
    // Set background color based on type
    const colors = {
        success: '#10b981',
        error: '#ef4444',
        info: '#3b82f6',
        warning: '#f59e0b'
    };
    notification.style.background = colors[type] || colors.info;
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Auto remove
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 4000);
}

function getNotificationIcon(type) {
    const icons = {
        success: 'check-circle',
        error: 'exclamation-circle',
        info: 'info-circle',
        warning: 'exclamation-triangle'
    };
    return icons[type] || icons.info;
}

function formatDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR');
}

function formatCurrency(value) {
    if (!value) return 'R$ 0,00';
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value);
}

function formatCPF(value) {
    // Remove tudo que não é dígito
    value = value.replace(/\D/g, '');
    
    // Aplica a máscara
    value = value.replace(/(\d{3})(\d)/, '$1.$2');
    value = value.replace(/(\d{3})(\d)/, '$1.$2');
    value = value.replace(/(\d{3})(\d{1,2})$/, '$1-$2');
    
    return value;
}

// =================== KEYBOARD SHORTCUTS ===================
document.addEventListener('keydown', function(e) {
    // ESC to close modals
    if (e.key === 'Escape') {
        document.querySelectorAll('.modal').forEach(modal => {
            if (modal.style.display === 'block') {
                hideModal(modal.id);
            }
        });
    }
    
    // Ctrl+N for new items
    if (e.ctrlKey && e.key === 'n') {
        e.preventDefault();
        const activeSection = document.querySelector('.content-section.active');
        if (activeSection.id === 'obras-section') {
            showModal('obra-modal');
        } else if (activeSection.id === 'responsaveis-section') {
            showModal('responsavel-modal');
        } else if (activeSection.id === 'relatorios-mensais-section') {
            showModal('relatorio-mensal-modal');
        }
    }
});
