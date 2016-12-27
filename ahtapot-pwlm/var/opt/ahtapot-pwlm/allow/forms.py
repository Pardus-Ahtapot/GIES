# -*- coding: utf-8 -*-

from django import forms

import allow.models


class RequestForm(forms.ModelForm):

    class Meta:
        model = allow.models.RequestUrl
        fields = '__all__'
