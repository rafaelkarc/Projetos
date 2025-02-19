// Simulação de banco de dados para feedbacks
let feedbacks = [];

// Função para exibir os feedbacks
function displayFeedbacks() {
  const container = document.getElementById("feedbacks-container");
  container.innerHTML = ""; // Limpa a lista antes de renderizar
  feedbacks.forEach((feedback) => {
    const feedbackItem = document.createElement("div");
    feedbackItem.classList.add("feedback-item");
    feedbackItem.innerHTML = `
            <div class="star-rating">
                ${"★".repeat(feedback.rating)}${"☆".repeat(5 - feedback.rating)}
            </div>
            <p>${feedback.comment}</p>
        `;
    container.appendChild(feedbackItem);
  });
}

// Função para enviar o feedback
document
  .getElementById("feedback-form")
  .addEventListener("submit", function (e) {
    e.preventDefault();

    const rating = document.querySelector('input[name="rating"]:checked');
    const comment = document.getElementById("comment").value.trim();

    if (!rating || !comment) {
      alert("Por favor, avalie e deixe um comentário!");
      return;
    }

    const newFeedback = {
      rating: parseInt(rating.value),
      comment: comment,
    };

    // Adiciona o novo feedback à lista
    feedbacks.push(newFeedback);
    displayFeedbacks();

    // Limpa o formulário após envio
    document.getElementById("feedback-form").reset();
    document
      .querySelectorAll(".star-rating input")
      .forEach((input) => (input.checked = false));
  });

// Exibir feedbacks ao carregar a página
displayFeedbacks();
