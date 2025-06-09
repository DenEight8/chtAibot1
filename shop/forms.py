from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
import re


class RegistrationForm(UserCreationForm):
    """Реєстрація нового користувача (додаємо e-mail)."""
    email = forms.EmailField(
        required=True,
        label="E-mail",
        help_text="Необхідний для підтвердження та відновлення пароля."
    )

    class RegistrationForm(forms.ModelForm):
        password1 = forms.CharField(label="Пароль",
                                    widget=forms.PasswordInput)
        password2 = forms.CharField(label="Підтвердіть пароль",
                                    widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Користувач із таким e-mail уже існує.")
        return email

    def clean_password2(self):
        p1 = self.cleaned_data.get("password1")
        p2 = self.cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Паролі не співпадають.")
        validate_password(p2)
        return p2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class QuickOrderForm(forms.Form):
    """Міні-форма «Купити в один клік»."""
    name = forms.CharField(max_length=64, label="Ім’я")
    phone = forms.CharField(max_length=32, label="Телефон")
    product_id = forms.IntegerField(widget=forms.HiddenInput)

    def clean_phone(self):
        phone = self.cleaned_data["phone"]
        if not re.fullmatch(r"^[\d\+\-\(\) ]{7,20}$", phone):
            raise forms.ValidationError("Введіть коректний номер телефону.")
        return phone
