from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate


class SignUpForm(forms.Form):
    username = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': "form-control",
            'id': 'inputUsername',
            'type': 'username',
            'placeholder': 'имя пользователя'
        }),
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'id': 'inputPassword',
            'type': 'password',
            'placeholder': 'Пароль'
        })
    )
    repeat_password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': "form-control",
            'id': 'ReInputPassword',
            'type': 'password',
            'placeholder': 'Повторите пароль'
        }),
    )
    def clean(self):
        password = self.cleaned_data['password']
        confirm_password = self.cleaned_data['repeat_password']

        if password != confirm_password:
            raise forms.ValidationError(
                'пароли не совпадают'
            )
    def save(self):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password']
        )
        user.save()
        auth = authenticate(**self.cleaned_data)
        return auth

class SignInForm(forms.Form):
    username = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'inputUsername',
        })
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control mt-2',
            'id': "inputPassword",
        })
    )


class SearchForm(forms.Form):
    query = forms.CharField(
        label='Поиск',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите id оборудования'
        })
    )
    category = forms.ChoiceField(
        label='Категория',
        choices=[
            ('all', 'Все категории'),
            ('books', 'Книги'),
            ('movies', 'Фильмы'),
            ('music', 'Музыка'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )