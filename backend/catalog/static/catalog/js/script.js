const tg = window.Telegram.WebApp;
tg.ready();
tg.expand();

// Принудительно отключаем вертикальный свайп для закрытия Mini App
tg.isVerticalSwipesEnabled = false; 

// Устанавливаем цвета
tg.setHeaderColor('#F2F2F2');
tg.setBackgroundColor('#F2F2F2');

// Фикс для клавиатуры: предотвращаем изменение высоты viewport
if (window.visualViewport) {
    window.visualViewport.addEventListener('resize', () => {
        // Оставляем высоту контейнера неизменной
        document.querySelector('.app-container').style.height = window.innerHeight + 'px';
    });
}

// Запрещаем прокрутку всего документа (оставляем только для .scrollable-content)
document.addEventListener('touchmove', function (e) {
    if (!e.target.closest('.scrollable-content')) {
        e.preventDefault();
    }
}, { passive: false });