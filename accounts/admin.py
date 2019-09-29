from django import forms
from django.contrib import admin

from .models import Profile


# region Profile
class ProfileAdminForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['user', 'email_confirmed', 'favourite_sport', 'show_favourite_sport']


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    form = ProfileAdminForm
    list_display = ['user', 'email_confirmed', 'favourite_sport', 'show_favourite_sport']
    readonly_fields = ['user', 'email_confirmed',]
# endregion
