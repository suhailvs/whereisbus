# models.py
from django.db import models
class KeralaDistrict(models.TextChoices):
    THIRUVANANTHAPURAM = 'thiruvananthapuram', 'Thiruvananthapuram'
    KOLLAM = 'kollam', 'Kollam'
    PATHANAMTHITTA = 'pathanamthitta', 'Pathanamthitta'
    ALAPPUZHA = 'alappuzha', 'Alappuzha'
    KOTTAYAM = 'kottayam', 'Kottayam'
    IDUKKI = 'idukki', 'Idukki'
    ERNAKULAM = 'ernakulam', 'Ernakulam'
    THRISSUR = 'thrissur', 'Thrissur'
    PALAKKAD = 'palakkad', 'Palakkad'
    MALAPPURAM = 'malappuram', 'Malappuram'
    KOZHIKODE = 'kozhikode', 'Kozhikode'
    WAYANAD = 'wayanad', 'Wayanad'
    KANNUR = 'kannur', 'Kannur'
    KASARAGOD = 'kasaragod', 'Kasaragod'

class Stop(models.Model):
    name = models.CharField(max_length=200)
    district = models.CharField(max_length=30, choices=KeralaDistrict.choices)
    landmark = models.CharField(max_length=300, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    def __str__(self):
        return self.name


class Bus(models.Model):
    bus_number = models.CharField(max_length=50)
    bus_type = models.CharField(max_length=100)
    stops = models.ManyToManyField(Stop, through='BusStop', related_name='buses')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.bus_number


class BusStop(models.Model):
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='bus_stops')  # explicit related_name
    stop = models.ForeignKey(Stop, on_delete=models.CASCADE, related_name='bus_stops')
    time = models.TimeField()
    is_boarding = models.BooleanField(default=False)
    is_destination = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.bus.bus_number} - {self.stop.name}'