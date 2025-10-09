from django.urls import path
from .views import stk_push

urlpatterns = [ 
    path('stk-push/', stk_push, name='stk-push'),
]