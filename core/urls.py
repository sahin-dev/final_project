from django.urls import path,include
from core.views import index,payment,dashboard,order_detail, product_list_view,invoice_view, category_list_view,category_product_list_view,vendor_list_view,vendor_detail_view,product_detail_view,tag_list,ajax_add_review,search_view,filter_product,add_to_cart,cart_view,delete_item_from_cart,update_cart,checkout_view,payment_failed_view,payment_completed_view,add_to_wishlist,wishlist_view,remove_wishlist
# from bkash.bkash import Bkash

app_name = "core"

urlpatterns = [
    #homepage
    path("", index, name='index'),
  
    path("products/", product_list_view, name = "product-list"),
    path("product/<pid>/", product_detail_view, name = "product-detail"),
    
    #Category
    path("category/", category_list_view, name = "category-list"),
    path("category/<cid>/", category_product_list_view, name = "category-product-list"),
    #Vendor
    
    path("vendors/", vendor_list_view, name = "vendor-list"),
    path("vendor/<vid>/", vendor_detail_view, name = "vendor-detail"),

    #tags
    path("product/tag/<slug:tag_slug>/", tag_list, name = "tags"),

    #add reviews
    path("ajax-add-review/<int:pid>/", ajax_add_review, name = "ajax-add-review"),
    #search
    path("search/", search_view, name = "search"),

    #filter
    path("filter-product/", filter_product, name = "filter-product"),

    #add to cart
    path("add-to-cart/", add_to_cart, name = "add-to-cart"),

    #cart page
    path("cart/", cart_view, name = "cart"),

    #delete item from cart
    path("delete-from-cart/", delete_item_from_cart, name = "delete-from-cart"),

    #update cart
    path("update-cart/", update_cart, name = "update-cart"),

    #checkout URL
    path("checkout/", checkout_view, name = "checkout"),
    #invoice URL
    path('invoice/', payment_completed_view,name='invoice' ),

    #path Paypal
    path('paypal/', include("paypal.standard.ipn.urls")),
    
    path("payment/<int:oid>", payment,name='payment'),
    #Bkash

    # path('bkash/', include('bkash.urls')),
    # path('bkash/', include('bkash.urls')),


    # url(r'^bKash_payment/', include('bKash_payment.urls')),


    #payment successful
    path('payment-completed/',payment_completed_view, name = "payment-completed" ),
    

    #failed
    path('payment-failed/',payment_failed_view, name = "payment-failed" ),


    #wishlist page
    path('wishlist/',wishlist_view, name = "wishlist" ),


    #Add_t0_wishlist
    path('add-to-wishlist/',add_to_wishlist, name = "add-to-wishlist" ),

    #del wishlist
    path('remove-from-wishlist/',remove_wishlist, name = "remove-from-wishlist" ),

    # dashboard
    path("dashboard/",dashboard,name='dashboard' ),
    path("dashboard/order/<int:id>",order_detail,name='order-detail')
    
]
