// ReFind Global Interactive Helper
document.addEventListener('DOMContentLoaded', () => {
    // Re-initialize icons whenever HTMX swaps new content
    document.body.addEventListener('htmx:afterSwap', () => {
        if (window.lucide) {
            window.lucide.createIcons();
        }
    });

    // Auto-dismiss alerts after 6 seconds
    setTimeout(() => {
        const alerts = document.querySelectorAll('[role="alert"]');
        alerts.forEach(alert => {
            alert.style.transition = 'opacity 0.5s ease-out';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        });
    }, 6000);
});
