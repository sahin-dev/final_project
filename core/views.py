from sslcommerz_lib import SSLCOMMERZ 
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404,redirect
from core.models import Product, Category, Vendor, ProductImages,CartOrderItems, CartOrder,ProductReview, wishlist_model, Address
from userauths.models import User
from taggit.models import Tag
from django.db.models import Count,Avg
from core.forms import ProductReviewForm
from django.template.loader import render_to_string
from django.contrib import messages

from django.urls import reverse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from paypal.standard.forms import PayPalPaymentsForm
from django.contrib.auth.decorators import login_required
from django.core import serializers


def index(request):
    #products = Product.objects.all().order_by("-id")
    products = Product.objects.filter(product_status = "published" ).order_by('-date')
    for product in products:
        print(product)
    
    categories = Category.objects.all()
    context = {
        "products" : products,
        "categories":categories

    }
    return render(request, 'core/index.html', context)

def product_list_view(request):
    products = Product.objects.filter(product_status = "published" )
    print(products)
    context = {
        "products" : products
    }
    return render(request, 'core/product-list.html', context)




def payment(request,oid):
    settings = { 'store_id': 'testbox', 'store_pass': 'qwerty', 'issandbox': True }
    print(request.POST.keys())
    sslcommez = SSLCOMMERZ(settings)
    order = CartOrder.objects.get(id=oid)
    host = request.get_host()
    post_body = {}
    post_body['total_amount'] = order.price
    post_body['currency'] = "BDT"
    post_body['tran_id'] = order.id
    post_body['success_url'] = 'http://{}{}'.format(host,reverse("core:invoice")),
    post_body['fail_url'] = "your fail url"
    post_body['cancel_url'] = "your cancel url"
    post_body['emi_option'] = 0
    post_body['cus_name'] = request.user
    post_body['cus_email'] = request.user.email
    post_body['cus_phone'] = "01700000000"
    post_body['cus_add1'] = "customer address"
    post_body['cus_city'] = "Dhaka"
    post_body['cus_country'] = "Bangladesh"
    post_body['shipping_method'] = "NO"
    post_body['multi_card_name'] = ""
    post_body['num_of_item'] = 1
    post_body['product_name'] = "Test"
    post_body['product_category'] = "Test Category"
    post_body['product_profile'] = "general"


    response = sslcommez.createSession(post_body)
    
    return HttpResponseRedirect(response['GatewayPageURL'],)
# Create your views here.
def category_list_view(request):

    categories = Category.objects.all()
    #categories = Category.objects.annotate(product_count=Count('product')).order_by('-product_count')[:5]

    context = {
        "categories": categories
    }
    return render(request, 'core/category-list.html', context)

def category_product_list_view(request, cid):
    category = Category.objects.get(cid = cid)
    products = Product.objects.filter(product_status="published", category = category)

    context = {
        "category": category,
        "products": products,

    }
    return render(request, 'core/category-product-list.html', context)

def vendor_list_view(request):
    vendors = Vendor.objects.all()
    context = {
        "vendors": vendors,

    }
    return render(request, 'core/vendor-list.html', context)


def vendor_detail_view(request, vid):
    vendor = Vendor.objects.get(vid = vid)
    products = Product.objects.filter(vendor=vendor, product_status="published")
    #weight_options = ["50g", "60g", "80g", "100g", "150g"]
    context = {
        "vendor": vendor,
        "products": products,
        


    }
    return render(request, 'core/vendor-detail.html', context)

def product_detail_view(request, pid):
    product = Product.objects.get(pid = pid)
    p_image = product.p_images.all()
    products = Product.objects.filter(category = product.category).exclude(pid=pid)


    ###################
    weight_options = ["50g", "80g", "100g", "150g","200g","500g","1000g"]

    ###############
    reviews = ProductReview.objects.filter(product= product).order_by("-date")
    #getting avg reviews
    average_rating = ProductReview.objects.filter(product= product).aggregate(rating=Avg('rating'))


    # Calculate the count of each rating
    rating_counts = reviews.values('rating').annotate(count=Count('rating')).order_by('rating')

    # Initialize dictionary to hold star counts
    star_counts = {i: 0 for i in range(1, 6)}

    # Fill the star_counts dictionary with actual counts
    for item in rating_counts:
        star_counts[item['rating']] = item['count']

    # Calculate total number of reviews
    total_reviews = reviews.count()

    # Calculate percentage for each star rating
    star_percentages = {star: (count / total_reviews) * 100 if total_reviews > 0 else 0 for star, count in star_counts.items()}

    # Calculate average rating percentage
    average_rating_percentage = (average_rating['rating'] / 5) * 100 if average_rating['rating'] else 0

    #Product review form
    review_form = ProductReviewForm()


    make_review = True
    if request.user.is_authenticated:
        user_review_count = ProductReview.objects.filter(user=request.user, product=product).count()
        if user_review_count > 0:
            make_review = False




    context = {
        "p": product,
        "p_image": p_image,
        "weight_options": weight_options,
        "current_weight": product.weight,
        "reviews": reviews,
        "products": products,
        "average_rating": average_rating,
        'average_rating_percentage': average_rating_percentage,
        'star_percentages': star_percentages,
        'review_form':review_form,
        'make_review':make_review,






    }
    return render(request, 'core/product-detail.html', context)


def tag_list(request,tag_slug=None):
    products = Product.objects.filter(product_status="published").order_by("-id")
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug = tag_slug)
        products = products.filter(tags__in=[tag])

    context = {
        "products": products,
        "tag": tag,

    }
    return render(request, 'core/tag.html', context)   

def  ajax_add_review(request,pid):
    #try:

    product = Product.objects.get(id=pid)
    # except Product.DoesNotExist:
    #     return JsonResponse({'error': 'Product not found'}, status=404)
    user = request.user


    review = ProductReview.objects.create(

        user = user,
        product = product,
        review = request.POST["review"],
        rating = request.POST["rating"],
    )

    context = {
        "user": user.username,
        "review": request.POST["review"],
        "rating": request.POST["rating"],

    }

    avg_reviews = ProductReview.objects.filter(product=product).aggregate(rating=Avg("rating"))

    return JsonResponse(
        {
            'bool':True,
            "context": context,
            'avg_reviews': avg_reviews,
        }
    )

def search_view(request):
    query = request.GET.get("q")

    products = Product.objects.filter(title__icontains=query).order_by("-date")

    context = {
        "products": products,
        "query": query,
        

    }
    return render(request, 'core/search.html', context)

def filter_product(request):
    categories = request.GET.getlist('category[]')
    vendors = request.GET.getlist('vendor[]')
    min_price = request.GET['min_price']
    max_price = request.GET['max_price']

    products = Product.objects.filter(product_status = "published" ).order_by("-id").distinct()

    products = products.filter(price__gte=min_price)
    products = products.filter(price__lte=max_price)

     
    if len(categories) > 0:
        products = products.filter(category__id__in=categories).distinct()

    if len(vendors) > 0:
        products = products.filter(vendor__id__in=vendors).distinct()  

    context = {
        "products": products,
    }

    data = render_to_string("core/async/product-list.html", context)
    return JsonResponse({"data": data})


def add_to_cart(request):
    cart_product = {}

    cart_product[str(request.GET['id'])] = {
        "title" : request.GET['title'],
        "qty" : request.GET['qty'],
        "price" : request.GET['price'],
        "image" : request.GET['image'],
        "pid" : request.GET['pid'],

    }
    
    if "cart_data_obj" in request.session:
        if str(request.GET["id"]) in request.session['cart_data_obj']:
            cart_data = request.session['cart_data_obj']
            cart_data[str(request.GET['id'])]["qty"] = int(cart_product[str(request.GET['id'])]['qty'])
            cart_data.update(cart_data)
            request.session['cart_data_obj'] = cart_data

        else:
            cart_data = request.session['cart_data_obj']
            cart_data.update(cart_product)
            request.session['cart_data_obj'] = cart_data


    else:

        request.session['cart_data_obj'] = cart_product

    return JsonResponse({"data": request.session['cart_data_obj'], 'totalcartitems': len(request.session['cart_data_obj'])})



def cart_view(request):
    cart_total_amount = 0
    if 'cart_data_obj' in request.session:
        for p_id ,item in request.session['cart_data_obj'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])


        return render(request, 'core/cart.html',{"cart_data": request.session['cart_data_obj'], 'totalcartitems': len(request.session['cart_data_obj']),'cart_total_amount':cart_total_amount})
     
    else:
         
        messages.warning(request, "Your cart is empty")
        #  return render(request, 'core/cart.html',{"cart_data": '', 'totalcartitems': len(request.session['cart_data_obj']),'cart_total_amount':cart_total_amount})
        return redirect("core:index")
    
def delete_item_from_cart(request):
    product_id = str(request.GET['id'])
    if 'cart_data_obj' in request.session:
        if product_id in request.session['cart_data_obj']:
            cart_data = request.session['cart_data_obj']
            del request.session['cart_data_obj'][product_id]
            request.session['cart_data_obj'] = cart_data

        cart_total_amount = 0
        if 'cart_data_obj' in request.session:
            for p_id ,item in request.session['cart_data_obj'].items():
                cart_total_amount += int(item['qty']) * float(item['price'])


        context = render_to_string("core/async/cart-list.html", {"cart_data": request.session['cart_data_obj'], 'totalcartitems': len(request.session['cart_data_obj']),'cart_total_amount':cart_total_amount})
        return JsonResponse({"data": context,'totalcartitems': len(request.session['cart_data_obj'])})
        


def update_cart(request):
    product_id = str(request.GET['id'])
    product_qty = request.GET['qty']


    if 'cart_data_obj' in request.session:
        if product_id in request.session['cart_data_obj']:
            cart_data = request.session['cart_data_obj']
            cart_data[str(request.GET['id'])]["qty"] = product_qty
 
            # del request.session['cart_data_obj'][product_id]
            request.session['cart_data_obj'] = cart_data

        cart_total_amount = 0
        if 'cart_data_obj' in request.session:
            for p_id ,item in request.session['cart_data_obj'].items():
                cart_total_amount += int(item['qty']) * float(item['price'])


        context = render_to_string("core/async/cart-list.html", {"cart_data": request.session['cart_data_obj'], 'totalcartitems': len(request.session['cart_data_obj']),'cart_total_amount':cart_total_amount})
        return JsonResponse({"data": context,'totalcartitems': len(request.session['cart_data_obj'])})
    
@login_required
def checkout_view(request):
        
        cart_total_amount = 0
    
        if 'cart_data_obj' in request.session:
            for p_id ,item in request.session['cart_data_obj'].items():
                cart_total_amount += int(item['qty']) * float(item['price'])

        order = CartOrder.objects.create(
            user = request.user,
            price = cart_total_amount,
        )
        
        host = request.get_host()
        paypal_dict = {
            'buisness' : settings.PAYPAL_RECEIVER_EMAIL,
            'amount' : '200',
            'item_name': "Order-Item-No-3",
            'invoice': "INVOICE_NO-3",
            'currency_code': "Taka",
            'notify_url' : 'http://{}{}'.format(host,reverse("core:paypal-ipn")),
            'return_url' : 'http://{}{}'.format(host,reverse("core:payment-completed")),
            'cancel_url' : 'http://{}{}'.format(host,reverse("core:payment-failed")),
           
     
        }

        paypal_payment_button = PayPalPaymentsForm(initial=paypal_dict)
        
    
        if 'cart_data_obj' in request.session:
            for p_id ,item in request.session['cart_data_obj'].items():
                cart_order_products = CartOrderItems.objects.create(
                    order = order,
                    invoice_no= "INVOICE_NO-"+str(order.id),
                    item = item['title'],
                    image = item['image'],
                    qty = item['qty'],
                    price=item['price'],
                    total = float(item['qty']) * float(item['price'])

                )

            #  return render(request, 'core/checkout.html')
            address = Address.objects.filter(user = request.user)[0]
        
        return render(request, 'core/checkout.html', {
                    "cart_data": request.session['cart_data_obj'],
                    'totalcartitems': len(request.session['cart_data_obj']),
                    'cart_total_amount': cart_total_amount,
                    'paypal_payment_button': paypal_payment_button,
                    'order':order,
                    'address':address
                })


@csrf_exempt   
def payment_completed_view(request):
    print(request.POST.keys())
    cart_total_amount = 0
    if 'cart_data_obj' in request.session:
        for p_id ,item in request.session['cart_data_obj'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])
    order = CartOrder.objects.get(id=request.POST['tran_id'])
    order_items = CartOrderItems.objects.filter(order = order)
    return render(request, 'core/invoice.html', {
                    "cart_data": order_items,
                    'totalcartitems': order_items,
                    'cart_total_amount': order.price,
                    # 'paypal_payment_button': paypal_payment_button
                    'tran_id':request.POST['tran_id'],
                    'amount':request.POST['amount'],
                    'date':request.POST['tran_date'],
                    'method':request.POST['card_type']
                })


@login_required
def payment_failed_view(request):
    return render(request, 'core/payment-failed.html')


@login_required
def wishlist_view(request):

    wishlist = wishlist_model.objects.all()
  
       
    context = {
        "w":wishlist
    }
    return render(request, "core/wishlist.html", context)


def add_to_wishlist(request):
    product_id = request.GET["id"]
    product = Product.objects.get(id=product_id)
    context = {}
    wishlist_count = wishlist_model.objects.filter(product= product,user=request.user).count()
    print(wishlist_count)
    if wishlist_count > 0 :
        context = {
            "bool" : True
        }
    else:
        new_wishlist = wishlist_model.objects.create(
            product=product,
            user = request.user
        )   
        context =  {
            "bool":True,
            # "wishlist_count": wishlist_count
        }

    return JsonResponse(context)

def remove_wishlist(request):
    pid = request.GET['id']
    # wishlist = wishlist_model.objects.filter(user = request.user)
    # product = wishlist_model.objects.get(id=pid)
    # delete_product = product.delete()

    # context = {
    #     'bool':True,
    #     'wishlist': wishlist
    # }

    # wishlist_json = serializers.serialize('json', wishlist)

    # t  = render_to_string("core\async\wishlist-list.html",context)
    # return JsonResponse({"data": t,"w":wishlist_json})

    # def remove_wishlist(request):
    # pid = request.GET.get('id')

    if not pid:
        return JsonResponse({"error": "No product ID provided"}, status=400)

    try:
        # Ensure the wishlist item belongs to the current user
        product = wishlist_model.objects.get(id=pid, user=request.user)
        product.delete()
        
        updated_wishlist = wishlist_model.objects.filter(user=request.user)
        # wishlist_count = wishlist_model.objects.filter(user=request.user).count()
        context = {'w': updated_wishlist,
                #    "wishlist_count":wishlist_count
                   
                   }
        data = render_to_string("core/async/wishlist-list.html", context, request=request)

        return JsonResponse({"data": data,})
    except wishlist_model.DoesNotExist:
        return JsonResponse({"error": "Product not found in wishlist"}, status=404)

@login_required
def dashboard(request):
    orders = CartOrder.objects.filter(user=request.user).order_by('-id')
    address = Address.objects.filter(user = request.user)
    
    if request.method  == "POST":
        address = request.POST.get("address")
        mobile = request.POST.get("phone")
        new_address = Address.objects.create(user = request.user,address =address,mobile=mobile)
        messages.success(request, "Address added successfully")
        return redirect("core:dashboard")
    context = {
        'orders':orders,
        'address':address
    }
    return render(request, "core/dashboard.html",context)

def order_detail(request,id):
    order = CartOrder.objects.get(user=request.user,id=id)
    orderItems = CartOrderItems.objects.filter(order=order)

    context = {
        'orderItems':orderItems,
        'order':order
    }

    return render (request, 'core/order-detail.html',context)
@csrf_exempt
def invoice_view(request):
    context = {
        'tran_id':request.POST['tran_id'],
        'amount':request.POST['amount'],
        'date':request.POST['tran_date'],
        'method':request.POST['card_type']
    }
    
    return render(request, 'core/invoice.html', context )


        

    
        
        




        
    



    









 
