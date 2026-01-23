const tg = window.Telegram.WebApp;

tg.ready();
tg.expand();
tg.enableClosingConfirmation();

tg.setHeaderColor('#F2F2F2');
tg.setBackgroundColor('#F2F2F2');

document.body.addEventListener('touchmove', function (e) {
    if (window.scrollY === 0) {
        e.preventDefault();
    }
}, { passive: false });
