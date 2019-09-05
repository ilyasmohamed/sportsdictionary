from django.urls import path

from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('search/', views.SearchResultsView.as_view(), name='term_search'),
    path('<slug:sport_slug>/', views.SportIndexView.as_view(), name='sport_index'),
    path('<slug:sport_slug>/<slug:term_slug>', views.TermDetailView.as_view(), name='term_detail'),
]

# urlpatterns += (
#     # urls for Term
#     path('dictionary/term/', views.TermListView.as_view(), name='dictionary_term_list'),
#     path('dictionary/term/create/', views.TermCreateView.as_view(), name='dictionary_term_create'),
#     path('dictionary/term/detail/<slug:slug>/', views.TermDetailView.as_view(), name='dictionary_term_detail'),
#     path('dictionary/term/update/<slug:slug>/', views.TermUpdateView.as_view(), name='dictionary_term_update'),
# )
#
# urlpatterns += (
#     # urls for Sport
#     path('dictionary/sport/', views.SportListView.as_view(), name='dictionary_sport_list'),
#     path('dictionary/sport/create/', views.SportCreateView.as_view(), name='dictionary_sport_create'),
#     path('dictionary/sport/detail/<slug:slug>/', views.SportDetailView.as_view(), name='dictionary_sport_detail'),
#     path('dictionary/sport/update/<slug:slug>/', views.SportUpdateView.as_view(), name='dictionary_sport_update'),
# )
#
# urlpatterns += (
#     # urls for Definition
#     path('dictionary/definition/', views.DefinitionListView.as_view(), name='dictionary_definition_list'),
#     path('dictionary/definition/create/', views.DefinitionCreateView.as_view(), name='dictionary_definition_create'),
#     path('dictionary/definition/detail/<int:pk>/', views.DefinitionDetailView.as_view(), name='dictionary_definition_detail'),
#     path('dictionary/definition/update/<int:pk>/', views.DefinitionUpdateView.as_view(), name='dictionary_definition_update'),
# )
#
# urlpatterns += (
#     # urls for Vote
#     path('dictionary/vote/', views.VoteListView.as_view(), name='dictionary_vote_list'),
#     path('dictionary/vote/create/', views.VoteCreateView.as_view(), name='dictionary_vote_create'),
#     path('dictionary/vote/detail/<int:pk>/', views.VoteDetailView.as_view(), name='dictionary_vote_detail'),
#     path('dictionary/vote/update/<int:pk>/', views.VoteUpdateView.as_view(), name='dictionary_vote_update'),
# )
