from django.urls import path
from . import views

app_name = 'download'

urlpatterns = [
    path('contracts/', views.getCompleteList, name='downloadContracts'),
    path('minors/', views.getMinorsList, name='downloadMinors'),
]
