// Função para carregar os posts armazenados no localStorage
function loadPosts() {
  const posts = JSON.parse(localStorage.getItem("posts")) || [];
  const postsList = document.getElementById("posts-list");
  postsList.innerHTML = ""; // Limpa a lista antes de adicionar os posts

  posts.forEach((post, index) => {
    const postElement = document.createElement("div");
    postElement.classList.add("post");

    // Título do post
    const postTitle = document.createElement("h3");
    postTitle.textContent = post.title;
    postElement.appendChild(postTitle);

    // Conteúdo do post
    const postContent = document.createElement("p");
    postContent.textContent = post.content;
    postElement.appendChild(postContent);

    // Botões de editar e excluir
    const buttons = document.createElement("div");
    buttons.classList.add("buttons");

    // Editar
    const editButton = document.createElement("button");
    editButton.textContent = "Editar";
    editButton.addEventListener("click", () => editPost(index));
    buttons.appendChild(editButton);

    // Excluir
    const deleteButton = document.createElement("button");
    deleteButton.textContent = "Excluir";
    deleteButton.addEventListener("click", () => deletePost(index));
    buttons.appendChild(deleteButton);

    postElement.appendChild(buttons);

    // Seções de comentários
    const commentSection = document.createElement("div");
    commentSection.classList.add("comment-section");
    commentSection.innerHTML = `<h4>Comentários</h4>`;

    // Adicionar campo para comentário
    const commentTextArea = document.createElement("textarea");
    commentTextArea.placeholder = "Adicionar um comentário...";
    commentSection.appendChild(commentTextArea);

    const commentButton = document.createElement("button");
    commentButton.textContent = "Adicionar Comentário";
    commentButton.addEventListener("click", () =>
      addComment(index, commentTextArea.value)
    );
    commentSection.appendChild(commentButton);

    postElement.appendChild(commentSection);

    postsList.appendChild(postElement);
  });
}

// Função para criar um novo post
document
  .getElementById("create-post-form")
  .addEventListener("submit", function (event) {
    event.preventDefault();

    const title = document.getElementById("post-title").value;
    const content = document.getElementById("post-content").value;

    if (title && content) {
      const posts = JSON.parse(localStorage.getItem("posts")) || [];
      posts.push({ title, content, comments: [] });
      localStorage.setItem("posts", JSON.stringify(posts));

      // Limpar os campos e recarregar os posts
      document.getElementById("post-title").value = "";
      document.getElementById("post-content").value = "";
      loadPosts();
    }
  });

// Função para editar um post
function editPost(index) {
  const posts = JSON.parse(localStorage.getItem("posts"));
  const post = posts[index];

  document.getElementById("post-title").value = post.title;
  document.getElementById("post-content").value = post.content;

  // Excluir o post original
  deletePost(index);

  // Mudar o botão para "Salvar" e adicionar o comportamento de salvar
  const createPostForm = document.getElementById("create-post-form");
  createPostForm.addEventListener("submit", function saveEditedPost(event) {
    event.preventDefault();

    const updatedTitle = document.getElementById("post-title").value;
    const updatedContent = document.getElementById("post-content").value;

    if (updatedTitle && updatedContent) {
      posts.push({
        title: updatedTitle,
        content: updatedContent,
        comments: [],
      });
      localStorage.setItem("posts", JSON.stringify(posts));

      // Limpar campos e recarregar posts
      document.getElementById("post-title").value = "";
      document.getElementById("post-content").value = "";
      loadPosts();

      createPostForm.removeEventListener("submit", saveEditedPost);
    }
  });
}

// Função para excluir um post
function deletePost(index) {
  const posts = JSON.parse(localStorage.getItem("posts"));
  posts.splice(index, 1);
  localStorage.setItem("posts", JSON.stringify(posts));
  loadPosts();
}

// Função para adicionar um comentário a um post
function addComment(postIndex, commentContent) {
  if (commentContent) {
    const posts = JSON.parse(localStorage.getItem("posts"));
    posts[postIndex].comments.push(commentContent);
    localStorage.setItem("posts", JSON.stringify(posts));
    loadPosts();
  }
}

// Carregar posts ao inicializar a página
loadPosts();
