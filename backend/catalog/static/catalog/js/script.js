const tg = window.Telegram.WebApp;

tg.ready();
tg.expand();

// Фиксируем высоту при старте, чтобы она не менялась при открытии клавиатуры
const doc = document.documentElement;
doc.style.setProperty('--app-height', `${window.innerHeight}px`);

// В CSS добавь для .app-container: height: var(--app-height);
document.querySelector('.app-container').style.height = `${window.innerHeight}px`;

tg.setHeaderColor('#F2F2F2');
tg.setBackgroundColor('#F2F2F2');

// Блокируем стандартный свайп Telegram "вниз для закрытия", если мы скроллим контент
let ts;
document.querySelector('.scrollable-content').addEventListener('touchstart', function (e) {
    ts = e.touches[0].clientY;
}, {passive: false});

document.querySelector('.scrollable-content').addEventListener('touchmove', function (e) {
    let te = e.touches[0].clientY;
    if (this.scrollTop === 0 && te > ts) {
        // Если мы в самом верху и тянем вниз - не даем закрыть приложение сразу
    }
}, {passive: false});