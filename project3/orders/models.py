from django.db import models
from django.contrib.auth.models import User


class Type(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return f"{self.name}"

class Price(models.Model):
    lg = models.FloatField() #if there are only one price for item sm=0
    sm = models.FloatField()

    def __str__(self):
        if self.sm != 0.0:
           return f"{self.sm}$\{self.lg}$"
        return f"{self.lg}$"

class Menu(models.Model):
    name = models.CharField(max_length=30)
    price = models.OneToOneField(Price,on_delete=models.CASCADE)
    type = models.ForeignKey(Type,on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name}, {self.type}, {self.price}."

class Topping(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return f"{self.name}"

class Order(models.Model):
    timedate = models.CharField(max_length=30)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    sum_price = models.FloatField()
    is_pay = models.BooleanField()

    def __str__(self):
        return f"{self.user.first_name.title()} {self.user.last_name.title()} Order"

class OrderItem(models.Model):
    menu = models.ForeignKey(Menu,on_delete=models.CASCADE)
    quantity = models.IntegerField()
    islg = models.BooleanField()
    sum_price = models.FloatField()
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    toppings = models.ManyToManyField(Topping, blank=True, related_name="orders")


    def __str__(self):
        return f"{self.menu} * {self.quantity}"
