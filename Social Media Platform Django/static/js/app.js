(() => {
  const toast = document.getElementById('live-toast');
  let timer;
  function show(message) {
    toast.textContent = message; toast.hidden = false;
    clearTimeout(timer); timer = setTimeout(() => { toast.hidden = true; }, 6000);
  }
  document.querySelectorAll('[data-confirm]').forEach(form => form.addEventListener('submit', event => {
    if (!window.confirm(form.dataset.confirm)) event.preventDefault();
  }));
  document.querySelectorAll('[data-share]').forEach(button => button.addEventListener('click', async () => {
    try {
      if (navigator.share) await navigator.share({url: button.dataset.share, title: 'A story on Gather'});
      else { await navigator.clipboard.writeText(button.dataset.share); show('Post link copied. Privacy settings still apply.'); }
    } catch (error) { if (error.name !== 'AbortError') show('Copy this post’s browser address to share it.'); }
  }));
  const imageInput = document.getElementById('id_image');
  if (imageInput) imageInput.addEventListener('change', () => {
    if (imageInput.files[0]?.size > 5 * 1024 * 1024) { show('Choose an image smaller than 5 MB.'); imageInput.value = ''; }
  });
  let retry = 1000, socket, stopped = false, unseen = 0;
  function connect() {
    if (stopped) return;
    socket = new WebSocket((location.protocol === 'https:' ? 'wss:' : 'ws:') + '//' + location.host + '/ws/notifications/');
    socket.onopen = () => { retry = 1000; };
    socket.onmessage = event => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'notification') {
          show(data.message); unseen++;
          document.querySelectorAll('[data-unread]').forEach(el => {
            el.textContent = String(Number(el.dataset.initial || (el.dataset.initial = el.textContent)) + unseen);
          });
        }
      } catch (_) {}
    };
    socket.onclose = event => {
      if (event.code === 4401) { stopped = true; return; }
      setTimeout(connect, retry); retry = Math.min(retry * 2, 30000);
    };
  }
  window.addEventListener('pagehide', () => { stopped = true; if (socket) socket.close(); });
  connect();
})();