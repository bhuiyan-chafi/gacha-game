from django.urls import path, include
from . import views

user_urls = [
    path('create/', views.createUser),
    path('list/', views.listOfUsers),
    path('<int:id>/', views.userDetails),
    path('<int:id>/delete', views.deleteUser),
]

urlpatterns = [
    path('test/', views.testCore),
    path('user/', include(user_urls))
]