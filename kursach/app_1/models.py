from django.db import models


class Equipment(models.Model):
    name = models.CharField(max_length=50)
    ipaddress = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f"оборудование с ipaddress : {self.ipaddress}"

# Create your models here.
class TcpPacket(models.Model):
    equipment_id = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='tcp_packets')
    timestamp = models.CharField(max_length=50)
    source_ip = models.CharField(max_length=50)
    destination_ip = models.CharField(max_length=50)
    protocol = models.CharField(max_length=20)
    details = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.timestamp} {self.source_ip} -> {self.destination_ip}"

