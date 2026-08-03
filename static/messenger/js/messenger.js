// static/messenger/js/messenger.js

let currentSocket = null;
let currentChatId = null;
let currentPage = 1;
let isLoadingMessages = false;
let hasMoreMessages = true;

document.addEventListener('DOMContentLoaded', function() {
    loadChats();
});

function loadChats() {
    const chatList = document.getElementById('chat-list');
    
    chatList.innerHTML = `
        <div class="text-center text-muted py-4">
            <i class="bi bi-arrow-repeat"></i> Загрузка чатов...
        </div>
    `;

    fetch('/messenger/api/chats/')
        .then(response => response.json())
        .then(data => {
            if (data.chats && data.chats.length > 0) {
                chatList.innerHTML = data.chats.map(chat => `
                    <div class="chat-item d-flex align-items-center p-3" data-chat-id="${chat.id}" onclick="openChat(${chat.id})">
                        <div class="chat-item-avatar me-3">
                            <i class="bi bi-person-circle"></i>
                        </div>
                        <div class="flex-grow-1 min-width-0">
                            <div class="chat-item-name">${chat.name}</div>
                            <div class="chat-item-last-message">${chat.last_message || 'Нет сообщений'}</div>
                        </div>
                    </div>
                `).join('');
            } else {
                chatList.innerHTML = `
                    <div class="empty-chats">
                        <p class="text-muted">У вас нет чатов</p>
                        <a href="/messenger/create/" class="btn btn-primary btn-sm">
                            <i class="bi bi-plus"></i> Создать чат
                        </a>
                    </div>
                `;
            }
        })
        .catch(error => {
            console.error('Ошибка загрузки чатов:', error);
            chatList.innerHTML = `
                <div class="text-center text-danger py-4">
                    <i class="bi bi-exclamation-triangle"></i> Ошибка загрузки
                </div>
            `;
        });
}

function openChat(chatId) {
    if (currentSocket && currentSocket.readyState === WebSocket.OPEN) {
        currentSocket.close();
    }
    
    currentChatId = chatId;
    currentPage = 1;
    hasMoreMessages = true;
    
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = protocol + '//' + window.location.host + '/ws/chat/' + chatId + '/';
    
    const chatContent = document.getElementById('chat-content');
    chatContent.innerHTML = `
        <div class="chat-header p-3 border-bottom bg-white flex-shrink-0">
            <h5 class="mb-0" id="chat-title"><i class="bi bi-arrow-repeat"></i> Загрузка...</h5>
        </div>
        <div class="chat-messages flex-grow-1 p-3 overflow-auto" id="chat-messages" style="background: #f8f9fa;">
            <div class="text-center text-muted py-4">
                <i class="bi bi-arrow-repeat"></i> Загрузка сообщений...
            </div>
        </div>
        <div class="chat-input" id="chat-input-fixed">
            <div class="d-flex gap-2 w-100">
                <input type="text" id="message-input" class="form-control" placeholder="Введите сообщение..." />
                <button onclick="sendMessage()" class="btn btn-primary">
                    <i class="bi bi-send"></i>
                </button>
            </div>
        </div>
    `;
    
    // 🔥 Привязываем поле ввода к правой панели
    fixChatInput();
    
    const socket = new WebSocket(wsUrl);
    currentSocket = socket;
    
    socket.onopen = function() {
        console.log('✅ WebSocket connected for chat', chatId);
        loadChatTitle(chatId);
        loadMessages(chatId);
    };
    
    socket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        displayMessage(data);
    };
    
    socket.onerror = function(e) {
        console.error('❌ WebSocket error', e);
        document.getElementById('chat-messages').innerHTML = `
            <div class="text-center text-danger py-4">
                <i class="bi bi-exclamation-triangle"></i> Ошибка подключения
            </div>
        `;
    };
    
    socket.onclose = function() {
        console.log('❌ WebSocket closed');
    };
}

function fixChatInput() {
    const chatInput = document.getElementById('chat-input-fixed');
    if (!chatInput) return;
    
    // Находим правую панель
    const chatMain = document.querySelector('.chat-main');
    if (!chatMain) return;
    
    // Получаем позицию правой панели
    const rect = chatMain.getBoundingClientRect();
    
    // Устанавливаем позицию поля ввода относительно правой панели
    chatInput.style.position = 'fixed';
    chatInput.style.bottom = '0';
    chatInput.style.left = rect.left + 'px';
    chatInput.style.width = rect.width + 'px';
    chatInput.style.zIndex = '9999';
    chatInput.style.minHeight = '70px';
    chatInput.style.maxHeight = '70px';
    chatInput.style.background = '#fff';
    chatInput.style.borderTop = '2px solid #dee2e6';
    chatInput.style.padding = '12px 20px';
    chatInput.style.display = 'flex';
    chatInput.style.alignItems = 'center';
    chatInput.style.boxShadow = '0 -2px 10px rgba(0,0,0,0.1)';
    
    // Обновляем позицию при изменении размера окна
    if (window._resizeListener) {
        window.removeEventListener('resize', window._resizeListener);
    }
    window._resizeListener = function() {
        const newRect = chatMain.getBoundingClientRect();
        chatInput.style.left = newRect.left + 'px';
        chatInput.style.width = newRect.width + 'px';
    };
    window.addEventListener('resize', window._resizeListener);
}

function closeChat() {
    const chatInput = document.getElementById('chat-input-fixed');
    if (chatInput) {
        chatInput.style.display = 'none';
    }
    if (window._resizeListener) {
        window.removeEventListener('resize', window._resizeListener);
        window._resizeListener = null;
    }
}

function loadMessages(chatId, append = false) {
    if (isLoadingMessages) return;
    isLoadingMessages = true;
    
    const messagesContainer = document.getElementById('chat-messages');
    
    if (!append) {
        messagesContainer.innerHTML = `
            <div class="text-center text-muted py-4">
                <i class="bi bi-arrow-repeat"></i> Загрузка сообщений...
            </div>
        `;
        currentPage = 1;
        hasMoreMessages = true;
    }
    
    const url = `/messenger/api/messages/${chatId}/?page=${currentPage}`;
    
    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                messagesContainer.innerHTML = `
                    <div class="text-center text-danger py-4">
                        <i class="bi bi-exclamation-triangle"></i> ${data.error}
                    </div>
                `;
                isLoadingMessages = false;
                return;
            }
            
            hasMoreMessages = data.has_previous;
            
            if (data.messages.length === 0) {
                if (!append) {
                    messagesContainer.innerHTML = `
                        <div class="text-center text-muted py-4">
                            В этом чате пока нет сообщений
                        </div>
                    `;
                }
                isLoadingMessages = false;
                return;
            }
            
            // ✅ Правильный способ: создаем копию и переворачиваем её
            // Используем slice() чтобы не мутировать исходный массив
            const messages = data.messages.slice();
            
            let html = '';
            
            // Если есть старые сообщения и мы добавляем их (append)
            if (hasMoreMessages && append) {
                html += `
                    <div class="text-center py-2">
                        <button onclick="loadMoreMessages()" class="btn btn-sm btn-outline-secondary">
                            <i class="bi bi-chevron-up"></i> Загрузить предыдущие
                        </button>
                    </div>
                `;
            }
            
            // Формируем сообщения (старые сверху, новые снизу)
            messages.forEach(msg => {
                const isMine = msg.employee_id === window.userId;
                html += `
                    <div class="message ${isMine ? 'message-mine' : 'message-other'}">
                        <div class="message-content">
                            ${!isMine ? `<div class="message-author">${msg.employee_name}</div>` : ''}
                            <div class="message-text">${escapeHtml(msg.message)}</div>
                            <div class="message-time">${msg.created_at}</div>
                        </div>
                    </div>
                `;
            });
            
            if (append) {
                // Добавляем старые сообщения в начало
                messagesContainer.innerHTML = html + messagesContainer.innerHTML;
            } else {
                // Первая загрузка — просто вставляем все сообщения
                messagesContainer.innerHTML = html;
                // Скроллим вниз к последнему сообщению
                setTimeout(() => {
                    messagesContainer.scrollTop = messagesContainer.scrollHeight;
                }, 100);
            }
            
            isLoadingMessages = false;
        })
        .catch(error => {
            console.error('Ошибка загрузки сообщений:', error);
            if (!append) {
                messagesContainer.innerHTML = `
                    <div class="text-center text-danger py-4">
                        <i class="bi bi-exclamation-triangle"></i> Ошибка загрузки
                    </div>
                `;
            }
            isLoadingMessages = false;
        });
}

function loadMoreMessages() {
    if (!hasMoreMessages || isLoadingMessages) return;
    currentPage += 1;
    loadMessages(currentChatId, true);
}

function loadChatTitle(chatId) {
    fetch('/messenger/api/chats/')
        .then(response => response.json())
        .then(data => {
            const chat = data.chats.find(c => c.id === chatId);
            if (chat) {
                document.getElementById('chat-title').textContent = chat.name;
            }
        })
        .catch(error => console.error('Ошибка загрузки названия:', error));
}

function displayMessage(data) {
    const messagesContainer = document.getElementById('chat-messages');
    if (!messagesContainer) return;
    
    const systemMessage = messagesContainer.querySelector('.text-muted.py-4');
    if (systemMessage) systemMessage.remove();
    
    const isMine = data.employee_id === window.userId;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isMine ? 'message-mine' : 'message-other'}`;
    messageDiv.innerHTML = `
        <div class="message-content">
            ${!isMine ? `<div class="message-author">${data.employee_full_name || 'Пользователь'}</div>` : ''}
            <div class="message-text">${escapeHtml(data.message)}</div>
            <div class="message-time">${data.created_at || 'только что'}</div>
        </div>
    `;
    
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function sendMessage() {
    const input = document.getElementById('message-input');
    if (!input) return;
    
    const message = input.value.trim();
    if (!message) return;
    
    if (currentSocket && currentSocket.readyState === WebSocket.OPEN) {
        currentSocket.send(JSON.stringify({
            'action': 'message',
            'message': message
        }));
        input.value = '';
        
        // displayMessage({
        //     'employee_id': window.userId,
        //     'message': message,
        //     'created_at': 'отправлено'
        // });
    } else {
        alert('Соединение с чатом не установлено');
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

document.addEventListener('keypress', function(e) {
    if (e.key === 'Enter' && document.activeElement.id === 'message-input') {
        sendMessage();
    }
});

function refreshChatList() {
    loadChats();
}