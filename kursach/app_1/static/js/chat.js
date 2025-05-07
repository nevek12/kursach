// chat.js
function appendResponse(text, elementId) {
    const responseBox = document.getElementById(elementId);
    responseBox.innerHTML += text + ' ';
    responseBox.scrollTop = responseBox.scrollHeight;
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function backspace(slice) {
    const responseBox = document.getElementById('response-box');
    responseBox.innerHTML = responseBox.innerHTML.slice(0, -slice);
}

function sendMessage() {
    const message = document.getElementById('input-box').value.trim();
    if (!message) return;

    document.getElementById('input-box').value = '';
    appendResponse('\nПользователь: ' + message, 'response-box');
    appendResponse('\nAI: thinking...', 'response-box');


    fetch('/generate/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            'message': message
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.parts) {
            backspace(12);
            let index = 0;
            function typeWriter() {
                if (index < data.parts.length) {

                    appendResponse(data.parts[index], 'response-box');
                    index++;
                    setTimeout(typeWriter, 100);
                }
            }
            typeWriter();
        }
    }).catch(error => {
        console.error('Error:', error);
        appendResponse('\nОшибка: ' + error.message, 'response-box');
    });
}

function sendInfoTcp() {

}

function sendEquipment(){
    fetch('/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            'source_ip': source_ip,
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.parts) {
            backspace(12);
            let index = 0;
            function typeWriter() {
                if (index < data.parts.length) {

                    appendResponse(data.parts[index], 'response-box');
                    index++;
                    setTimeout(typeWriter, 100);
                }
            }
            typeWriter();
        }
    }).catch(error => {
        console.error('Error:', error);
        appendResponse('\nОшибка: ' + error.message, 'response-box');
    });
}

// Инициализация после загрузки документа
document.addEventListener('DOMContentLoaded', () => {
    // Обработчик кнопки
    document.querySelector('button').addEventListener('click', sendMessage);

    // Обработчик Enter
    document.getElementById('input-box').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
            e.preventDefault();
        }
    });
    document.getElementById('id_query').addEventListener('click', sendEquipment)
});

