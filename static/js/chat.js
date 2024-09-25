var ws = new WebSocket(`ws://localhost:8000/chat`);

ws.onmessage = function(event) {
    let messages = document.getElementById('messages')
    let message = document.createElement('li')
    let content = document.createTextNode(event.data)
    message.appendChild(content)
    messages.appendChild(message)
};

function sendMessage(event) {
    let input = document.getElementById("messageText")
    ws.send(input.value)
    input.value = ''
    event.preventDefault()
};

