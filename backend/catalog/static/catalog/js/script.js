const tg = window.Telegram.WebApp;
tg.ready();
tg.expand();
const overflow = 100; // запас
document.body.style.overflow = 'hidden';
document.body.style.height = window.innerHeight + 'px';
document.documentElement.style.height = window.innerHeight + 'px';
tg.setHeaderColor('#F2F2F2');
tg.setBackgroundColor('#F2F2F2');
window.visualViewport.addEventListener('resize', () => {
    document.querySelector('.app-container').style.height = window.innerHeight + 'px';
});