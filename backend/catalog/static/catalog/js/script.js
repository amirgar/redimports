const tg = window.Telegram.WebApp;

tg.ready();
tg.expand();
tg.enableClosingConfirmation();

tg.setHeaderColor('#ffffff');
tg.setBackgroundColor('#ffffff');

document.body.addEventListener('touchmove', function (e) {
    if (window.scrollY === 0) {
        e.preventDefault();
    }
}, { passive: false });
