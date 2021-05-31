from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UsernameField
from django import forms
from django.utils.translation import gettext, gettext_lazy as _
import re
from .models import CourierProfile, Order, Courier

from django.core.exceptions import ValidationError

UserModel = get_user_model()

BIRTH_YEAR_CHOICES = [str(year) for year in range(1921, 2022)]


class CourierRegisterForm(forms.Form):
    # username = forms.CharField(blank=True, max_length=150, unique=True, )
    email = forms.EmailField(label='Адрес E-mail', max_length=150,
                             widget=forms.EmailInput(attrs={'class': 'form-control', 'autocomplete': 'email'}),
                             help_text='Для регистрации укажите пожалуйста свой актуальный адрес электронной почты (E-mail)')
    first_name = forms.CharField(label='Имя', max_length=70,
                                 widget=forms.TextInput(attrs={'class': 'form-control'}),
                                 help_text='Имя на Вашем родном языке')
    last_name = forms.CharField(label='Фамилия', max_length=70,
                                widget=forms.TextInput(attrs={'class': 'form-control'}),
                                help_text='Фамилия на Вашем родном языке')
    mobile_phone = forms.CharField(label='Мобильный телефон', max_length=28,
                                   widget=forms.TextInput(attrs={'class': 'form-control'}),
                                   help_text='Ваш актуальный номер мобильного телефона с кодом страны')
    password = forms.CharField(label='Пароль', max_length=128,
                               widget=forms.PasswordInput(attrs={'class': 'form-control'}),
                               help_text='Укажите пароль, он будет также выслан к Вам на почту')

    def clean_email(self):
        return self.cleaned_data['email'].lower()

    def clean_mobile_phone(self):
        phone = self.cleaned_data['mobile_phone']
        pattern = r'^\+?\(?[0-9]{1,4}\)?[-\s\./0-9]+$'
        if re.match(pattern, phone):
            return phone
        else:
            raise ValidationError('Неправильно введён мобильный номер (пример правильного: +375291234567)')

    def _post_clean(self):
        super()._post_clean()
        # Validate the password after self.instance is updated with form data
        # by super().
        password = self.cleaned_data.get('password')
        if password:
            try:
                password_validation.validate_password(password)
            except ValidationError as error:
                self.add_error('password', error)

    def as_div(self):
        "Return this form rendered as HTML <div>s."
        return self._html_output(
            normal_row='<div%(html_class_attr)s>%(label)s %(field)s%(help_text)s</div><br>',
            error_row='%s',
            row_ender='</div>',
            help_text_html=' <span class="helptext">%s</span>',
            errors_on_separate_row=True,
        )

    def save(self):
        user = User.objects.create_user(username=self.cleaned_data['email'],
                                        email=self.cleaned_data['email'],
                                        password=self.cleaned_data['password'],
                                        first_name=self.cleaned_data['first_name'],
                                        last_name=self.cleaned_data['last_name'],
                                        is_active=False)

        courier = Courier.objects.create(user=user, mobile_phone=self.cleaned_data['mobile_phone'])
        # Client.objects.filter(email=self.cleaned_data['email']).update(user=user)

        return courier, self.cleaned_data['password']


# TODO забыли пароль
class CourierAuthorizationForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.TextInput(attrs={'class': 'form-control', 'autofocus': True}),
                                help_text='Для авторизации укажите пожалуйста свой адрес электронной почты (E-mail)',
                                label='E-mail')
    password = forms.CharField(
        label=_("Пароль"),
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'current-password'}),
        help_text='Пароль указанный при регистрации'
    )

    def as_div(self):
        "Return this form rendered as HTML <div>s."
        return self._html_output(
            normal_row='<div%(html_class_attr)s>%(label)s %(field)s%(help_text)s</div><br>',
            error_row='%s',
            row_ender='</div>',
            help_text_html=' <span class="helptext">%s</span>',
            errors_on_separate_row=True,
        )


class ProfileCreationForm(forms.ModelForm):
    class Meta:
        model = CourierProfile
        fields = ['courier_type', 'regions', 'working_hours']
        widgets = {
            'courier_type': forms.Select(attrs={'class': 'form-control'}, choices=CourierProfile.COURIER_TYPE_CHOICES),
            'regions': forms.TextInput(attrs={'class': 'form-control'}),
            'working_hours': forms.TextInput(attrs={'class': 'form-control'})
        }
        help_texts = {
            'regions': 'Введите номера районов в которых Вам будет удобно работать, в формате [1, 2, 3, ...]',
            'working_hours': 'Введите удобные вам часы работы в формате ["HH:MM-HH:MM", "HH:MM-HH:MM", ...]  (Промежутки времени не должны пересекаться)'
        }

    def as_div(self):
        """Return this form rendered as HTML <div>s."""
        return self._html_output(
            normal_row='<div%(html_class_attr)s>%(label)s %(field)s%(help_text)s</div><br>',
            error_row='%s',
            row_ender='</div>',
            help_text_html=' <span class="helptext">%s</span>',
            errors_on_separate_row=True,
        )

    def save(self, commit=True):
        if commit:
            super().save(commit)
        else:
            profiles = CourierProfile.objects.all().order_by('-courier_id')
            if len(profiles) == 0:
                courier_id = 0
            else:
                courier_id = profiles[0].courier_id + 1

            return CourierProfile(**self.cleaned_data, courier_id=courier_id)
