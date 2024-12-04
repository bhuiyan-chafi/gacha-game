from django.urls import path, include
from . import views

# Define player and admin routes
player = [
    path('list/', views.listPlayersFromUserService, name='list-players'),
    path('create/', views.createPlayerInUserService, name='create-player'),
    path('<int:id>/details/', views.playerDetailsFromUserService,
         name='player-details'),
    path('<int:id>/delete/', views.deletePlayerFromUserService, name='delete-player'),
]

admin = [
    path('list/', views.listAdminsFromUserService, name='list-admins'),
    path('create/', views.createAdminInUserService, name='create-admin'),
    path('<int:id>/details/', views.adminDetailsFromUserService, name='admin-details'),
    path('<int:id>/delete/', views.deleteAdminFromUserService, name='delete-admin'),
]

# Define the main urlpatterns
urlpatterns = [
    path('player/', include(player)),
    path('admin/', include(admin)),
]
