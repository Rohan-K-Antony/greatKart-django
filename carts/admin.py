from django.contrib import admin
from .models import Cart,CartItem
# Register your models here.
admin.site.register(Cart)

class cartItemAdmin(admin.ModelAdmin):
    list_display = ['product','user']
admin.site.register(CartItem,cartItemAdmin)