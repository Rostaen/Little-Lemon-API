from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('groups/manager/users', views.manager),
    path('groups/manager/users/<int:id>', views.manager_delete_user),
    path('groups/delivery-crew/users', views.delivery_crew),
    path('groups/delivery-crew/users/<int:id>', views.delivery_crew_delete_user),
    path('menu-items', views.menu_items),
    path('menu-items/<int:id>', views.single_menu_item),
    path('categories', views.categories),
]
