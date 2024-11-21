from django.urls import path
from . import views

urlpatterns = [
    path('test/', views.gateWayOneTest, name='auth-service-test'),
    path('create/', views.createUser, name='auth-service-create-user'),
    path('list/', views.listOfUsers, name='auth-service-list-users'),
    path('<int:id>/details/', views.userDetails,
         name='auth-service-user-details'),
    path('<int:id>/delete/', views.deleteUser, name='auth-service-delete-user'),
    path('user/login/', views.loginUser, name='user-login'),
    path('user/<int:id>/logout/', views.logoutUser, name='user-logout'),
]
