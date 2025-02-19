document
  .getElementById("checkout-form")
  .addEventListener("submit", function (event) {
    event.preventDefault();

    // Limpar mensagens de erro
    document.getElementById("error-message").textContent = "";

    // Pegando os valores dos campos
    const name = document.getElementById("name").value;
    const email = document.getElementById("email").value;
    const phone = document.getElementById("phone").value;
    const address = document.getElementById("address").value;
    const payment = document.getElementById("payment").value;

    // Validação dos campos
    if (!name || !email || !phone || !address || !payment) {
      document.getElementById("error-message").textContent =
        "Por favor, preencha todos os campos!";
      return;
    }

    // Validação do formato do e-mail
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      document.getElementById("error-message").textContent =
        "Por favor, insira um e-mail válido!";
      return;
    }

    // Validação do telefone (exemplo simples de número)
    const phoneRegex = /^\d{10,11}$/;
    if (!phoneRegex.test(phone)) {
      document.getElementById("error-message").textContent =
        "Por favor, insira um número de telefone válido!";
      return;
    }

    // Se passar na validação, exibe mensagem de sucesso
    alert("Compra finalizada com sucesso!");
  });
