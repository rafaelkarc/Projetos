$(document).ready(function () {
  // Inicialização
  inicializarCalculadora();

  // Event listeners para os formulários
  $("#vnaForm").on("submit", calcularVNA);
  $("#puParForm").on("submit", calcularPuPar);
  $("#puOperacaoForm").on("submit", calcularPuOperacao);
  $("#filtrosForm").on("submit", aplicarFiltros);

  // Event listeners para o identificador de ativos
  $("#lerCelulaForm").on("submit", lerCelula);
  $("#buscarAtivoForm").on("submit", buscarAtivo);
  $("#listarAbasForm").on("submit", listarAbas);
  $("#lerColunaForm").on("submit", lerColuna);

  // NOVA FUNCIONALIDADE: Event listener para busca automática por código IF
  $("#codigoIF").on("blur", function () {
    const codigoIF = $(this).val().trim();
    if (codigoIF) {
      buscarDadosAtivo(codigoIF);
    }
  });

  // Definir data atual como padrão
  const hoje = new Date().toISOString().split("T")[0];
  $("#dataCalculo").val(hoje);
});

// Variável global para controlar fluxos
let contadorFluxos = 1;

function inicializarCalculadora() {
  console.log("Calculadora PU/IPCA inicializada");

  // Verificar status da planilha
  verificarStatusPlanilha();
}

function verificarStatusPlanilha() {
  $.ajax({
    url: "/status_planilha",
    method: "GET",
    success: function (response) {
      if (response.success) {
        console.log("Status da planilha:", response.status);
      }
    },
    error: function (xhr, status, error) {
      console.error("Erro ao verificar status da planilha:", error);
    },
  });
}

// Função para calcular VNA
function calcularVNA(e) {
  e.preventDefault();

  mostrarLoading();
  esconderResultados();

  const formData = {
    vne: parseFloat($("#vne").val()),
    ipca_emissao: parseFloat($("#ipcaEmissao").val()),
    ipca_atual: parseFloat($("#ipcaAtual").val()),
  };

  // Validação básica
  if (!validarDadosVNA(formData)) {
    esconderLoading();
    return;
  }

  $.ajax({
    url: "/calcular_vna",
    method: "POST",
    contentType: "application/json",
    data: JSON.stringify(formData),
    success: function (response) {
      esconderLoading();

      if (response.success) {
        $("#resultado-vna").text("VNA: " + response.vna_calculado.toFixed(2));
        $("#resultado-fator").text(
          "Fator de Correção: " + response.fator_correcao.toFixed(6),
        );
        $("#resultado-ipca").text(
          "Indexador (IPCA atual IBGE): " + response.ipca_atual,
        );

        mostrarStatus(
          "success",
          "VNA calculado com sucesso!",
          response.salvamento_sucesso,
        );
      } else {
        mostrarStatus("error", "Erro ao calcular VNA: " + response.error);
      }
    },
    error: function (xhr, status, error) {
      esconderLoading();
      mostrarStatus("error", "Erro na comunicação com o servidor: " + error);
    },
  });
}

// Função para calcular PU PAR
function calcularPuPar(e) {
  e.preventDefault();

  mostrarLoading();
  esconderResultados();

  const formData = {
    vna: parseFloat($("#vnaParInput").val()),
    taxa_juros: parseFloat($("#taxaJuros").val()),
    dias_uteis: parseInt($("#diasUteis").val()),
    base_calculo: parseInt($("#baseCalculo").val()),
  };

  // Validação básica
  if (!validarDadosPuPar(formData)) {
    esconderLoading();
    return;
  }

  $.ajax({
    url: "/calcular_pu_par",
    method: "POST",
    contentType: "application/json",
    data: JSON.stringify(formData),
    success: function (response) {
      esconderLoading();

      if (response.success) {
        exibirResultadosPuPar(response);
        mostrarStatus(
          "success",
          "PU PAR calculado com sucesso!",
          response.salvamento_sucesso,
        );
      } else {
        mostrarStatus("error", "Erro ao calcular PU PAR: " + response.error);
      }
    },
    error: function (xhr, status, error) {
      esconderLoading();
      mostrarStatus("error", "Erro na comunicação com o servidor: " + error);
    },
  });
}

// FUNÇÃO MODIFICADA: calcularPuOperacao com integração ao buscar ativo
function calcularPuOperacao(e) {
  e.preventDefault();

  mostrarLoading();
  esconderResultados();

  const fluxos = coletarFluxos();
  const codigoIF = $("#codigoIF").val().trim(); // NOVA FUNCIONALIDADE

  const formData = {
    taxa_mercado: parseFloat($("#taxaMercado").val()),
    base_calculo: parseInt($("#baseCalculoOperacao").val()),
    fluxos: fluxos,
    codigo_if: codigoIF, // NOVA FUNCIONALIDADE: Enviar código IF
  };

  // Validação básica (mais flexível se código IF foi fornecido)
  if (!validarDadosPuOperacao(formData, !!codigoIF)) {
    esconderLoading();
    return;
  }

  $.ajax({
    url: "/calcular_pu_operacao",
    method: "POST",
    contentType: "application/json",
    data: JSON.stringify(formData),
    success: function (response) {
      esconderLoading();

      if (response.success) {
        exibirResultadosPuOperacao(response);
        mostrarStatus(
          "success",
          "PU Operação calculado com sucesso!",
          response.salvamento_sucesso,
        );
      } else {
        mostrarStatus(
          "error",
          "Erro ao calcular PU Operação: " + response.error,
        );
      }
    },
    error: function (xhr, status, error) {
      esconderLoading();
      mostrarStatus("error", "Erro na comunicação com o servidor: " + error);
    },
  });
}

// Função para aplicar filtros estatísticos
function aplicarFiltros(e) {
  e.preventDefault();

  mostrarLoading();
  esconderResultados();

  const formData = {
    taxas: $("#taxasInput").val(),
  };

  // Validação básica
  if (!validarDadosFiltros(formData)) {
    esconderLoading();
    return;
  }

  $.ajax({
    url: "/aplicar_filtros",
    method: "POST",
    contentType: "application/json",
    data: JSON.stringify(formData),
    success: function (response) {
      esconderLoading();

      if (response.success) {
        exibirResultadosFiltros(response);
        mostrarStatus(
          "success",
          "Filtros aplicados com sucesso!",
          response.salvamento_sucesso,
        );
      } else {
        mostrarStatus("error", "Erro ao aplicar filtros: " + response.error);
      }
    },
    error: function (xhr, status, error) {
      esconderLoading();
      mostrarStatus("error", "Erro na comunicação com o servidor: " + error);
    },
  });
}

// NOVA FUNCIONALIDADE: Buscar dados do ativo automaticamente
function buscarDadosAtivo(codigoIF) {
  // Mostrar indicador de busca
  $("#indicadorBusca").show();
  $("#dadosAtivo").hide();

  $.ajax({
    url: "/buscar_ativo",
    method: "POST",
    contentType: "application/json",
    data: JSON.stringify({ search_value: codigoIF }),
    success: function (response) {
      $("#indicadorBusca").hide();

      if (response.success && response.matches && response.matches.length > 0) {
        const ativo = response.matches[0].valores;

        // Extrair dados do ativo
        const nomeAtivo = ativo[0] || "N/A";
        const puEmissao = ativo[20] || "N/A";
        const taxaAtivo = ativo[31] || "N/A";
        const indexador = ativo[29] || "N/A";

        // Exibir dados do ativo
        $("#nomeAtivo").text(nomeAtivo);
        $("#puEmissao").text(
          typeof puEmissao === "number"
            ? puEmissao.toLocaleString("pt-BR", { minimumFractionDigits: 2 })
            : puEmissao,
        );
        $("#taxaAtivo").text(
          typeof taxaAtivo === "number"
            ? (taxaAtivo * 100).toFixed(2) + "%"
            : taxaAtivo,
        );
        $("#indexadorAtivo").text(indexador);

        // Preencher automaticamente a taxa de mercado se não estiver preenchida
        if (!$("#taxaMercado").val() && typeof taxaAtivo === "number") {
          $("#taxaMercado").val(taxaAtivo * 100); // Converter para percentual
        }

        // Criar fluxo padrão se não existir
        if (
          $(".fluxo-item").length === 1 &&
          !$("#fluxoDias1").val() &&
          !$("#fluxoValor1").val()
        ) {
          $("#fluxoDias1").val(252);
          if (typeof puEmissao === "number") {
            $("#fluxoValor1").val(puEmissao);
          }
        }

        $("#dadosAtivo").show();
      } else {
        mostrarStatus(
          "warning",
          "Ativo não encontrado com o código IF: " + codigoIF,
        );
      }
    },
    error: function (xhr, status, error) {
      $("#indicadorBusca").hide();
      mostrarStatus("error", "Erro ao buscar ativo: " + error);
    },
  });
}

// Funções do Identificador de Ativos (mantidas exatamente como no original)
function lerCelula(e) {
  e.preventDefault();

  mostrarLoading();

  const formData = {
    file_path: $("#filePath").val(),
    sheet_name: $("#sheetName").val(),
    cell_address: $("#cellAddress").val(),
  };

  $.ajax({
    url: "/ler_celula",
    method: "POST",
    contentType: "application/json",
    data: JSON.stringify(formData),
    success: function (response) {
      esconderLoading();

      if (response.success) {
        $("#valorCelula").text(response.value || "Vazio");
        $("#tipoCelula").text(response.value_type || "N/A");
        $("#timestampCelula").text(response.timestamp || "N/A");
        $("#resultadoLerCelula").show();
        mostrarStatus("success", "Célula lida com sucesso!");
      } else {
        mostrarStatus("error", "Erro ao ler célula: " + response.error);
      }
    },
    error: function (xhr, status, error) {
      esconderLoading();
      mostrarStatus("error", "Erro na comunicação com o servidor: " + error);
    },
  });
}

function buscarAtivo(e) {
  e.preventDefault();

  mostrarLoading();

  const formData = {
    search_value: $("#searchValue").val(),
  };

  $.ajax({
    url: "/buscar_ativo",
    method: "POST",
    contentType: "application/json",
    data: JSON.stringify(formData),
    success: function (response) {
      esconderLoading();

      if (response.success) {
        let conteudo =
          '<div class="alert alert-success">Busca realizada com sucesso!</div>';

        if (response.matches && response.matches.length > 0) {
          conteudo += "<h6>Resultados encontrados:</h6>";
          response.matches.forEach((match, index) => {
            conteudo += `
                            <div class="card mb-2">
                                <div class="card-body">
                                    <h6 class="card-title">Resultado ${
                                      index + 1
                                    }</h6>
                                    <p><strong>Linha:</strong> ${
                                      match.linha
                                    }</p>
                                    <p><strong>Coluna:</strong> ${
                                      match.coluna
                                    }</p>
                                    <p><strong>Descrição da Coluna:</strong> ${
                                      match.descricao_coluna
                                    }</p>
                                    <p><strong>Dados da Linha:</strong></p>
                                    <div class="table-responsive">
                                        <table class="table table-sm table-bordered">
                                            <tbody>
                                                <tr>
                                                    ${match.valores
                                                      .slice(0, 10)
                                                      .map(
                                                        (valor, i) =>
                                                          `<td><small><strong>Col ${
                                                            i + 1
                                                          }:</strong><br>${
                                                            valor || "N/A"
                                                          }</small></td>`,
                                                      )
                                                      .join("")}
                                                </tr>
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            </div>
                        `;
          });
        } else {
          conteudo +=
            '<div class="alert alert-warning">Nenhum resultado encontrado.</div>';
        }

        $("#conteudoBuscarAtivo").html(conteudo);
        $("#resultadoBuscarAtivo").show();
        mostrarStatus("success", "Busca realizada com sucesso!");
      } else {
        mostrarStatus("error", "Erro ao buscar ativo: " + response.error);
      }
    },
    error: function (xhr, status, error) {
      esconderLoading();
      mostrarStatus("error", "Erro na comunicação com o servidor: " + error);
    },
  });
}

function listarAbas(e) {
  e.preventDefault();

  mostrarLoading();

  const formData = {
    file_path: $("#filePathAbas").val(),
  };

  $.ajax({
    url: "/listar_abas",
    method: "POST",
    contentType: "application/json",
    data: JSON.stringify(formData),
    success: function (response) {
      esconderLoading();

      if (response.success) {
        let conteudo =
          '<div class="alert alert-success">Abas listadas com sucesso!</div>';

        if (response.sheets && response.sheets.length > 0) {
          conteudo += '<ul class="list-group">';
          response.sheets.forEach((sheet, index) => {
            conteudo += `<li class="list-group-item">${
              index + 1
            }. ${sheet}</li>`;
          });
          conteudo += "</ul>";
        } else {
          conteudo +=
            '<div class="alert alert-warning">Nenhuma aba encontrada.</div>';
        }

        $("#conteudoListarAbas").html(conteudo);
        $("#resultadoListarAbas").show();
        mostrarStatus("success", "Abas listadas com sucesso!");
      } else {
        mostrarStatus("error", "Erro ao listar abas: " + response.error);
      }
    },
    error: function (xhr, status, error) {
      esconderLoading();
      mostrarStatus("error", "Erro na comunicação com o servidor: " + error);
    },
  });
}

function lerColuna(e) {
  e.preventDefault();

  mostrarLoading();

  const formData = {
    file_path: $("#filePathColuna").val(),
    sheet_name: $("#sheetNameColuna").val(),
    column: $("#columnLetter").val(),
    start_row: parseInt($("#startRow").val()) || 1,
    end_row: parseInt($("#endRow").val()) || null,
  };

  $.ajax({
    url: "/ler_coluna",
    method: "POST",
    contentType: "application/json",
    data: JSON.stringify(formData),
    success: function (response) {
      esconderLoading();

      if (response.success) {
        let conteudo =
          '<div class="alert alert-success">Coluna lida com sucesso!</div>';

        if (response.values && response.values.length > 0) {
          conteudo +=
            '<div class="table-responsive"><table class="table table-sm table-striped">';
          conteudo +=
            "<thead><tr><th>Linha</th><th>Valor</th></tr></thead><tbody>";
          response.values.forEach((valor, index) => {
            const linha = (formData.start_row || 1) + index;
            conteudo += `<tr><td>${linha}</td><td>${
              valor || "Vazio"
            }</td></tr>`;
          });
          conteudo += "</tbody></table></div>";
        } else {
          conteudo +=
            '<div class="alert alert-warning">Nenhum valor encontrado na coluna.</div>';
        }

        $("#conteudoLerColuna").html(conteudo);
        $("#resultadoLerColuna").show();
        mostrarStatus("success", "Coluna lida com sucesso!");
      } else {
        mostrarStatus("error", "Erro ao ler coluna: " + response.error);
      }
    },
    error: function (xhr, status, error) {
      esconderLoading();
      mostrarStatus("error", "Erro na comunicação com o servidor: " + error);
    },
  });
}

function coletarFluxos() {
  const fluxos = [];

  $(".fluxo-item").each(function () {
    const data = $(this).find(".fluxo-data").val();
    const diasUteis = parseInt($(this).find(".fluxo-dias").val()) || 0;
    const valor = parseFloat($(this).find(".fluxo-valor").val()) || 0;

    if (diasUteis >= 0 && valor > 0) {
      fluxos.push({
        data: data,
        dias_uteis: diasUteis,
        valor: valor,
      });
    }
  });

  return fluxos;
}

// Funções utilitárias
function mostrarLoading() {
  $("#loadingSpinner").show();
}

function esconderLoading() {
  $("#loadingSpinner").hide();
}

function esconderResultados() {
  $(
    "#vnaResultados, #puParResultados, #puOperacaoResultados, #filtrosResultados",
  ).hide();
  $(
    "#resultadoLerCelula, #resultadoBuscarAtivo, #resultadoListarAbas, #resultadoLerColuna",
  ).hide();
}

function mostrarStatus(tipo, mensagem, salvamentoSucesso = null) {
  let classe = "alert-info";
  let icone = "fas fa-info-circle";

  switch (tipo) {
    case "success":
      classe = "alert-success";
      icone = "fas fa-check-circle";
      break;
    case "error":
      classe = "alert-danger";
      icone = "fas fa-exclamation-circle";
      break;
    case "warning":
      classe = "alert-warning";
      icone = "fas fa-exclamation-triangle";
      break;
  }

  let conteudo = `<i class="${icone}"></i> ${mensagem}`;

  if (salvamentoSucesso !== null) {
    if (salvamentoSucesso) {
      conteudo +=
        ' <span class="badge badge-success ml-2">Salvo na planilha</span>';
    } else {
      conteudo +=
        ' <span class="badge badge-warning ml-2">Não salvo na planilha</span>';
    }
  }

  $("#statusContent").html(conteudo);
  $("#statusGlobal")
    .removeClass("alert-info alert-success alert-danger alert-warning")
    .addClass(classe)
    .show();

  // Auto-hide após 5 segundos
  setTimeout(() => {
    $("#statusGlobal").fadeOut();
  }, 5000);
}

// Funções de validação
function validarDadosVNA(dados) {
  if (!dados.vne || dados.vne <= 0) {
    mostrarStatus("error", "VNE deve ser maior que zero");
    return false;
  }
  if (!dados.ipca_emissao || dados.ipca_emissao <= 0) {
    mostrarStatus("error", "IPCA de emissão deve ser maior que zero");
    return false;
  }
  if (!dados.ipca_atual || dados.ipca_atual <= 0) {
    mostrarStatus("error", "IPCA atual deve ser maior que zero");
    return false;
  }
  return true;
}

function validarDadosPuPar(dados) {
  if (!dados.vna || dados.vna <= 0) {
    mostrarStatus("error", "VNA deve ser maior que zero");
    return false;
  }
  if (dados.taxa_juros < 0) {
    mostrarStatus("error", "Taxa de juros deve ser maior ou igual a zero");
    return false;
  }
  if (dados.dias_uteis < 0) {
    mostrarStatus("error", "Dias úteis deve ser maior ou igual a zero");
    return false;
  }
  return true;
}

// FUNÇÃO MODIFICADA: Validação mais flexível para PU Operação quando código IF é fornecido
function validarDadosPuOperacao(dados, temCodigoIF = false) {
  // Se tem código IF, a validação é mais flexível
  if (temCodigoIF) {
    // Taxa pode ser preenchida automaticamente
    if (!dados.taxa_mercado && dados.taxa_mercado !== 0) {
      mostrarStatus("warning", "Taxa de mercado será obtida do ativo...");
    }
    // Fluxos podem ser criados automaticamente
    if (!dados.fluxos || dados.fluxos.length === 0) {
      mostrarStatus(
        "info",
        "Fluxos serão criados automaticamente baseados no ativo...",
      );
    }
    return true;
  }

  // Validação original para modo manual
  if (!dados.taxa_mercado && dados.taxa_mercado !== 0) {
    mostrarStatus("error", "Taxa de mercado é obrigatória");
    return false;
  }
  if (dados.taxa_mercado < 0) {
    mostrarStatus("error", "Taxa de mercado deve ser maior ou igual a zero");
    return false;
  }
  if (!dados.fluxos || dados.fluxos.length === 0) {
    mostrarStatus(
      "error",
      "Pelo menos um fluxo de pagamento deve ser fornecido",
    );
    return false;
  }
  return true;
}

function validarDadosFiltros(dados) {
  if (!dados.taxas || dados.taxas.trim() === "") {
    mostrarStatus("error", "Lista de taxas é obrigatória");
    return false;
  }
  return true;
}

// Funções de exibição de resultados
function exibirResultadosVNA(response) {
  $("#vnaCalculado").text(
    response.vna_calculado.toLocaleString("pt-BR", {
      minimumFractionDigits: 8,
    }),
  );
  $("#fatorCorrecao").text(
    response.fator_correcao.toLocaleString("pt-BR", {
      minimumFractionDigits: 8,
    }),
  );
  $("#dataCalculoResult").text(response.data_calculo);
  $("#vnaResultados").show();
}

function exibirResultadosPuPar(response) {
  $("#puParCalculado").text(
    response.pu_par.toLocaleString("pt-BR", { minimumFractionDigits: 8 }),
  );
  $("#dataCalculoPuPar").text(response.data_calculo);
  $("#puParResultados").show();
}

// FUNÇÃO MODIFICADA: Exibir resultados PU Operação com informações do ativo
function exibirResultadosPuOperacao(response) {
  $("#puOperacaoCalculado").text(
    response.pu_operacao.toLocaleString("pt-BR", { minimumFractionDigits: 8 }),
  );
  $("#dataCalculoPuOperacao").text(response.data_calculo);

  // NOVA FUNCIONALIDADE: Exibir informações do ativo se disponível
  if (response.info_ativo) {
    const ativo = response.info_ativo;
    $("#nomeAtivoResultado").text(ativo.nome || "N/A");
    $("#codigoIFResultado").text(ativo.codigo_if || "N/A");
    $("#puEmissaoResultado").text(
      ativo.pu_emissao
        ? ativo.pu_emissao.toLocaleString("pt-BR", { minimumFractionDigits: 2 })
        : "N/A",
    );
    $("#taxaAtivoResultado").text(
      ativo.taxa ? (ativo.taxa * 100).toFixed(2) + "%" : "N/A",
    );
    $("#indexadorAtivoResultado").text(ativo.indexador || "N/A");
    $("#infoAtivoResultado").show();
  } else {
    $("#infoAtivoResultado").hide();
  }

  $("#puOperacaoResultados").show();
}

function exibirResultadosFiltros(response) {
  const resultado = response.resultado;
  $("#quantidadeOriginal").text(resultado.quantidade_original);
  $("#quantidadeFiltrada").text(resultado.quantidade_filtrada);
  $("#outliersRemovidos").text(resultado.outliers_removidos);
  $("#taxasOriginais").text(resultado.taxas_originais.join(", "));
  $("#taxasFiltradas").text(resultado.taxas_filtradas.join(", "));
  $("#filtrosResultados").show();
}

// Funções para gerenciar fluxos
function adicionarFluxo() {
  contadorFluxos++;
  const novoFluxo = `
        <div class="fluxo-item" data-fluxo="${contadorFluxos}">
            <div class="row">
                <div class="col-md-4">
                    <div class="form-group">
                        <label>Data</label>
                        <input type="date" class="form-control fluxo-data" name="fluxoData${contadorFluxos}">
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="form-group">
                        <label>Dias Úteis <span class="text-danger">*</span></label>
                        <input type="number" class="form-control fluxo-dias" name="fluxoDias${contadorFluxos}" min="0" required>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="form-group">
                        <label>Valor <span class="text-danger">*</span></label>
                        <div class="input-group">
                            <input type="number" class="form-control fluxo-valor" name="fluxoValor${contadorFluxos}" step="0.01" required>
                            <div class="input-group-append">
                                <button type="button" class="btn btn-outline-danger btn-remove-fluxo" onclick="removerFluxo(${contadorFluxos})">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;

  $("#fluxosContainer").append(novoFluxo);
  atualizarBotoesRemover();
}

function removerFluxo(numero) {
  $(`.fluxo-item[data-fluxo="${numero}"]`).remove();
  atualizarBotoesRemover();
}

function atualizarBotoesRemover() {
  const totalFluxos = $(".fluxo-item").length;
  if (totalFluxos > 1) {
    $(".btn-remove-fluxo").show();
  } else {
    $(".btn-remove-fluxo").hide();
  }
}

// --- FUNÇÕES PARA CADASTRO DE ATIVOS ---

// Inicializar eventos da aba de cadastro
$(document).ready(function () {
  // Carregar lista de ativos quando a aba for ativada
  $("#cadastro-tab").on("shown.bs.tab", function () {
    carregarListaAtivos();
  });

  // Evento de submit do formulário de cadastro
  $("#cadastroAtivoForm").on("submit", function (e) {
    e.preventDefault();
    cadastrarAtivo();
  });

  // Evento do botão limpar
  $("#limparFormulario").on("click", function () {
    limparFormularioCadastro();
  });

  // Evento do botão atualizar lista
  $("#atualizarLista").on("click", function () {
    carregarListaAtivos();
  });
});

function cadastrarAtivo() {
  const formData = {
    // Campos obrigatórios
    codigo_if: $("#codigoIfCadastro").val().trim(),
    nome: $("#nomeAtivoCadastro").val().trim(),
    emissor: $("#emissorCadastro").val().trim(),

    // Informações básicas
    status: $("#statusCadastro").val(),
    emissao: $("#emissaoCadastro").val().trim(),
    papel: $("#papelCadastro").val(),
    serie: $("#serieCadastro").val().trim(),

    // Agentes e participantes
    escriturador: $("#escrituradorCadastro").val().trim(),
    agente_fiduciario: $("#agenteFiduciarioCadastro").val().trim(),
    coordenador_lider: $("#coordenadorLiderCadastro").val().trim(),
    cedente: $("#cedenteCadastro").val().trim(),
    investidor: $("#investidorCadastro").val().trim(),
    estrutura: $("#estruturaCadastro").val().trim(),

    // Datas
    data_emissao: $("#dataEmissaoCadastro").val(),
    data_vencimento: $("#dataVencimentoCadastro").val(),
    data_final_distribuicao: $("#dataFinalDistribuicaoCadastro").val(),
    data_resgate_antecipado: $("#dataResgateAntecipadoCadastro").val(),
    data_primeira_integralizacao: $(
      "#dataPrimeiraIntegralizacaoCadastro",
    ).val(),

    // Características financeiras
    pu_emissao: $("#puEmissaoCadastro").val() || null,
    taxa: $("#taxaCadastro").val() || null,
    indexador: $("#indexadorCadastro").val().trim(),
    agio: $("#agioCadastro").val() || null,
    taxa_flutuante: $("#taxaFlutanteCadastro").val() || null,
    taxa_juros_pre_spread: $("#taxaJurosPreSpreadCadastro").val() || null,

    // Volumes e quantidades
    qtd_emitida: $("#qtdEmitidaCadastro").val() || null,
    volume_emissao: $("#volumeEmissaoCadastro").val() || null,
    qtd_integralizada: $("#qtdIntegralizadaCadastro").val() || null,
    saldo_devedor: $("#saldoDevedorCadastro").val() || null,
    isin: $("#isinCadastro").val().trim(),

    // Características operacionais
    tipo_oferta: $("#tipoOfertaCadastro").val(),
    gestao: $("#gestaoCadastro").val().trim(),
    servicing: $("#servicingCadastro").val().trim(),
    pagamento_juros: $("#pagamentoJurosCadastro").val(),
    amortizacao: $("#amortizacaoCadastro").val(),
    observacao: $("#observacaoCadastro").val().trim(),
  };

  // Validações básicas
  if (!formData.codigo_if || !formData.nome || !formData.emissor) {
    mostrarStatusCadastro(
      "Preencha todos os campos obrigatórios (Código IF, Nome e Emissor).",
      "danger",
    );
    return;
  }

  // Mostrar loading
  mostrarStatusCadastro("Cadastrando ativo...", "info");

  $.ajax({
    url: "/cadastrar_ativo",
    method: "POST",
    contentType: "application/json",
    data: JSON.stringify(formData),
    success: function (response) {
      if (response.success) {
        mostrarStatusCadastro("Ativo cadastrado com sucesso!", "success");
        limparFormularioCadastro();
        carregarListaAtivos();
      } else {
        mostrarStatusCadastro(
          response.error || "Erro ao cadastrar ativo.",
          "danger",
        );
      }
    },
    error: function (xhr) {
      let errorMsg = "Erro ao cadastrar ativo.";
      if (xhr.responseJSON && xhr.responseJSON.error) {
        errorMsg = xhr.responseJSON.error;
      }
      mostrarStatusCadastro(errorMsg, "danger");
    },
  });
}

function carregarListaAtivos() {
  const tbody = $("#tabelaAtivos");
  tbody.html(
    '<tr><td colspan="8" class="text-center text-muted"><i class="fas fa-spinner fa-spin"></i> Carregando ativos...</td></tr>',
  );

  $.ajax({
    url: "/listar_ativos",
    method: "GET",
    success: function (response) {
      if (response.success) {
        preencherTabelaAtivos(response.ativos);
      } else {
        tbody.html(
          '<tr><td colspan="8" class="text-center text-danger">Erro ao carregar ativos.</td></tr>',
        );
      }
    },
    error: function () {
      tbody.html(
        '<tr><td colspan="8" class="text-center text-danger">Erro ao carregar ativos.</td></tr>',
      );
    },
  });
}

// Função preencherTabelaAtivos removida (duplicada - mantida versão mais completa abaixo)

function excluirAtivo(ativoId, codigoIf) {
  if (!confirm(`Tem certeza que deseja excluir o ativo ${codigoIf}?`)) {
    return;
  }

  $.ajax({
    url: `/excluir_ativo/${ativoId}`,
    method: "DELETE",
    success: function (response) {
      if (response.success) {
        mostrarStatusCadastro("Ativo excluído com sucesso!", "success");
        carregarListaAtivos();
      } else {
        mostrarStatusCadastro(
          response.error || "Erro ao excluir ativo.",
          "danger",
        );
      }
    },
    error: function (xhr) {
      let errorMsg = "Erro ao excluir ativo.";
      if (xhr.responseJSON && xhr.responseJSON.error) {
        errorMsg = xhr.responseJSON.error;
      }
      mostrarStatusCadastro(errorMsg, "danger");
    },
  });
}

function mostrarStatusCadastro(mensagem, tipo) {
  const statusDiv = $("#statusCadastro");
  const alertDiv = $("#alertCadastro");
  const mensagemDiv = $("#mensagemCadastro");

  // Remover classes anteriores
  alertDiv.removeClass("alert-success alert-danger alert-warning alert-info");

  // Adicionar nova classe
  alertDiv.addClass(`alert-${tipo}`);

  // Definir mensagem
  mensagemDiv.html(mensagem);

  // Mostrar
  statusDiv.show();

  // Auto-hide para mensagens de sucesso
  if (tipo === "success") {
    setTimeout(function () {
      statusDiv.fadeOut();
    }, 3000);
  }
}

function limparFormularioCadastro() {
  $("#cadastroAtivoForm")[0].reset();
  $("#statusCadastro").hide();
}

function formatarNumero(numero) {
  return new Intl.NumberFormat("pt-BR", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(numero);
}

// Função para preencher a tabela de ativos
function preencherTabelaAtivos(ativos) {
  const tbody = document.getElementById("tabelaAtivos");
  tbody.innerHTML = ""; // Limpa o conteúdo atual

  if (ativos && ativos.length > 0) {
    tbody.innerHTML = ativos
      .map(
        (ativo, index) => `
      <tr id="ativo-${ativo.id || index}">
        <td>${ativo.codigo_if || "-"}</td>
        <td>${ativo.nome || "-"}</td>
        <td>${ativo.emissor || "-"}</td>
        <td>R$ ${
          ativo.pu_emissao ? parseFloat(ativo.pu_emissao).toFixed(2) : "-"
        }</td>
        <td>${ativo.taxa ? parseFloat(ativo.taxa).toFixed(2) + "%" : "-"}</td>
        <td>${ativo.indexador || "-"}</td>
        <td>${
          ativo.data_cadastro
            ? new Date(ativo.data_cadastro).toLocaleDateString("pt-BR")
            : "-"
        }</td>
        <td>
          ${
            ativo.id
              ? `<button class="btn btn-sm btn-warning" onclick="editarAtivo(${
                  ativo.id
                })">
            <i class="fas fa-edit"></i> Editar
          </button>`
              : '<span class="text-muted">-</span>'
          }
        </td>
      </tr>
    `,
      )
      .join("");
  } else {
    tbody.innerHTML = `
      <tr>
        <td colspan="8" class="text-center text-muted">
          <i class="fas fa-info-circle"></i> Nenhum ativo encontrado
        </td>
      </tr>
    `;
  }
}

// Função para carregar ativos
async function carregarAtivos() {
  try {
    const response = await fetch("/listar_ativos");
    const data = await response.json();

    if (data.success && data.ativos && data.ativos.length > 0) {
      preencherTabelaAtivos(data.ativos);
    } else {
      const tbody = document.getElementById("tabelaAtivos");
      tbody.innerHTML = `
        <tr>
          <td colspan="8" class="text-center text-muted">
            <i class="fas fa-info-circle"></i> Nenhum ativo encontrado
          </td>
        </tr>
      `;
    }
  } catch (error) {
    console.error("Erro ao carregar ativos:", error);
    const tbody = document.getElementById("tabelaAtivos");
    tbody.innerHTML = `
      <tr>
        <td colspan="8" class="text-center text-danger">
          <i class="fas fa-exclamation-triangle"></i> Erro ao carregar ativos
        </td>
      </tr>
    `;
  }
}

// Função para editar ativo
function editarAtivo(id) {
  const row = document.getElementById(`ativo-${id}`);
  if (!row) return;

  // Buscar dados atuais do ativo
  const cells = row.querySelectorAll("td");
  const codigoIf = cells[0].textContent.trim();
  const nome = cells[1].textContent.trim();
  const emissor = cells[2].textContent.trim();
  const puEmissao = cells[3].textContent.replace("R$ ", "").replace("-", "");
  const taxa = cells[4].textContent.replace("%", "").replace("-", "");
  const indexador = cells[5].textContent.trim();

  // Criar formulário de edição inline
  row.innerHTML = `
    <td colspan="8">
      <div class="card">
        <div class="card-header">
          <h6 class="mb-0">
            <i class="fas fa-edit text-warning"></i> Editando Ativo ID: ${id}
          </h6>
        </div>
        <div class="card-body">
          <form id="editForm-${id}">
            <div class="row">
              <div class="col-md-4">
                <div class="form-group">
                  <label>Código IF:</label>
                  <input type="text" class="form-control" id="edit-codigo-${id}" value="${
                    codigoIf !== "-" ? codigoIf : ""
                  }" />
                </div>
              </div>
              <div class="col-md-4">
                <div class="form-group">
                  <label>Nome:</label>
                  <input type="text" class="form-control" id="edit-nome-${id}" value="${
                    nome !== "-" ? nome : ""
                  }" />
                </div>
              </div>
              <div class="col-md-4">
                <div class="form-group">
                  <label>Emissor:</label>
                  <input type="text" class="form-control" id="edit-emissor-${id}" value="${
                    emissor !== "-" ? emissor : ""
                  }" />
                </div>
              </div>
            </div>
            <div class="row">
              <div class="col-md-4">
                <div class="form-group">
                  <label>PU Emissão:</label>
                  <input type="number" class="form-control" id="edit-pu-${id}" step="0.01" value="${puEmissao}" />
                </div>
              </div>
              <div class="col-md-4">
                <div class="form-group">
                  <label>Taxa (%):</label>
                  <input type="number" class="form-control" id="edit-taxa-${id}" step="0.01" value="${taxa}" />
                </div>
              </div>
              <div class="col-md-4">
                <div class="form-group">
                  <label>Indexador:</label>
                  <input type="text" class="form-control" id="edit-indexador-${id}" value="${
                    indexador !== "-" ? indexador : ""
                  }" />
                </div>
              </div>
            </div>
            <div class="text-center">
              <button type="button" class="btn btn-success" onclick="salvarEdicao(${id})">
                <i class="fas fa-save"></i> Salvar
              </button>
              <button type="button" class="btn btn-secondary ml-2" onclick="cancelarEdicao(${id})">
                <i class="fas fa-times"></i> Cancelar
              </button>
            </div>
          </form>
        </div>
      </div>
    </td>
  `;
}

// Função para salvar edição
async function salvarEdicao(id) {
  const codigoIf = document.getElementById(`edit-codigo-${id}`).value;
  const nome = document.getElementById(`edit-nome-${id}`).value;
  const emissor = document.getElementById(`edit-emissor-${id}`).value;
  const puEmissao = document.getElementById(`edit-pu-${id}`).value;
  const taxa = document.getElementById(`edit-taxa-${id}`).value;
  const indexador = document.getElementById(`edit-indexador-${id}`).value;

  try {
    const response = await fetch(`/atualizar_ativo/${id}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        codigo_if: codigoIf,
        nome: nome,
        emissor: emissor,
        pu_emissao: puEmissao ? parseFloat(puEmissao) : null,
        taxa: taxa ? parseFloat(taxa) : null,
        indexador: indexador,
      }),
    });

    const data = await response.json();

    if (data.success) {
      // Mostrar mensagem de sucesso
      const alertDiv = document.createElement("div");
      alertDiv.className = "alert alert-success alert-dismissible fade show";
      alertDiv.innerHTML = `
        <i class="fas fa-check-circle"></i> Ativo atualizado com sucesso!
        <button type="button" class="close" data-dismiss="alert">
          <span>&times;</span>
        </button>
      `;
      document
        .querySelector(".container-fluid")
        .insertBefore(alertDiv, document.querySelector(".row"));

      // Recarregar lista
      carregarAtivos();

      // Remover alerta após 3 segundos
      setTimeout(() => {
        if (alertDiv.parentNode) {
          alertDiv.parentNode.removeChild(alertDiv);
        }
      }, 3000);
    } else {
      alert("Erro ao atualizar ativo: " + (data.error || "Erro desconhecido"));
    }
  } catch (error) {
    console.error("Erro ao salvar ativo:", error);
    alert("Erro ao salvar ativo. Verifique a conexão e tente novamente.");
  }
}

// Função para cancelar edição
function cancelarEdicao(id) {
  carregarAtivos(); // Recarrega a lista para cancelar a edição
}
function carregarAtivosDaPlanilha() {
  $.ajax({
    url: "/carregar_ativos_planilha",
    method: "POST",
    contentType: "application/json",
    success: function (response) {
      if (response.success) {
        preencherTabelaAtivos(response.ativos);
        mostrarStatus("success", "Ativos carregados da planilha com sucesso!");
      } else {
        mostrarStatus("error", "Erro ao carregar ativos: " + response.error);
      }
    },
    error: function (xhr, status, error) {
      mostrarStatus("error", "Erro na comunicação com o servidor: " + error);
    },
  });
}

// Associar o botão "Carregar Ativos"
$(document).ready(function () {
  $("#btnCarregarAtivos").on("click", carregarAtivosDaPlanilha);
});
