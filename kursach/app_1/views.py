from django.shortcuts import render
from django.views import View
# from django.core.paginator import Paginator
# from .models import Post
from django.urls import reverse
from .forms import SignUpForm, SignInForm
from django.contrib.auth import login, authenticate, logout
from django.http import HttpResponseRedirect

class MainView(View):
    pass





class SignUpView(View):
    def get(self, request, *args, **kwargs):
        form = SignUpForm()
        return render(request, 'app_1/signup.html', context={
            'form': form,
        })
    def post(self, request, *args, **kwargs):
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            if user is not None:
                login(request, user)
                return HttpResponseRedirect('/')
        return render(request, 'app_1/signup.html', context={
            'form': form,
        })

class SignInView(View):
    def get(self, request, *args, **kwargs):
        form = SignInForm()
        return render(request, 'app_1/signin.html', context={
            'form': form,
        })
    def post(self, request, *args, **kwargs):
        form = SignInForm(request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return HttpResponseRedirect('/')
            else:
                form.add_error(None, 'Неправильный пароль или указанная учётная запись не существует!')
                return render(request, 'app_1/signin.html', context={'form':form})


def sign_out(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))

def index(request):
    return render(request, 'app_1/index.html')