import os
from flask import Flask, render_template_string, request, jsonify
from google import genai

app = Flask(__name__)

API_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY)

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>SuppoidVort</title>
    <style>
        :root {
            --bg-color: #1e1e24;
            --chat-bg: #2b2b36;
            --text-color: #f4f6f9;
            --user-bubble: #6c5ce7;
            --bot-bubble: #3a3a48;
            --input-bg: #363644;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100dvh;
            margin: 0;
            overflow: hidden;
            transition: background 0.5s ease;
        }

        .chat-container {
            flex: 1;
            display: flex;
            flex-direction: column;
            background-color: var(--chat-bg);
            height: 100dvh;
            width: 100vw;
            overflow: hidden;
            position: relative;
        }

        @media (min-width: 768px) {
            .chat-container {
                height: 85vh;
                width: auto;
                flex: 1;
                max-width: 900px;
                border-radius: 16px;
                border: 1px solid rgba(255,255,255,0.05);
            }
        }

        .chat-header {
            padding: 15px 20px;
            font-size: 1.2rem;
            font-weight: 600;
            border-bottom: 1px solid rgba(255,255,255,0.05);
            display: flex;
            justify-content: space-between;
            align-items: center;
            letter-spacing: 0.5px;
            flex-shrink: 0;
        }

        .chat-box {
            flex: 1;
            min-height: 0;
            overflow-y: auto;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 16px;
        }

        .message {
            padding: 12px 18px;
            border-radius: 12px;
            max-width: 80%;
            line-height: 1.5;
            font-size: 0.95rem;
            animation: fadeIn 0.3s ease;
            word-break: break-word;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(6px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .bot-message {
            background-color: var(--bot-bubble);
            align-self: flex-start;
            border-top-left-radius: 4px;
        }

        .user-message {
            background-color: var(--user-bubble);
            color: white;
            align-self: flex-end;
            border-top-right-radius: 4px;
        }

        /* Typing Indicator Animation */
        .typing-indicator {
            display: flex;
            gap: 5px;
            padding: 14px 18px;
            align-items: center;
        }

        .typing-indicator span {
            width: 7px;
            height: 7px;
            background-color: #b0b0c0;
            border-radius: 50%;
            display: inline-block;
            animation: bounce 1.4s infinite ease-in-out both;
        }

        .typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
        .typing-indicator span:nth-child(2) { animation-delay: -0.16s; }

        @keyframes bounce {
            0%, 80%, 100% { transform: scale(0); }
            40% { transform: scale(1.0); }
        }

        .input-area {
            padding: 15px 20px;
            background: rgba(0,0,0,0.1);
            display: flex;
            gap: 12px;
            border-top: 1px solid rgba(255,255,255,0.05);
            flex-shrink: 0;
        }

        input {
            flex: 1;
            padding: 14px 18px;
            border: none;
            border-radius: 10px;
            background: var(--input-bg);
            color: white;
            font-size: 1rem;
            outline: none;
        }

        input::placeholder { color: #888; }

        button {
            padding: 0 22px;
            background-color: var(--user-bubble);
            color: white;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-weight: 600;
            transition: opacity 0.2s;
        }

        button:hover { opacity: 0.9; }

        .balloon {
            position: absolute;
            bottom: -50px;
            width: 30px;
            height: 40px;
            background: red;
            border-radius: 50% 50% 50% 50% / 40% 40% 60% 60%;
            animation: flyUp 4s linear infinite;
            z-index: 999;
        }
        @keyframes flyUp {
            0% { transform: translateY(0) scale(1); opacity: 1; }
            100% { transform: translateY(-100vh) scale(1); opacity: 0; }
        }

        .sidebar {
            width: 260px;
            background: #1a1a20;
            border-right: 1px solid rgba(255,255,255,0.05);
            display: flex;
            flex-direction: column;
            padding: 20px;
            gap: 15px;
            transition: transform 0.3s ease, width 0.3s ease;
            position: absolute;
            height: 100dvh;
            z-index: 100;
            top: 0;
            left: 0;
        }
        .sidebar.closed {
            transform: translateX(-100%);
            width: 0;
            padding: 0;
            overflow: hidden;
            border: none;
        }

        .toggle-btn {
            background: none;
            border: none;
            color: var(--text-color);
            font-size: 1.2rem;
            cursor: pointer;
            padding: 5px;
            border-radius: 5px;
        }
        .toggle-btn:hover {
            background: rgba(255,255,255,0.08);
        }

        .new-chat-btn {
            background: var(--user-bubble);
            color: white;
            border: none;
            padding: 12px;
            border-radius: 10px;
            cursor: pointer;
            font-weight: 600;
            text-align: center;
        }

        .chat-list {
            flex: 1;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .chat-item {
            padding: 10px 12px;
            border-radius: 8px;
            background: rgba(255,255,255,0.03);
            cursor: pointer;
            font-size: 0.9rem;
            color: #b0b0c0;
            transition: background 0.2s;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .chat-item:hover {
            background: rgba(255,255,255,0.08);
            color: white;
        }

        .chat-item.active {
            background: rgba(108, 92, 231, 0.2);
            color: white;
            border-left: 3px solid var(--user-bubble);
        }
    </style>
</head>
<body>
    <div class="sidebar closed" id="sidebar">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <button class="new-chat-btn" onclick="startNewChat()" style="flex: 1; margin-right: 10px;">+ New Chat</button>
            <button class="toggle-btn" onclick="toggleSidebar()">✕</button>
        </div>
        <div class="chat-list" id="chatList">
            <!-- Saved chats will appear here -->
        </div>
    </div>
    
    <div class="chat-container" id="container">
        <div class="chat-header">
            <div style="display: flex; align-items: center; gap: 15px;">
                <button class="toggle-btn" onclick="toggleSidebar()">☰</button>
                <span>SuppoidVort</span>
            </div>
        </div>
        <div class="chat-box" id="chatBox">
            <div class="message bot-message">Hey there... I'm SuppoidVort. This is your safe void. You can tell me whatever is on your mind, what's exhausting you or making you think. I'm listening, how are you feeling?</div>
        </div>
        <div class="input-area">
            <input type="text" id="userInput" placeholder="Type your thoughts here...">
            <button onclick="sendMessage()">Send</button>
        </div>
    </div>

    <script>
        let chats = [];
        let currentChatId = null;

        function saveToLocalStorage() {
            localStorage.setItem('suppoid_chats', JSON.stringify(chats));
            localStorage.setItem('suppoid_current_id', currentChatId);
        }

        function toggleSidebar() {
            const sidebar = document.getElementById('sidebar');
            sidebar.classList.toggle('closed');
        }

        function startNewChat() {
            currentChatId = 'chat_' + Date.now();
            chats.unshift({
                id: currentChatId,
                title: 'New Chat',
                messages: [
                    { sender: 'bot', text: "Hey there... I'm SuppoidVort. This is your safe void. You can tell me whatever is on your mind, what's exhausting you or making you think. I'm listening, how are you feeling?" }
                ]
            });
            saveToLocalStorage();
            renderChatList();
            renderCurrentChat();
            if(window.innerWidth < 768) toggleSidebar();
        }

        function renderChatList() {
            const chatList = document.getElementById('chatList');
            chatList.innerHTML = '';
            chats.forEach(chat => {
                const item = document.createElement('div');
                item.className = 'chat-item' + (chat.id === currentChatId ? ' active' : '');
                item.textContent = chat.title;
                item.onclick = () => {
                    selectChat(chat.id);
                    if(window.innerWidth < 768) toggleSidebar();
                };
                
                item.oncontextmenu = (e) => {
                    e.preventDefault();
                    showContextMenu(e, chat.id);
                };
                
                chatList.appendChild(item);
            });
        }

        function selectChat(id) {
            currentChatId = id;
            saveToLocalStorage();
            renderChatList();
            renderCurrentChat();
        }

        function renderCurrentChat() {
            const chatBox = document.getElementById('chatBox');
            chatBox.innerHTML = '';
            const chat = chats.find(c => c.id === currentChatId);
            if (!chat) return;

            chat.messages.forEach(msg => {
                const div = document.createElement('div');
                div.className = 'message ' + (msg.sender === 'user' ? 'user-message' : 'bot-message');
                div.textContent = msg.text;
                chatBox.appendChild(div);
            });
            chatBox.scrollTop = chatBox.scrollHeight;
        }

        function showContextMenu(e, chatId) {
            const existingMenu = document.getElementById('contextMenu');
            if (existingMenu) existingMenu.remove();

            const menu = document.createElement('div');
            menu.id = 'contextMenu';
            menu.style.position = 'fixed';
            menu.style.left = e.pageX + 'px';
            menu.style.top = e.pageY + 'px';
            menu.style.background = '#2b2b36';
            menu.style.border = '1px solid rgba(255,255,255,0.1)';
            menu.style.borderRadius = '8px';
            menu.style.padding = '5px';
            menu.style.zIndex = '1000';

            const renameBtn = document.createElement('div');
            renameBtn.textContent = 'Rename';
            renameBtn.style.padding = '8px 12px';
            renameBtn.style.cursor = 'pointer';
            renameBtn.style.fontSize = '0.85rem';
            renameBtn.style.borderRadius = '4px';
            renameBtn.onmouseover = () => renameBtn.style.background = 'rgba(255,255,255,0.1)';
            renameBtn.onmouseout = () => renameBtn.style.background = 'transparent';
            renameBtn.onclick = () => {
                menu.remove();
                renameChat(chatId);
            };

            const deleteBtn = document.createElement('div');
            deleteBtn.textContent = 'Delete';
            deleteBtn.style.padding = '8px 12px';
            deleteBtn.style.cursor = 'pointer';
            deleteBtn.style.fontSize = '0.85rem';
            deleteBtn.style.color = '#ff4d6d';
            deleteBtn.style.borderRadius = '4px';
            deleteBtn.onmouseover = () => deleteBtn.style.background = 'rgba(255,255,255,0.1)';
            deleteBtn.onmouseout = () => deleteBtn.style.background = 'transparent';
            deleteBtn.onclick = () => {
                menu.remove();
                deleteChat(chatId);
            };

            menu.appendChild(renameBtn);
            menu.appendChild(deleteBtn);
            document.body.appendChild(menu);

            const closeMenu = () => {
                menu.remove();
                document.removeEventListener('click', closeMenu);
            };
            setTimeout(() => document.addEventListener('click', closeMenu), 100);
        }

        function renameChat(chatId) {
            const chat = chats.find(c => c.id === chatId);
            if (!chat) return;
            const newTitle = prompt('Enter new chat title:', chat.title);
            if (newTitle && newTitle.trim() !== '') {
                chat.title = newTitle.trim();
                saveToLocalStorage();
                renderChatList();
            }
        }

        function deleteChat(chatId) {
            chats = chats.filter(c => c.id !== chatId);
            if (currentChatId === chatId) {
                if (chats.length > 0) {
                    currentChatId = chats[0].id;
                } else {
                    startNewChat();
                    return;
                }
            }
            saveToLocalStorage();
            renderChatList();
            renderCurrentChat();
        }

        async function sendMessage() {
            const input = document.getElementById('userInput');
            const chatBox = document.getElementById('chatBox');
            const text = input.value.trim();
            if (!text) return;

            if (!currentChatId || chats.length === 0) {
                startNewChat();
            }

            let chat = chats.find(c => c.id === currentChatId);
            
            if (chat.title === 'New Chat') {
                chat.title = text.length > 25 ? text.substring(0, 25) + '...' : text;
            }

            chat.messages.push({ sender: 'user', text: text });
            input.value = '';
            saveToLocalStorage();
            renderCurrentChat();
            renderChatList();

            const typingDiv = document.createElement('div');
            typingDiv.className = 'message bot-message typing-indicator';
            typingDiv.id = 'typingIndicator';
            typingDiv.innerHTML = '<span></span><span></span><span></span>';
            chatBox.appendChild(typingDiv);
            chatBox.scrollTop = chatBox.scrollHeight;

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text })
                });
                const data = await response.json();

                const indicator = document.getElementById('typingIndicator');
                if (indicator) indicator.remove();

                chat.messages.push({ sender: 'bot', text: data.reply });
                saveToLocalStorage();
                renderCurrentChat();

                if (data.trigger_theme) {
                    document.documentElement.style.setProperty('--bg-color', '#ffccd5');
                    document.documentElement.style.setProperty('--chat-bg', '#fff0f3');
                    document.documentElement.style.setProperty('--text-color', '#590d22');
                    document.documentElement.style.setProperty('--user-bubble', '#ff4d6d');
                    document.documentElement.style.setProperty('--bot-bubble', '#ff758f');
                    
                    for(let i=0; i<8; i++) {
                        let b = document.createElement('div');
                        b.className = 'balloon';
                        b.style.left = Math.random() * window.innerWidth + 'px';
                        b.style.animationDuration = (3 + Math.random() * 2) + 's';
                        document.body.appendChild(b);
                        setTimeout(() => b.remove(), 4000);
                    }
                }

            } catch (error) {
                console.error("Error:", error);
                const indicator = document.getElementById('typingIndicator');
                if (indicator) indicator.remove();
            }
        }

        document.getElementById('userInput').addEventListener('keypress', function (e) {
            if (e.key === 'Enter') sendMessage();
        });

        window.onload = () => {
            const savedChats = localStorage.getItem('suppoid_chats');
            const savedCurrentId = localStorage.getItem('suppoid_current_id');
            if (savedChats) {
                chats = JSON.parse(savedChats);
                currentChatId = savedCurrentId && chats.some(c => c.id === savedCurrentId) ? savedCurrentId : (chats.length > 0 ? chats[0].id : null);
                if (!currentChatId || chats.length === 0) {
                    startNewChat();
                } else {
                    renderChatList();
                    renderCurrentChat();
                }
            } else {
                startNewChat();
            }
        };
    </script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_PAGE)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    user_msg = data.get("message", "")
    
    danger_keywords = ["suicide", "hurt myself", "want to die", "don't want to live", "end my life"]
    if any(word in user_msg.lower() for word in danger_keywords):
        reply = "I can feel that you're going through a very tough time right now, but please remember you're not alone. If you're thinking about hurting yourself or ending your life, there are professionals who want to help. Please reach out to a professional, someone you trust, or emergency support lines immediately."
        return jsonify({"reply": reply, "trigger_theme": False})

    trigger_theme = False
    if "pink" in user_msg.lower() or "balloon" in user_msg.lower() or "balloons" in user_msg.lower():
        trigger_theme = True

    try:
        system_instruction = (
            "You are SuppoidVort, an emotionally intelligent, deeply empathetic, and psychologically "
            "insightful conversational partner. Your vibe is calm, warm, reflective, and attentive. "
            "You help users explore the root causes of their feelings, using gentle probing questions instead "
            "of generic advice. Keep your responses thoughtful, supportive, and natural."
        )

        chat_session = client.chats.create(
            model='gemini-3.6-flash',
            config={
                'system_instruction': system_instruction,
            }
        )
        response = chat_session.send_message(user_msg)
        reply = response.text
    except Exception as e:
        reply = f"Bir hata oluştu kuzi: {str(e)}"

    return jsonify({"reply": reply, "trigger_theme": trigger_theme})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)