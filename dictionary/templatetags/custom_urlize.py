import re

from django import template
from django.core.exceptions import ObjectDoesNotExist
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
from django.utils.html import escape

from dictionary.models import Sport, Term

register = template.Library()


word_split_re = re.compile(r'[ \t]+(?![^\[]*\])')


@register.filter(name='customUrlize')
@stringfilter
def custom_urlize(value, sport_arg):
    value = value.replace('\r', ' \r')
    value = value.replace('\n', '\n ')
    words = word_split_re.split(escape(value))

    p = re.compile('\[\[([a-zA-Z-]+:)?([a-zA-Z0-9-]+){1}(\|[a-zA-Z0-9- ]+)?\]\]')

    for i, word in enumerate(words):
        match = p.match(word)
        if match:
            sport = match.group(1)[:-1] if match.group(1) else None
            term_slug = match.group(2)
            label = match.group(3)[1:].strip() if match.group(3) else None

            definition_term_sport = sport_arg
            interlink_anchor = get_interlink_anchor(sport, term_slug, label, definition_term_sport)
            words[i] = mark_safe(interlink_anchor)

    return mark_safe(' '.join(words))


def get_interlink_anchor(sport_ref, term_slug, label, definition_term_sport):
    bad_link = False

    try:
        if sport_ref:
            sport = Sport.objects.get(slug=sport_ref)
            term = Term.objects.get(slug=term_slug, sport=sport)
        else:
            term = Term.objects.get(slug=term_slug, sport=definition_term_sport)
            if not label:
                label = term.text.lower()
    except ObjectDoesNotExist:
        bad_link = True

    if not label:
        label = term_slug

    if bad_link:
        return f'<a href="#" class="bad-link">{label}</a>'
    else:
        return f'<a href="{term.get_absolute_url()}" class="term-link-in-definition">{label}</a>'