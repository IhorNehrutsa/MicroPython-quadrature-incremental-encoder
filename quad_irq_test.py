# quad_irq_test.py

from time import sleep
from machine import Pin

# YOU MAY USE
from quad_irq import *
# OR
#from encoder_portable import *

#Encoder
ENCODER_DATA = 17  # yellow
ENCODER_CLK = 16  # green
ENCODER_SW = 18  # orange

CORRECT_COUNTER = True  # False

try:    
    data = Pin(ENCODER_DATA, mode=Pin.IN, pull=Pin.PULL_UP)
    clk = Pin(ENCODER_CLK, mode=Pin.IN, pull=Pin.PULL_UP)
    sw = Pin(ENCODER_SW, mode=Pin.IN, pull=Pin.PULL_UP)
    print('data', data, data.value())
    print('clk', clk, clk.value())
    print('sw', sw, sw.value())

    #enc1 = Encoder(data, clk, ppr=15, x124=1, c=sw)
    #enc1 = Encoder(data, clk, ppr=30, x124=2)#, c=sw)
    #enc1 = Encoder(data, clk, ppr=60, x124=4) #, c=sw)
    enc1 = Encoder(data, clk)
    print(enc1)

    _data = None
    _clk = None
    _sw = None
    _counter = None

    while True:
        __data = data.value()
        __clk = clk.value()
        __sw = sw.value()
        __counter = enc1.position()  #enc1.counter()
        
        if (_data != __data) or (_clk != __clk) or (_sw != __sw)  or (_counter != __counter):
            _data = __data
            _clk = __clk
            _sw = __sw
            _counter = __counter

            if CORRECT_COUNTER:
                if _sw == 0:
                    # enc1.set_counter(enc1.ppr * round(enc1.counter() / enc1.ppr))
                    enc1.position(0)

            #print("enc1={}, dir={}, rps={:10.3f}, data={}, clk={}, sw={}".format(_counter, enc1.dir(), enc1.rps(), _data, _clk, _sw), end='        \r')
            print("enc1={}, data={}, clk={}, sw={}".format(_counter, _data, _clk, _sw), end='        \r')
            
        sleep(0.1)

finally:
    try:
        enc1.deinit()
    except:
        pass
