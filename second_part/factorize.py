import multiprocessing


def factorize_number(number):
    factors = []
    for i in range(1, number + 1):
        if number % i == 0:
            factors.append(i)
    return factors


def factorize(*numbers):
    result = [factorize_number(number) for number in numbers]
    return result


def multi_factorize_number(number):
    factors = []
    for i in range(1, number + 1):
        if number % i == 0:
            factors.append(i)
    return factors


def multi_factorize(*numbers):
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        results = pool.map(factorize_number, numbers)
    return results


if __name__ == "__main__":
    import time

    numbers = [128, 255, 99999, 10651060]

    start_time = time.time()
    result = factorize(*numbers)
    end_time = time.time()

    m_start_time = time.time()
    m_result = multi_factorize(*numbers)
    m_end_time = time.time()

    print("Synchronous execution time:", end_time - start_time)
    print(result)

    print("Parallel execution time:", m_end_time - m_start_time)
    print(m_result)
