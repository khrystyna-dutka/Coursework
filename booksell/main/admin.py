from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelChoiceField, ModelForm
from django.utils.safestring import mark_safe
from .models import *
from PIL import Image

class HintAdminForm(ModelForm):
    RESULUTION = (3, 2.7)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slug'].help_text = mark_safe('<span style="color: red; font-size: 12px; font-weight: 600;">*Вкажіть назву книги ОДНИМ словом на англійській мові')
        self.fields['image'].help_text = mark_safe('<span style="color: red; font-size: 12px; font-weight: 600;">*Будь ласка, завантажуйте зображення у вертикальному форматі (розмір площини зображення {}x{})'.format(*self.RESULUTION))

    def clean_image(self):
        image = self.cleaned_data['image']
        img = Image.open(image)
        max_height, max_width = Product.MAX_RESULUTION
        if img.height > max_height or img.width > max_width:
            raise ValidationError('Зображення занадто велике! Замініть його, будь ласка')
        if image.size > Product.MAX_SIZE:
            raise ValidationError('Розмір файла не має перевищувати 5Мб')
        return image

class EducationalAdmin(admin.ModelAdmin):
    form = HintAdminForm

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            return ModelChoiceField(Category.objects.filter(slug='educational'))

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class FictionAdmin(admin.ModelAdmin):
    form = HintAdminForm

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            return ModelChoiceField(Category.objects.filter(slug='fiction'))

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class ChildrenAdmin(admin.ModelAdmin):
    form = HintAdminForm

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            return ModelChoiceField(Category.objects.filter(slug='children'))

        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(Category)
admin.site.register(Educational, EducationalAdmin)
admin.site.register(Fiction, FictionAdmin)
admin.site.register(Children, ChildrenAdmin)
admin.site.register(CartProduct)
admin.site.register(Cart)
admin.site.register(Customer)
admin.site.register(Order)
