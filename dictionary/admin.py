from django.contrib import admin
from django import forms
from .models import Term, SuggestedTerm, Sport, Definition, Vote


# region admin config
admin.site.site_title = 'Sports Dictionary Admin'
admin.site.site_header = 'Sports Dictionary Administration'
# endregion


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
    list_display = ['text', 'slug', 'sport', 'created', 'last_updated', 'approvedFl', 'num_approved_definitions']
    list_filter = ('sport', 'created', 'approvedFl')
    inlines = [DefinitionInline]
    readonly_fields = ['slug']
    search_fields = ['text']
# endregion


# region SuggestedTerm
class SuggestedTermAdminForm(forms.ModelForm):
    class Meta:
        model = SuggestedTerm
        fields = ['text', 'definitionText', 'example_usage', 'review_status', 'sport', 'user']


@admin.register(SuggestedTerm)
class SuggestedTermAdmin(admin.ModelAdmin):
    form = SuggestedTermAdminForm
    list_display = ['text', 'sport', 'review_status', 'created', 'last_updated']
    list_filter = ('review_status',)
# endregion


# region Definition
class DefinitionAdminForm(forms.ModelForm):
    class Meta:
        model = Definition
        fields = ['term', 'text', 'example_usage', 'user', 'approvedFl']


@admin.register(Definition)
class DefinitionAdmin(admin.ModelAdmin):
    form = DefinitionAdminForm
    list_display = ['text', 'created',  'last_updated', 'approvedFl', 'num_upvotes', 'num_downvotes', 'net_votes']
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
