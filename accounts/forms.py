from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm, PasswordChangeForm
from django.contrib.auth.models import User

from .models import Artwork, UserProfile, Comment


class CustomAuthenticationForm(AuthenticationForm):
    pass


class ArtworkForm(forms.ModelForm):
    label_text = forms.CharField(label='Label for Image', required=False)

    class Meta:
        model = Artwork
        fields = ['title', 'description', 'image', 'price']
        labels = {
            'price': 'Price(USDT)',

        }

    approved = forms.BooleanField(initial=False)


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'first_name', 'last_name', 'national_code', 'email', 'telegramID',
                  'digital_wallet_address']
        labels = {
            'digital_wallet_address': 'Digital Wallet Address (USDT)',

        }


class UserProfileUpdateForm(forms.Form):
    first_name = forms.CharField(label='نام')
    last_name = forms.CharField(label='نام خانوادگی')
    phone_number = forms.CharField(label='شماره تلفن')
    email = forms.EmailField(label='ایمیل')
    telegram_id = forms.CharField(label='آیدی تلگرام')
    instagram_id = forms.CharField(label='آیدی اینستاگرام')
    digital_wallet_address = forms.CharField(label='آدرس کیف دیجیتال')


class UsernameUpdateForm(UserChangeForm):
    class Meta:
        model = User
        fields = ['username']


class FavoriteArtForm(forms.Form):
    artwork_id = forms.IntegerField(widget=forms.HiddenInput())


class PasswordChangeCustomForm(PasswordChangeForm):
    class Meta:
        model = User


class GiftArtworkForm(forms.Form):
    recipient = forms.ModelChoiceField(queryset=User.objects.all(), label='Select Receiver', empty_label=None)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']

