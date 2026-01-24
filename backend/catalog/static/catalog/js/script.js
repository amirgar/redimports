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

document.addEventListener('DOMContentLoaded', () => {

    document.querySelectorAll('.product-image-container').forEach(container => {
        const images = Array.from(container.querySelectorAll('.product-img'));
        const dots = Array.from(container.querySelectorAll('.dot'));

        if (images.length <= 1) return;

        let index = 0;
        let startX = 0;

        container.addEventListener('touchstart', e => {
            startX = e.touches[0].clientX;
        });

        container.addEventListener('touchend', e => {
            const endX = e.changedTouches[0].clientX;
            const diff = startX - endX;

            if (Math.abs(diff) < 40) return;

            images[index].classList.remove('active');
            dots[index]?.classList.remove('active');

            if (diff > 0) {
                index = (index + 1) % images.length;
            } else {
                index = (index - 1 + images.length) % images.length;
            }

            images[index].classList.add('active');
            dots[index]?.classList.add('active');
        });
    });

});
