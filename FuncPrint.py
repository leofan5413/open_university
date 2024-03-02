import time

def _func_in_(name="", line=1):
    l_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print("[" + l_time.__str__() + "][" + name +"][" + line.__str__() + "] IN")


def _func_out_(name="", line=1):
    l_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print("[" + l_time.__str__() + "][" + name +"][" + line.__str__() + "] OUT")


def _func_logd_(name="", line=1, log=""):
    l_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print("[" + l_time.__str__() + "][" + name +"][" + line.__str__() + "] " + log.__str__())

def _func_logi_(name="", line=1, log="", end="\n"):
    l_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print("[" + l_time.__str__() + "][" + name +"][" + line.__str__() + "] " + log.__str__(), end=end)

def _func_loge_(name="", line=1, log=""):
    l_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print("[" + l_time.__str__() + "][" + name +"][" + line.__str__() + "][ERROR]" + log.__str__())
