from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from . import views
from .forms import LoginForm

urlpatterns = [
    path('profile/', views.profile, name='profile'),


    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html',
                                                authentication_form=LoginForm,
                                                redirect_authenticated_user=True),
         name='login'),

    path('logout/', auth_views.LogoutView.as_view(), name='logout'),


    path('account_activation_sent/', views.account_activation_sent, name='account_activation_sent'),
    url(r'^account_activation/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.account_activation, name='account_activation'),
    path('account_activation_complete/',
         views.account_activation_complete, name='account_activation_complete'),


    path('password_reset/',
         auth_views.PasswordResetView.as_view(
             template_name='accounts/password_reset.html',
             email_template_name='accounts/password_reset_email.html',
             subject_template_name='accounts/password_reset_subject.txt',
             success_url=reverse_lazy('password_reset_sent')
         ),
         name='password_reset'),
    path('password_reset/sent/',
         auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_sent.html'),
         name='password_reset_sent'),
    url(r'^password_reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'),
        name='password_reset_confirm'),
    path('password_reset/complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'),
         name='password_reset_complete'),
]
