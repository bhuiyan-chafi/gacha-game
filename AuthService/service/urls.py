from django.urls import path, include
from . import views

urlpatterns = [
    path('test/', views.authAppTest),
    path('create/', views.createUser),
    path('list/', views.listOfUsers),
    path('<int:id>/details/', views.userDetails),
    path('<int:id>/delete/', views.deleteUser),
]
