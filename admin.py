from django.contrib import admin
from .models import Property, Favorite, PropertyImage, Review
from .models import Profile

admin.site.register(Profile)

class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1
    fields = ['image', 'order']

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'address', 'price', 'rooms', 'is_active')
    list_filter = ('is_active', 'rooms')
    search_fields = ('title', 'address')
    inlines = [PropertyImageInline]

admin.site.register(Favorite)
admin.site.register(Review)  # добавляем регистрацию отзывов