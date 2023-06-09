from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path("menu-items", views.menu_items),
    path("menu-items/<int:id>", views.single_item),
    path("category/<int:pk>", views.category_detail, name="category-detail"),
    path("secret/", views.secret),
    path("api-token-auth/", obtain_auth_token),
    path("manager-view/", views.manager_view),
    path("throttle-check/", views.throttle_check),
    path("throttle-check-auth/", views.throttle_check_auth),
    path("groups/manager/users", views.managers),
    path("groups/manager/users/<int:id>", views.managers_user),
    path("groups/delivery-crew/users", views.deliverycrew),
    path("groups/delivery-crew/users/<int:id>", views.deliverycrew_user),
    path("cart/menu-items", views.cartitems),
    path("orders", views.order),
    path("orders/<int:id>", views.order_item),
]
