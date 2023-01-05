# -*- coding: utf-8 -*-
"""
-------------------------------------------------
  File Name：   urls
  Description : MiniMES Company
  Author :    Karo Lin
  date：     2022/10/7
  Copyright follow MIT definitions.
-------------------------------------------------
  Change Activity:
          2022/10/7:
-------------------------------------------------
"""
__author__ = 'Karo Lin'

app_name = 'fileupload'

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('savetomodel', views.savetomodel, name='savetomodel'),
    path('<int:image_id>/update/', views.update, name='update'),
]
