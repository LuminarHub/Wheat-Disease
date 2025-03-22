from django.urls import path
from .views import *


urlpatterns = [
    path('',login_view, name='login'),
    path('register/',RegView.as_view(), name='reg'),
    path('home/',Home.as_view(),name="home"),
    path('chatbot/',ChatbotView.as_view(),name="bot"),
    path('schemes/',SchemeView.as_view(),name="scheme"),
    path('prediction/',PredictionView.as_view(),name='prediction'),
    path('auth/logout/', CustomLogoutView.as_view(), name='logout')
]