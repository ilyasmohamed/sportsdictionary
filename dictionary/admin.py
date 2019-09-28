from django.contrib import admin
from django import forms
from .models import Profile, Term, Category, SuggestedTerm, Sport, Definition, Vote


# region admin config
admin.site.site_title = 'Sports Dictionary Admin'
admin.site.site_header = 'Sports Dictionary Administration'
# endregion


# region Profile
class ProfileAdminForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['user',]


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    form = ProfileAdminForm
    list_display = ['user']
    readonly_fields = ['user']
# endregion


# region Sport
class SportAdminForm(forms.ModelForm):
    class Meta:
        model = Sport
        fields = ['name', 'slug', 'emoji', 'active']


@admin.register(Sport)
class SportAdmin(admin.ModelAdmin):
    form = SportAdminForm
    list_display = ['name', 'slug', 'emoji', 'active']
    list_editable = ('emoji', 'active')
    readonly_fields = ['slug']
# endregion


# region Term
class DefinitionInline(admin.TabularInline):
    model = Definition
    extra = 0


class TermAdminForm(forms.ModelForm):
    class Meta:
        model = Term
        fields = ['text', 'slug', 'sport', 'categories', 'user', 'approvedFl']

    def __init__(self, *args, **kwargs):
        super(TermAdminForm, self).__init__(*args, **kwargs)
        if 'instance' in kwargs and kwargs['instance']:
            sport = kwargs['instance'].sport
            self.fields['categories'].queryset = Category.objects.filter(sport=sport)


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
        fields = ['user', 'definition', 'vote_type']


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    # form = VoteAdminForm
    list_display = ['created', 'vote_type']
# endregion


# region Category
class CategoryAdminForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'sport']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    form = CategoryAdminForm
    list_display = ['name', 'sport']
# endregion
