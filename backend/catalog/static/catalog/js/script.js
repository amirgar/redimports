window.addEventListener('DOMContentLoaded', () => {
    const tg = window.Telegram.WebApp;
    tg.ready();
    tg.expand();

    // Отключаем закрытие свайпом вниз, чтобы работал внутренний скролл
    if (tg.isVersionAtLeast('7.7')) {
        tg.disableVerticalSwipes();
    }

    tg.setHeaderColor('#FFFFFF');
});