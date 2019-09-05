from django.shortcuts import get_object_or_404, get_list_or_404
from django.views import generic

from .models import Term, Definition, Sport


class IndexView(generic.ListView):
    model = Term
    context_object_name = 'terms'
    template_name = 'dictionary/index.html'
    paginate_by = 50


class SearchResultsView(generic.ListView):
    context_object_name = 'terms'
    template_name = 'dictionary/search.html'
    paginate_by = 50

    def get_queryset(self):
        search_key = self.request.GET.get('term')
        terms = Term.objects.filter(text__icontains=search_key)
        return terms

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_term'] = self.request.GET.get('term')
        context['results_count'] = context['paginator'].count
        return context


class SportIndexView(generic.ListView):
    context_object_name = 'terms'
    template_name = 'dictionary/sport_index.html'
    paginate_by = 50

    def get_queryset(self):
        sport_slug = self.kwargs['sport_slug']
        sport = get_object_or_404(Sport, slug=sport_slug)
        return Term.objects.filter(sport=sport)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sport_slug = self.kwargs['sport_slug']
        sport = get_object_or_404(Sport, slug=sport_slug)
        context['sport'] = sport
        return context


class TermDetailView(generic.DetailView):
    context_object_name = 'term'
    slug_url_kwarg = 'term_slug'
    template_name = 'dictionary/term_detail.html'

    def get_object(self):
        sport_slug = self.kwargs['sport_slug']
        term_slug = self.kwargs.get(self.slug_url_kwarg)

        sport = get_object_or_404(Sport, slug=sport_slug)
        term = get_object_or_404(Term, sport=sport, slug=term_slug)

        return term

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        definitions = Definition.approved_definitions.filter(term=self.object)
        context['definitions'] = definitions

        return context
