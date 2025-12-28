function generateSlug(text, maxLength = 50) {
    return text
        .toLowerCase()
        .replace(/[^a-z0-9\s-]/g, '')
        .replace(/\s+/g, '-')
        .replace(/-+/g, '-')
        .replace(/^-|-$/g, '')
        .substring(0, maxLength);
}

function initDropdowns() {
    document.addEventListener('click', function (e) {
        if (e.target.classList.contains('dropdown-trigger') || e.target.closest('.dropdown-trigger')) {
            e.preventDefault();
            const dropdown = e.target.closest('.dropdown');
            const content = dropdown.querySelector('.dropdown-content');

            document.querySelectorAll('.dropdown-content').forEach(function (dc) {
                if (dc !== content) {
                    dc.classList.remove('show');
                }
            });

            content.classList.toggle('show');
        } else if (!e.target.closest('.dropdown')) {
            document.querySelectorAll('.dropdown-content').forEach(function (dc) {
                dc.classList.remove('show');
            });
        }
    });
}

function showErrorMessage(message) {
    const existingMessages = document.querySelector('.form-messages');
    if (existingMessages) {
        existingMessages.remove();
    }

    const messagesDiv = document.createElement('div');
    messagesDiv.className = 'form-messages';
    messagesDiv.innerHTML = `
        <div class="form-message error">
            <span class="message-icon">⚠️</span>
            <span class="message-text">${message}</span>
        </div>
    `;

    const settingsMain = document.querySelector('.settings-main');
    settingsMain.insertBefore(messagesDiv, settingsMain.firstChild);
    messagesDiv.scrollIntoView({ behavior: 'smooth' });
}