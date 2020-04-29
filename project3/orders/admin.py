from django.contrib import admin


from .models import Menu, Type, Price, Order, OrderItem, Topping
# Register your models here.


admin.site.register(Menu)
admin.site.register(Type)
admin.site.register(Price)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Topping)
