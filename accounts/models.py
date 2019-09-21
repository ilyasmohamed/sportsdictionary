from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User


User._meta.get_field('email')._unique = True


# region Profile Model
class Profile(models.Model):
    # Fields
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email_confirmed = models.BooleanField(default=False)
    favourite_sport = models.ForeignKey('dictionary.Sport', models.SET_NULL, blank=True, null=True)
    show_favourite_sport = models.BooleanField(default=False)

    # Methods
    def __str__(self):
        return f'{self.user} Profile'
# endregion


# region Profile creation
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
# endregion
