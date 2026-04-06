from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Property(models.Model):
    title = models.CharField('Название', max_length=200)
    address = models.CharField('Адрес', max_length=300)
    price = models.DecimalField('Цена', max_digits=12, decimal_places=2)
    rooms = models.PositiveSmallIntegerField('Количество комнат')
    area = models.DecimalField('Площадь (м²)', max_digits=6, decimal_places=1)
    description = models.TextField('Описание')
    latitude = models.FloatField('Широта', blank=True, null=True)
    longitude = models.FloatField('Долгота', blank=True, null=True)
    main_image = models.ImageField('Главное фото', upload_to='properties/', blank=True, null=True)
    is_active = models.BooleanField('Активно', default=True)
    created_at = models.DateTimeField('Дата добавления', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    views_count = models.PositiveIntegerField('Просмотры', default=0, editable=False)
    calls_count = models.PositiveIntegerField('Звонки', default=0, editable=False)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Объект недвижимости'
        verbose_name_plural = 'Объекты недвижимости'

class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField('Фото', upload_to='properties/')
    order = models.PositiveIntegerField('Порядок', default=0)

    class Meta:
        ordering = ['order']
        verbose_name = 'Фото объекта'
        verbose_name_plural = 'Фото объектов'

    def __str__(self):
        return f"Фото для {self.property.title}"

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'property')
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'

    def __str__(self):
        return f'{self.user.username} - {self.property.title}'

class Review(models.Model):
    name = models.CharField('Имя клиента', max_length=100)
    text = models.TextField('Текст отзыва')
    photo = models.ImageField('Фото клиента', upload_to='reviews/', blank=True, null=True)
    rating = models.PositiveSmallIntegerField(
        'Оценка', 
        default=5,
        choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')]
    )
    is_active = models.BooleanField('Активно', default=True)
    created_at = models.DateTimeField('Дата добавления', auto_now_add=True)

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} - {self.rating}★'

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField('Телефон', max_length=20, blank=True, help_text='В формате +7XXXXXXXXXX')

    def __str__(self):
        return f'{self.user.username} - {self.phone}'

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

# Сигналы для автоматического создания профиля при создании пользователя
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()