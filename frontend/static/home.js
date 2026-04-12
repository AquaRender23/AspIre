function toggleChat(){

let chatbox = document.getElementById("chatbox");

if(chatbox.style.display === "block"){
chatbox.style.display = "none";
}
else{
chatbox.style.display = "block";
}

}

function toggleProfile(){
var box = document.getElementById("profile-popup");
if(box.style.display === "block"){
box.style.display = "none";
}
else{
box.style.display = "block";
}}

function sendMessage(){

let message = document.getElementById("chat-input").value;
let chat = document.getElementById("chat-messages");

// show user message
let userMsg = document.createElement("div");
userMsg.className = "user-msg";
userMsg.innerText = "You: " + message;
chat.appendChild(userMsg);
chat.scrollTop = chat.scrollHeight;
fetch("/chatbot", {
method: "POST",
headers: {
"Content-Type": "application/json"
},
body: JSON.stringify({message: message})
})
.then(res => res.json())
.then(data => {

let aiMsg = document.createElement("div");
aiMsg.className = "ai-msg";
aiMsg.innerText = "Aspira: " + data.reply;

chat.appendChild(aiMsg);
chat.scrollTop = chat.scrollHeight;
});

document.getElementById("chat-input").value = "";

}