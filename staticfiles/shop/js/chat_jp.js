const chatWin = document.getElementById('chatbot-window');
const header = document.getElementById('chatbot-header');
let isMoving = false, offsetX = 0, offsetY = 0, fixedSide = null;

// Drag
header.onmousedown = function(e) {
  isMoving = true;
  offsetX = e.clientX - chatWin.offsetLeft;
  offsetY = e.clientY - chatWin.offsetTop;
  document.body.style.userSelect = "none";
};
window.onmouseup = function() { isMoving = false; document.body.style.userSelect = ""; };
window.onmousemove = function(e) {
  if (isMoving && !fixedSide) {
    chatWin.style.left = (e.clientX - offsetX) + "px";
    chatWin.style.top = (e.clientY - offsetY) + "px";
    chatWin.style.right = "";
    chatWin.style.bottom = "";
    chatWin.style.position = "fixed";
  }
};
// Fix to side
function toggleFix() {
  if (!fixedSide) {
    chatWin.style.right = "0"; chatWin.style.bottom = "0";
    chatWin.style.left = ""; chatWin.style.top = "";
    fixedSide = true;
  } else {
    fixedSide = false;
  }
}
// Minimize/Close
function minimizeChat() { chatWin.style.display = "none"; }
function closeChat() { chatWin.style.display = "none"; }
// Відправка повідомлення
function sendChatMsg(e) {
  e.preventDefault();
  // ... AJAX тут
}
