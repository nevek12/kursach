import re

from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.generic import ListView
from django.contrib.auth import login, authenticate, logout
from django.http import HttpResponseRedirect

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from .forms import SignUpForm, SignInForm
from .models import TcpPacket, Equipment

from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM

#регистрирует пользователя
def sign_out(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))



#обработка пришедших данных оборудования
@method_decorator(csrf_exempt, name='dispatch')
class TcpDumpData(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # забираем данные о tcp оборудовании
        packet_data = request.data.get("packet_data")
        # проверяем ipaddress
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ipaddress = x_forwarded_for.split(',')[0].strip()
        else:
            ipaddress = request.META.get('REMOTE_ADDR')

        if not packet_data:
            return JsonResponse({"status": "error", "message": "No packet data provided"}, status=400)
        # проверка на разрешенный ipaddress
        if not Equipment.objects.filter(ipaddress=ipaddress).exists():
            return JsonResponse({'status': 'error', 'message': 'your equipment not found'}, status=403)

        # Парсинг данных пакета
        parsed_data = self.parse_packet(packet_data, ipaddress)

        if parsed_data:
            # сохранение данных в бд
            self.save_packet(parsed_data)
            return JsonResponse({"status": "success", "data": parsed_data})

        return JsonResponse({"status": "error", "message": "Invalid packet format"}, status=400)

    def parse_packet(self, raw_data: str, ipaddress: str) -> dict:
        """Парсинг сырых данных из tcpdump"""
        pattern = r"(\d+:\d+:\d+\.\d+) IP (.+?) > (.+?): (.+)"
        match = re.match(pattern, raw_data)

        if not match:
            return None

        return {'tcppacket': {
                                "timestamp": match.group(1),
                                "source_ip": '.'.join(match.group(2).split(".")[:-1]) + ':' + match.group(2).split(".")[-1],
                                "destination_ip": '.'.join(match.group(3).split(".")[:-1]) + ':' + match.group(3).split(".")[-1],
                                "protocol": "IP",
                                "details": match.group(4)
                             },
                'equipment': {'ipaddress': ipaddress}
               }

    def save_packet(self, data: dict):
        """Сохранение пакета в базу данных"""

        TcpPacket.objects.create(
            equipment_id = Equipment.objects.get(ipaddress=data['equipment']['ipaddress']),
            timestamp=data['tcppacket']['timestamp'],
            source_ip=data['tcppacket']['source_ip'],
            destination_ip=data['tcppacket']['destination_ip'],
            protocol=data['tcppacket']['protocol'],
            details=data['tcppacket']['details']
        )

#Для регистрации пользователя
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
#для входа пользователя
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

#обработка запроса для нейросети от пользователя
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

#главная страница
class MainView(TemplateView):

    def get(self, request, *args, **kwargs):
        return render(request, 'app_1/index.html', self.packet_list() | self.equipment_list())

    def post(self, request, *args, **kwargs):
        # получаем имя оборудования для поиска
        name_equipment = request.POST.get('query', '').strip()
        #проверка что оборудование существует
        if Equipment.objects.filter(name=name_equipment).exists():
            equipment = Equipment.objects.get(name=name_equipment)
            packets = equipment.tcp_packets.all()
            return render(request, 'app_1/show_tcp.html', {'packets': packets})
        else:
            # Передаем ошибку и данные из packet_list + equipment_list

            context = self.packet_list() | self.equipment_list()
            context['error'] = f"Оборудование '{name_equipment}' не найдено"
            return render(request, 'app_1/index.html', context)

    #вывод недавних tcpзапросов
    def packet_list(self):
        # Загружаем TcpPacket с предварительной загрузкой связанных equipment
        packets = TcpPacket.objects.select_related('equipment_id').order_by('-created_at')[:10]
        return {"packets": packets}

    #вывод оборудований
    def equipment_list(self):
        equipments = Equipment.objects.all()
        return {"equipments": equipments}


#добавление оборудования
class AddEquipmentView(TemplateView):
    def get(self, request, *args, **kwargs):
        return render(request, 'app_1/add_equipment.html')
    def post(self, request, *args, **kwargs):
        name = request.POST.get('name')
        ip_address = request.POST.get('ip_address')
        if name and ip_address:
            Equipment.objects.create(
                name=name,
                ipaddress=ip_address
            )
            return redirect(reverse('index'))
        return render(request, 'app_1/add_equipment.html')

# класс для вывода оборудования
class EquipmentListView(ListView):
    model = Equipment
    template_name = 'equipment_list.html'  # Шаблон, который будем использовать
    context_object_name = 'equipments'
    success_url = reverse_lazy('equipment_list')

# класс для удаление оборудования
class EquipmentDeleteView(View):
    def post(self, request, *args, **kwargs):
        equipment = get_object_or_404(Equipment, pk=kwargs['pk'])
        equipment.delete()
        return redirect('equipment_list')

