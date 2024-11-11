from django.urls import path, include
from . import views

player = [
    path('list/', views.listOfPlayers),
    path('create/', views.createPlayer),
    path('<int:id>/details/', views.playerDetails),
    path('<int:id>/delete/', views.deletePlayer),
]

admin = [
    path('list/', views.listOfAdmins),
    path('create/', views.createAdmin),
    path('<int:id>/details/', views.AdminDetails),
    path('<int:id>/delete/', views.deleteAdmin),
]

urlpatterns = [
    path('test/', views.testCoreApp),
    path('admin/', include(admin),),
    path('player/', include(player))
]