from django.shortcuts import render, redirect
from userauths.forms import UserRegisterForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.conf import settings
from userauths.models import User
from django.contrib.auth import get_user_model


User = get_user_model()

# Create your views here.
def register_view(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST or None)
        if form.is_valid():
            new_user = form.save()
            username = form.cleaned_data.get("username")
            messages.success(request, f"Hey {username}, your account was created successfully.")
            new_user = authenticate(username=form.cleaned_data['email'], password=form.cleaned_data['password1'])
            if new_user is not None:
                login(request, new_user)
                return redirect("core:index")
            else:
                messages.error(request, "Authentication failed. Please try again.")
    else:
        form = UserRegisterForm()

    context = {
        'form': form,
    }
    return render(request, "userauths/sign-up.html", context)

def login_view(request):
    if request.user.is_authenticated:
        messages.warning(request, f"Hey you're alreasy Logged In.!")
        return redirect("core:index")
    
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user = User.objects.get(email=email)
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "You are logged in.!")
                return redirect("core:index")
            else:
                messages.warning(request, "Uername or Password Incorrect Try again!! ")

        except User.DoesNotExist:
            messages.warning(request, f"User with email {email} doesn't exist.!")
            

        
    
  
    return render(request, "userauths/sign-in.html")


def logout_view(request):
    logout(request)
    messages.success(request, "You Logged Outtt!. ")
    return redirect("userauths:sign-in")

def confirm_mail(request):
    context = {
        'mail':request.user.email
    }
    return render(request,'userauths/mail-confirmation.html',context)
  