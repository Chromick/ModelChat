const $room = document.getElementById('room');
const $username = document.getElementById('username');
const $messages = document.getElementById('messages');
const $form = document.getElementById('form');
const $input = document.getElementById('input');
const $connectBtn = document.getElementById('connectBtn');

$room.value = localStorage.getItem('room') || 'geral';
$username.value = localStorage.getItem('username') || '';

let ws = null;

function appendMessage(item) {
  const div = document.createElement('div');
  div.className = 'msg';
  const when = new Date(item.created_at).toLocaleTimeString();
  div.innerHTML =
    `<div class="meta">[${when}] <strong>${item.username}</strong> em <em>${item.room}</em></div>` +
    `<div>${item.content}</div>`;
  $messages.appendChild(div);
  $messages.scrollTop = $messages.scrollHeight;
}

function appendHistory(items) {
  $messages.innerHTML = '';
  items.forEach(appendMessage);
}

function connect() {
  const room = ($room.value || 'geral').trim();
  const username = ($username.value || 'anon').trim();
  if (!room) return alert('Informe a sala');
  if (!username) return alert('Informe o nome');

  localStorage.setItem('room', room);
  localStorage.setItem('username', username);

  const wsProto = location.protocol === 'https:' ? 'wss' : 'ws';
  const url = `${wsProto}://${location.host}/ws/${encodeURIComponent(room)}`;
  ws = new WebSocket(url);

  ws.onmessage = (evt) => {
    const data = JSON.parse(evt.data);
    if (data.type === 'history') {
      appendHistory(data.items || []);
    } else if (data.type === 'message') {
      appendMessage(data.item);
    }
  };

  ws.onopen = () => console.log('WS conectado');
  ws.onclose = () => console.log('WS desconectado');
  ws.onerror = (e) => console.error('WS erro', e);
}

$connectBtn.addEventListener('click', () => {
  if (ws) ws.close();
  connect();
});

$form.addEventListener('submit', (e) => {
  e.preventDefault();
  const content = $input.value.trim();
  if (!content || !ws || ws.readyState !== WebSocket.OPEN) return;
  ws.send(JSON.stringify({ content, username: $username.value }));
  $input.value = '';
});
