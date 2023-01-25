from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Account
# Register your models here.

class AccountAdmin(UserAdmin):
    list_filter =()
    filter_horizontal=()
    fieldsets=()
    list_display = ['email','first_name','last_name','username','last_login','is_active','date_joined']
    list_display_links =['email','first_name','username','last_name']
    readonly_fields = ['last_login','date_joined']
    ordering = ['-date_joined',]

admin.site.register(Account,AccountAdmin)
