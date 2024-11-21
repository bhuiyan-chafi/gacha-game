from django.urls import path, include
from . import views

user_urls = [
    path('create/', views.createUser, name='create-user'),
    path('list/', views.listOfUsers, name='user-list'),
    path('<int:id>/details/', views.userDetails, name='user-details'),
    path('<int:id>/delete/', views.deleteUser, name='user-delete'),
    path('login/', views.loginUser, name='user-login'),
    path('<int:id>/logout/', views.logoutUser, name='user-logout'),
]
app_name = 'core'  # Add this line
urlpatterns = [
    path('test/', views.testCore, name='core-test'),
    path('user/', include(user_urls))
]
