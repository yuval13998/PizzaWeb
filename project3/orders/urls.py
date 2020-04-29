from django.urls import path

from . import views

urlpatterns = [
    path("cart", views.cart, name="cart"),
    path("login",views.login,name="login"),
    path("logout",views.logout,name="logout"),
    path("register",views.register,name="register"),
    path("homepage",views.homepage,name="homepage"),
    path("profile",views.profile,name="profile"),
    path("selection",views.selection,name="selection"),
    path("<int:type_id>/selection",views.selectionType,name="selectionType"),
    path("addMenutoOrder",views.addMenutoOrder,name="addMenutoOrder"),
    path("validUserName",views.validUserName,name="validUserName"),
    path("DeleteItem",views.DeleteItem,name="DeleteItem"),
    path("AddItem",views.AddItem,name="AddItem"),
    path("MinusItem",views.MinusItem,name="MinusItem"),
    path("PayOrder",views.PayOrder,name="PayOrder"),
    path("CheckCartEmpty",views.CheckCartEmpty,name="CheckCartEmpty"),
    path("AddPizzaOrder",views.AddPizzaOrder,name="AddPizzaOrder"),
    path("ToppingsToMenu",views.ToppingsToMenu,name="ToppingsToMenu"),


]
