from django.contrib import admin
from .models import Payment,Order,OrderProduct
# Register your models here.

class orderProductInline(admin.TabularInline):
    model = OrderProduct
    extra = 0
    readonly_fields = ('payment', 'user', 'product', 'quantity', 'product_price', 'ordered')


class orderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'full_name', 'phone', 'email', 'city', 'order_total', 'status', 'is_ordered', 'created_at']
    list_filter = ['status', 'is_ordered']
    search_fields = ['order_number', 'first_name', 'last_name', 'phone', 'email']
    list_per_page = 20
    inlines = [orderProductInline]

class orderProductAdmin(admin.ModelAdmin):
    list_display = ['order','product']
admin.site.register(Payment)
admin.site.register(Order,orderAdmin)
admin.site.register(OrderProduct,orderProductAdmin)
