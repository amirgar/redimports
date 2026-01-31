from .models import SiteSettings

def site_settings(request):
    # Возвращаем словарь, который будет подмешиваться во все шаблоны
    return {
        'site_settings': SiteSettings.objects.first()
    }