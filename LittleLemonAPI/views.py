from django.core.paginator import EmptyPage, Paginator
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import BasePermission, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from datetime import date

from .models import Cart, Category, MenuItem, Order, OrderItem
from .serializers import (
    CartSerializer,
    CategorySerializer,
    MenuItemSerializer,
    OrderSerializer,
    UserSerializer,
)
from .throttles import TenCallsPerMinute


@api_view(["GET", "POST", "PUT", "PATCH", "DELETE"])
def menu_items(request):
    if request.method == "GET":
        items = MenuItem.objects.select_related("category").all()
        category_name = request.query_params.get("category")
        to_price = request.query_params.get("to_price")
        search = request.query_params.get("search")
        ordering = request.query_params.get("ordering")
        perpage = request.query_params.get("perpage", default=2)
        page = request.query_params.get("page", default=1)
        if category_name:
            items = items.filter(category__title=category_name)
        if to_price:
            items = items.filter(price__lte=to_price)
        if search:
            items = items.filter(title__contains=search)
        if ordering:
            ordering_fields = ordering.split(",")
            items = items.order_by(*ordering_fields)
        paginator = Paginator(items, per_page=perpage)
        try:
            items = paginator.page(number=page)
        except EmptyPage:
            items = []
        serialized_item = MenuItemSerializer(items, many=True)
        return Response(serialized_item.data)
    if not request.user.groups.filter(name="Manager").exists():
        return Response("You must be a Manager to do this.", status.HTTP_403_FORBIDDEN)
    if request.method == "POST":
        serialized_item = MenuItemSerializer(data=request.data)
        serialized_item.is_valid(raise_exception=True)
        serialized_item.save()
        return Response(serialized_item.data, status.HTTP_201_CREATED)


@api_view(["GET", "PUT", "PATCH", "DELETE"])
def single_item(request, id):
    item = get_object_or_404(MenuItem, pk=id)
    if request.method == "GET":
        serialized_item = MenuItemSerializer(item)
        return Response(serialized_item.data)
    if not request.user.groups.filter(name="Manager").exists():
        return Response("You must be a Manager to do this.", status.HTTP_403_FORBIDDEN)
    if request.method == "PUT" or request.method == "PATCH":
        serialized_item = MenuItemSerializer(item, data=request.data, partial=True)
        serialized_item.is_valid(raise_exception=True)
        serialized_item.save()
        return Response(serialized_item.data, status.HTTP_200_OK)
    if request.method == "DELETE":
        item.delete()
        return Response("Deleted item", status.HTTP_200_OK)


@api_view()
def category_detail(request, pk):
    category = get_object_or_404(Category, pk=pk)
    serialized_category = CategorySerializer(category)
    return Response(serialized_category.data)


@api_view()
@permission_classes([IsAuthenticated])
def secret(request):
    return Response({"message": "Steven is a noob!"})


@api_view()
@permission_classes([IsAuthenticated])
def manager_view(request):
    if request.user.groups.filter(name="Manager").exists():
        return Response({"message": "Only Manager Should See This"})
    return Response({"message": "You are not authorized"}, 403)


@api_view()
@throttle_classes([AnonRateThrottle])
def throttle_check(request):
    return Response({"message": "successful"})


@api_view()
@permission_classes([IsAuthenticated])
@throttle_classes([TenCallsPerMinute])
def throttle_check_auth(request):
    return Response({"message": "message for the logged in users only"})


class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name="Manager").exists()


@api_view(["GET", "POST"])
@permission_classes([IsManager])
def managers(request):
    manager_users = User.objects.filter(groups__name="Manager")
    if request.method == "GET":
        return Response(
            UserSerializer(manager_users.all(), many=True).data,
            status=status.HTTP_200_OK,
        )
    username = request.data["username"]
    if username:
        user = get_object_or_404(User, username=username)
        manager_group = Group.objects.get(name="Manager")
        if request.method == "POST":
            user.groups.add(manager_group)
            return Response({"message": "ok"}, status=status.HTTP_201_CREATED)


@api_view(["DELETE"])
@permission_classes([IsManager])
def managers_user(request, id):
    user = get_object_or_404(User, id=id)
    manager_group = Group.objects.get(name="Manager")
    user.groups.remove(manager_group)
    return Response({"message": "ok"}, status=status.HTTP_200_OK)


@api_view(["GET", "POST"])
@permission_classes([IsManager])
def deliverycrew(request):
    delieverycrew_users = User.objects.filter(groups__name="Delivery crew")
    if request.method == "GET":
        return Response(
            UserSerializer(delieverycrew_users.all(), many=True).data,
            status=status.HTTP_200_OK,
        )
    username = request.data["username"]
    if username:
        user = get_object_or_404(User, username=username)
        deliverycrew_group = Group.objects.get(name="Delivery crew")
        if request.method == "POST":
            user.groups.add(deliverycrew_group)
            return Response({"message": "ok"}, status=status.HTTP_201_CREATED)


@api_view(["DELETE"])
@permission_classes([IsManager])
def deliverycrew_user(request, id):
    user = get_object_or_404(User, id=id)
    deliverycrew_group = Group.objects.get(name="Delivery crew")
    user.groups.remove(deliverycrew_group)
    return Response({"message": "ok"}, status=status.HTTP_200_OK)


@api_view(["GET", "POST", "DELETE"])
@permission_classes([IsAuthenticated])
def cartitems(request):
    if request.method == "GET":
        items = Cart.objects.filter(user=request.user)
        return Response(
            CartSerializer(items.all(), many=True).data, status=status.HTTP_200_OK
        )
    if request.method == "POST":
        itemid = request.data["item"]
        quantity = int(request.data["quantity"])
        menuitem = MenuItem.objects.get(id=itemid)
        cart = Cart(
            user=request.user,
            menuitem=menuitem,
            quantity=quantity,
            unit_price=menuitem.price,
            price=menuitem.price * quantity,
        )
        cart.save()
        return Response(CartSerializer(cart).data, status=status.HTTP_201_CREATED)
    if request.method == "DELETE":
        items = Cart.objects.filter(user=request.user)
        items.delete()
        return Response("Emptied cart", status=status.HTTP_200_OK)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def order(request):
    if request.method == "GET":
        if request.user.groups.filter(name="Manager").exists():
            # do manager stuff
            items = Order.objects.all()
            return Response(
                OrderSerializer(items, many=True).data, status=status.HTTP_200_OK
            )
        elif request.user.groups.filter(name="Delivery crew").exists():
            # do delivery crew stuff
            items = Order.objects.filter(delivery_crew=request.user)
            return Response(
                OrderSerializer(items, many=True).data, status=status.HTTP_200_OK
            )
        else:
            # do customer stuff
            items = Order.objects.filter(user=request.user)
            return Response(
                OrderSerializer(items, many=True).data, status=status.HTTP_200_OK
            )
    if request.method == "POST":
        order = Order(user=request.user, total=0, date=date.today())
        order.save()
        total = 0
        for item in Cart.objects.filter(user=request.user):
            orderitem = OrderItem(
                order=order,
                menuitem=item.menuitem,
                quantity=item.quantity,
                unit_price=item.unit_price,
                price=item.price,
            )
            orderitem.save()
            total += item.price
            item.delete()
        order.total = total
        order.save()
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


@api_view(["GET", "PUT", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def order_item(request, id):
    if request.method == "GET":
        order = get_object_or_404(Order, id=id)
        if request.user != order.user:
            return Response("This is not your order.", status=status.HTTP_403_FORBIDDEN)
        return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)
    if request.method == "PUT":
        order = get_object_or_404(Order, id=id)
        if not request.user.groups.filter(name="Manager").exists():
            return Response(
                "You must be a manager to edit the order.",
                status.HTTP_403_FORBIDDEN,
            )
        serialized_order = OrderSerializer(request.data, partial=True)
        serialized_order.is_valid(raise_exception=True)
        serialized_order.save()
    if request.method == "PATCH":
        order = get_object_or_404(Order, id=id)
        orderstatus = request.data.get("status", None)
        delivery_crew = request.data.get("delivery_crew", None)
        if request.user.groups.filter(name="Manager").exists():
            if orderstatus is not None:
                order.status = orderstatus
            if delivery_crew is not None:
                deliverer = get_object_or_404(User, username=delivery_crew)
                if not deliverer.groups.filter(name="Delivery crew").exists():
                    return Response(
                        f"User with username {delivery_crew} is not in the delivery crew",
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                order.delivery_crew = deliverer
            order.save()
            return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)
        if request.user.groups.filter(name="Delivery crew").exists():
            if orderstatus is not None:
                order.status = orderstatus
            order.save()
            return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)

    if request.method == "DELETE":
        order = get_object_or_404(Order, id=id)
        if request.user.groups.filter(name="Manager").exists():
            order.delete()
            return Response("Order deleted", status=status.HTTP_200_OK)
        return Response(
            "You must be a manager to delete an order.",
            status=status.HTTP_403_FORBIDDEN,
        )
