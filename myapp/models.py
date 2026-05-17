# models.py

from django.db import models


class Stop(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Bus(models.Model):
    STATUS_CHOICES = (
        ('on time', 'On Time'),
        ('delay', 'Delay'),
    )

    bus_number = models.CharField(max_length=50)
    source = models.CharField(max_length=200)
    destination = models.CharField(max_length=200)

    departure_time = models.TimeField()
    arrival_time = models.TimeField()

    duration = models.CharField(max_length=50)

    total_stops = models.IntegerField(default=0)

    bus_type = models.CharField(max_length=100)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='on time'
    )

    def __str__(self):
        return self.bus_number


class BusStop(models.Model):
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    time = models.TimeField()

    is_boarding = models.BooleanField(default=False)
    is_destination = models.BooleanField(default=False)

    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']