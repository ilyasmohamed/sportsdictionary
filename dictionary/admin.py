from django.contrib import admin
from django import forms
from .models import Term, Sport, Definition, Vote


# region Sport
class SportAdminForm(forms.ModelForm):
    class Meta:
        model = Sport
        fields = ['name', 'slug']


@admin.register(Sport)
class SportAdmin(admin.ModelAdmin):
    form = SportAdminForm
    list_display = ['name', 'slug']
    readonly_fields = ['slug']
# endregion


# region Term
class DefinitionInline(admin.TabularInline):
    model = Definition
    extra = 0


class TermAdminForm(forms.ModelForm):
    class Meta:
        model = Term
        fields = ['text', 'slug', 'sport', 'user', 'approvedFl']


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    form = TermAdminForm
    list_display = ['text', 'slug', 'sport', 'created', 'last_updated', 'approvedFl']
    list_filter = ('sport', 'created', 'approvedFl')
    inlines = [DefinitionInline]
    readonly_fields = ['slug']
# endregion


# region Definition
class DefinitionAdminForm(forms.ModelForm):
    class Meta:
        model = Definition
        fields = ['term', 'text', 'user', 'approvedFl']


@admin.register(Definition)
class DefinitionAdmin(admin.ModelAdmin):
    form = DefinitionAdminForm
    list_display = ['text', 'created',  'updated', 'approvedFl']
    list_filter = ('created', 'approvedFl')
# endregion


# region Vote
class VoteAdminForm(forms.ModelForm):
    class Meta:
        model = Vote
        fields = ['user', 'definition', 'downvote']


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    # form = VoteAdminForm
    list_display = ['created', 'downvote']
    # readonly_fields = ['created', 'downvote']
# endregion
