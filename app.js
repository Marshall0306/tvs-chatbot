class Chatbox {
    constructor() {
        this.args = {
            openButton: document.querySelector('.chatbox__button'),
            chatBox: document.querySelector('.chatbox__support'),
            sendButton: document.querySelector('.send__button')
        };

        this.state = false;
        this.messages = [];
    }

    display() {
        const { openButton, chatBox, sendButton } = this.args;

        openButton.addEventListener('click', () => {
            this.toggleState(chatBox);
            if (this.state) {
                this.addWelcomeMessage(chatBox); 
            }
        });

        sendButton.addEventListener('click', () => this.onSendButton(chatBox));

        const node = chatBox.querySelector('input');
        node.addEventListener("keyup", ({ key }) => {
            if (key === "Enter") {
                this.onSendButton(chatBox);
            }
        });
    }

    toggleState(chatbox) {
        this.state = !this.state;

        if (this.state) {
            chatbox.classList.add('chatbox--active');
            this.enterFullScreen(chatbox);
        } else {
            chatbox.classList.remove('chatbox--active');
            this.exitFullScreen();
        }
    }

    enterFullScreen(chatbox) {
        if (chatbox.requestFullscreen) {
            chatbox.requestFullscreen();
        } else if (chatbox.mozRequestFullScreen) { 
            chatbox.mozRequestFullScreen();
        } else if (chatbox.webkitRequestFullscreen) { 
            chatbox.webkitRequestFullscreen();
        } else if (chatbox.msRequestFullscreen) { 
            chatbox.msRequestFullscreen();
        }
    }

    onSendButton(chatbox) {
        const textField = chatbox.querySelector('input');
        let text1 = textField.value;
        if (text1 === "") {
            return;
        }

        let msg1 = { name: "User", message: text1 };
        this.messages.push(msg1);
        this.updateChatText(chatbox);

        fetch($SCRIPT_ROOT + '/predict', {
            method: 'POST',
            body: JSON.stringify({ message: text1 }),
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json'
            },
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                if (data.redirect) {
                    window.location.href = data.redirect;
                } else {
                    this.messages.push({ name: "Sam", message: data.answer });
                    this.updateChatText(chatbox);
                }
                textField.value = '';
            })
            .catch((error) => {
                console.error('Error:', error);
                this.messages.push({ name: "Sam", message: "Sorry, there was an error processing your request." });
                this.updateChatText(chatbox);
                textField.value = '';
            });
    }

    updateChatText(chatbox) {
        const html = this.messages.slice().reverse().map(item =>
            `<div class="messages__item messages__item--${item.name === "Sam" ? "visitor" : "operator"}">${item.message}</div>`
        ).join('');

        const chatmessage = chatbox.querySelector('.chatbox__messages');
        chatmessage.innerHTML = html;
    }

    addWelcomeMessage(chatbox) {
        if (this.messages.length === 0) { 
            this.messages.push({ name: "Sam", message: "Hello, Greetings from TVS Electronics!" });
            this.updateChatText(chatbox);
        }
    }
}

const chatbox = new Chatbox();
chatbox.display();