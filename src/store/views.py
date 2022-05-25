from urllib import request
from django.shortcuts import render,get_object_or_404,redirect
from .models import (Category,Item,OrderItem,Order,Address,Payment,
                    Wishlist,ProductReview,Coupon)
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from django.contrib import messages
from django.views.generic import View
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from store.forms import (CheckoutForm,ReviewAdd,RefundForm,CouponForm)
from django.conf import settings
from django.http import JsonResponse
from pypaystack import Transaction
from django.db.models import Q
import string
import json
import random
import datetime
from core.models import Post
# Create your views here.


def homefunc(request):
    categories = Category.objects.all().order_by('name')
    product  = Item.objects.all().order_by('-id')

    page = request.GET.get('page', 1)

    paginator = Paginator(product, 8)
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    post =Post.objects.order_by('-publish_date').filter(publish_date__lt=timezone.now())

    page = request.GET.get('page', 1)

    paginator = Paginator(post, 10)
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    context ={
        'categories' : categories,
        'page_obj':page_obj,
        'posts':posts,
        

    }
    return render(request,"store/store-page.html",context)

def productFunc(request,slug):
    item=get_object_or_404(Item,slug=slug)
    related_products=Item.objects.filter(category=item.category)
    reviewForm=ReviewAdd(request.POST or None)
    comments = ProductReview.objects.filter(product=item)
    
    if reviewForm.is_valid():
        # save the form data to model
        reviews = ProductReview()
        reviews.user = request.user
        reviews.product=item
        reviews.review_text=request.POST['review_text']
        reviews.review_rating=request.POST['review_rating'],
        reviews.save()
 
    
    context = {
        'item':item,
        'related_products':related_products,
        'reviewForm':reviewForm,
        'comments':comments

    }

    return render(request,"store/product-page.html",context)

@login_required
def add_to_cart(request,slug):
    item = get_object_or_404(Item,slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False)
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order= order_qs[0]
        #check if order item is already ordered

        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated.")
            return redirect("store:cart-order")
        else:
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart.")
            return redirect("store:cart-order")

    #if order doesn't exist
    else:
        ordered_date=timezone.now()
        order =Order.objects.create(user=request.user,ordered_date=ordered_date, delivery_date= ordered_date )
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart.")
        return redirect("store:cart-order")

@login_required
def remove_from_cart(request,slug):

    item = get_object_or_404(Item,slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order= order_qs[0]
        #check if order item is already ordered

        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                        item=item,
                        user=request.user,
                        ordered=False)[0]
            order.items.remove(order_item)
            order_item.delete()
            messages.info(request, "This item was removed from your cart.")
        else:
        # item is not part of cart message
            messages.info(request, "This item was not in your cart")
            return redirect('store:cart-order')
    else:
        # no order message
        messages.info(request, "You do not have an active order")
        return redirect('store:Items_detail',slug=slug)
    return redirect('store:Items_detail',slug=slug)

@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "This item quantity was updated.")
            return redirect("store:cart-order")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect('blog:Items_detail',slug=slug)

    else:
        messages.info(request, "You do not have an active order")
        return redirect('store:cart-order')

class cartfunc(LoginRequiredMixin,View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            wlist=Wishlist.objects.filter(user=self.request.user).order_by('-id')
            context = {
                'object': order,
                'wlist':wlist
            }
            return render(self.request, 'store/cart-page.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return render(self.request, 'store/cart-page.html')


def search(request):
    categorys = Category.objects.all().order_by('name')
    

    #Search
    query = request.GET.get('q','')
    #The empty string handles an empty "request"
    if query:
        queryset = (Q(name__icontains=query)|
                    Q(description__icontains=query)|
                    Q(category__name__icontains=query))
        results =  Item.objects.filter(queryset).distinct()
    

    else:
       results = []
    queryset_cat =( Q(category__name__icontains=query))
    related_product = Item.objects.filter(queryset_cat)

    return render(request, 'core/shop.html',{        
                                                'query':query,
                                                'results':results,
                                                'categorys' : categorys,
                                                'related_product':related_product,
   } )

def category(request,category_slug):
    #Category
    categorys = Category.objects.all().order_by('name')
    category = None

    items=Item.objects.all().order_by('-id')
    minprice = request.GET.get('minPrice')
    maxprice = request.GET.get('maxPrice')

    if category_slug:
        category = get_object_or_404(categorys,slug=category_slug)
        item = Item.objects.filter(category=category)
        itemed=item.filter( Q(price__range=(minprice,maxprice))|
                            Q(discount_price__range=(minprice,maxprice))
                            )
        
    #pagination and item
   

    page = request.GET.get('page', 1)

    if maxprice:

        paginator = Paginator(itemed, 12)
        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
    else:
        paginator = Paginator(item, 12)
        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)


    return render(request,'store/shop.html',{   
                                                    'category':category,
                                                    'page_obj':page_obj,
                                                    'categorys' : categorys,
                                                    
                                                    

                                                   } )



# Create your views here.
def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid

class CheckoutView(LoginRequiredMixin,View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckoutForm()
            context = {
                'order': order,
                'form':form,
                'couponform' : CouponForm(),
                'DISPLAY_COUPON_FORM': True,   
            }
            shipping_address_qs = Address.objects.filter(
                user=self.request.user,
                address_type='S',
                default=True
            )
            if shipping_address_qs.exists():
                context.update(
                    {'default_shipping_address': shipping_address_qs[0]})
            
            return render(self.request, 'store/checkout-page.html',context)
        except ObjectDoesNotExist:
            messages.info(self.request, "you do not have an active order")
            return redirect("core:checkout")

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():

                use_default_shipping = form.cleaned_data.get(
                    'use_default_shipping')
                if use_default_shipping:
                    #print("Using the default shipping address")
                    messages.info(self.request, "Using the default shipping address")
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        address_type='S', 
                        default=True
                    )
                    if address_qs.exists():
                        shipping_address = address_qs[0]
                        order.shipping_address = shipping_address
                        order.save()
                    else:
                        messages.info(
                            self.request, "No default shipping address available")
                        return redirect('core:checkout')
                else:
                    print("User is entering a new shipping address")
                    name = form.cleaned_data.get(
                        'name')
                    email = form.cleaned_data.get(
                        'email')
                    address = form.cleaned_data.get(
                        'address')
                    
                    phone_no=form.cleaned_data.get(
                        'phone_no')

                    if is_valid_form([address, name,email,phone_no]):
                        shipping_address = Address(
                            user=self.request.user,
                            name=name,
                            email=email,
                            phone_no=phone_no,
                            address=address,
                            address_type='S'
                        )
                        shipping_address.save()

                        order.shipping_address = shipping_address
                        order.save()

                        set_default_shipping = form.cleaned_data.get(
                            'set_default_shipping')
                        if set_default_shipping:
                            shipping_address.default = True
                            shipping_address.save()

                    else:
                        messages.info(
                            self.request, "Please fill in the required shipping address fields")
                            

                payment_option = form.cleaned_data.get('payment_option')
                
                
                if payment_option == 'P':
                    return redirect('store:payment', payment_option='Paystack')
                elif payment_option == 'C':
                    return redirect('core:flutter', payment_option='flutter')
                else:
                    messages.warning(
                        self.request, "Invalid payment option selected")
                    return redirect('core:checkout')
            else:
                 print("User is entering a new user")
        
        except ObjectDoesNotExist: 

            messages.error(self.request, "You do not have an active order")
            return redirect("core:order-summary")



def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

class Paymentview(LoginRequiredMixin,View):
    def get(self,*args,**kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if order.shipping_address:
                pk_public = settings.PAYSTACK_PUBLIC_KEY
                context = {
                    'order': order,
                    'pk_public':pk_public,
                    'DISPLAY_COUPON_FORM': False

                    }
                return render(self.request, 'store/paystack.html ',context)
            else:

                messages.warning(self.request, "You do have not added a billing addres")
                return redirect("core:order-summary")
        except ObjectDoesNotExist:
            pass

def verify(request,id):
    transaction = Transaction(authorization_key=settings.PAYSTACK_SECRET_KEY)
    response= transaction.verify(id)
    data = JsonResponse(response,safe=False)

    order =Order.objects.get(user=request.user, ordered=False)
    payment = Payment()
    payment.stripe_charge_id = response
    payment.user =request.user
    payment.amount = order.get_total()
    payment.save()

    order_items = order.items.all()
    order_items.update(ordered =True)
    for item in order_items:
        item.save()
    order.ordered =True
    order.payment = payment
    order.ref_code = create_ref_code()

    current_time = order.delivery_date
    current_date_temp = datetime.datetime.strftime(current_time,"%d/%m/%Y")
    d_day =current_time + datetime.timedelta(days=5)
    order.delivery_date =d_day
    order.save()

    messages.success(request,'your order was succesful ' + order.ref_code )
    return redirect ('/marketplace')


