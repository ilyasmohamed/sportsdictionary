from django.core import mail
from django.contrib.auth.models import User
from django.urls import reverse
from django.test import TestCase


class SignUpMailTests(TestCase):
    def setUp(self):
        self.data = {
            'username': 'ilyas',
            'email': 'ilyas@gmail.com',
            'password1': 'abcdef123456',
            'password2': 'abcdef123456'
        }
        self.response = self.client.post(reverse('signup'), self.data)
        self.email = mail.outbox[0]

    def test_email_subject(self):
        self.assertEqual('Activate Your Sports Dictionary Account', self.email.subject)

    def test_email_body(self):
        context = self.response.context
        token = context.get('token')
        uid = context.get('uid')
        account_activation_url = reverse('account_activation', kwargs={
            'uidb64': uid,
            'token': token
        })
        self.assertIn(account_activation_url, self.email.body)

        username = self.data['username']
        self.assertIn(f'Hi {username}', self.email.body)

        self.assertIn('Please click on the link below to confirm your registration', self.email.body)

    def test_email_to(self):
        self.assertIn(self.data['email'], self.email.to)
