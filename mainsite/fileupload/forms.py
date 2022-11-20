# -*- coding: utf-8 -*-
"""
-------------------------------------------------
  File Name：   forms
  Description : MiniMES Company
  Author :    Karo Lin
  date：     2022/10/8
  Copyright follow MIT definitions.
-------------------------------------------------
  Change Activity:
          2022/10/8:
-------------------------------------------------
"""
__author__ = 'Karo Lin'

from django import forms
from django.forms import TextInput, FileInput
from captcha.fields import CaptchaField
from .models import UploadIcons


class UploadFileForm(forms.Form):
    file = forms.FileField(label='Image',
                           widget=(
                               forms.FileInput(
                                   attrs={'class': 'form-control', 'accept': 'image/gif,image/jpeg, image/png'}
                                                )
                                )

                           )


class UploadIconModelForm(forms.ModelForm):
    captcha = CaptchaField(label='驗證碼：')

    class Meta:
        model = UploadIcons
        fields = ['Title', 'IconImage', 'captcha']
        labels = {
            'Title': 'Icon Title',
            'IconImage': 'Icon Photo',
        }
        widgets = {
            'Title': TextInput(attrs={'class': 'form-control', 'id': 'title'}),
            'IconImage': FileInput(attrs={'class': 'form-control mb-3', 'id': 'upload_icon', 'onchange': 'ShowName()'}),
            'captcha': TextInput(attrs={'class': 'form-control'}),
        }
