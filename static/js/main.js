function showNotification(message, type = 'info') {
    const container = document.getElementById('notifications');
    if (!container) return;
    const notice = document.createElement('div');
    notice.className = 'notification notification-' + type;
    notice.textContent = message;
    notice.style.background = type === 'error' ? '#e31937' : '#2ecc71';
    notice.style.color = '#fff';
    notice.style.padding = '1rem';
    notice.style.marginBottom = '10px';
    notice.style.borderRadius = '8px';
    container.appendChild(notice);
    setTimeout(() => notice.remove(), 4000);
}