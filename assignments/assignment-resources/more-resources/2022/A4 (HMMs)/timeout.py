import signal
import time


class TimeOutException(Exception):
    pass


def alarm_handler(signum, frame):
    print("ALARM signal received")
    raise TimeOutException()


def loop(n):
    for sec in range(n):
        print("sec {}".format(sec))
        time.sleep(1)


if __name__ == '__main__':
    signal.signal(signal.SIGALRM, alarm_handler)
    signal.alarm(8)

    try:
        loop(10)
    except TimeOutException as ex:
        print(ex)

    signal.alarm(3)
    try:
        loop(10)
    except TimeOutException as ex:
        print(ex)
    signal.alarm(0)


    loop(6)