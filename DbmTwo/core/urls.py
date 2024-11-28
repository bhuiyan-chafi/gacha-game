from django.urls import path, include
from . import views

player = [
    path('list/', views.listOfPlayers, name="list_players"),
    path('create/', views.createPlayer, name="create_player"),
    path('<int:id>/details/', views.playerDetails, name="player_details"),
    path('<int:id>/delete/', views.deletePlayer, name="delete_player"),
]

admin = [
    path('list/', views.listOfAdmins, name="list_admins"),
    path('create/', views.createAdmin, name="create_admin"),
    path('<int:id>/details/', views.AdminDetails, name="admin_details"),
    path('<int:id>/delete/', views.deleteAdmin, name="delete_admin"),
]

urlpatterns = [
    path('test/', views.testCoreApp),
    path('admin/', include(admin),),
    path('player/', include(player))
]
