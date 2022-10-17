from django.db import models


class UploadIcons(models.Model):
    Title = models.CharField(max_length=32, verbose_name='Icon Title')
    IconImage = models.ImageField(upload_to='icons/%Y/%m/%d/', verbose_name='Icon')
