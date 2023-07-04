from django.contrib import admin

# Register your models here.
from .models import Conta, Categoria

# class AdminConta(admin.ModelAdmin):
    
# class AdminConta(admin.ModelAdmin):

admin.site.register(Conta)
admin.site.register(Categoria)

