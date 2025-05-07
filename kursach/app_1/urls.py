from django.urls import path
from .views import *

urlpatterns = [
    path('', SearchView.as_view(), name='index'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('signin/', SignInView.as_view(), name='signin'),
    path('signout/', sign_out, name='signout'),
    path('tag/', ChatView.as_view(), name='chat'),
    path('generate/', GenerateResponseView.as_view(), name='generate_response'),
    path('api/tcpdump/', TcpDumpData.as_view(), name='tcp_info'),
    path('add_equipment/', AddEquipmentView.as_view(), name='add_equipment'),
    path('equipment/', EquipmentListView.as_view(), name='equipment_list'),
    path('equipment/delete/<int:pk>/', EquipmentDeleteView.as_view(), name='delete_equipment'),
]