const chatBox = document.getElementById('chat-box');
const userInput = document.getElementById('user-input');
const quickActions = document.getElementById('quick-actions');
let history = [];

// Add a hidden typing indicator
const typingIndicator = document.createElement('div');
typingIndicator.classList.add('typing-indicator');
typingIndicator.innerHTML = '<div class="dot"></div><div class="dot"></div><div class="dot"></div>';
chatBox.appendChild(typingIndicator);

function scrollToBottom() {
    chatBox.scrollTop = chatBox.scrollHeight;
}

async function sendMessage(text = null) {
    const message = text || userInput.value.trim();
    if (!message) return;

    // UI Updates
    if (!text) userInput.value = '';
    appendMessage('user', message);
    showTyping(true);

    // Hide suggestions after first message to clean up UI
    if (quickActions) quickActions.style.display = 'none';

    try {
        const response = await fetch('http://127.0.0.1:8000/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message, history: history })
        });

        const data = await response.json();

        history.push({ role: 'user', parts: [message] });
        history.push({ role: 'model', parts: [data.response] });

        showTyping(false);
        appendMessage('bot', data.response);
    } catch (error) {
        console.error('Error:', error);
        showTyping(false);
        appendMessage('bot', "⚠️ I'm observing connection issues. Please ensuring the backend is running.");
    }
}

function sendQuickMessage(text) {
    sendMessage(text);
}

function appendMessage(role, text) {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message', role === 'user' ? 'user-message' : 'bot-message');

    const contentDiv = document.createElement('div');
    contentDiv.classList.add('message-content');

    // Parse Markdown for bot, simple text for user
    if (role === 'bot') {
        contentDiv.innerHTML = marked.parse(text);
    } else {
        contentDiv.textContent = text;
    }

    msgDiv.appendChild(contentDiv);

    // Insert before typing indicator
    chatBox.insertBefore(msgDiv, typingIndicator);
    scrollToBottom();
}

function showTyping(show) {
    if (show) {
        typingIndicator.style.display = 'flex';
        chatBox.appendChild(typingIndicator); // Move to bottom
    } else {
        typingIndicator.style.display = 'none';
    }
    scrollToBottom();
}

// Enter key support
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});

// Clear chat feature
document.getElementById('clear-chat').addEventListener('click', () => {
    history = [];
    // remove all messages except the first welcome one and typing indicator
    const messages = chatBox.querySelectorAll('.message:not(:first-child)');
    messages.forEach(msg => msg.remove());
    if (quickActions) quickActions.style.display = 'flex';
});

// Dashboard Sidebar Link
const dashboardLink = document.querySelector('.menu-item:nth-child(3)');
if (dashboardLink) {
    dashboardLink.addEventListener('click', () => {
        window.open('http://localhost:8501', '_blank');
    });
}

