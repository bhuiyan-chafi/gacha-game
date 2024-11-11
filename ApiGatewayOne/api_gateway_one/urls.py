from django.urls import path, include
from . import views

auth_app = [
    path('test/', views.authAppTest),
    path('create/', views.createUser),
    path('list/', views.listOfUsers),
    path('<int:id>/details/', views.userDetails),
    path('<int:id>/delete/', views.deleteUser),
]

user_as_player = [
    # user/player/
    path('create/', views.createPlayer),
    path('list/', views.listOfPlayers),
    path('<int:id>/details/', views.playerDetails),
    path('<int:id>/delete/', views.deletePlayer),
]

user_as_admin = [
    # user/admin/
    path('create/', views.createAdmin),
    path('list/', views.listOfAdmins),
    path('<int:id>/details/', views.adminDetails),
    path('<int:id>/delete/', views.deleteAdmin),
]

user_app = [
    path('test/', views.userAppTest),
    # user/
    path('player/', include(user_as_player)),
    path('admin/', include(user_as_admin)),
]

urlpatterns = [
    path('auth/', include(auth_app)),
    path('user/', include(user_app)),
]
