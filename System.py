# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division, with_statement

class System():
	"""docstring for System."""
	class Parameters():
		"""docstring for Parameters."""
		def __init__(
						self,
						n_users,
						n_CPUs,
						easeInTime,
						maxIters,
						bufferCapacity,
						threadpoolSize,
						quantum,
						ctxxTime,
						serviceTimeMean,
						requestTimeoutMin,
						requestTimeoutMax,
						thinkTimeMean,
						thinkTimeStdv,
						retryThinkTimeMean,
						retryThinkTimeStdv
					):
			self.n_users = n_users
			self.n_CPUs = n_CPUs
			self.easeInTime = easeInTime
			self.maxIters = maxIters
			self.bufferCapacity = bufferCapacity
			self.threadpoolSize = threadpoolSize
			self.quantum = quantum
			self.ctxxTime = ctxxTime
			self.serviceTimeMean = serviceTimeMean
			self.requestTimeoutMin = requestTimeoutMin
			self.requestTimeoutMax = requestTimeoutMax
			self.thinkTimeMean = thinkTimeMean
			self.thinkTimeStdv = thinkTimeStdv
			self.retryThinkTimeMean = retryThinkTimeMean
			self.retryThinkTimeStdv = retryThinkTimeStdv

	class Metrics():
		"""docstring for Metrics."""
		def __init__(
						self,
						time = 0.0,
						n_arrivals = 0,
						n_processed = 0,
						n_timedOut = 0,
						n_dropped = 0,
						n_timedOutInProcess = 0,
						totalResponseTime = 0.0,
						weightedSumOfRequestsInSystem = 0.0,
						totalProcessedTime = 0.0,
						totalCtxxTime = 0.0
					):
			self.time = time
			self.n_arrivals = n_arrivals
			self.n_processed = n_processed
			self.n_timedOut = n_timedOut
			self.n_dropped = n_dropped
			self.n_timedOutInProcess = n_timedOutInProcess
			self.totalResponseTime = totalResponseTime
			self.weightedSumOfRequestsInSystem = weightedSumOfRequestsInSystem
			self.totalProcessedTime = totalProcessedTime
			self.totalCtxxTime = totalCtxxTime

		def calculate(self, n_CPUs):
			self.arrivalRate = self.n_arrivals / self.time
			self.throughput = self.n_processed / self.time
			self.goodput = (self.n_processed - (self.n_timedOut - self.n_timedOutInProcess)) / self.time
			self.badput = self.throughput - self.goodput
			self.responseTime = self.totalResponseTime / self.n_processed
			self.utilization = (self.totalProcessedTime + self.totalCtxxTime) / self.time / n_CPUs
			self.contextSwitchBusyTimeFraction = self.totalCtxxTime / (self.totalProcessedTime + self.totalCtxxTime)
			self.requestsInSystem = self.weightedSumOfRequestsInSystem / self.totalProcessedTime
			self.droppedFraction = self.n_dropped / (self.n_dropped + self.n_processed)
			self.dropRate = self.n_dropped / self.time
			self.timedOutFraction = (self.n_timedOut - self.n_timedOutInProcess) / (self.n_dropped + self.n_processed)

		def display(self):
			print("                         time |", self.time)
			print("                   n_arrivals |", self.n_arrivals)
			print("                  n_processed |", self.n_processed)
			print("                   n_timedOut |", self.n_timedOut)
			print("                    n_dropped |", self.n_dropped)
			print("          n_timedOutInProcess |", self.n_timedOutInProcess)
			print("            totalResponseTime |", self.totalResponseTime)
			print("weightedSumOfRequestsInSystem |", self.weightedSumOfRequestsInSystem)
			print("           totalProcessedTime |", self.totalProcessedTime)
			print("                totalCtxxTime |", self.totalCtxxTime)
			print("                  arrivalRate |", self.arrivalRate)
			print("                   throughput |", self.throughput)
			print("                      goodput |", self.goodput)
			print("                       badput |", self.badput)
			print("                 responseTime |", self.responseTime)
			print("                  utilization |", self.utilization)
			print("contextSwitchBusyTimeFraction |", self.contextSwitchBusyTimeFraction)
			print("             requestsInSystem |", self.requestsInSystem)
			print("              droppedFraction |", self.droppedFraction)
			print("                     dropRate |", self.dropRate)
			print("             timedOutFraction |", self.timedOutFraction)

	class RequestsInSystem():
		"""docstring for RequestsInSystem."""
		def __init__(self, lastModifiedTimestamp = 0.0, count = 0, timedOutCount = 0):
			self.lastModifiedTimestamp = lastModifiedTimestamp
			self.count = count
			self.timedOutCount = timedOutCount
