from typing import List

from smartify import P


class Parameter:
    def __init__(self, p: P, long=None, short=None):
        self.p = p
        self.short = short
        self.long = long or p.name


class Service:
    name = 'NAME'
    desc = 'DESCRIPTION'
    long_desc = 'LONG DESCRIPTION'

    as_dir = False

    parameters = []  # type: List[Parameter]
    services = []  # type: List['Service']

    @classmethod
    def run(cls, *args, service: 'Service', **kwargs):
        pass

    @classmethod
    def get(cls, name):
        for service in cls.services:
            if service.name == name:
                return service

    @classmethod
    def register(cls, service: 'Service'):
        ServiceDepot.register(service)


class ServiceDepot:
    services = dict()

    @classmethod
    def register(cls, service: Service):
        if service.name in cls.services:
            raise ValueError(service.name + '重复')

        cls.services[service.name] = service
