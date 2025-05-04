from django.shortcuts import render
from django.views import View
from django.urls import reverse
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from .forms import SignUpForm, SignInForm, SearchForm
from django.contrib.auth import login, authenticate, logout
from django.http import HttpResponseRedirect

from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import requests
import re

from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM

from .models import TcpPacket


class MainView(View):
    pass



def sign_out(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))

def packet_list(source_ip=192):
    tcppacket = TcpPacket.objects.filter(source_ip=192)
    return {"packets": tcppacket.all().order_by("-created_at")}

#Ображается наше оборудование
@method_decorator(csrf_exempt, name='dispatch')
class TcpDumpData(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        packet_data = request.data.get("packet_data")

        if not packet_data:
            return JsonResponse({"status": "error", "message": "No packet data provided"}, status=400)

        # Парсинг данных пакета
        parsed_data = self.parse_packet(packet_data)

        if parsed_data:
            self.save_packet(parsed_data)
            return JsonResponse({"status": "success", "data": parsed_data})

        return JsonResponse({"status": "error", "message": "Invalid packet format"}, status=400)

    def parse_packet(self, raw_data: str) -> dict:
        """Парсинг сырых данных из tcpdump"""
        pattern = r"(\d+:\d+:\d+\.\d+) IP (.+?) > (.+?): (.+)"
        match = re.match(pattern, raw_data)

        if not match:
            return None

        return {
            "timestamp": match.group(1),
            "source_ip": match.group(2).split(".")[0],
            "destination_ip": match.group(3).split(".")[0],
            "protocol": "IP",
            "details": match.group(4)
        }

    def save_packet(self, data: dict):
        """Сохранение пакета в базу данных"""
        TcpPacket.objects.create(
            timestamp=data['timestamp'],
            source_ip=data['source_ip'],
            destination_ip=data['destination_ip'],
            protocol=data['protocol'],
            details=data['details']
        )

#Прописать аннотацию для доступа к контенту после авторизации, в том числе и для API
#Фанйнтюнинг модели (чтобы на русском лучше отвечала). И поработать над постобработкой
def index(request):
    return render(request, 'app_1/index.html', packet_list())

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

        # # Логика генерации ответа (пример 1)
        # response = requests.post('http://localhost:11434/api/generate', json={
        #     "model": "llama3.2",
        #     "prompt": user_message,
        #     "stream": False
        #     #добавить параметр ответа на процессоре
        # })
        # full_text = response.json()['response']
        template = """Question: {question}

        Answer: Let's think step by step. Write in Russian"""

        prompt = ChatPromptTemplate.from_template(template)

        model = OllamaLLM(model="llama3.2")

        chain = prompt | model

        full_text = chain.invoke({"question": user_message})

        full_text = re.sub(r'\*\*\s*(.*?)\s*\*\*', r'<strong>\1</strong>', full_text)

        parts = re.findall(r'(<strong>.*?</strong>[:]?|\n|\S+)', full_text)

        return JsonResponse({'parts': parts})


def http_method_not_allowed(self, request, *args, **kwargs):
    return JsonResponse({'error': 'Method not allowed'}, status=405)


class SearchView(TemplateView):

    def get(self, request, *args, **kwargs):
        return render(request, 'app_1/index.html', packet_list())


    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     form = SearchForm(self.request.GET or None)
    #     results = []
    #
    #     if form.is_valid():
    #         query = form.cleaned_data.get('query')
    #         category = form.cleaned_data.get('category') or 'all'
    #
    #         # Здесь должна быть ваша логика поиска
    #         # Пример:
    #         # results = YourModel.objects.filter(...)
    #
    #     context['form'] = form
    #     context['results'] = results
    #     return context

