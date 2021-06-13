from django.shortcuts import render, redirect, get_object_or_404
#from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required
from django.db.models import F
#from .models import Product, Post, Point, Order, Category, Cart
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import OrderForm, Order1Form
# Create your views here.
from .models import Product,Category,Point, Cart, Order, Post 
from django.utils import timezone

def index(request):
    products = Product.objects.order_by('-pub_date')
    categories = Category.objects.all()
    #orders= Order.objects.all()
    lank_products = Product.objects.order_by('-hit')[:4]
    context = {'lank_products':lank_products, 'products': products, 'categories': categories}
    #context = {'categories': categories}
    return render(request, 'shop/index.html', context)#index use products,orders from table product.order



def profile(request, pk):#user.pk = pk 1 david
    user = User.objects.get(pk=pk)
    categories = Category.objects.all()
    
    context = {'user': user, 'categories': categories}
    return render(request, 'shop/profile.html', context)

def notice(request):
    posts = Post.objects.all()
    paginator = Paginator(posts, 3)
    page = request.GET.get('page')

    categories = Category.objects.all()

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    context = {'posts':posts, 'categories': categories}
    return render(request, 'shop/notice.html', context)

 

def notice_detail(request, pk):
    categories = Category.objects.all()
    post = Post.objects.get(pk=pk)
    context = {"post": post, "categories":  categories}
    return render(request, 'shop/notice_detail.html', context)



def show_category(request, category_id):#category_id는 index에서 받아 온 숫자를 URLS에서 할당함 여기서 1 
    categories = Category.objects.all()#카테로리 전체 한국 일본 중국 요리 전부
    category = Category.objects.get(pk=category_id)#pk가 1인 object 곧 KOREAN FOOD(한국요리) 
    #products = Product.objects.filter(category=category).order_by('pub_date')#category가 category(KOREAN FOOD)인
    #product objects 할당. product에 category_id만 있지만 category에 연결된 외래키이므로 이렇게 사용가능한것같다
    # 곧 product에 category가 한국요리 전체를 products에 할당해서 쓰겠다 
    # 모든 한국요리 가격 수량 해설 등 모든 것 가짐 즉 카테로리를 한국 요리로 누르고 왔으니 그 요리 정보를 여기에 담음

    products = Product.objects.filter(category_id=category_id).order_by('pub_date')
    lank_products = Product.objects.filter(category_id=category_id).order_by('-hit')[:4]# 그 중에서 인기 순 정렬
    paginator = Paginator(products, 7)
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    context = {'lank_products': lank_products, 'products': products, 'category': category, 'categories': categories}
    return render(request, 'shop/category.html', context)#이런 context를 category.html에서 사용할 거야


def product_detail(request, pk):#category.html에서 product.pk로 urls.py로 가서는 pk로 받아서 여기로 가져옴,pk =5 갈비
    categories = Category.objects.all()#카테로리 전체 한국 일본 중국 요리 전부
    product = Product.objects.get(pk=pk)#product에서 pk가 category.html에서 받아온 product.pk 곧 url에서 pk로 받은 
    #곧 n번째 pk =5 요리 예 갈비인 product objects - 갈비 가격 수량 등
    category = Category.objects.get(pk=product.category.pk)
    #category pk는 1,2,3, 한국요리, 일본요리,중국요리 중 하나인데 
    #product.category.5는 ? category.5는 product.pk가 5인 category라면 말이 된다. ????
    #
    Product.objects.filter(pk=pk).update(hit=product.hit+1)#5 갈비 
    point = int(product.price * 0.01)
    quantity_list = []
    for i in range(1, product.quantity) :
        quantity_list.append(i)
    context = {"quantity_list": quantity_list, "product": product, "point": point, "category": category, "categories": categories}
    return render(request, 'shop/detail.html', context)


def cart(request, pk):#user.pk =1 or 16
    categories = Category.objects.all()
    user = User.objects.get(pk=pk)#user david 1111 objects
    cart = Cart.objects.filter(user=user)#david cart 
    #paginator = Paginator(cart, 10)
    #page = request.GET.get('page')
    #try:
        #cart = paginator.page(page)
    #except PageNotAnInteger:
        #cart = paginator.page(1)
    #except EmptyPage:
       #cart = paginator.page(paginator.num_pages)
    context = {'user': user, 'cart': cart, 'categories': categories}
    return render(request, 'shop/cart.html', context)


def delete_cart(request, pk): #user.pk =1 or 16 david
    
    user = request.user#david
    cart = Cart.objects.filter(user=user)#
    quantity = 0

    if request.method == 'POST':
     
        pk =int(request.POST.get('product'))
        product = Product.objects.get(pk=pk)
        for i in cart:
            if i.products == product :
                quantity =  i.quantity

        if quantity > 0 :
            product = Product.objects.filter(pk=pk)
            cart = Cart.objects.filter(user=user, products__in=product)
            cart.delete()
            return redirect('shop:cart', user.pk)

       

  


#####################################################################################################
 
@login_required
def cart_or_buy(request, pk):#product.pk를 urls통해 pk로 받음 갈비
    quantity = int(request.POST.get('quantity'))#detail.html에서 선택한 quantity를 받음.
    product = Product.objects.get(pk=pk)#pk=5인 objects 갈비 가격 재고수량....
    user = request.user#login user
    categories = Category.objects.all()#
    initial = {'name': product.name, 'amount': product.price, 'quantity': quantity}#갈비 가격 그리고 카트에 담은 수
    cart = Cart.objects.filter(user=user)#user가 login한 user의 카트 objects - user, products, quantity
    order = Order.objects.filter(user=user) 
    if request.method == 'POST':
        if 'add_cart' in request.POST:
            for i in cart :
                if i.products == product:#카트에 product가 갈비가 있으면  
                    product = Product.objects.filter(pk=pk)#갈비 정보
                    Cart.objects.filter(user=user, products__in=product).update(quantity=F('quantity') + quantity)
                    messages.success(request,'장바구니 등록 완료')
                    return redirect('shop:cart', user.pk)


            Cart.objects.create(user=user, products=product, quantity=quantity)
            messages.success(request, '장바구니 등록 완료')
            return redirect('shop:cart', user.pk)

        elif 'buy' in request.POST:
            form = OrderForm(request.POST, initial=initial)
            if form.is_valid():
                order = form.save(commit=False)
                order.user = request.user
                order.amount = product.price
                order.name = product.name
                order.order_date=timezone.now()
                order.products=product
                order.number=1234
                
                order.save()
                return redirect('shop:Norder_list', user.pk)

            else:
                form = OrderForm(initial=initial)

            #context = {'user': user, 'cart': cart, 'categories': categories, 'product':product}
            context = {'product':product}
            return render(request, 'shop/Norder_list.html', context)
               

def Norder_list(request, pk):
    categories = Category.objects.all()
    user = User.objects.get(pk=pk)
    orders = Order.objects.filter(user=user)
    paginator = Paginator(orders, 5)
    page = request.GET.get('page')
    try:
        orders = paginator.page(page)
    except PageNotAnInteger:
        orders = paginator.page(1)
    except EmptyPage:
        orders = paginator.page(paginator.num_pages)
    context = {'user': user, 'orders': orders, 'categories': categories}
    return render(request, 'shop/Norder_list.html', context)               