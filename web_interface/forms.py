# -*- coding: utf-8 -*-
from django.forms import ModelForm
from django import forms
from models import PreviewRequest
from captcha.fields import CaptchaField

class PreviewRequestForm(ModelForm):
    class Meta:
        model = PreviewRequest
    url = forms.URLField(widget=forms.TextInput({ 'placeholder' : 'Url*' }), label='')
    email = forms.EmailField(widget=forms.TextInput({ 'placeholder' : 'Email*' }), label='')
    captcha = CaptchaField(label='Please enter the characters bellow:')