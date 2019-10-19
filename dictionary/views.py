from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.views import generic
from django.views.generic.list import MultipleObjectMixin
from django.views.decorators.http import require_POST

from .models import Term, Category, Definition, Sport, TermOfTheDay, Vote

try:
    from django.utils import simplejson as json
except ImportError:
    import json


def get_page_range_to_display_for_pagination(page_obj):
    display_left = display_right = 5

    current_page = page_obj.number
    last_page = page_obj.paginator.page_range.stop - 1

    if current_page <= display_left:
        display_left = current_page - 1
        display_right = display_right + (display_right - display_left)
    if current_page + display_right > last_page:
        left_over = display_right - (last_page - current_page)
        display_right = display_right - left_over

        pages_from_display_left_to_start = current_page - display_left - 1
        if pages_from_display_left_to_start >= left_over:
            display_left += left_over
        else:
            display_left += pages_from_display_left_to_start

    return range(current_page - display_left, current_page + display_right + 1)


class IndexView(generic.ListView):
    context_object_name = 'terms_of_the_day'
    template_name = 'dictionary/index.html'
    paginate_by = 20
    paginate_orphans = 5
    queryset = TermOfTheDay.terms.today_and_before()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        page_obj = context['page_obj']
        page_range_to_display = get_page_range_to_display_for_pagination(page_obj)
        context['page_range_to_display'] = page_range_to_display

        return context


class SearchResultsView(generic.ListView):
    context_object_name = 'terms'
    template_name = 'dictionary/search.html'
    paginate_by = 20
    paginate_orphans = 5

    def get_queryset(self):
        search_key = self.request.GET.get('term')
        terms = Term.approved_terms.select_related('sport').prefetch_related('categories').filter(text__icontains=search_key).annotate(Count('definitions'))
        return terms

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_term'] = self.request.GET.get('term')
        context['results_count'] = context['paginator'].count

        page_obj = context['page_obj']
        page_range_to_display = get_page_range_to_display_for_pagination(page_obj)
        context['page_range_to_display'] = page_range_to_display
        context['is_search_pagination'] = True

        return context


class SportIndexView(generic.ListView):
    context_object_name = 'terms'
    template_name = 'dictionary/sport_index.html'
    paginate_by = 20
    paginate_orphans = 5

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.categories_filtered_by = []

    def get_queryset(self):
        sport_slug = self.kwargs['sport_slug']
        self.sport = get_object_or_404(Sport, slug=sport_slug)

        category_list = self.request.GET.getlist('category')

        if not category_list:
            return Term.approved_terms.select_related('sport').prefetch_related('categories').filter(sport=self.sport).annotate(Count('definitions'))
        else:
            categories = []
            for category_name in category_list:
                category = get_object_or_404(Category, sport=self.sport, name=category_name)
                categories.append(category)
            self.categories_filtered_by = categories
            return Term.approved_terms.filter(sport=self.sport, categories__in=categories)\
                .annotate(num_catgories=Count('categories')).filter(num_catgories=len(categories))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['sport'] = self.sport
        context['categories'] = self.sport.categories.all()
        context['categories_filtered_by'] = self.categories_filtered_by

        page_obj = context['page_obj']
        page_range_to_display = get_page_range_to_display_for_pagination(page_obj)
        context['page_range_to_display'] = page_range_to_display

        return context


class TermDetailView(generic.DetailView, MultipleObjectMixin):
    context_object_name = 'term'
    slug_url_kwarg = 'term_slug'
    template_name = 'dictionary/term_detail.html'
    paginate_by = 15

    def get_object(self):
        sport_slug = self.kwargs['sport_slug']
        term_slug = self.kwargs.get(self.slug_url_kwarg)

        term = get_object_or_404(Term, sport__slug=sport_slug, slug=term_slug)

        return term

    def get_context_data(self, **kwargs):
        definitions = Definition.approved_definitions.filter(term=self.object).order_by('-net_votes')
        context = super(TermDetailView, self).get_context_data(object_list=definitions, **kwargs)
        return context


def random_term(request):
    term = Term.approved_terms.random()
    return redirect(term)


@login_required
@require_POST
def upvote(request, definition_pk):
    user = request.user
    definition = Definition.objects.get(pk=definition_pk)

    if definition.votes.filter(user=user).filter(vote_type=Vote.UPVOTE).exists():
        definition.delete_upvote(user)
    else:
        definition.upvote(user)

    response = {
        'net_votes': definition.net_votes,
    }

    return HttpResponse(json.dumps(response), content_type='application/json')


@login_required
@require_POST
def downvote(request, definition_pk):
    user = request.user
    definition = Definition.objects.get(pk=definition_pk)

    if definition.votes.filter(user=user).filter(vote_type=Vote.DOWNVOTE).exists():
        definition.delete_downvote(user)
    else:
        definition.downvote(user)

    response = {
        'net_votes': definition.net_votes,
    }

    return HttpResponse(json.dumps(response), content_type='application/json')
