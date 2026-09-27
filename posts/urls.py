from django.urls import path

from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.feed, name='feed'),
    path('explore/', views.explore, name='explore'),
    path('create/', views.post_create, name='post_create'),
    path('<int:pk>/', views.post_detail, name='post_detail'),
    path('<int:pk>/delete/', views.post_delete, name='post_delete'),
    path('<int:pk>/like/', views.like_toggle, name='like_toggle'),
    path('<int:pk>/comment/', views.add_comment, name='add_comment'),
]
