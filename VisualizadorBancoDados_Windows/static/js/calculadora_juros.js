/**
 * Calculadora de Juros - Script Completo
 * Manipula o formulário de juros e exibe resultados apenas em "Juros por Ativo"
 */

console.log("[OK] calculadora_juros.js carregado");

document.addEventListener("DOMContentLoaded", function () {
  console.log("[OK] Calculadora de Juros inicializada");

  // Adicionar event listener ao formulário de juros
  const jurosForm = document.getElementById("jurosForm");
  if (jurosForm) {
    jurosForm.addEventListener("submit", function (e) {
      e.preventDefault();
      calcularJuros();
    });
    console.log("[OK] Event listener adicionado ao formulário de juros");
  }

  // Adicionar event listener ao botão "Calcular Todos"
  const calcularTodosBtn = document.getElementById("calcularTodosJuros");
  if (calcularTodosBtn) {
    calcularTodosBtn.addEventListener("click", function () {
      calcularTodosJuros();
    });
    console.log('[OK] Event listener adicionado ao botão "Calcular Todos"');
  }
});

/**
 * Função para calcular juros de um ativo específico
 */
function calcularJuros() {
  const codigoIf = document.getElementById("codigoIfJuros").value.trim();
  const data = document.getElementById("dataJuros").value;

  // Validar entrada
  if (!codigoIf) {
    alert("Por favor, digite o código IF do ativo");
    return;
  }

  console.log(`[DEBUG] Calculando juros para: ${codigoIf}, data: ${data}`);

  // Mostrar loading
  mostrarLoading(true);

  // Preparar payload
  const payload = {
    codigo_if: codigoIf,
  };

  if (data) {
    payload.data = data;
  }

  // Fazer requisição ao endpoint
  fetch("/calcular_juros", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  })
    .then((response) => response.json())
    .then((data) => {
      mostrarLoading(false);

      console.log("[DEBUG] Resposta do servidor:", data);

      if (data.sucesso) {
        // Exibir resultados
        exibirResultadosJuros(data);
      } else {
        // Exibir erro
        alert("Erro: " + (data.erro || "Erro desconhecido"));
      }
    })
    .catch((error) => {
      mostrarLoading(false);
      console.error("[ERRO] Erro na requisição:", error);
      alert("Erro ao calcular juros: " + error.message);
    });
}

/**
 * Função para calcular juros de todos os ativos
 */
function calcularTodosJuros() {
  console.log("[DEBUG] Calculando juros para todos os ativos");

  // Mostrar loading
  mostrarLoading(true);

  // Fazer requisição ao endpoint
  fetch("/calcular_juros_todos", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({}),
  })
    .then((response) => response.json())
    .then((data) => {
      mostrarLoading(false);

      console.log("[DEBUG] Resposta do servidor:", data);

      if (data.sucesso) {
        alert(
          `✅ Cálculo concluído! ${data.total_calculados} ativos processados.`,
        );
        // Recarregar a tabela de histórico
        carregarHistoricoJuros();
      } else {
        alert("Erro: " + (data.erro || "Erro desconhecido"));
      }
    })
    .catch((error) => {
      mostrarLoading(false);
      console.error("[ERRO] Erro na requisição:", error);
      alert("Erro ao calcular juros: " + error.message);
    });
}

/**
 * Função para exibir resultados dos juros
 */
function exibirResultadosJuros(data) {
  // Preencher campos de resultado
  document.getElementById("codigoIfResultado").textContent =
    data.codigo_if || "-";

  document.getElementById("dataResultado").textContent =
    data.data_calculo || "-";

  document.getElementById("vnaResultado").textContent = data.emissao
    ? formatarNumero(data.emissao)
    : "-";

  document.getElementById("porcentagemResultado").textContent = data.taxa
    ? formatarPercentual(data.taxa / 100)
    : "-";

  document.getElementById("jurosCalculadoResultado").textContent =
    data.juros_calculado ? formatarNumero(data.juros_calculado) : "-";

  document.getElementById("dataCalculoJurosResultado").textContent =
    data.data_calculo || "-";

  // Mostrar área de resultados
  document.getElementById("jurosResultados").style.display = "block";

  // Scroll para resultados
  document
    .getElementById("jurosResultados")
    .scrollIntoView({ behavior: "smooth" });

  console.log("✅ Cálculo de juros realizado com sucesso");
  console.log(data);
}

/**
 * Função para carregar histórico de juros
 */
function carregarHistoricoJuros() {
  console.log("[DEBUG] Carregando histórico de juros");

  fetch("/juros_historico", {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  })
    .then((response) => response.json())
    .then((data) => {
      console.log("[DEBUG] Histórico carregado:", data);

      if (data.sucesso && data.historico) {
        preencherTabelaHistorico(data.historico);
      }
    })
    .catch((error) => {
      console.error("[ERRO] Erro ao carregar histórico:", error);
    });
}

/**
 * Função para preencher a tabela de histórico
 */
function preencherTabelaHistorico(historico) {
  const tbody = document.querySelector("#historicoJurosTable tbody");

  if (!tbody) {
    console.warn("[AVISO] Tabela de histórico não encontrada");
    return;
  }

  // Limpar tabela
  tbody.innerHTML = "";

  if (historico.length === 0) {
    tbody.innerHTML =
      '<tr><td colspan="6" class="text-center text-muted">Nenhum cálculo de juros registrado</td></tr>';
    return;
  }

  // Preencher tabela
  historico.forEach((item) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
            <td>${item.codigo_if || "-"}</td>
            <td>${item.data_dia_25 || "-"}</td>
            <td>${item.vna ? formatarNumero(item.vna) : "-"}</td>
            <td>${item.porcentagem ? formatarPercentual(item.porcentagem / 100) : "-"}</td>
            <td>${item.juros ? formatarNumero(item.juros) : "-"}</td>
            <td>${item.data_calculo || "-"}</td>
        `;
    tbody.appendChild(tr);
  });
}

/**
 * Função para formatar número
 */
function formatarNumero(numero) {
  if (numero === null || numero === undefined || isNaN(numero)) {
    return "-";
  }

  return new Intl.NumberFormat("pt-BR", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 8,
  }).format(numero);
}

/**
 * Função para formatar percentual
 */
function formatarPercentual(percentual) {
  if (percentual === null || percentual === undefined || isNaN(percentual)) {
    return "-";
  }

  // Se o valor já está em formato decimal (ex: 0.09), multiplicar por 100
  let valor = percentual;
  if (percentual < 1) {
    valor = percentual * 100;
  }

  return valor.toFixed(6) + "%";
}

/**
 * Função para mostrar/ocultar loading
 */
function mostrarLoading(mostrar) {
  const spinner = document.getElementById("loadingSpinner");
  if (spinner) {
    spinner.style.display = mostrar ? "block" : "none";
  }
}

console.log("[OK] Todas as funções de juros carregadas");
