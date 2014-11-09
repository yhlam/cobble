from django import forms


class UserConfigUpdateForm(forms.Form):
    read = forms.BooleanField(required=False)
    prioritize = forms.BooleanField(required=False)
