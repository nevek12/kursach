from django.shortcuts import render
from django.views import View
from django.urls import reverse
from .forms import SignUpForm, SignInForm
from django.contrib.auth import login, authenticate, logout
from django.http import HttpResponseRedirect, StreamingHttpResponse

from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import requests
class MainView(View):
    pass



def sign_out(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))

def index(request):
    return render(request, 'app_1/index.html')

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

class ChatView(TemplateView):
    template_name = 'app_1/chat.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Можно добавить дополнительный контекст при необходимости
        return context


@method_decorator(csrf_exempt, name='dispatch')
class GenerateResponseView(View):
    def post(self, request, *args, **kwargs):
        user_message = request.POST.get('message', '')

        # Логика генерации ответа (пример)
        response = requests.post('http://localhost:11434/api/generate', json={
            "model": "llama3.2",
            "prompt": user_message,
            "stream": False
        })
        full_text = response.json()['response']

        parts = full_text.split(' ')

        return JsonResponse({'parts': parts})


def http_method_not_allowed(self, request, *args, **kwargs):
    return JsonResponse({'error': 'Method not allowed'}, status=405)
