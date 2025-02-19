// Sua chave da API (substitua com a sua chave de API)
const API_KEY = "SUA_API_KEY_AQUI";

// Elementos HTML
const searchBtn = document.getElementById("search-btn");
const cityInput = document.getElementById("city-input");
const weatherInfo = document.getElementById("weather-info");

// Função para exibir os dados do clima
function displayWeather(data) {
  const { name, main, weather } = data;

  const temperature = (main.temp - 273.15).toFixed(1); // Convertendo de Kelvin para Celsius
  const description = weather[0].description;

  weatherInfo.innerHTML = `
        <h2>${name}</h2>
        <div class="temp">${temperature}°C</div>
        <p>${description}</p>
        <p>Temperatura mínima: ${(main.temp_min - 273.15).toFixed(1)}°C</p>
        <p>Temperatura máxima: ${(main.temp_max - 273.15).toFixed(1)}°C</p>
    `;
  weatherInfo.style.display = "block";
}

// Função para buscar o clima da cidade
async function getWeather(city) {
  const url = `https://api.openweathermap.org/data/2.5/weather?q=${city}&appid=${API_KEY}&lang=pt_br`;

  try {
    const response = await fetch(url);
    const data = await response.json();

    if (data.cod === "404") {
      alert("Cidade não encontrada!");
    } else {
      displayWeather(data);
    }
  } catch (error) {
    console.error("Erro ao buscar clima:", error);
  }
}

// Adicionar evento de click ao botão de busca
searchBtn.addEventListener("click", () => {
  const city = cityInput.value.trim();

  if (city) {
    getWeather(city);
  } else {
    alert("Por favor, insira o nome de uma cidade!");
  }
});

// Adicionar evento de pressionar Enter ao campo de input
cityInput.addEventListener("keypress", (e) => {
  if (e.key === "Enter") {
    searchBtn.click();
  }
});
