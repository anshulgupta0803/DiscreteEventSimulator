# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division, with_statement

class Request():
	"""docstring for Request."""
	def __init__(self, arrivalTS, totalServiceTime):
		self.arrivalTS = arrivalTS								# Arrival timestamp
		self.totalServiceTime = totalServiceTime				# Total service time
		self.remainingServiceTime = totalServiceTime			# Remaining service time
		self.timeoutEvent = False								# To keep track of timeout event
