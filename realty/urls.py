from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('catalog/', views.catalog, name='catalog'),
    path('property/<int:property_id>/', views.property_detail, name='property_detail'),
    path('about/', views.about, name='about'),
    path('toggle-favorite/<int:property_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('favorites/', views.favorites_list, name='favorites'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('increment-call/<int:property_id>/', views.increment_call, name='increment_call'),
]