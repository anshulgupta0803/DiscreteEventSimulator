#!/usr/bin/env python3

from Simulator import Simulator
from System import System

parameters = System.Parameters(
					n_users = 50,
					n_CPUs = 4,
					easeInTime = 20.0,
					maxIters = 10000,
					bufferCapacity = 800,
					threadpoolSize = 200,
					quantum = 0.5,
					ctxxTime = 1,
					serviceTimeMean = 2,
					requestTimeoutMin = 100.0,
					requestTimeoutMax = 300.0,
					thinkTimeMean = 12.0,
					thinkTimeStdv = 4.0,
					retryThinkTimeMean = 12.0,
					retryThinkTimeStdv = 4.0
				)

simulator = Simulator(parameters)
metrics = simulator.run()
metrics.display()
