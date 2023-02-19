from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Account,UserProfile
from django.utils.html import format_html
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

class UserProfileAdmin(admin.ModelAdmin):
    def thumbnail(self,object):
        return format_html(f"<img src={object.profile_picture.url} width=40 style ='border-radius : 50px'></img>")
    thumbnail.short_description = "Photo"
    list_display =['thumbnail','user','address_line_1','address_line_2']

admin.site.register(UserProfile,UserProfileAdmin)