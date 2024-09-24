# game/forms.py
from django import forms

class GameForm(forms.Form):
    x = forms.IntegerField(min_value=1, max_value=5, label='Row')
    y = forms.IntegerField(min_value=1, max_value=5, label='Column')
