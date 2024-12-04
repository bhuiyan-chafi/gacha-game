from django.urls import path, include
from . import views

urlpatterns = [
    path('test/', views.authAppTest, name='test-auth-service'),
    path('token/verify/', views.verifyToken, name='verify-token'),
    path('create/', views.createUser, name='create-user'),
    path('list/', views.listOfUsers, name='list-user'),
    path('<int:id>/details/', views.userDetails, name='user-details'),
    path('<int:id>/delete/', views.deleteUser, name='delete-user'),
    path('user/login/', views.loginUser, name='user-login'),
    path('user/<int:id>/logout/', views.logoutUser, name='user-logout'),
]
