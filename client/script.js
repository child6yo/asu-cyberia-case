const chatbox = document.getElementById('chatbox');
const input = document.getElementById('message-input');
const sendBtn = document.getElementById('send-btn');

const API_URL = "https://pkbn5sdd-8000.asse.devtunnels.ms"; 

// получаем или генерим айди пользователя
let userId = localStorage.getItem('user_id');
if (!userId) {
  userId = crypto.randomUUID();
  localStorage.setItem('user_id', userId);
}

const isFirstLoad = !localStorage.getItem('chat_history');

// восстановление чата по айди
function loadChatHistory() {
  const chatHistory = JSON.parse(localStorage.getItem('chat_history'));
  if (chatHistory) {
    chatHistory.forEach(msg => addMessage(msg.text, msg.sender));
  }
}

// сохранение чата
function saveChatHistory() {
  const chatHistory = [];
  document.querySelectorAll('.message').forEach(msgDiv => {
    chatHistory.push({
      text: msgDiv.innerHTML || msgDiv.textContent,
      sender: msgDiv.classList.contains('user') ? 'user' : 'bot',
    });
  });
  localStorage.setItem('chat_history', JSON.stringify(chatHistory));
}

// обработка текста, маркдаун
function processMarkdown(text) {
  let safeText = text
    .replace(/&/g, "&amp;")
    .replace(/</g, "<")
    .replace(/>/g, ">")
    .replace(/"/g, "&quot;")
    .replace(/\n/g, "<br>"); 

  safeText = safeText.replace(/\*(.*?)\*/g, '<strong>$1</strong>');
  const urlRegex = /(https?:\/\/[^\s<>"{}|\\^`[\]]+)/gi;
  return safeText.replace(urlRegex, '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>');
}

// добавление сообщения
function addMessage(text, sender) {
  const msgDiv = document.createElement('div');
  msgDiv.classList.add('message', sender);
  msgDiv[sender === 'bot' ? 'innerHTML' : 'textContent'] = sender === 'bot' ? processMarkdown(text) : text;
  chatbox.appendChild(msgDiv);
  chatbox.scrollTop = chatbox.scrollHeight;
  saveChatHistory();
}

// отправка сообщения
async function sendMessage() {
  const text = input.value.trim();
  if (!text) return;

  input.value = '';
  sendBtn.disabled = true;
  addMessage(text, 'user');

  const loadingDiv = document.createElement('div');
  loadingDiv.classList.add('message', 'bot');
  loadingDiv.textContent = 'Думаю...';
  chatbox.appendChild(loadingDiv);
  chatbox.scrollTop = chatbox.scrollHeight;

  try {
    const response = await fetch(`${API_URL}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId, message: text })
    });

    loadingDiv.remove();

    if (!response.ok) throw new Error('Сервер не отвечает');

    const data = await response.json();
    const TRIGGER_PHRASE = "Спасибо! Ваш проект сохранён.";

    addMessage(data.response || 'Без ответа', 'bot');

    if (data.project && typeof data.response === 'string' && data.response.includes(TRIGGER_PHRASE)) {
      const p = data.project;
      let formatted = `<div class="project-summary"><h3>Проект: ${p.name || 'Без названия'}</h3>`;
      
      if (p.customer) {
        formatted += `<p><strong>Клиент:</strong> ${p.customer.name || '—'}</p>`;
        if (p.customer.email) formatted += `<p><strong>Email:</strong> ${p.customer.email}</p>`;
        if (p.customer.phone) formatted += `<p><strong>Телефон:</strong> ${p.customer.phone}</p>`;
      }

      if (p.description) formatted += `<p><strong>Описание:</strong> ${p.description}</p>`;
      if (p.requirements) formatted += `<p><strong>Требования:</strong> ${p.requirements}</p>`;
      if (p.estimate) formatted += `<p><strong>Оценка:</strong> ${p.estimate}</p>`;

      formatted += `</div>`;
      addMessage(formatted, 'bot');
    }
  } catch {
    loadingDiv.remove();
    addMessage('Не удалось получить ответ. Проверьте подключение.', 'bot');
  } finally {
    sendBtn.disabled = false;
  }
}

// запрет на спам сообщениями пока бот формирует ответ
input.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey && !sendBtn.disabled) {
    e.preventDefault();
    sendMessage();
  }
});

sendBtn.addEventListener('click', sendMessage);

// инициализация
loadChatHistory();
if (isFirstLoad) {
  addMessage('Здравствуйте! Я — виртуальный помощник. Чем могу помочь?', 'bot');
}

// перезагрузка чата
document.getElementById('reset-btn').addEventListener('click', () => {
  
  chatbox.innerHTML = '';
  
  localStorage.removeItem('user_id');
  localStorage.removeItem('chat_history');
  
  userId = crypto.randomUUID();
  localStorage.setItem('user_id', userId);
  
  addMessage('Здравствуйте! Я — виртуальный помощник. Чем могу помочь?', 'bot');
});