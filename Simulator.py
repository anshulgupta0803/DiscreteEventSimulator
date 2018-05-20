# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division, with_statement

import logging
import colorlog
import progressbar

from System import System
from Event import Event, Arrival, CtxSwitch, Departure, QuantumOver, Timeout, newArrival
from Cpu import Cpu, CpuState
from Request import Request

import heapq
from time import time
from random import seed
from random import expovariate as Exp
from random import normalvariate as Norm
from random import uniform as Range

# Set seed for Random Number Generator with the current time
seed(time())

progressbar.streams.wrap_stderr()
logger = colorlog.getLogger("Web Server Simulator")
handler = logging.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter('%(log_color)s%(asctime)s [%(levelname)-8s] %(message)s'))
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

clip = lambda x : x if x > 0 else 0.0
isZero = lambda x : -1e-12 < x and x < 1e-12

class Simulator():
	"""docstring for Simulator."""
	def __init__(self, system):
		self.system = system

	def processRequest(self, request, cpu, time, quantum):
		cpu.setBusy(request, time)
		remainingServiceTime = request.remainingServiceTime
		eventTS = time + (remainingServiceTime if (remainingServiceTime < quantum) else quantum)
		newEvent = QuantumOver(eventTS, cpu)
		return newEvent

	def run(self):
		logger.debug("Begin Simulator")
		self.metrics = System.Metrics()
		self.requestsInSystem = System.RequestsInSystem()
		events = []	# Min-Heap
		CPUs = []
		idleCPUs = []
		n_threads = 0

		# Initialize CPUs
		logger.debug("Initializing CPUs")
		for _ in range(0, self.system.n_CPUs):
			cpu = Cpu()
			idleCPUs.append(cpu)
			CPUs.append(cpu)

		requestBuffer = []
		threadPool = []

		easeInSampler         = lambda : Range(0.0, self.system.easeInTime)
		serviceTimeSampler    = lambda : Exp(1.0 / self.system.serviceTimeMean)
		timeoutSampler        = lambda : Range(self.system.requestTimeoutMin, self.system.requestTimeoutMax)
		thinkTimeSampler      = lambda : Norm(self.system.thinkTimeMean, self.system.thinkTimeStdv)
		retryThinkTimeSampler = lambda : Norm(self.system.retryThinkTimeMean, self.system.retryThinkTimeStdv)

		for _ in range(0, self.system.n_users):
			arrivalTS = self.metrics.time + easeInSampler()
			totalServiceTime = serviceTimeSampler()
			timeout = timeoutSampler()
			arrivalEvent, timeoutEvent = newArrival(arrivalTS, totalServiceTime, timeout)
			heapq.heappush(events, arrivalEvent)
			heapq.heappush(events, timeoutEvent)

		iterations = 0
		pbar = progressbar.ProgressBar(max_value=self.system.maxIters, redirect_stdout=True)
		while True:
			e = None
			try:
				e = heapq.heappop(events)
			except IndexError as ex:
				logger.info("All events processed")
				break

			self.metrics.time = e.timestamp

			if type(e) == Arrival:
				logger.debug("Event :: Arrival with Service Time " + str(e.request.remainingServiceTime))
				self.metrics.n_arrivals += 1
				self.metrics.weightedSumOfRequestsInSystem += (self.metrics.time - self.requestsInSystem.lastModifiedTimestamp) * self.requestsInSystem.count
				self.requestsInSystem.count += 1
				self.requestsInSystem.lastModifiedTimestamp = self.metrics.time
				if n_threads < self.system.threadpoolSize:
					try:
						cpu = idleCPUs.pop()
						heapq.heappush(events, self.processRequest(e.request, cpu, self.metrics.time, self.system.quantum))
					except IndexError as ex:
						logger.debug("No Idle CPUs. Pushing the request in threadPool")
						threadPool.append(e.request)
					n_threads += 1
				elif len(requestBuffer) < self.system.bufferCapacity:
					logger.debug("Number of threads more than threadpoolSize. Pushing the request in requestBuffer")
					requestBuffer.append(e.request)
				else:
					logger.debug("Dropping the request")
					e.request.timeoutEvent = False
					self.metrics.n_dropped += 1
					self.requestsInSystem.count -= 1

					# The client cannot know whether the request was dropped right away
					# Therefore waits for a timeout and then retry think time
					# before issuing a new request
					arrivalTS = self.metrics.time + \
								timeoutSampler() + \
								clip(retryThinkTimeSampler())
					totalServiceTime = serviceTimeSampler()
					timeout = timeoutSampler()
					arrivalEvent, timeoutEvent = newArrival(arrivalTS, totalServiceTime, timeout)
					heapq.heappush(events, arrivalEvent)
					heapq.heappush(events, timeoutEvent)

			elif type(e) == Departure:
				logger.debug("Event :: Departure")
				self.metrics.weightedSumOfRequestsInSystem += (self.metrics.time - self.requestsInSystem.lastModifiedTimestamp) * self.requestsInSystem.count
				self.requestsInSystem.count -= 1
				self.requestsInSystem.lastModifiedTimestamp = self.metrics.time
				if e.request.timeoutEvent:
					# Timeout hasn't occured yet
					e.request.timeoutEvent = False
					# Schedule the next request
					arrivalTS = self.metrics.time + clip(thinkTimeSampler())
					totalServiceTime = serviceTimeSampler()
					timeout = timeoutSampler()
					arrivalEvent, timeoutEvent = newArrival(arrivalTS, totalServiceTime, timeout)
					heapq.heappush(events, arrivalEvent)
					heapq.heappush(events, timeoutEvent)
				else:
					self.requestsInSystem.timedOutCount -= 1

				self.metrics.totalResponseTime += self.metrics.time - e.request.arrivalTS
				self.metrics.n_processed += 1

			elif type(e) == CtxSwitch:
				logger.debug("Event :: Context Switch")
				if e.cpu.state != CpuState.CTXSWITCH:
					logger.error("CPU is not in Context Switching")
					break
				newRequest = e.cpu.newRequest
				oldRequest = e.cpu.oldRequest
				ctxStart = e.cpu.ctxStart

				e.cpu.totalCtxxTime += self.metrics.time - ctxStart
				remainingServiceTime = oldRequest.remainingServiceTime
				if isZero(remainingServiceTime):
					heapq.heappush(events, Departure(self.metrics.time, oldRequest))
				else:
					threadPool.append(oldRequest)

				heapq.heappush(events, self.processRequest(newRequest, e.cpu, self.metrics.time, self.system.quantum))

			elif type(e) == QuantumOver:
				logger.debug("Event :: Quantum Over")
				if e.cpu.state == CpuState.BUSY:
					request = e.cpu.request
					processedTime = self.metrics.time - e.cpu.quantumStartTS
				else:
					logger.error("CPU was not BUSY at Quantum Over")
					break
				e.cpu.request.remainingServiceTime -= processedTime
				e.cpu.totalProcessedTime += processedTime
				oldRequest = e.cpu.request

				if len(threadPool) > 0:
					newRequest = threadPool[0]
					threadPool.remove(threadPool[0])
					e.cpu.ctxSwitch(newRequest, oldRequest, self.metrics.time)
					heapq.heappush(events, CtxSwitch(self.metrics.time + self.system.ctxxTime, e.cpu))
				elif not(isZero(oldRequest.remainingServiceTime)):
					heapq.heappush(events, self.processRequest(oldRequest, e.cpu, self.metrics.time, self.system.quantum))
				elif len(requestBuffer) > 0:
					newRequest = requestBuffer[0]
					requestBuffer.remove(requestBuffer[0])
					e.cpu.ctxSwitch(newRequest, oldRequest, self.metrics.time)
					heapq.heappush(events, CtxSwitch(self.metrics.time + self.system.ctxxTime, e.cpu))
				else:
					n_threads -= 1
					e.cpu.setIdle()
					idleCPUs.append(e.cpu)
					heapq.heappush(events, Departure(self.metrics.time, oldRequest))

			elif type(e) == Timeout:
				if e.request.timeoutEvent:
					logger.debug("Event :: Timeout")
					self.metrics.n_timedOut += 1
					self.requestsInSystem.timedOutCount += 1
					arrivalTS = self.metrics.time + clip(retryThinkTimeSampler())
					totalServiceTime = serviceTimeSampler()
					timeout = timeoutSampler()
					arrivalEvent, timeoutEvent = newArrival(arrivalTS, totalServiceTime, timeout)
					heapq.heappush(events, arrivalEvent)
					heapq.heappush(events, timeoutEvent)
				else:
					pass

			else:
				logger.error("Invalid Event")
				break

			iterations += 1
			pbar.update(iterations)
			if iterations >= self.system.maxIters:
				logger.info("Maximum iterations reached")
				break

		pbar.finish()
		for cpu in CPUs:
			self.metrics.totalProcessedTime += cpu.totalProcessedTime
			self.metrics.totalCtxxTime += cpu.totalCtxxTime

		self.metrics.n_timedOutInProcess = self.requestsInSystem.timedOutCount
		self.metrics.calculate(self.system.n_CPUs)
		return self.metrics
