from django.urls import path, include
from . import views

urlpatterns = [
    path('list/', views.listOfGacha, name='gacha-list'),
    path('create/', views.createGacha, name='create-gacha'),
    path('<int:id>/details/', views.gachaDetails, name='gacha-details'),
    path('<int:id>/delete/', views.deleteGacha, name='gacha-delete'),
]
