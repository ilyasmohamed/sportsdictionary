from django.shortcuts import render
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404, render
from django.views import generic
from .models import Term, Definition, Sport


class IndexView(generic.ListView):
    model = Term
    context_object_name = 'terms'
    template_name = 'dictionary/index.html'
    paginate_by = 50


class SportIndexView(generic.ListView):
    context_object_name = 'terms'
    template_name = 'dictionary/sport_index.html'
    paginate_by = 50

    def get_queryset(self):
        sport_slug = self.kwargs['sport_slug']
        sport = get_object_or_404(Sport, slug=sport_slug)
        return Term.objects.filter(sport=sport)


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
