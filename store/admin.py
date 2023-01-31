from django.contrib import admin
from .models import product,Variation
# Register your models here.
class productAdmin(admin.ModelAdmin):
    list_display = ['product_name','price','stock','category','modified_date','is_available']
    prepopulated_fields ={'slug': ('product_name',)}
    list_filter=['category','is_available','price']
admin.site.register(product,productAdmin)

class productVariationAdmin(admin.ModelAdmin):
    list_display=['product','variation_category','variation_value','is_active']
    list_editable=['is_active',]
    list_filter = ['product']
admin.site.register(Variation,productVariationAdmin)