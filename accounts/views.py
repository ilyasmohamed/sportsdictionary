from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.utils.http import urlsafe_base64_encode

from accounts.decorators import anonymous_required
from dictionary.models import Definition, Vote
from .forms import SignUpForm
from .tokens import account_activation_token


@login_required
def profile(request):
    definitions = Definition.approved_definitions.filter(user=request.user).order_by('-created')
    user_votes = Vote.objects.filter(user=request.user).filter(definition__deleteFl=False)
    upvotes = user_votes.filter(vote_type=Vote.UPVOTE).order_by('-created')
    downvotes = user_votes.filter(vote_type=Vote.DOWNVOTE).order_by('-created')

    context = {
        'definitions': definitions,
        'upvotes': upvotes,
        'downvotes': downvotes,
    }
    return render(request, 'accounts/profile.html', context)


@anonymous_required
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            subject = 'Activate Your Sports Dictionary Account'
            message = render_to_string('accounts/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            user.email_user(subject, message)
            return redirect('account_activation_sent')
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})


@anonymous_required
def account_activation_sent(request):
    return render(request, 'accounts/account_activation_sent.html')


@anonymous_required
def account_activation(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.profile.email_confirmed = True
        user.save()
        return redirect('account_activation_complete')
    else:
        return render(request, 'accounts/account_activation_invalid.html')


@anonymous_required
def account_activation_complete(request):
    return render(request, 'accounts/account_activation_complete.html')
