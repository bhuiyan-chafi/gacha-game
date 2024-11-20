from django.urls import path
from . import views

urlpatterns = [
    path('test/', views.authServiceTest, name='auth-service-test'),
    path('create/', views.createUser, name='auth-service-create-user'),
    path('list/', views.listOfUsers, name='auth-service-list-users'),
    path('<int:id>/details/', views.userDetails,
         name='auth-service-user-details'),
    path('<int:id>/delete/', views.deleteUser, name='auth-service-delete-user'),
]
