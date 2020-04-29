from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect
from .models import OrderItem,Topping, Menu, Order, Type
from django.contrib.auth.models import User
from datetime import datetime
import re
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout


def homepage(request):
    return render(request,"orders/homepage.html")

# Create your views here.
@login_required(login_url='login')
def cart(request):
    try:
        user = request.user
        order = Order.objects.get(user=user.id,is_pay=False)
        oi = OrderItem.objects.filter(order=order).all()
    except User.DoesNotExist:
        raise Http404("User does not exist")
    except Order.DoesNotExist:
        return redirect(f'profile')
    except OrderItem.DoesNotExist:
        oi = []
    if order.is_pay:
        return redirect(f'profile')

    context = {
    "order":order,
    "orderItem": oi,
    }
    return render(request,"orders/shoppingCart.html",context)

def login(request):
    if request.method == "GET":
        return render(request,"orders/login.html",context=None)
    username = request.POST["username"]
    password = request.POST["pass"]
    try:
        user = authenticate(request, username=username, password=password)
    except User.DoesNotExist:
        context = {
        "msg":"username or password are wrong..."
        }
        return render(request,"orders/login.html",context)
    if user is not None:
        auth_login(request, user)
        return redirect(f'profile')
    else:
        return render(request,"orders/login.html",{"msg":"username or password are wrong..."})

@login_required(login_url='login')
def logout(request):
    auth_logout(request)
    return render(request,"orders/homepage.html")

def register(request):
    if request.method == "GET":
        return render(request,"orders/register.html")
    email = request.POST["email"]
    fname = request.POST["fname"]
    lname = request.POST["lname"]
    password = request.POST["password"]
    username = request.POST["username"]
    newuser = User.objects.create_user(username=username,email=email,password=password)
    newuser.last_name = lname
    newuser.first_name = fname
    newuser.save()
    auth_login(request, newuser)
    return redirect(f'profile')


#check if valid name and return json
def validUserName(request):
    username = request.GET.get('username', None)
    data = {
        'is_taken': User.objects.filter(username=username).exists()
    }
    return JsonResponse(data)

@login_required(login_url='login')
def profile(request):
    try:
        user = request.user
        orders = Order.objects.filter(user=user.id).all().order_by('is_pay')
        msg="You didn't order anything yet..."
    except User.DoesNotExist:
        return render(request,"orders/homepage.html")
    except Order.DoesNotExist:
        msg = "You didn't order anything yet..."
        orders = ""
    context = {
    "user":user,
    "orders":orders,
    "msg":msg
    }
    return render(request,"orders/profile.html",context)

@login_required(login_url='login')
def selection(request):
    types = Type.objects.all()
    context = {
    "types":types,
    "type":"true"
    }
    return render(request,"orders/selection.html",context)

@login_required(login_url='homepage')
def selectionType(request,type_id):
    if request.method == "GET":
        try:
            type = Type.objects.get(pk=type_id)
        except Type.DoesNotExist:
            raise Http404("Type does not exist")
        try:
            menus = Menu.objects.filter(type=type.id)
        except Menu.DoesNotExist:
            raise Http404("Menus does not exist")
        if "pizza" in type.name:
            toppings = Topping.objects.all()
            context = {
            "menus":menus,
            "type":type,
            "toppings":toppings
            }
        else:
            context = {
            "menus":menus,
            "type":type
            }
        return render(request,"orders/selection.html",context)
    elif request.method == "POST":
        return redirect(f'addOrderItem')


#get menu id from selection page and add it to the cart
def addMenutoOrder(request):
    if request.method == "GET":
        menu_id = request.GET.get('menuid', None)
        islg = request.GET.get('islg', None)
        try:
            menu = Menu.objects.get(id=menu_id)
        except Menu.DoesNotExist:
            raise ValueError(f"I'm a error message")
        user = request.user
        if Order.objects.filter(user=user.id).exclude(is_pay=True).exists():
            order = Order.objects.get(user=user.id,is_pay=False)
        else:
            order = Order(timedate=datetime.today().strftime('%H:%M %d/%m/%y'),user=user,sum_price=0,is_pay=False)
            order.save()
            order = Order.objects.get(user=user.id,is_pay=False)
        if islg == "true":
            if OrderItem.objects.filter(menu=menu,islg=True,order=order).exists():
                oi = OrderItem.objects.get(menu=menu,islg=True,order=order)
                oi.quantity += 1
            oi = OrderItem(menu=menu,quantity=1,islg=True,sum_price=menu.price.lg,order=order)
        else:
            if OrderItem.objects.filter(menu=menu,islg=False,order=order).exists():
                oi = OrderItem.objects.get(menu=menu,islg=False,order=order)
                oi.quantity += 1
            oi = OrderItem(menu=menu,quantity=1,islg=False,sum_price=menu.price.sm,order=order)
        oi.save()
        order.sum_price += oi.sum_price
        order.save()
        data = {
            'menuadded': "menu added succssesfully!"
        }
        return JsonResponse(data)

#adding pizza with toppings to the order
def AddPizzaOrder(request):
    if request.method == "GET":
        menu_id = request.GET.get('menuid', None)
        islg = request.GET.get('islg', None)
        toppings = request.GET.get("toppings",None)
        try:
            menu = Menu.objects.get(id=menu_id)
        except Menu.DoesNotExist:
            raise ValueError(f"I'm a error message")
        user = request.user
        #search exist orders
        if Order.objects.filter(user=user.id).exclude(is_pay=True).exists():
            order = Order.objects.get(user=user.id,is_pay=False)
        else:
            order = Order(timedate=datetime.today().strftime('%H:%M %d/%m/%y'),user=user,sum_price=0,is_pay=False)
            order.save()
            order = Order.objects.get(user=user.id,is_pay=False)
        if islg == "true":
            oi = OrderItem(menu=menu,quantity=1,islg=True,sum_price=menu.price.lg,order=order)
        else:
            oi = OrderItem(menu=menu,quantity=1,islg=False,sum_price=menu.price.sm,order=order)
        oi.save()
        toppingsid = [int(s) for s in re.findall(r'\b\d+\b', toppings)]
        for topping in toppingsid:
            oi.toppings.add(topping)
        oi.save()
        order.sum_price += oi.sum_price
        order.save()
        data = {
            'menuadded': "good job we added an order"
        }
        return JsonResponse(data)


def DeleteItem(request):
    if request.method == "GET":
        orderitemId = request.GET.get("orderItem",None)
        try:
            orderitem = OrderItem.objects.get(id=orderitemId)
        except OrderItem.DoesNotExist:
            raise Http404("This item is not exist")
        order = Order.objects.get(id=orderitem.order.id)
        if orderitem.islg:
            order.sum_price -= orderitem.menu.price.lg
            orderitem.delete()
        else:
            order.sum_price -= orderitem.menu.price.sm
            orderitem.delete()
        if order.sum_price < 0:
            order.sum_price=0.0
        order.save()
        return JsonResponse({'msg':'delete'})

def AddItem(request):
    if request.method == "GET":
        orderitemId = request.GET.get("orderItem",None)
        try:
            orderitem = OrderItem.objects.get(id=orderitemId)
        except OrderItem.DoesNotExist:
            raise Http404("This item is not exist")
        orderitem.quantity += 1
        order = Order.objects.get(id=orderitem.order.id)
        if orderitem.islg:
            orderitem.sum_price = orderitem.sum_price+orderitem.menu.price.lg
            order.sum_price += orderitem.menu.price.lg
        else:
            orderitem.sum_price = orderitem.sum_price+orderitem.menu.price.sm
            order.sum_price += orderitem.menu.price.sm
        orderitem.save()
        order.save()
        return JsonResponse({'msg':orderitem.quantity})

def MinusItem(request):
    if request.method == "GET":
        orderitemId = request.GET.get("orderItem",None)
        try:
            orderitem = OrderItem.objects.get(id=orderitemId)
        except OrderItem.DoesNotExist:
            raise Http404("This item is not exist")
        orderitem.quantity -= 1
        order = Order.objects.get(id=orderitem.order.id)
        if orderitem.islg:
            orderitem.sum_price = orderitem.sum_price-orderitem.menu.price.lg
            order.sum_price -= orderitem.menu.price.lg
        else:
            orderitem.sum_price = orderitem.sum_price-orderitem.menu.price.sm
            order.sum_price -= orderitem.menu.price.sm
        orderitem.save()
        order.save()
        return JsonResponse({'msg':orderitem.quantity})

def PayOrder(request):
    orderid = request.GET.get('order',None)
    try:
        order = Order.objects.get(id=orderid)
    except Order.DoesNotExist:
        raise Http404("This order is not exist")
    order.is_pay = True
    order.save()
    return JsonResponse({'msg':'M&Y thank you for your order... Your order in her way!'})


def ToppingsToMenu(request):
    oid = request.GET.get('oid',None)
    try:
        oi = OrderItem.objects.get(id=oid)
    except Order.DoesNotExist:
        raise Http404("This order is not exist")
    toppings = oi.toppings.all()
    str = ""
    names = []
    if toppings is not None:
        for t in toppings:
            names.append(t.name)
    str = ",".join(names)
    if str is "":
        str = "no toppings..."
    return JsonResponse({'msg':str})


@login_required(login_url='login')
def CheckCartEmpty(request):
    try:
        user = request.user
        order = Order.objects.get(user=user.id,is_pay=False)
        items = OrderItem.objects.filter(order=order).all()
    except User.DoesNotExist:
        raise Http404("User does not exist")
    except Order.DoesNotExist:
        raise Http404("Order does not exist")
    except OrderItem.DoesNotExist:
        items = []
    if order.is_pay:
        raise Http404("Order exist, but pay...")
    if items.count() > 0:
        full = True
    else:
        full = False
    data = {
    "full":full
    }
    return JsonResponse(data)
