/**
 * Script para Calculadora de Amortização
 * Integra com o endpoint /calcular_amortizacao
 */

document.addEventListener("DOMContentLoaded", function () {
  // Adicionar event listener ao formulário de amortização
  const amortizacaoForm = document.getElementById("amortizacaoForm");

  if (amortizacaoForm) {
    amortizacaoForm.addEventListener("submit", function (e) {
      e.preventDefault();
      calcularAmortizacao();
    });
  }
});

/**
 * Função para calcular amortização
 */
function calcularAmortizacao() {
  const valorPrincipal = document.getElementById("valorPrincipalAmort").value;
  const chaveInput = document.getElementById("chaveAmort").value;

  // Validar entrada
  if (!valorPrincipal || !chaveInput) {
    alert("Por favor, preencha todos os campos obrigatórios");
    return;
  }

  // Converter a data para o formato correto (YYYY-MM-DD HH:MM:SS)
  let chave = chaveInput.trim();

  // Se for apenas data (YYYY-MM-DD), adicionar hora
  if (chave.match(/^\d{4}-\d{2}-\d{2}$/)) {
    chave = chave + " 00:00:00";
  }
  // Se for formato DD/MM/YYYY, converter para YYYY-MM-DD HH:MM:SS
  else if (chave.match(/^\d{2}\/\d{2}\/\d{4}$/)) {
    const partes = chave.split("/");
    chave = `${partes[2]}-${partes[1]}-${partes[0]} 00:00:00`;
  }
  // Se for apenas DD-MM-YYYY, converter para YYYY-MM-DD HH:MM:SS
  else if (chave.match(/^\d{2}-\d{2}-\d{4}$/)) {
    const partes = chave.split("-");
    chave = `${partes[2]}-${partes[1]}-${partes[0]} 00:00:00`;
  }

  console.log("Chave convertida:", chave);

  // Mostrar loading
  mostrarLoading(true);

  // Fazer requisição ao endpoint
  const url = `${window.location.protocol}//${window.location.hostname}:${window.location.port}/calcular_amortizacao`;

  console.log("URL:", url);
  console.log("Payload:", {
    valor_principal: parseFloat(valorPrincipal),
    chave: chave,
  });

  fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      valor_principal: parseFloat(valorPrincipal),
      chave: chave,
    }),
  })
    .then((response) => {
      console.log("Response status:", response.status);
      return response.json();
    })
    .then((data) => {
      mostrarLoading(false);

      console.log("Response data:", data);

      if (data.success) {
        // Exibir resultados
        exibirResultadosAmortizacao(data);
      } else {
        // Exibir erro
        alert("Erro: " + data.error);
      }
    })
    .catch((error) => {
      mostrarLoading(false);
      console.error("Erro na requisição:", error);
      alert("Erro ao calcular amortização: " + error.message);
    });
}

/**
 * Função para exibir resultados da amortização
 */
function exibirResultadosAmortizacao(data) {
  // Preencher campos de resultado
  document.getElementById("valorPrincipalResultado").textContent =
    formatarNumero(data.valor_principal);

  document.getElementById("chaveResultado").textContent = data.chave;

  document.getElementById("porcentagemAmortResultado").textContent =
    formatarPercentual(data.porcentagem);

  document.getElementById("resultadoAmortizacao").textContent = data.resultado;

  document.getElementById("dataCalculoAmortResultado").textContent =
    data.data_calculo;

  // Mostrar área de resultados
  document.getElementById("amortizacaoResultados").style.display = "block";

  // Scroll para resultados
  document
    .getElementById("amortizacaoResultados")
    .scrollIntoView({ behavior: "smooth" });

  console.log("✅ Cálculo de amortização realizado com sucesso");
  console.log(data);
}

/**
 * Função para formatar número
 */
function formatarNumero(numero) {
  return new Intl.NumberFormat("pt-BR", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 8,
  }).format(numero);
}

/**
 * Função para formatar percentual
 */
function formatarPercentual(percentual) {
  return new Intl.NumberFormat("pt-BR", {
    minimumFractionDigits: 6,
    maximumFractionDigits: 8,
    style: "percent",
  }).format(percentual);
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
