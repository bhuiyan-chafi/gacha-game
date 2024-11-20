from django.urls import path, include
from . import views

urlpatterns = [
    path('list/', views.listOfGacha),
    path('create/', views.createGacha),
    path('<int:id>/details/', views.gachaDetails),
    path('<int:id>/delete/', views.deleteGacha),
]
