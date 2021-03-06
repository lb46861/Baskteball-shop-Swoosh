from hashlib import blake2b
from django.http import HttpResponse
from django.shortcuts import redirect, render
from .forms import *
from .models import Product, ProductDetail, Order, OrderDetails
import uuid, random
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.views import View
import stripe
from django.utils import timezone
from django.conf import settings
from .filters import ProductFilter
from django.core.paginator import Paginator
stripe.api_key = settings.STRIPE_SECRET_KEY


def register(request):   
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        if request.user.is_authenticated:
            return redirect('productlist')
        else:
            form = UserForm()
    
    return render(request, 'account/register.html', {'form':form})


def deleteproduct(product):
    product = Product.objects.get(id=product)
    product.delete()
    return 'Product successfully deleted!'

@login_required(login_url='login')
def editproduct(request, id):
    product = Product.objects.get(id = id)
    form = ProductForm(instance=product)
    info = ''
    if request.method=='POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            info = 'Product successfully edited!'

    data = {
        'form': form,
        'info': info
    }
    return render(request, "admin/editproduct.html", data)


def editproductdetail(request):
    form = ProductDetailForm()
    if request.method=='POST':
        form = ProductDetailForm(request.POST)
        if form.is_valid():
            product = Product.objects.get(id = form['product_id'].value())
            size = Size.objects.get(id = form['size_id'].value())
            quantity = form['quantity'].value()
            myProductDetail, create = ProductDetail.objects.get_or_create(product_id = product, size_id = size)
            myProductDetail.quantity = quantity
            myProductDetail.save()
            messages.success(request, 'Product detail edited!')
            return redirect('productlist')
        else:
            return HttpResponse('Something went wrong!')
    data = {
        'form': form,
    }
    return render(request, "admin/editproductdetail.html", data)

@login_required(login_url='login')
def editorder(request, id):
    info = ''
    order = Order.objects.get(id = id)
    form = OrderForm(instance=order)
    if request.method=='POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            info = 'Product successfully edited!'

    data = {
        'info': info,
        'form': form,
        'order': order
    }
    return render(request, "admin/editorder.html", data)

@login_required(login_url='login')
def addproduct(request):
    form = ProductForm()

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product successfully added!')
            return redirect('productlist')
        else:
            return HttpResponse('Something went wrong!')

    return render(request, 'admin/addproduct.html', {'form':form})

def productlist(request):
    info = ''
    if request.method == 'POST':
        product = request.POST['product']
        action = request.POST['action']
        if action == 'delete':
            info = deleteproduct(product)
      
    products = Product.objects.all()
    myFilter = ProductFilter(request.GET, queryset=products)
    products = myFilter.qs
    paginator = Paginator(products, 5)
    page = request.GET.get('page')
    products_pages = paginator.get_page(page)
    data = {
        'info':info,
        'products': products,
        'myFilter': myFilter,
        'products_pages': products_pages
    }
    return render(request, 'products/productlist.html', data)

@login_required(login_url='login')
def addToCart(request, myProduct):
    customer = request.user
    order, created = Order.objects.get_or_create(customer_id = customer, status='cart')
    itemDetail, created = OrderDetails.objects.get_or_create(order_id=order, product=myProduct)
    if myProduct.quantity > 0:
        itemDetail.quantity += 1
        itemDetail.save()
        myProduct.quantity -= 1
        myProduct.save()
        return 'Product addedd successfully!'
    else:
        return 'No more products left in stock!'


def removeOne(request, myProduct):
    customer = request.user
    order = Order.objects.get(customer_id = customer, status='cart')
    itemDetail = OrderDetails.objects.get(order_id=order, product=myProduct)
    if itemDetail.quantity == 1:
        itemDetail.delete()
    else:
        itemDetail.quantity -= 1
        itemDetail.save()
    myProduct.quantity += 1
    myProduct.save()
    return 'Product removed successfully!'



def removeAll(request, myProduct):
    customer = request.user
    order = Order.objects.get(customer_id = customer, status='cart')
    itemDetail = OrderDetails.objects.get(order_id=order, product=myProduct)
    while itemDetail.quantity > 0:
        itemDetail.quantity -= 1
        myProduct.quantity += 1
    itemDetail.delete()
    myProduct.save()
    return 'Products removed successfully!'


def isAvailable(productdetail):
    available = 0
    for prod in productdetail:
        if prod.quantity > 0:
            available += 1
            break
    return available

def productdetail(request, id):
    stock = ''
    if request.method == 'POST' and request.user.is_authenticated:
        productDetailID = request.POST['myproduct']
        myProduct = ProductDetail.objects.get(id = productDetailID)
        option = request.POST['option']
        if option == 'tocart':
            stock = addToCart(request, myProduct)
        elif option == 'buy':
            addToCart(request, myProduct)
            return redirect('mycart')
    elif request.method == 'POST':
        return redirect('login')

    product = Product.objects.get(id = id)
    productdetail = ProductDetail.objects.filter(product_id = id)
    available = isAvailable(productdetail)
    similiarProducts = Product.objects.filter(category_id = product.category_id).exclude(id=product.id)

    data = {
        'product': product,
        'productdetail' : productdetail,
        'available': available,
        'similiarProducts': similiarProducts,
        'stock': stock
    }
    return render(request, 'products/productdetail.html',data)

@login_required(login_url='login')
def cart(request):
    stock = ''
    if request.method == 'POST':
        productDetailID = request.POST['myproduct']
        myProduct = ProductDetail.objects.get(id = productDetailID)
        option = request.POST['option']
        if option == 'add':
            stock = addToCart(request, myProduct)
        elif option == 'removeOne':
            stock = removeOne(request, myProduct)
        elif option == 'removeAll':
            stock = removeAll(request, myProduct)

    customer = request.user
    order, created = Order.objects.get_or_create(customer_id = customer, status='cart')
    cartItems = order.orderdetails_set.all()
    data = {
        'cartItems': cartItems,
        'order': order,
        'stock': stock
    }

    return render(request, 'account/mycart.html', data)

@login_required(login_url='login')
def order(request, id):
    order = Order.objects.get(id = id)
    orderItems = order.orderdetails_set.all()
    data = {
        'order': order,
        'orderItems': orderItems,
    }
    return render(request, 'account/order.html', data)


@login_required(login_url='login')
def myorders(request):
    customer = request.user
    orders = Order.objects.filter(customer_id = customer, status = 'payed')
    data ={
        'orders': orders,
    }
    return render(request, 'account/myorders.html', data)


def deleteorder(order):
    order = Order.objects.get(id=order)
    order.delete()
    return 'Product successfully deleted!'

@login_required(login_url='login')
def allorders(request):
    info = ''
    orders = Order.objects.filter(status = 'payed')
    if request.method == 'POST':
        order = request.POST['order']
        action = request.POST['action']
        if action == 'delete':
            info = deleteorder(order)
    data ={
        'orders': orders,
        'info': info
    }
    return render(request, 'admin/allorders.html', data)

@login_required(login_url='login')
def profile(request):
    msg = ''
    if request.method == 'POST':
        action = request.POST['action']
        if action == 'save':
            form = UpdateUserForm(request.POST, instance=request.user)
            if form.is_valid():
                form.save()
                msg = 'Your profile is updated successfully!'

        elif action == 'reset':
            form = UpdateUserForm(instance=request.user)

    else:
        form = UpdateUserForm(instance=request.user)
    data = {
        'msg': msg,
        'form': form
    }

    return render(request, 'account/myaccount.html', data)



class ChangePasswordView(SuccessMessageMixin, PasswordChangeView):
    template_name = 'account/change_password.html'
    success_message = "Successfully Changed Your Password!"
    success_url = reverse_lazy('myaccount')


mycheckout_session = ''
def success_payment(request, session_id):
    if(mycheckout_session == session_id):
        customer = request.user
        order = Order.objects.get(customer_id=customer, status='cart')
        number = uuid.uuid1(random.randint(0, 281474976710655))
        order.number = number
        order.status = 'payed'
        order.date = timezone.now()
        order.save()
        data =  {
            'order': order,
            'cartItems': order.orderdetails_set.all()
        }
        return render(request, 'account/success_payment.html', data)
    else:
        return HttpResponse(status = 404)



class CreateCheckoutSessionView(View):
    def post(self, request, *args, **kwargs):
        customer = request.user
        order =  Order.objects.get(customer_id= customer, status='cart')
        YOUR_DOMAIN = 'http://localhost:8000'
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount' : order.get_total_stripe,
                        'product_data': {
                            'name': f"Order ID: {order.id}",
                        },
                    },
                    'quantity': 1,
                },
            ],
            metadata = {
                'order_id': order.id,
            },
            mode='payment',
            success_url= YOUR_DOMAIN + "/success/{CHECKOUT_SESSION_ID}/",
            cancel_url = YOUR_DOMAIN + '/cart/',
        )
        global mycheckout_session
        mycheckout_session = checkout_session.id
        return redirect(checkout_session.url, code=303)
