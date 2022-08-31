import json
from django.shortcuts import render
from django.http import JsonResponse
import json
from .models import *
from users.decorators import unauthenticated_user,allowed_users,admin_only

# Create your views here.



def products(request):
    products = Product.objects.all()
    context = {'products':products}
    return render(request,'Products/products_home.html',context )



# def product_store(request):
#     context = {}
#     return render(request,'OurProducts/product_store.html',context)


def product_checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer = customer, complete = False)
        items = order.orderitem_set.all()
    else:
        items = []
        order = {'get_cart_total':0, 'get_cart_items':0}

    context = {'items':items,'order':order}
    return render(request,'Products/product_checkout.html',context)


def product_cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer = customer, complete = False)
        items = order.orderitem_set.all()
    else:
        items = []
        order = {'get_cart_total':0, 'get_cart_items':0}

    context = {'items':items,'order':order}
    return render(request,'Products/product_cart.html',context)

def updateItem(request):
    data = json.loads(request.data)
    action = data['action']
    productId = data['productId']

    print('Action:',action)
    print('productId:',productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer = customer, complete = False)
    
    orderItem, created = OrderItem.objects.get_or_created(prder=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity +1)
    elif action == 'remove':
         orderItem.quantity = (orderItem.quantity -1)

    orderItem.save()

    if orderItem.quantity <=0:
        orderItem.delete()
        
    return JsonResponse('Items was added', safe = False )