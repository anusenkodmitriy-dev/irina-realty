from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.db.models import Q
from decimal import Decimal
from .models import Property, Favorite, Review
from .forms import UserRegistrationForm  # новая форма

def index(request):
    """Главная страница"""
    latest_properties = Property.objects.filter(is_active=True).order_by('-created_at')[:6]
    popular_properties = Property.objects.filter(is_active=True).order_by('-views_count')[:6]
    reviews = Review.objects.filter(is_active=True)[:10]

    if request.user.is_authenticated:
        favorites = list(Favorite.objects.filter(user=request.user).values_list('property_id', flat=True))
    else:
        favorites = request.session.get('favorites', [])

    return render(request, 'realty/index.html', {
        'properties': latest_properties,
        'popular_properties': popular_properties,
        'reviews': reviews,
        'favorites': favorites,
    })

def catalog(request):
    """Каталог всех объектов с фильтрацией и пагинацией"""
    properties = Property.objects.filter(is_active=True)

    q = request.GET.get('q')
    if q:
        properties = properties.filter(Q(title__icontains=q) | Q(address__icontains=q))

    price_min = request.GET.get('price_min')
    if price_min:
        properties = properties.filter(price__gte=price_min)
    price_max = request.GET.get('price_max')
    if price_max:
        properties = properties.filter(price__lte=price_max)

    selected_rooms = request.GET.getlist('rooms')
    if selected_rooms:
        rooms_int = [int(r) for r in selected_rooms if r.isdigit()]
        if rooms_int:
            properties = properties.filter(rooms__in=rooms_int)

    area_min = request.GET.get('area_min')
    if area_min:
        properties = properties.filter(area__gte=area_min)
    area_max = request.GET.get('area_max')
    if area_max:
        properties = properties.filter(area__lte=area_max)

    sort = request.GET.get('sort')
    if sort == 'price_asc':
        properties = properties.order_by('price')
    elif sort == 'price_desc':
        properties = properties.order_by('-price')
    elif sort == 'date_desc':
        properties = properties.order_by('-created_at')
    elif sort == 'date_asc':
        properties = properties.order_by('created_at')
    else:
        properties = properties.order_by('-created_at')

    paginator = Paginator(properties, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.user.is_authenticated:
        favorites = list(Favorite.objects.filter(user=request.user).values_list('property_id', flat=True))
    else:
        favorites = request.session.get('favorites', [])

    return render(request, 'realty/catalog.html', {
        'page_obj': page_obj,
        'selected_rooms': selected_rooms,
        'favorites': favorites,
    })

def property_detail(request, property_id):
    """Детальная страница объекта"""
    property_obj = get_object_or_404(Property, id=property_id, is_active=True)
    property_obj.views_count += 1
    property_obj.save(update_fields=['views_count'])

    current_price = property_obj.price
    similar_properties = Property.objects.filter(
        is_active=True,
        price__range=(current_price * Decimal('0.8'), current_price * Decimal('1.2'))
    ).exclude(id=property_obj.id)[:4]

    if request.user.is_authenticated:
        favorites = list(Favorite.objects.filter(user=request.user).values_list('property_id', flat=True))
    else:
        favorites = request.session.get('favorites', [])

    return render(request, 'realty/property_detail.html', {
        'property': property_obj,
        'similar_properties': similar_properties,
        'favorites': favorites,
    })

def about(request):
    """Страница 'О риелторе'"""
    return render(request, 'realty/about.html')

@require_POST
def toggle_favorite(request, property_id):
    property_obj = get_object_or_404(Property, id=property_id)
    if request.user.is_authenticated:
        fav, created = Favorite.objects.get_or_create(user=request.user, property=property_obj)
        if not created:
            fav.delete()
            status = 'removed'
        else:
            status = 'added'
        favorites = list(Favorite.objects.filter(user=request.user).values_list('property_id', flat=True))
    else:
        favs = request.session.get('favorites', [])
        if property_id in favs:
            favs.remove(property_id)
            status = 'removed'
        else:
            favs.append(property_id)
            status = 'added'
        request.session['favorites'] = favs
        favorites = favs
    return JsonResponse({'status': status, 'favorites': favorites})

def favorites_list(request):
    if request.user.is_authenticated:
        favs = Favorite.objects.filter(user=request.user).select_related('property')
        properties = [fav.property for fav in favs]
    else:
        fav_ids = request.session.get('favorites', [])
        properties = Property.objects.filter(id__in=fav_ids, is_active=True)

    sort = request.GET.get('sort')
    if sort == 'price_asc':
        properties = sorted(properties, key=lambda p: p.price)
    elif sort == 'price_desc':
        properties = sorted(properties, key=lambda p: p.price, reverse=True)
    elif sort == 'date_asc':
        properties = sorted(properties, key=lambda p: p.created_at)
    elif sort == 'date_desc':
        properties = sorted(properties, key=lambda p: p.created_at, reverse=True)

    return render(request, 'realty/favorites.html', {'properties': properties})

# Новая регистрация с телефоном
class RegisterView(CreateView):
    form_class = UserRegistrationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')

@require_POST
def increment_call(request, property_id):
    property_obj = get_object_or_404(Property, id=property_id)
    property_obj.calls_count += 1
    property_obj.save(update_fields=['calls_count'])
    return JsonResponse({'status': 'ok', 'calls': property_obj.calls_count})