import re

from django.core.cache import cache

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models as models, IntegrityError
from django.template.defaultfilters import slugify
from django.urls import reverse

from dictionary.managers import SportManager, ApprovedTermManager, PendingSuggestedTermManager, \
    ApprovedDefinitionManager, ActiveSportsManager, TermOfTheDayManager


def unique_slugify(instance, value, slug_field_name='slug', queryset=None,
                   slug_separator='-'):
    """
    Calculates and stores a unique slug of ``value`` for an instance.

    ``slug_field_name`` should be a string matching the name of the field to
    store the slug in (and the field to check against for uniqueness).

    ``queryset`` usually doesn't need to be explicitly provided - it'll default
    to using the ``.all()`` queryset from the model's default manager.
    """
    slug_field = instance._meta.get_field(slug_field_name)

    slug = getattr(instance, slug_field.attname)
    slug_len = slug_field.max_length

    # Sort out the initial slug, limiting its length if necessary.
    slug = slugify(value)
    if slug_len:
        slug = slug[:slug_len]
    slug = _slug_strip(slug, slug_separator)
    original_slug = slug

    # Create the queryset if one wasn't explicitly provided and exclude the
    # current instance from the queryset.
    if queryset is None:
        queryset = instance.__class__._default_manager.all()
    if instance.pk:
        queryset = queryset.exclude(pk=instance.pk)

    # Find a unique slug. If one matches, at '-2' to the end and try again
    # (then '-3', etc).
    next = 2
    while not slug or queryset.filter(**{slug_field_name: slug}):
        slug = original_slug
        end = '%s%s' % (slug_separator, next)
        if slug_len and len(slug) + len(end) > slug_len:
            slug = slug[:slug_len - len(end)]
            slug = _slug_strip(slug, slug_separator)
        slug = '%s%s' % (slug, end)
        next += 1

    setattr(instance, slug_field.attname, slug)


def _slug_strip(value, separator='-'):
    """
    Cleans up a slug by removing slug separator characters that occur at the
    beginning or end of a slug.

    If an alternate separator is used, it will also replace any instances of
    the default '-' separator with the new separator.
    """
    separator = separator or ''
    if separator == '-' or not separator:
        re_sep = '-'
    else:
        re_sep = '(?:-|%s)' % re.escape(separator)
    # Remove multiple instances and if an alternate separator is provided,
    # replace the default '-' separator.
    if separator != re_sep:
        value = re.sub('%s+' % re_sep, separator, value)
    # Remove separator from the beginning and end of the slug.
    if separator:
        if separator != '-':
            re_sep = re.escape(separator)
        value = re.sub(r'^%s+|%s+$' % (re_sep, re_sep), '', value)
    return value


# region Sport Model
class Sport(models.Model):
    # Fields
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField()
    emoji = models.CharField(max_length=10, blank=True)
    active = models.BooleanField(default=True)

    # Managers
    objects = SportManager()
    active_sports = ActiveSportsManager()

    class Meta:
        ordering = ('name',)

    # Methods
    def save(self, *args, **kwargs):
        if self.pk is None:
            value = self.name
            unique_slugify(self, value)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.name}'

    def get_absolute_url(self):
        return reverse('sport_index', args=(self.slug,))

    def get_update_url(self):
        return reverse('dictionary_sport_update', args=(self.slug,))

    def natural_key(self):
        return (self.name,)
# endregion


# region Definition Model
class Category(models.Model):
    name = models.CharField(max_length=50)

    # Relationship Fields
    sport = models.ForeignKey(
        'dictionary.Sport',
        on_delete=models.CASCADE, related_name="categories",
    )

    class Meta:
        ordering = ('name',)
        verbose_name_plural = "categories"
        constraints = [
            models.UniqueConstraint(fields=['name', 'sport'],
                                    name='unique_category_per_sport'),
        ]

    # Methods
    def __str__(self):
        return f'{self.name}'

    def get_absolute_url(self):
        name = self.name.replace(' ', '_')
        cache_key = f'{self.id}-{name}'
        cache_time = 86400
        data = cache.get(cache_key)
        if not data:
            base_url = reverse('sport_index', args=(self.sport.slug,))
            data = f'{base_url}?category={self.name}'
            cache.set(cache_key, data, cache_time)
        return data
# endregion


# region Suggested Term & Term Models
class AbstractTerm(models.Model):
    # Fields
    text = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    categories = models.ManyToManyField(Category, related_name='%(class)ss', blank=True)

    # Relationship Fields
    sport = models.ForeignKey(
        'dictionary.Sport',
        on_delete=models.CASCADE, related_name="%(class)ss",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, related_name="%(class)ss",
        null=True, blank=True
    )

    # Managers
    objects = models.Manager()

    class Meta:
        abstract = True

    # Methods
    def __str__(self):
        return f'{self.text} - {self.sport}'


class Term(AbstractTerm):
    # Fields
    slug = models.SlugField()
    approvedFl = models.BooleanField(default=True)

    # Relationship Fields
    suggested_term = models.OneToOneField(
        'dictionary.SuggestedTerm',
        on_delete=models.CASCADE, null=True
    )

    # Managers
    approved_terms = ApprovedTermManager()

    class Meta:
        default_manager_name = 'objects'
        ordering = ('text',)
        constraints = [
            models.UniqueConstraint(fields=['text', 'sport'], name='unique_term_in_sport'),
        ]
        permissions = [
            ("can_approve_term", "Can approve a term"),
            ("can_disapprove_term", "Can disapprove a term"),
        ]

    # Methods
    def save(self, *args, **kwargs):
        if self.pk is None:
            value = self.text
            unique_slugify(self, value, queryset=Term.objects.filter(sport=self.sport))
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('term_detail', args=(self.sport.slug, self.slug))

    def get_update_url(self):
        return reverse('dictionary_term_update', args=(self.slug,))

    def num_approved_definitions(self):
        return self.definitions.filter(approvedFl=True).count()
    num_approved_definitions.short_description = 'Approved Definitions'


class SuggestedTerm(AbstractTerm):
    definitionText = models.TextField()
    example_usage = models.TextField(null=True, blank=True)

    ACCEPTED = 'ACC'
    REJECTED = 'REJ'
    PENDING = 'PEN'
    REVIEW_STATUS_CHOICES = [
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Rejected'),
        (PENDING, 'Pending'),
    ]
    review_status = models.CharField(
        max_length=3,
        choices=REVIEW_STATUS_CHOICES,
        default=PENDING,
    )

    # Managers
    pending_terms = PendingSuggestedTermManager()

    class Meta:
        default_manager_name = 'objects'
        permissions = [
            ("can_accept_suggested_term", "Can accept a suggested term"),
            ("can_reject_suggested_term", "Can reject a suggested term"),
        ]

    # Methods
    def save(self, *args, **kwargs):
        created = self.pk is None
        super().save(*args, **kwargs)
        if not created:
            if self.is_accepted() and not self.term_exists():
                # create the term
                term = Term.objects.create(
                    text=self.text,
                    user=self.user,
                    sport=self.sport,
                    suggested_term=self
                )
                # create the definition
                Definition.objects.create(
                    text=self.definitionText,
                    example_usage=self.example_usage,
                    user=self.user,
                    term=term
                )

    def term_exists(self):
        try:
            Term.objects.get(suggested_term=self)
            return True
        except ObjectDoesNotExist:
            return False

    def is_pending_review(self):
        return self.review_status == self.PENDING

    def is_accepted(self):
        return self.review_status == self.ACCEPTED

    def is_rejected(self):
        return self.review_status == self.REJECTED
# endregion


# region Definition Model
class TermOfTheDay(models.Model):
    # Fields
    day = models.DateField(unique=True)

    # Relationship Fields
    term = models.ForeignKey(
        'dictionary.Term',
        on_delete=models.CASCADE, related_name="terms_of_the_day",
    )

    # Managers
    objects = models.Manager()
    terms = TermOfTheDayManager()

    class Meta:
        verbose_name_plural = "Terms of the day"

    # Methods
    def __str__(self):
        term_text = self.term.text
        term_text = (term_text[:40] + '...') if len(term_text) > 40 else term_text
        return f'{self.day} - {term_text}'
# endregion


# region Definition Model
class Definition(models.Model):
    # Fields
    text = models.TextField()
    example_usage = models.TextField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    approvedFl = models.BooleanField(default=True)
    net_votes = models.IntegerField(default=0)
    num_upvotes = models.IntegerField(default=0)
    num_downvotes = models.IntegerField(default=0)

    # Relationship Fields
    term = models.ForeignKey(
        'dictionary.Term',
        on_delete=models.CASCADE, related_name="definitions",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, related_name="definitions",
    )

    # Managers
    objects = models.Manager()
    approved_definitions = ApprovedDefinitionManager()

    class Meta:
        ordering = ('-created',)
        permissions = [
            ("can_approve_definition", "Can approve a definition"),
            ("can_disapprove_definition", "Can disapprove a definition"),
        ]

    # Methods
    def save(self, *args, **kwargs):
        self.net_votes = self.num_upvotes - self.num_downvotes
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.text}'

    # Voting methods
    # TODO: ensure any concurrency issues are sorted out
    def upvote(self, user):
        try:
            if self.votes.filter(user=user).filter(vote_type=Vote.DOWNVOTE).exists():
                self.delete_downvote(user=user)
            self.votes.create(user=user, definition=self, vote_type=Vote.UPVOTE)
            self.num_upvotes += 1
            self.save()
        except IntegrityError:
            return 'already_voted'

    def delete_upvote(self, user):
        try:
            v = self.votes.get(user=user, definition=self, vote_type=Vote.UPVOTE)
            self.num_upvotes -= 1
            self.save()
            v.delete()
        except IntegrityError:
            return 'error'

    def downvote(self, user):
        try:
            if self.votes.filter(user=user).filter(vote_type=Vote.UPVOTE).exists():
                self.delete_upvote(user=user)
            self.votes.create(user=user, definition=self, vote_type=Vote.DOWNVOTE)
            self.num_downvotes += 1
            self.save()
        except IntegrityError:
            return 'already_voted'

    def delete_downvote(self, user):
        try:
            v = self.votes.get(user=user, definition=self, vote_type=Vote.DOWNVOTE)
            self.num_downvotes -= 1
            self.save()
            v.delete()
        except IntegrityError:
            return 'error'
# endregion


# region Vote Model
class Vote(models.Model):
    # Fields
    created = models.DateTimeField(auto_now_add=True, editable=False)

    UPVOTE = 1
    DOWNVOTE = -1
    VOTE_TYPES = (
        (UPVOTE, 'Upvote'),
        (DOWNVOTE, 'Downvote'),
    )
    vote_type = models.IntegerField(choices=VOTE_TYPES, default=UPVOTE)

    # Relationship Fields
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, related_name="votes",
    )
    definition = models.ForeignKey(
        'dictionary.Definition',
        on_delete=models.CASCADE, related_name="votes",
    )

    class Meta:
        ordering = ('-created',)
        constraints = [
            models.UniqueConstraint(fields=['user', 'definition'],
                                    name='unique_vote_by_user_for_definition'),
        ]

    # Methods
    def __str__(self):
        vote_type = 'Up' if self.vote_type == Vote.UPVOTE else 'Down'
        definition_text = (self.definition.text[:40] + '...') if len(self.definition.text) > 40 else self.definition.text
        return f'{vote_type}vote by {self.user} on definition [{definition_text}] for term [{self.definition.term.text}]'
# endregion
