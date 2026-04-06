from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import Favorite, Property

@receiver(user_logged_in)
def transfer_session_favorites(sender, request, user, **kwargs):
    session_favorites = request.session.get('favorites', [])
    if session_favorites:
        for prop_id in session_favorites:
            try:
                property_obj = Property.objects.get(id=prop_id)
                Favorite.objects.get_or_create(user=user, property=property_obj)
            except Property.DoesNotExist:
                pass
        # Очищаем сессию, чтобы не оставалось дублей
        request.session['favorites'] = []