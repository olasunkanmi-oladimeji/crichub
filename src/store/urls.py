from store.views import (homefunc,productFunc,
                        add_to_cart,remove_from_cart,remove_single_item_from_cart
                        ,cartfunc,CheckoutView,Paymentview,verify,
                        category,search)
from django.urls import path

app_name="store"

urlpatterns = [
    path("", homefunc, name="store"),
    path('product-category/<slug:category_slug>',category,name='category_detail'),
    path('search',search,name='search'),
    path('<slug>/', productFunc, name="Items_detail"),
    path('Add-To-cart/<slug>',add_to_cart,name='add_to_cart'),
    path('Remove-FROM-cart/<slug>',remove_from_cart,name='remove_from_cart'),
    path('Remove-Item-cart/<slug>',remove_single_item_from_cart,name='remove_item_cart'),
    path('order-cart', cartfunc.as_view(),name='cart-order'),
     path('checkout',CheckoutView.as_view(),name='checkout'),
    path('payment/<payment_option>',Paymentview.as_view(),name='payment'),
    path('payment/verify/<id>', verify,name='verify'),

    
]
