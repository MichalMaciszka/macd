import pandas as pd
import matplotlib.pyplot as plt


def EMA(num, array, start_index):
    alpha = 2/(num + 1)
    licznik = 0
    mianownik = 0

    for i in range(num + 1):
        licznik += pow(1-alpha, i) * array[start_index - i]
        mianownik += pow(1-alpha, i)

    return licznik / mianownik


def buy(capital, amount, price):
    amount += (capital/price)
    capital = 0
    return capital, amount


def sell(capital, amount, price):
    capital += amount * price
    amount = 0
    return capital, amount


def decide(macd, signal, i, capital, amount, price):
    if macd[i-1] > signal[i-1]:
        return sell(capital, amount, price)
    return buy(capital, amount, price)


def williams_indicator(array, index, n):
    tmp = []
    for i in range(n):
        tmp.append(data[index - i])
    maxVal = max(tmp)
    minVal = min(tmp)
    current = array[index]
    val = ((maxVal - current)/(maxVal-minVal)) * (-100)
    return val


if __name__ == '__main__':
    data = pd.read_csv("cdpr.csv")

    latency = 0

    data = data['Zamkniecie']
    data = data.tolist()

    macd = []

    for i in range(26, len(data)):
        EMA_12 = EMA(12, data, i - latency)
        EMA_26 = EMA(26, data, i - latency)
        macd.append(EMA_12 - EMA_26)

    signal = []
    for i in range(9, len(macd)):
        signal.append(EMA(9, macd, i))

    williams = []
    x = 14
    for i in range(x-1, len(data)):
        williams.append(williams_indicator(data, i, x))

    del data[0:26]
    del macd[0:9]
    del data[0:9]
    del williams[0:(35 - x + 1)]

    print(len(data))
    print(len(macd))
    print(len(signal))
    print(len(williams))

    x_axis = list(range(1, len(data)+1))

    capital = 1000
    amount = 0

    print("POCZATEK: ")
    print("W PLN: ", capital)
    print("W akcjach: ", (amount * data[0]))

    next_buy = False
    next_sell = False
    l = 0

    for i in range(1, len(data)):
        if next_buy:
            if l == 0:
                capital, amount = buy(capital, amount, data[i])
                next_buy = False
            else:
                l -= 1
        elif next_sell:
            if l == 0:
                capital, amount = sell(capital, amount, data[i])
                next_sell = False
            else:
                l -= 1

        if macd[i] == signal[i]:
            capital, amount = decide(macd, signal, i, capital, amount, data[i])
        elif macd[i] > signal[i] and macd[i-1] < signal[i-1]:
            capital, amount = buy(capital, amount, data[i])
        elif macd[i] < signal[i] and macd[i-1] > signal[i-1]:
            capital, amount = sell(capital, amount, data[i])

        if williams[i] > -20:
            if not next_sell:
                l = 3
            next_sell = True
        elif williams[i] < -80:
            if not next_buy:
                l = 3
            next_buy = True

    print("KONIEC")
    print("W PLN: ", capital)
    print("W akcjach: ", (data[-1] * amount))

    plt.figure(figsize=(17, 6))
    plt.plot(x_axis, data, 'black', label='Zamkniecie', linewidth=2)
    plt.grid(True)
    plt.savefig("notowania.jpg", dpi=400)
    plt.figure(figsize=(17, 6))
    plt.plot(x_axis, macd, 'blue', label='MACD', linewidth=1)
    plt.plot(x_axis, signal, 'red', label='SIGNAL', linewidth=1)
    plt.grid(True)
    plt.savefig('wykres.jpg', dpi=400)
    plt.figure(figsize=(17, 6))
    plt.plot(x_axis, williams, 'orange')
    plt.grid(True)
    plt.savefig("r williams", dpi=400)
    plt.show()
    plt.clf()
