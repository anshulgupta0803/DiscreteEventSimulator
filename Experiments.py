from Simulator import Simulator
from System import System
import os
import matplotlib.pyplot as plt
import scipy
from scipy import stats

def confidenceIntervals(samples, beta):
	mean = scipy.mean(samples)
	std = scipy.std(samples)
	n_samples = len(samples)
	alpha = stats.norm.ppf((1 + beta) / 2)
	margin = std * alpha / scipy.sqrt(n_samples)

	return (mean - margin, mean, mean + margin)

def correctness(prefix):
	parameters = System.Parameters(
							n_users = 50,
							n_CPUs = 1,
							easeInTime = 20.0,
							maxIters = 10000,
							bufferCapacity = 8000000,
							threadpoolSize = 2000000,
							quantum = 10000.0,
							ctxxTime = 0.0,
							serviceTimeMean = 0.5,
							requestTimeoutMin = 1000.0,
							requestTimeoutMax = 2000.0,
							thinkTimeMean = 12.0,
							thinkTimeStdv = 4.0,
							retryThinkTimeMean = 12.0,
							retryThinkTimeStdv = 4.0
						)

	x_data = []
	throughput_y_data = []
	responseTime_y_data = []
	responseTime_ci = []
	utilization_y_data = []

	min_users = 1
	max_users = 60
	beta = 0.95

	for users in range(min_users, max_users + 1):
		print("Users:", users)
		repeatRuns = 10
		parameters.n_users = users
		x_data.append(users)
		throughput = 0.0
		responseTime_samples = []
		utilization = 0.0
		for _ in range(0, repeatRuns):
			simulator = Simulator(parameters)
			metrics = simulator.run()
			throughput += metrics.throughput
			responseTime_samples.append(metrics.responseTime)
			utilization += metrics.utilization


		(responseTime_lb, responseTime_mean, responseTime_ub) = confidenceIntervals(responseTime_samples, beta)
		throughput_y_data.append(scipy.mean(throughput))
		utilization_y_data.append(scipy.mean(utilization))
		responseTime_y_data.append(responseTime_mean)
		responseTime_ci.append((responseTime_ub - responseTime_lb) / 2)

	f = open(prefix + "_data.tsv", "w")
	print("Users\tThroughput\tResponseTime\tUtilization", file=f)
	for i in range(min_users - 1, max_users):
		print(x_data[i], end="\t", file=f)
		print("{0:.4f}".format(throughput_y_data[i]), end="\t", file=f)
		print("{0:.4f}".format(responseTime_y_data[i]), end="\t", file=f)
		print("{0:.4f}".format(utilization_y_data[i]), file=f)
	f.close()

	plt.title("Throughput v/s Users")
	plt.xlabel("Users")
	plt.ylabel("Throughput (req / s)")
	plt.plot(x_data, throughput_y_data, "c")
	plt.grid(True)
	plt.savefig(prefix + "_Throughput.png")
	plt.close()

	plt.title("Response Time v/s Users")
	plt.xlabel("Users")
	plt.ylabel("Response Time (s)")
	plt.plot(x_data, responseTime_y_data, "m")
	plt.errorbar(x_data, responseTime_y_data, yerr=responseTime_ci, linestyle="None")
	plt.grid(True)
	plt.savefig(prefix + "_ResponseTime.png")
	plt.close()

	plt.title("CPU Utilization v/s Users")
	plt.xlabel("Users")
	plt.ylabel("CPU Utilization")
	plt.plot(x_data, utilization_y_data, "y")
	plt.grid(True)
	plt.savefig(prefix + "_Utilization.png")
	plt.close()

def run1(prefix):
	parameters = System.Parameters(
							n_users = 25,
							n_CPUs = 4,
							easeInTime = 20.0,
							maxIters = 10000,
							bufferCapacity = 800,
							threadpoolSize = 200,
							quantum = 0.5,
							ctxxTime = 0.01,
							serviceTimeMean = 2.0,
							requestTimeoutMin = 5.0,
							requestTimeoutMax = 15.0,
							thinkTimeMean = 12.0,
							thinkTimeStdv = 4.0,
							retryThinkTimeMean = 12.0,
							retryThinkTimeStdv = 4.0
						)

	x_data = []
	throughput_y_data = []
	responseTime_y_data = []
	responseTime_ci = []
	utilization_y_data = []
	goodput_y_data = []
	badput_y_data = []
	dropRate_y_data = []
	droppedFraction_y_data = []
	timedOutFraction_y_data = []

	min_users = 1
	max_users = 40
	beta = 0.95

	for users in range(min_users, max_users + 1):
		print("Users:", users)
		repeatRuns = 10
		parameters.n_users = users
		x_data.append(users)
		throughput = 0.0
		responseTime_samples = []
		utilization = 0.0
		goodput = 0.0
		badput = 0.0
		dropRate = 0.0
		droppedFraction = 0.0
		timedOutFraction = 0.0
		for _ in range(0, repeatRuns):
			simulator = Simulator(parameters)
			metrics = simulator.run()
			throughput += metrics.throughput
			responseTime_samples.append(metrics.responseTime)
			utilization += metrics.utilization
			goodput += metrics.goodput
			badput += metrics.badput
			dropRate += metrics.dropRate
			droppedFraction += metrics.droppedFraction
			timedOutFraction += metrics.timedOutFraction

		(responseTime_lb, responseTime_mean, responseTime_ub) = confidenceIntervals(responseTime_samples, beta)
		throughput_y_data.append(scipy.mean(throughput) / repeatRuns)
		utilization_y_data.append(scipy.mean(utilization) / repeatRuns)
		responseTime_y_data.append(responseTime_mean)
		responseTime_ci.append((responseTime_ub - responseTime_lb) / 2)
		goodput_y_data.append(scipy.mean(goodput) / repeatRuns)
		badput_y_data.append(scipy.mean(badput) / repeatRuns)
		dropRate_y_data.append(scipy.mean(dropRate) / repeatRuns)
		droppedFraction_y_data.append(scipy.mean(droppedFraction) / repeatRuns)
		timedOutFraction_y_data.append(scipy.mean(timedOutFraction) / repeatRuns)

	f = open(prefix + "_data.tsv", "w")
	print("Users\tThroughput\tResponseTime\tUtilization\tGoodput\tBadput\tDropRate", file=f)
	for i in range(min_users - 1, max_users):
		print(x_data[i], end="\t", file=f)
		print("{0:.4f}".format(throughput_y_data[i]), end="\t", file=f)
		print("{0:.4f}".format(responseTime_y_data[i]), end="\t", file=f)
		print("{0:.4f}".format(utilization_y_data[i]), end="\t", file=f)
		print("{0:.4f}".format(goodput_y_data[i]), end="\t", file=f)
		print("{0:.4f}".format(badput_y_data[i]), end="\t", file=f)
		print("{0:.4f}".format(dropRate_y_data[i]), file=f)
	f.close()

	plt.title("Throughput v/s Users")
	plt.xlabel("Users")
	plt.ylabel("Throughput (req / s)")
	plt.plot(x_data, throughput_y_data, "c")
	plt.grid(True)
	plt.savefig(prefix + "_Throughput.png")
	plt.close()

	plt.title("Goodput v/s Users")
	plt.xlabel("Users")
	plt.ylabel("Goodput (req / s)")
	plt.plot(x_data, goodput_y_data, "c")
	plt.grid(True)
	plt.savefig(prefix + "_Goodput.png")
	plt.close()

	plt.title("Badput v/s Users")
	plt.xlabel("Users")
	plt.ylabel("Badput (req / s)")
	plt.plot(x_data, badput_y_data, "c")
	plt.grid(True)
	plt.savefig(prefix + "_Badput.png")
	plt.close()

	plt.title("Request Drop Rate v/s Users")
	plt.xlabel("Users")
	plt.ylabel("Request Drop Rate (req / s)")
	plt.plot(x_data, dropRate_y_data, "c")
	plt.grid(True)
	plt.savefig(prefix + "_DropRate.png")
	plt.close()

	plt.title("Request Drop Fracttion v/s Users")
	plt.xlabel("Users")
	plt.ylabel("Request Drop Fraction")
	plt.plot(x_data, droppedFraction_y_data, "c")
	plt.grid(True)
	plt.savefig(prefix + "_DroppedFraction.png")
	plt.close()

	plt.title("Timed out Fracttion v/s Users")
	plt.xlabel("Users")
	plt.ylabel("Timed Out Fraction")
	plt.plot(x_data, timedOutFraction_y_data, "c")
	plt.grid(True)
	plt.savefig(prefix + "_TimedOutFraction.png")
	plt.close()

	plt.title("Response Time v/s Users")
	plt.xlabel("Users")
	plt.ylabel("Response Time (s)")
	plt.plot(x_data, responseTime_y_data, "c")
	plt.errorbar(x_data, responseTime_y_data, yerr=responseTime_ci, linestyle="None")
	plt.grid(True)
	plt.savefig(prefix + "_ResponseTime.png")
	plt.close()

	plt.title("CPU Utilization v/s Users")
	plt.xlabel("Users")
	plt.ylabel("CPU Utilization")
	plt.plot(x_data, utilization_y_data, "c")
	plt.grid(True)
	plt.savefig(prefix + "_Utilization.png")
	plt.close()

	plt.title("CPU Utilization v/s Throughput")
	plt.xlabel("Throught")
	plt.ylabel("CPU Utilization")
	plt.plot(throughput_y_data, utilization_y_data, "c")
	plt.grid(True)
	plt.savefig(prefix + "_UtilizationThroughput.png")
	plt.close()

def run2(prefix):
	parameters = System.Parameters(
							n_users = 25,
							n_CPUs = 4,
							easeInTime = 20.0,
							maxIters = 10000,
							bufferCapacity = 800,
							threadpoolSize = 200,
							quantum = 0.5,
							ctxxTime = 0.01,
							serviceTimeMean = 2.0,
							requestTimeoutMin = 5.0,
							requestTimeoutMax = 15.0,
							thinkTimeMean = 12.0,
							thinkTimeStdv = 4.0,
							retryThinkTimeMean = 12.0,
							retryThinkTimeStdv = 4.0
						)

	x_data = []
	throughput_y_data = []
	responseTime_y_data = []
	responseTime_ci = []
	utilization_y_data = []
	goodput_y_data = []
	badput_y_data = []
	dropRate_y_data = []
	droppedFraction_y_data = []
	timedOutFraction_y_data = []

	min_ctxxTime = 0.0
	max_ctxxTime = 1.0
	step = 0.05
	beta = 0.95

	for ctxxTime in [0.00, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0]:
		print("ctxxTime:", ctxxTime)
		repeatRuns = 10
		parameters.ctxxTime = ctxxTime
		x_data.append(ctxxTime)
		throughput = 0.0
		responseTime_samples = []
		utilization = 0.0
		goodput = 0.0
		badput = 0.0
		dropRate = 0.0
		droppedFraction = 0.0
		timedOutFraction = 0.0
		for _ in range(0, repeatRuns):
			simulator = Simulator(parameters)
			metrics = simulator.run()
			throughput += metrics.throughput
			responseTime_samples.append(metrics.responseTime)
			utilization += metrics.utilization
			goodput += metrics.goodput
			badput += metrics.badput
			dropRate += metrics.dropRate
			droppedFraction += metrics.droppedFraction
			timedOutFraction += metrics.timedOutFraction

		(responseTime_lb, responseTime_mean, responseTime_ub) = confidenceIntervals(responseTime_samples, beta)
		throughput_y_data.append(scipy.mean(throughput) / repeatRuns)
		utilization_y_data.append(scipy.mean(utilization) / repeatRuns)
		responseTime_y_data.append(responseTime_mean)
		responseTime_ci.append((responseTime_ub - responseTime_lb) / 2)
		goodput_y_data.append(scipy.mean(goodput) / repeatRuns)
		badput_y_data.append(scipy.mean(badput) / repeatRuns)
		dropRate_y_data.append(scipy.mean(dropRate) / repeatRuns)
		droppedFraction_y_data.append(scipy.mean(droppedFraction) / repeatRuns)
		timedOutFraction_y_data.append(scipy.mean(timedOutFraction) / repeatRuns)

	# f = open(prefix + "_data.tsv", "w")
	# print("ctxxTime\tThroughput\tResponseTime\tUtilization\tGoodput\tBadput\tDropRate", file=f)
	# for i in range(min_users - 1, max_users):
	# 	print(x_data[i], end="\t", file=f)
	# 	print("{0:.4f}".format(throughput_y_data[i]), end="\t", file=f)
	# 	print("{0:.4f}".format(responseTime_y_data[i]), end="\t", file=f)
	# 	print("{0:.4f}".format(utilization_y_data[i]), end="\t", file=f)
	# 	print("{0:.4f}".format(goodput_y_data[i]), end="\t", file=f)
	# 	print("{0:.4f}".format(badput_y_data[i]), end="\t", file=f)
	# 	print("{0:.4f}".format(dropRate_y_data[i]), file=f)
	# f.close()

	plt.title("Throughput v/s CtxxTime")
	plt.xlabel("CtxxTime")
	plt.ylabel("Throughput (req / s)")
	plt.plot(x_data, throughput_y_data, "c")
	plt.grid(True)
	plt.savefig(prefix + "_Throughput.png")
	plt.close()

	plt.title("Goodput v/s CtxxTime")
	plt.xlabel("CtxxTime")
	plt.ylabel("Goodput (req / s)")
	plt.plot(x_data, goodput_y_data, "c")
	plt.grid(True)
	plt.savefig(prefix + "_Goodput.png")
	plt.close()

	plt.title("Badput v/s CtxxTime")
	plt.xlabel("CtxxTime")
	plt.ylabel("Badput (req / s)")
	plt.plot(x_data, badput_y_data, "c")
	plt.grid(True)
	plt.savefig(prefix + "_Badput.png")
	plt.close()

	plt.title("Request Drop Rate v/s CtxxTime")
	plt.xlabel("CtxxTime")
	plt.ylabel("Request Drop Rate (req / s)")
	plt.plot(x_data, dropRate_y_data, "c")
	plt.grid(True)
	plt.savefig(prefix + "_DropRate.png")
	plt.close()

	plt.title("Request Drop Fracttion v/s CtxxTime")
	plt.xlabel("CtxxTime")
	plt.ylabel("Request Drop Fraction")
	plt.plot(x_data, droppedFraction_y_data, "c")
	plt.grid(True)
	plt.savefig(prefix + "_DroppedFraction.png")
	plt.close()

	plt.title("Timed out Fracttion v/s CtxxTime")
	plt.xlabel("CtxxTime")
	plt.ylabel("Timed Out Fraction")
	plt.plot(x_data, timedOutFraction_y_data, "c")
	plt.grid(True)
	plt.savefig(prefix + "_TimedOutFraction.png")
	plt.close()

	plt.title("Response Time v/s CtxxTime")
	plt.xlabel("CtxxTime")
	plt.ylabel("Response Time (s)")
	plt.plot(x_data, responseTime_y_data, "c")
	plt.errorbar(x_data, responseTime_y_data, yerr=responseTime_ci, linestyle="None")
	plt.grid(True)
	plt.savefig(prefix + "_ResponseTime.png")
	plt.close()

	plt.title("CPU Utilization v/s CtxxTime")
	plt.xlabel("CtxxTime")
	plt.ylabel("CPU Utilization")
	plt.plot(x_data, utilization_y_data, "c")
	plt.grid(True)
	plt.savefig(prefix + "_Utilization.png")
	plt.close()

	plt.title("CPU Utilization v/s Throughput")
	plt.xlabel("Throught")
	plt.ylabel("CPU Utilization")
	plt.plot(throughput_y_data, utilization_y_data, "c")
	plt.grid(True)
	plt.savefig(prefix + "_UtilizationThroughput.png")
	plt.close()


def run3(prefix):
	parameters = System.Parameters(
							n_users = 25,
							n_CPUs = 4,
							easeInTime = 20.0,
							maxIters = 10000,
							bufferCapacity = 800,
							threadpoolSize = 200,
							quantum = 0.5,
							ctxxTime = 0.01,
							serviceTimeMean = 2.0,
							requestTimeoutMin = 5.0,
							requestTimeoutMax = 15.0,
							thinkTimeMean = 12.0,
							thinkTimeStdv = 4.0,
							retryThinkTimeMean = 12.0,
							retryThinkTimeStdv = 4.0
						)

	x_data = []
	throughput_y_data = []
	responseTime_y_data = []
	responseTime_ci = []
	utilization_y_data = []
	goodput_y_data = []
	badput_y_data = []
	dropRate_y_data = []
	droppedFraction_y_data = []
	timedOutFraction_y_data = []

	min_quantum = 0.5
	max_quantum = 4.0
	step = 0.5
	beta = 0.95

	for ctxxTime in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 3.0, 4.0]:
		print("Quantum:", ctxxTime)
		repeatRuns = 10
		parameters.quantum = ctxxTime
		x_data.append(ctxxTime)
		throughput = 0.0
		responseTime_samples = []
		utilization = 0.0
		goodput = 0.0
		badput = 0.0
		dropRate = 0.0
		droppedFraction = 0.0
		timedOutFraction = 0.0
		for _ in range(0, repeatRuns):
			simulator = Simulator(parameters)
			metrics = simulator.run()
			throughput += metrics.throughput
			responseTime_samples.append(metrics.responseTime)
			utilization += metrics.utilization
			goodput += metrics.goodput
			badput += metrics.badput
			dropRate += metrics.dropRate
			droppedFraction += metrics.droppedFraction
			timedOutFraction += metrics.timedOutFraction

		(responseTime_lb, responseTime_mean, responseTime_ub) = confidenceIntervals(responseTime_samples, beta)
		throughput_y_data.append(scipy.mean(throughput) / repeatRuns)
		utilization_y_data.append(scipy.mean(utilization) / repeatRuns)
		responseTime_y_data.append(responseTime_mean)
		responseTime_ci.append((responseTime_ub - responseTime_lb) / 2)
		goodput_y_data.append(scipy.mean(goodput) / repeatRuns)
		badput_y_data.append(scipy.mean(badput) / repeatRuns)
		dropRate_y_data.append(scipy.mean(dropRate) / repeatRuns)
		droppedFraction_y_data.append(scipy.mean(droppedFraction) / repeatRuns)
		timedOutFraction_y_data.append(scipy.mean(timedOutFraction) / repeatRuns)

	# f = open(prefix + "_data.tsv", "w")
	# print("ctxxTime\tThroughput\tResponseTime\tUtilization\tGoodput\tBadput\tDropRate", file=f)
	# for i in range(min_users - 1, max_users):
	# 	print(x_data[i], end="\t", file=f)
	# 	print("{0:.4f}".format(throughput_y_data[i]), end="\t", file=f)
	# 	print("{0:.4f}".format(responseTime_y_data[i]), end="\t", file=f)
	# 	print("{0:.4f}".format(utilization_y_data[i]), end="\t", file=f)
	# 	print("{0:.4f}".format(goodput_y_data[i]), end="\t", file=f)
	# 	print("{0:.4f}".format(badput_y_data[i]), end="\t", file=f)
	# 	print("{0:.4f}".format(dropRate_y_data[i]), file=f)
	# f.close()

	plt.title("Throughput v/s Quantum")
	plt.xlabel("Quantum")
	plt.ylabel("Throughput (req / s)")
	plt.plot(x_data, throughput_y_data, "c")
	plt.grid(True)
	plt.savefig(prefix + "_Throughput.png")
	plt.close()

	plt.title("Goodput v/s Quantum")
	plt.xlabel("Quantum")
	plt.ylabel("Goodput (req / s)")
	plt.plot(x_data, goodput_y_data, "c")
	plt.grid(True)
	plt.savefig(prefix + "_Goodput.png")
	plt.close()

	plt.title("Badput v/s Quantum")
	plt.xlabel("Quantum")
	plt.ylabel("Badput (req / s)")
	plt.plot(x_data, badput_y_data, "c")
	plt.grid(True)
	plt.savefig(prefix + "_Badput.png")
	plt.close()

	plt.title("Request Drop Rate v/s Quantum")
	plt.xlabel("Quantum")
	plt.ylabel("Request Drop Rate (req / s)")
	plt.plot(x_data, dropRate_y_data, "c")
	plt.grid(True)
	plt.savefig(prefix + "_DropRate.png")
	plt.close()

	plt.title("Request Drop Fracttion v/s Quantum")
	plt.xlabel("Quantum")
	plt.ylabel("Request Drop Fraction")
	plt.plot(x_data, droppedFraction_y_data, "c")
	plt.grid(True)
	plt.savefig(prefix + "_DroppedFraction.png")
	plt.close()

	plt.title("Timed out Fracttion v/s Quantum")
	plt.xlabel("Quantum")
	plt.ylabel("Timed Out Fraction")
	plt.plot(x_data, timedOutFraction_y_data, "c")
	plt.grid(True)
	plt.savefig(prefix + "_TimedOutFraction.png")
	plt.close()

	plt.title("Response Time v/s Quantum")
	plt.xlabel("Quantum")
	plt.ylabel("Response Time (s)")
	plt.plot(x_data, responseTime_y_data, "c")
	plt.errorbar(x_data, responseTime_y_data, yerr=responseTime_ci, linestyle="None")
	plt.grid(True)
	plt.savefig(prefix + "_ResponseTime.png")
	plt.close()

	plt.title("CPU Utilization v/s Quantum")
	plt.xlabel("Quantum")
	plt.ylabel("CPU Utilization")
	plt.plot(x_data, utilization_y_data, "c")
	plt.grid(True)
	plt.savefig(prefix + "_Utilization.png")
	plt.close()

	plt.title("CPU Utilization v/s Throughput")
	plt.xlabel("Throught")
	plt.ylabel("CPU Utilization")
	plt.plot(throughput_y_data, utilization_y_data, "c")
	plt.grid(True)
	plt.savefig(prefix + "_UtilizationThroughput.png")
	plt.close()

if not(os.path.exists("graphs")):
	os.mkdir("graphs")

correctness(os.path.join("graphs", "correctness"))
run1(os.path.join("graphs", "run1"))
run2(os.path.join("graphs", "run2"))
run3(os.path.join("graphs", "run3"))
