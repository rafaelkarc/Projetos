// Variável global para armazenar a tabela atual
let currentTable = null;

// Carregar estatísticas ao iniciar
$(document).ready(function() {
    loadStats();
});

// Função para carregar estatísticas
function loadStats() {
    $.ajax({
        url: '/database/stats',
        method: 'GET',
        success: function(response) {
            if (response.success) {
                $('#stat-calculos-vna').text(response.stats.calculos_vna);
                $('#stat-pu-par').text(response.stats.pu_par);
                $('#stat-pu-operacao').text(response.stats.pu_operacao);
                $('#stat-ativos').text(response.stats.ativos);
                $('#stat-filtros').text(response.stats.filtros_estatisticos);
            }
        },
        error: function(xhr) {
            console.error('Erro ao carregar estatísticas:', xhr);
        }
    });
}

// Função para mostrar tabela específica
function showTable(tableName) {
    currentTable = tableName;
    
    // Remover classe active de todos os cards
    $('.stats-card').removeClass('active');
    
    // Adicionar classe active ao card clicado
    event.currentTarget.classList.add('active');
    
    // Mostrar container da tabela
    $('#tableContainer').show();
    
    // Atualizar título
    const titles = {
        'calculos_vna': 'Cálculos VNA',
        'pu_par': 'Cálculos PU PAR',
        'pu_operacao': 'Cálculos PU Operação',
        'ativos': 'Ativos Cadastrados',
        'filtros': 'Filtros Estatísticos',
        'logs': 'Logs do Sistema'
    };
    $('#tableTitle').text(titles[tableName] || 'Dados');
    
    // Carregar dados
    loadTableData(tableName);
}

// Função para carregar dados da tabela
function loadTableData(tableName) {
    $('#tableContent').html(`
        <div class="loading">
            <i class="fas fa-spinner fa-spin fa-3x"></i>
            <p>Carregando dados...</p>
        </div>
    `);
    
    $.ajax({
        url: `/database/${tableName}`,
        method: 'GET',
        success: function(response) {
            if (response.success) {
                renderTable(tableName, response.data);
            } else {
                $('#tableContent').html(`
                    <div class="no-data">
                        <i class="fas fa-exclamation-triangle fa-3x"></i>
                        <p>Erro ao carregar dados: ${response.error}</p>
                    </div>
                `);
            }
        },
        error: function(xhr) {
            $('#tableContent').html(`
                <div class="no-data">
                    <i class="fas fa-exclamation-triangle fa-3x"></i>
                    <p>Erro ao carregar dados</p>
                </div>
            `);
        }
    });
}

// Função para renderizar tabela
function renderTable(tableName, data) {
    if (!data || data.length === 0) {
        $('#tableContent').html(`
            <div class="no-data">
                <i class="fas fa-inbox fa-3x"></i>
                <p>Nenhum registro encontrado</p>
            </div>
        `);
        return;
    }
    
    let html = '<div class="table-responsive"><table class="table table-striped table-hover">';
    
    // Cabeçalho da tabela baseado no tipo
    if (tableName === 'calculos_vna') {
        html += `
            <thead>
                <tr>
                    <th>ID</th>
                    <th>VNE</th>
                    <th>IPCA Emissão</th>
                    <th>IPCA Atual</th>
                    <th>VNA Calculado</th>
                    <th>Fator Correção</th>
                    <th>Data Cálculo</th>
                    <th>Status</th>
                    <th>Ações</th>
                </tr>
            </thead>
            <tbody>
        `;
        
        data.forEach(item => {
            html += `
                <tr>
                    <td>${item.id}</td>
                    <td>${formatNumber(item.vne)}</td>
                    <td>${formatNumber(item.ipca_emissao)}</td>
                    <td>${formatNumber(item.ipca_atual)}</td>
                    <td>${formatNumber(item.vna_calculado)}</td>
                    <td>${formatNumber(item.fator_correcao)}</td>
                    <td>${formatDate(item.data_calculo)}</td>
                    <td><span class="status-badge status-${item.status.toLowerCase()}">${item.status}</span></td>
                    <td>
                        <button class="btn-action btn-delete" onclick="deleteRecord('calculos_vna', ${item.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                </tr>
            `;
        });
        
    } else if (tableName === 'pu_par') {
        html += `
            <thead>
                <tr>
                    <th>ID</th>
                    <th>VNA</th>
                    <th>Taxa Juros (%)</th>
                    <th>Dias Úteis</th>
                    <th>Base Cálculo</th>
                    <th>PU PAR</th>
                    <th>Data Cálculo</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
        `;
        
        data.forEach(item => {
            html += `
                <tr>
                    <td>${item.id}</td>
                    <td>${formatNumber(item.vna)}</td>
                    <td>${formatNumber(item.taxa_juros)}</td>
                    <td>${item.dias_uteis}</td>
                    <td>${item.base_calculo}</td>
                    <td>${formatNumber(item.pu_par)}</td>
                    <td>${formatDate(item.data_calculo)}</td>
                    <td><span class="status-badge status-${item.status.toLowerCase()}">${item.status}</span></td>
                </tr>
            `;
        });
        
    } else if (tableName === 'pu_operacao') {
        html += `
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Código IF</th>
                    <th>Nome Ativo</th>
                    <th>Taxa Mercado (%)</th>
                    <th>Base Cálculo</th>
                    <th>PU Operação</th>
                    <th>Indexador</th>
                    <th>Data Cálculo</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
        `;
        
        data.forEach(item => {
            html += `
                <tr>
                    <td>${item.id}</td>
                    <td>${item.codigo_if || '-'}</td>
                    <td>${item.nome_ativo || '-'}</td>
                    <td>${formatNumber(item.taxa_mercado)}</td>
                    <td>${item.base_calculo}</td>
                    <td>${formatNumber(item.pu_operacao)}</td>
                    <td>${item.indexador || '-'}</td>
                    <td>${formatDate(item.data_calculo)}</td>
                    <td><span class="status-badge status-${item.status.toLowerCase()}">${item.status}</span></td>
                </tr>
            `;
        });
        
    } else if (tableName === 'ativos') {
        html += `
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Status</th>
                    <th>Código IF</th>
                    <th>Nome</th>
                    <th>Emissor</th>
                    <th>PU Emissão</th>
                    <th>Taxa (%)</th>
                    <th>Indexador</th>
                    <th>Cadastrado em</th>
                    <th>Ações</th>
                </tr>
            </thead>
            <tbody>
        `;
        
        data.forEach(item => {
            html += `
                <tr>
                    <td>${item.id}</td>
                    <td><span class="status-badge status-${item.status.toLowerCase()}">${item.status}</span></td>
                    <td>${item.codigo_if}</td>
                    <td>${item.nome}</td>
                    <td>${item.emissor}</td>
                    <td>${item.pu_emissao ? formatNumber(item.pu_emissao) : '-'}</td>
                    <td>${item.taxa ? formatNumber(item.taxa) + '%' : '-'}</td>
                    <td>${item.indexador || '-'}</td>
                    <td>${formatDate(item.data_cadastro)}</td>
                    <td>
                        <button class="btn-action btn-edit" onclick="editAtivo(${item.id})">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn-action btn-delete" onclick="deleteRecord('ativos', ${item.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                </tr>
            `;
        });
        
    } else if (tableName === 'logs') {
        html += `
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Tipo Operação</th>
                    <th>Tabela</th>
                    <th>Registro ID</th>
                    <th>Detalhes</th>
                    <th>Data</th>
                </tr>
            </thead>
            <tbody>
        `;
        
        data.forEach(item => {
            html += `
                <tr>
                    <td>${item.id}</td>
                    <td>${item.tipo_operacao}</td>
                    <td>${item.tabela}</td>
                    <td>${item.registro_id || '-'}</td>
                    <td>${item.detalhes || '-'}</td>
                    <td>${formatDate(item.data_log)}</td>
                </tr>
            `;
        });
    }
    
    html += '</tbody></table></div>';
    $('#tableContent').html(html);
}

// Função para atualizar tabela atual
function refreshCurrentTable() {
    if (currentTable) {
        loadTableData(currentTable);
        loadStats();
    }
}

// Função para deletar registro
function deleteRecord(tableName, id) {
    if (!confirm('Tem certeza que deseja deletar este registro?')) {
        return;
    }
    
    $.ajax({
        url: `/database/${tableName}/${id}`,
        method: 'DELETE',
        success: function(response) {
            if (response.success) {
                alert('Registro deletado com sucesso!');
                refreshCurrentTable();
            } else {
                alert('Erro ao deletar registro: ' + response.error);
            }
        },
        error: function(xhr) {
            alert('Erro ao deletar registro');
        }
    });
}

// Função para editar ativo
function editAtivo(id) {
    // Buscar dados do ativo
    $.ajax({
        url: `/database/ativos`,
        method: 'GET',
        success: function(response) {
            if (response.success) {
                const ativo = response.data.find(a => a.id === id);
                if (ativo) {
                    $('#edit-id').val(ativo.id);
                    $('#edit-codigo-if').val(ativo.codigo_if);
                    $('#edit-nome').val(ativo.nome);
                    $('#edit-emissor').val(ativo.emissor);
                    $('#edit-pu-emissao').val(ativo.pu_emissao || '');
                    $('#edit-taxa').val(ativo.taxa || '');
                    $('#edit-indexador').val(ativo.indexador || '');
                    $('#editModal').show();
                }
            }
        }
    });
}

// Função para fechar modal
function closeModal() {
    $('#editModal').hide();
}

// Submissão do formulário de edição
$('#editForm').on('submit', function(e) {
    e.preventDefault();
    
    const id = $('#edit-id').val();
    const dados = {
        codigo_if: $('#edit-codigo-if').val(),
        nome: $('#edit-nome').val(),
        emissor: $('#edit-emissor').val(),
        pu_emissao: $('#edit-pu-emissao').val() || null,
        taxa: $('#edit-taxa').val() || null,
        indexador: $('#edit-indexador').val() || null
    };
    
    $.ajax({
        url: `/database/ativos/${id}`,
        method: 'PUT',
        contentType: 'application/json',
        data: JSON.stringify(dados),
        success: function(response) {
            if (response.success) {
                alert('Ativo atualizado com sucesso!');
                closeModal();
                refreshCurrentTable();
            } else {
                alert('Erro ao atualizar ativo: ' + response.error);
            }
        },
        error: function(xhr) {
            alert('Erro ao atualizar ativo');
        }
    });
});

// Fechar modal ao clicar fora
$(window).on('click', function(e) {
    if (e.target.id === 'editModal') {
        closeModal();
    }
});

// Funções auxiliares de formatação
function formatNumber(value) {
    if (value === null || value === undefined) return '-';
    return parseFloat(value).toLocaleString('pt-BR', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 8
    });
}

function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleString('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}




// ========================================
// SIMULADOR DE INVESTIMENTO
// ========================================

// Variável global para o gráfico
let chartSimulacao = null;

// Toggle do simulador
function toggleSimulator() {
  const content = document.getElementById('simulatorContent');
  const btn = document.querySelector('.btn-toggle-simulator');
  
  if (content.style.display === 'none') {
    content.style.display = 'block';
    btn.querySelector('i').classList.remove('fa-chevron-right');
    btn.querySelector('i').classList.add('fa-chevron-down');
  } else {
    content.style.display = 'none';
    btn.querySelector('i').classList.remove('fa-chevron-down');
    btn.querySelector('i').classList.add('fa-chevron-right');
  }
}

// Carregar ativos no select do simulador
function carregarAtivosSimulador() {
  fetch('/database/ativos')
    .then(response => response.json())
    .then(data => {
      const select = document.getElementById('simAtivo');
      select.innerHTML = '<option value="">Selecione um ativo...</option>';
      
      if (data.success && data.ativos.length > 0) {
        data.ativos.forEach(ativo => {
          const option = document.createElement('option');
          option.value = JSON.stringify({
            id: ativo.id,
            nome: ativo.nome,
            taxa: ativo.taxa,
            indexador: ativo.indexador
          });
          option.textContent = `${ativo.codigo_if} - ${ativo.nome}`;
          select.appendChild(option);
        });
      }
    })
    .catch(error => {
      console.error('Erro ao carregar ativos:', error);
    });
}

// Carregar dados do ativo selecionado
function carregarDadosAtivo() {
  const select = document.getElementById('simAtivo');
  if (!select.value) return;
  
  const ativo = JSON.parse(select.value);
  document.getElementById('simTaxa').value = ativo.taxa || '';
  document.getElementById('simIndexador').value = ativo.indexador || 'IPCA';
}

// Mostrar/ocultar campo de taxa personalizada
document.getElementById('simCenario')?.addEventListener('change', function() {
  const customGroup = document.getElementById('customIndexGroup');
  if (this.value === 'custom') {
    customGroup.style.display = 'block';
  } else {
    customGroup.style.display = 'none';
  }
});

// Simular investimento
function simularInvestimento() {
  // Obter valores
  const valor = parseFloat(document.getElementById('simValor').value);
  const taxa = parseFloat(document.getElementById('simTaxa').value);
  const prazo = parseInt(document.getElementById('simPrazo').value);
  const indexador = document.getElementById('simIndexador').value;
  const cenario = document.getElementById('simCenario').value;
  
  // Validar campos
  if (!valor || valor <= 0) {
    alert('Por favor, informe o valor do investimento.');
    return;
  }
  
  if (!taxa || taxa < 0) {
    alert('Por favor, informe a taxa de juros.');
    return;
  }
  
  if (!prazo || prazo <= 0) {
    alert('Por favor, informe o prazo em meses.');
    return;
  }
  
  // Obter taxa do indexador
  let taxaIndexador = 0;
  if (indexador !== 'PRE') {
    if (cenario === 'custom') {
      taxaIndexador = parseFloat(document.getElementById('simCustomIndex').value) || 0;
    } else {
      const cenarios = {
        'otimista': 3.0,
        'moderado': 4.5,
        'pessimista': 6.0
      };
      taxaIndexador = cenarios[cenario] || 4.5;
    }
  }
  
  // Calcular rendimento
  const taxaTotal = indexador === 'PRE' ? taxa : taxa + taxaIndexador;
  const taxaMensal = taxaTotal / 100 / 12;
  const valorFinal = valor * Math.pow(1 + taxaMensal, prazo);
  const rendimento = valorFinal - valor;
  const rentabilidade = (rendimento / valor) * 100;
  
  // Calcular composição (aproximada)
  const taxaJurosMensal = taxa / 100 / 12;
  const taxaIndexMensal = taxaIndexador / 100 / 12;
  
  const valorComJuros = valor * Math.pow(1 + taxaJurosMensal, prazo);
  const juros = valorComJuros - valor;
  const correcao = rendimento - juros;
  
  // Exibir resultados
  document.getElementById('resValorInicial').textContent = formatarMoeda(valor);
  document.getElementById('resPrazo').textContent = `${prazo} meses (${(prazo/12).toFixed(1)} anos)`;
  document.getElementById('resTaxaTotal').textContent = `${taxaTotal.toFixed(2)}% a.a.`;
  document.getElementById('resValorFinal').textContent = formatarMoeda(valorFinal);
  document.getElementById('resRendimento').textContent = formatarMoeda(rendimento);
  document.getElementById('resRentabilidade').textContent = `${rentabilidade.toFixed(2)}%`;
  document.getElementById('resJuros').textContent = formatarMoeda(juros);
  document.getElementById('resCorrecao').textContent = formatarMoeda(correcao);
  
  // Mostrar resultado
  document.getElementById('resultadoPlaceholder').style.display = 'none';
  document.getElementById('resultadoSimulacao').style.display = 'block';
  
  // Gerar gráfico
  gerarGraficoSimulacao(valor, taxaMensal, prazo);
}

// Gerar gráfico de evolução
function gerarGraficoSimulacao(valorInicial, taxaMensal, prazo) {
  const ctx = document.getElementById('chartSimulacao');
  if (!ctx) return;
  
  // Destruir gráfico anterior
  if (chartSimulacao) {
    chartSimulacao.destroy();
  }
  
  // Gerar dados
  const labels = [];
  const valores = [];
  
  for (let mes = 0; mes <= prazo; mes++) {
    labels.push(`Mês ${mes}`);
    const valor = valorInicial * Math.pow(1 + taxaMensal, mes);
    valores.push(valor.toFixed(2));
  }
  
  // Criar gráfico
  chartSimulacao = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: 'Evolução do Investimento',
        data: valores,
        borderColor: '#667eea',
        backgroundColor: 'rgba(102, 126, 234, 0.1)',
        borderWidth: 2,
        fill: true,
        tension: 0.4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: true,
          position: 'top'
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              return 'R$ ' + parseFloat(context.parsed.y).toLocaleString('pt-BR', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
              });
            }
          }
        }
      },
      scales: {
        y: {
          beginAtZero: false,
          ticks: {
            callback: function(value) {
              return 'R$ ' + value.toLocaleString('pt-BR');
            }
          }
        }
      }
    }
  });
}

// Limpar simulador
function limparSimulador() {
  document.getElementById('simValor').value = '';
  document.getElementById('simAtivo').value = '';
  document.getElementById('simTaxa').value = '';
  document.getElementById('simIndexador').value = 'IPCA';
  document.getElementById('simPrazo').value = '';
  document.getElementById('simCenario').value = 'moderado';
  document.getElementById('customIndexGroup').style.display = 'none';
  
  document.getElementById('resultadoPlaceholder').style.display = 'block';
  document.getElementById('resultadoSimulacao').style.display = 'none';
  
  if (chartSimulacao) {
    chartSimulacao.destroy();
    chartSimulacao = null;
  }
}

// Função auxiliar para formatar moeda
function formatarMoeda(valor) {
  return 'R$ ' + valor.toLocaleString('pt-BR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });
}

// Carregar ativos ao abrir a página
$(document).ready(function() {
  carregarAtivosSimulador();
});

