from django.test import TestCase
from django.urls import reverse

from .models import Bus, BusStop, Stop


class BusSearchViewTests(TestCase):
    def setUp(self):
        self.tvm = Stop.objects.create(name='Thiruvananthapuram')
        self.kollam = Stop.objects.create(name='Kollam')
        self.ekm = Stop.objects.create(name='Ernakulam')
        self.tsr = Stop.objects.create(name='Thrissur')

        self.bus_1 = Bus.objects.create(
            bus_number='KL 07',
            source='Thiruvananthapuram',
            destination='Thrissur',
            departure_time='06:15:00',
            arrival_time='09:40:00',
            duration='3h 25m',
            total_stops=4,
            bus_type='fast express',
            status='on time',
        )
        self.bus_2 = Bus.objects.create(
            bus_number='KL 12',
            source='Thiruvananthapuram',
            destination='Kollam',
            departure_time='07:30:00',
            arrival_time='08:25:00',
            duration='55m',
            total_stops=2,
            bus_type='ordinary',
            status='delay',
        )

        BusStop.objects.create(bus=self.bus_1, stop=self.tvm, time='06:15:00', order=1)
        BusStop.objects.create(bus=self.bus_1, stop=self.kollam, time='07:30:00', order=2, is_boarding=True)
        BusStop.objects.create(bus=self.bus_1, stop=self.ekm, time='09:15:00', order=3, is_destination=True)
        BusStop.objects.create(bus=self.bus_1, stop=self.tsr, time='09:40:00', order=4)

        BusStop.objects.create(bus=self.bus_2, stop=self.tvm, time='07:30:00', order=1)
        BusStop.objects.create(bus=self.bus_2, stop=self.kollam, time='08:25:00', order=2, is_destination=True)

    def test_search_filters_buses_by_its_own_stops(self):
        response = self.client.get(
            reverse('bus_search'),
            {'from_stop': self.kollam.id, 'to_stop': self.tsr.id},
        )

        buses = list(response.context['buses'])

        self.assertEqual(buses, [self.bus_1])

    def test_search_excludes_reverse_stop_order(self):
        response = self.client.get(
            reverse('bus_search'),
            {'from_stop': self.tsr.id, 'to_stop': self.kollam.id},
        )

        self.assertEqual(list(response.context['buses']), [])

    def test_bus_detail_uses_selected_bus_stops(self):
        response = self.client.get(reverse('bus_detail', args=[self.bus_2.id]))

        bus_stops = list(response.context['selected_bus'].busstop_set.all())

        self.assertEqual([bus_stop.stop.name for bus_stop in bus_stops], ['Thiruvananthapuram', 'Kollam'])
