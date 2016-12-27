# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from datetime import datetime

# Create your models here.


class RequestUrl(models.Model):

    url = models.CharField(blank=False, max_length=60)
    user = models.CharField(blank=False, max_length=60)
    ip = models.CharField(blank=False, max_length=20)
    is_operated = models.BooleanField(default=False)
    created_date = models.DateTimeField(default=datetime.now())
    last_updated = models.DateTimeField(default=datetime.now())
    status = models.CharField(default="Bekliyor", max_length=15)
    operated_by = models.CharField(default="-", max_length=60)

    def __str__(self):
        return self.url + " | " + self.user + " | " + self.ip

    class Meta:

        verbose_name = u"İstenen Bağlantı"
        verbose_name_plural = u"İstenen Bağlantılar"
