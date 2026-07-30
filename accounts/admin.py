from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserProfile
from .forms import CustomUserCreationForm, CustomUserChangeForm

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['username', 'email', 'currency', 'monthly_savings_target', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        ('Financial Settings', {'fields': ('currency', 'monthly_savings_target')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Financial Settings', {'fields': ('currency', 'monthly_savings_target')}),
    )

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'occupation', 'phone_number']
    search_fields = ['user__username', 'occupation']

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
