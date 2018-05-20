# -*- coding: utf-8 -*-


from __future__ import print_function, absolute_import, division, with_statement
from enum import Enum

class Cpu():
	"""docstring for Cpu."""
	def __init__(self):
		self.setIdle()						# State: IDLE or BUSY
		self.request = None					# Request being processed
		self.newRequest = None				# Used in context switching
		self.oldRequest = None				# Used in context switching
		self.quantumStartTS = 0				# Quantum start timestamp
		self.ctxStart = 0					# Timestamp when the context switching starts of the current request
		self.totalCtxxTime = 0.0			# Total context switching time
		self.totalProcessedTime = 0.0

	def setIdle(self):
		self.state = CpuState.IDLE

	def setBusy(self, request, quantumStart):
		self.state = CpuState.BUSY
		self.request = request
		self.quantumStartTS = quantumStart

	def ctxSwitch(self, newRequest, oldRequest, ctxStart):
		self.state = CpuState.CTXSWITCH
		self.newRequest = newRequest
		self.oldRequest = oldRequest
		self.ctxStart = ctxStart

class CpuState(Enum):
	IDLE = 0
	BUSY = 1
	CTXSWITCH = 2
