const tg = window.Telegram.WebApp;
tg.ready();
tg.expand();

// Фиксируем высоту, чтобы клавиатура не поднимала весь интерфейс
const overflow = 100; // запас
document.body.style.overflow = 'hidden';
document.body.style.height = window.innerHeight + 'px';
document.documentElement.style.height = window.innerHeight + 'px';

// Настройка цветов
tg.setHeaderColor('#F2F2F2');
tg.setBackgroundColor('#F2F2F2');

// Обработка клавиатуры для Android/iOS
window.visualViewport.addEventListener('resize', () => {
    // При открытии клавиатуры мы не даем app-container уменьшаться
    document.querySelector('.app-container').style.height = window.innerHeight + 'px';
});