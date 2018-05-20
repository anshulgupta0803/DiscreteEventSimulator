# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division, with_statement
from Request import Request

def newArrival(arrivalTS, totalServiceTime, timeout):
	request = Request(arrivalTS, totalServiceTime)

	arrivalEvent = Arrival(arrivalTS, request)
	timeoutEvent = Timeout(arrivalTS + timeout, request)

	return (arrivalEvent, timeoutEvent)

class Event():
	"""docstring for Event."""
	def __init__(self, timestamp):
		self.timestamp = timestamp			# Timestamp

	# For heap to compare events
	def __lt__(self, other):
		return self.timestamp < other.timestamp


class Arrival(Event):
	"""docstring for Arrival."""
	def __init__(self, timestamp, request):
		super(Arrival, self).__init__(timestamp)
		self.request = request

class CtxSwitch(Event):
	"""docstring for CtxSwitch."""
	def __init__(self, timestamp, cpu):
		super(CtxSwitch, self).__init__(timestamp)
		self.cpu = cpu

class Departure(Event):
	"""docstring for Departure."""
	def __init__(self, timestamp, request):
		super(Departure, self).__init__(timestamp)
		self.request = request

class QuantumOver(Event):
	"""docstring for QuantumOver."""
	def __init__(self, timestamp, cpu):
		super(QuantumOver, self).__init__(timestamp)
		self.cpu = cpu

class Timeout(Event):
	"""docstring for Timeout."""
	def __init__(self, timestamp, request):
		super(Timeout, self).__init__(timestamp)
		self.request = request
		self.request.timeoutEvent = True
