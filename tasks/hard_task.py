import time

"""
Checking redis workers
"""
def complex_calculations(number, times):
    result =0
    for i in range(times):
        sum = number + times
        time.sleep(0.2)
        result += sum
    return result
