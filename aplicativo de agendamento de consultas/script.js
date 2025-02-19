// Dados temporários de disponibilidade (normalmente você usaria um banco de dados)
const availableSlots = {
  "2025-02-13": ["09:00", "10:00", "11:00", "14:00", "15:00", "16:00"],
  "2025-02-14": ["08:00", "09:00", "10:00", "13:00", "14:00", "15:00"],
  "2025-02-15": ["09:00", "11:00", "12:00", "14:00", "15:00", "17:00"],
};

// Elementos HTML
const checkAvailabilityBtn = document.getElementById("check-availability-btn");
const datePicker = document.getElementById("date-picker");
const availableTimesContainer = document.getElementById("available-times");
const timePicker = document.getElementById("time-picker");
const appointmentForm = document.getElementById("appointment-form");
const confirmationContainer = document.getElementById("confirmation-container");

// Função para verificar a disponibilidade de horários para a data selecionada
function checkAvailability() {
  const selectedDate = datePicker.value;

  if (!selectedDate) {
    alert("Por favor, selecione uma data.");
    return;
  }

  // Limpar horários anteriores
  availableTimesContainer.innerHTML = "";

  // Verificar se há horários disponíveis para a data
  const availableTimes = availableSlots[selectedDate];

  if (availableTimes) {
    availableTimes.forEach((time) => {
      const timeSlotDiv = document.createElement("div");
      timeSlotDiv.textContent = time;
      timeSlotDiv.onclick = () => selectTime(time);
      availableTimesContainer.appendChild(timeSlotDiv);
    });
  } else {
    availableTimesContainer.innerHTML =
      "Nenhum horário disponível para esta data.";
  }
}

// Função para selecionar um horário
function selectTime(time) {
  // Limpar seleção anterior
  const options = Array.from(timePicker.options);
  options.forEach((option) => option.remove());

  // Adicionar o horário selecionado ao seletor de horários
  const option = document.createElement("option");
  option.value = time;
  option.textContent = time;
  timePicker.appendChild(option);

  // Mostrar o formulário de agendamento
  appointmentForm.style.display = "block";
}

// Função para agendar a consulta
function bookAppointment(event) {
  event.preventDefault();

  const selectedDate = datePicker.value;
  const selectedTime = timePicker.value;

  if (!selectedDate || !selectedTime) {
    alert("Por favor, selecione uma data e um horário.");
    return;
  }

  // Confirmar agendamento
  confirmationContainer.innerHTML = `Consulta agendada para ${selectedDate} às ${selectedTime}.`;

  // Limpar o formulário
  datePicker.value = "";
  timePicker.innerHTML = '<option value="">Selecione um horário</option>';
  availableTimesContainer.innerHTML = "";
  appointmentForm.style.display = "none";
  confirmationContainer.style.display = "block";
}

// Adicionar evento de clique para verificar a disponibilidade
checkAvailabilityBtn.addEventListener("click", checkAvailability);

// Adicionar evento de envio para agendar a consulta
appointmentForm.addEventListener("submit", bookAppointment);
