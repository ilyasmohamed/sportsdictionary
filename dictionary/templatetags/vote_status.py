from django import template

from dictionary.models import Vote

register = template.Library()


@register.filter(name='vote_status')
def vote_status(definition, user):
    if not user.is_authenticated:
        return 'Not voted on'

    vote = definition.votes.filter(user=user)
    if not vote.exists():
        return 'Not voted on'
    else:
        return f'{vote[0].get_vote_type_display()}d'
