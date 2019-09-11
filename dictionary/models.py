import re
from random import randint

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models as models
from django.db.models.aggregates import Count
from django.template.defaultfilters import slugify
from django.urls import reverse


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


# region Sport Model & Managers
class SportManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class Sport(models.Model):
    # Fields
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField()

    # Managers
    objects = SportManager()

    class Meta:
        ordering = ('-pk',)

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


# region Suggested Term & Term Models & Managers
class AbstractTerm(models.Model):
    # Fields
    text = models.CharField(max_length=50)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

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


class ApprovedTermManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(approvedFl=True)

    def random(self):
        count = self.get_queryset().aggregate(count=Count('id'))['count']
        random_index = randint(0, count - 1)
        return self.all()[random_index]


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


class PendingSuggestedTermManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(review_status='PEN')


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


# region Definition Model & Managers
class ApprovedDefinitionManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(approvedFl=True)


class Definition(models.Model):
    # Fields
    text = models.TextField()
    example_usage = models.TextField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    approvedFl = models.BooleanField(default=True)

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
    def __str__(self):
        return f'{self.text}'

    def num_upvotes(self):
        return self.votes.filter(downvote=False).count()

    def num_downvotes(self):
        return self.votes.filter(downvote=True).count()

    def net_votes(self):
        return self.num_upvotes() - self.num_downvotes()
# endregion


# region Vote Model & Managers
class Vote(models.Model):
    # Fields
    created = models.DateTimeField(auto_now_add=True, editable=False)
    downvote = models.BooleanField(default=False)

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

    # Methods
    def __str__(self):
        vote_type = 'Down' if self.downvote else 'Up'
        return f'{vote_type}vote on definition for {self.definition.term} by {self.user}'
# endregion
