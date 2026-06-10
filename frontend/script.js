const API_URL = "http://localhost:8000/ask";

const questionInput = document.getElementById("questionInput");
const chatBox = document.getElementById("chatBox");

function addMessage(text, sender) {
  const message = document.createElement("div");
  message.classList.add("message", sender);
  message.innerText = text;
  chatBox.appendChild(message);
  chatBox.scrollTop = chatBox.scrollHeight;
}

async function askQuestion() {
  const question = questionInput.value.trim();

  if (!question) {
    addMessage("Masukkan pertanyaan terlebih dahulu.", "bot");
    return;
  }

  addMessage(question, "user");
  questionInput.value = "";

  addMessage("Sedang mencari jawaban dari OpenSearch...", "bot");

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        question: question
      })
    });

    const data = await response.json();

    const botMessages = document.querySelectorAll(".message.bot");
    const lastBotMessage = botMessages[botMessages.length - 1];

    if (data.answer) {
      lastBotMessage.innerText = data.answer;
    } else if (data.response) {
      lastBotMessage.innerText = data.response;
    } else if (data.message) {
      lastBotMessage.innerText = data.message;
    } else {
      lastBotMessage.innerText = "Jawaban diterima, tetapi format response backend belum sesuai.";
    }

  } catch (error) {
    const botMessages = document.querySelectorAll(".message.bot");
    const lastBotMessage = botMessages[botMessages.length - 1];

    lastBotMessage.innerText = 
      "Gagal menghubungi backend. Pastikan FastAPI berjalan di http://localhost:8000 dan endpoint /ask tersedia.";

    console.error(error);
  }
}

questionInput.addEventListener("keydown", function(event) {
  if (event.key === "Enter") {
    askQuestion();
  }
});
