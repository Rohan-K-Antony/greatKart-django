from django.contrib import admin
from .models import product
# Register your models here.
class productAdmin(admin.ModelAdmin):
    list_display = ['product_name','price','stock','category','modified_date','is_available']
    prepopulated_fields ={'slug': ('product_name',)}
    list_filter=['category','is_available','price']
admin.site.register(product,productAdmin)