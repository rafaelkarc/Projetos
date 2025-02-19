// Dados de exemplo para autenticação (em um sistema real, isso viria de um banco de dados)
const users = [{ username: "admin", password: "123456" }];

// Função de Login
document.getElementById("login-form").addEventListener("submit", function (e) {
  e.preventDefault();

  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;
  const errorMessage = document.getElementById("login-error");

  // Verificar se o usuário e senha são válidos
  const user = users.find(
    (user) => user.username === username && user.password === password
  );

  if (user) {
    // Mostrar o painel de controle e esconder o login
    document.getElementById("login-container").style.display = "none";
    document.getElementById("dashboard-container").style.display = "block";
  } else {
    errorMessage.textContent = "Usuário ou senha incorretos!";
  }
});

// Função para logar o admin
document.getElementById("logout-btn").addEventListener("click", function () {
  document.getElementById("login-container").style.display = "block";
  document.getElementById("dashboard-container").style.display = "none";
});

// Dados de exemplo para a tabela de usuários
const usersData = [
  { id: 1, name: "João Silva", email: "joao@exemplo.com" },
  { id: 2, name: "Maria Oliveira", email: "maria@exemplo.com" },
  { id: 3, name: "Pedro Souza", email: "pedro@exemplo.com" },
];

// Preencher a tabela de usuários
function fillUserTable() {
  const tbody = document.querySelector("#user-table tbody");
  usersData.forEach((user) => {
    const row = document.createElement("tr");
    row.innerHTML = `
          <td>${user.id}</td>
          <td>${user.name}</td>
          <td>${user.email}</td>
      `;
    tbody.appendChild(row);
  });
}
fillUserTable();

// Gráficos de exemplo
const ctxSales = document.getElementById("salesChart").getContext("2d");
const ctxUsers = document.getElementById("usersChart").getContext("2d");

const salesChart = new Chart(ctxSales, {
  type: "line",
  data: {
    labels: ["Jan", "Feb", "Mar", "Apr", "May"],
    datasets: [
      {
        label: "Vendas",
        data: [50, 100, 75, 120, 150],
        borderColor: "#007bff",
        backgroundColor: "rgba(0, 123, 255, 0.2)",
        fill: true,
      },
    ],
  },
});

const usersChart = new Chart(ctxUsers, {
  type: "bar",
  data: {
    labels: ["Jan", "Feb", "Mar", "Apr", "May"],
    datasets: [
      {
        label: "Novos Usuários",
        data: [5, 10, 8, 12, 15],
        backgroundColor: "#28a745",
        borderColor: "#28a745",
        borderWidth: 1,
      },
    ],
  },
});
