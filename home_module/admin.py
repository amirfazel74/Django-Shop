# admin.py
from django.contrib import admin
from .models import Slider


@admin.register(Slider)
class SliderAdmin(admin.ModelAdmin):
    list_display = ('title', 'badge_text', 'is_active', 'order')
    list_editable = ('is_active', 'order')


from django.contrib import admin

# Register your models here.

