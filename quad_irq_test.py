# quad_irq_test.py

from time import sleep
try:
    from machine import Pin
except ImportError:
    from pyb import Pin

from quad_irq import *

#Encoder
ENCODER_DATA = 17  # yellow
ENCODER_CLK = 16  # green
ENCODER_SW = 18 # orange

CORRECT_COUNTER = False

try:    
    data = Pin(ENCODER_DATA, mode=Pin.IN, pull=Pin.PULL_UP)
    clk = Pin(ENCODER_CLK, mode=Pin.IN, pull=Pin.PULL_UP)
    sw = Pin(ENCODER_SW, mode=Pin.IN, pull=Pin.PULL_UP)
    print('data', data, data.value())
    print('clk', clk, clk.value())
    print('sw', sw, sw.value())

    #enc1 = QUAD(data, clk, ppr=15, x124=ClockMultiplier.x1, c=sw)
    enc1 = QUAD(data, clk, ppr=30, x124=ClockMultiplier.x2, c=sw)
    #enc1 = QUAD(data, clk, ppr=60, x124=ClockMultiplier.x4) #, c=sw)
    print(enc1)

    _data = None
    _clk = None
    _sw = None
    _count = None

    while True:
        __data = data.value()
        __clk = clk.value()
        __sw = sw.value()
        __count = enc1.count()
        
        if (_data != __data) or (_clk != __clk) or (_sw != __sw)  or (_count != __count):
            _data = __data
            _clk = __clk
            _sw = __sw
            _count = __count

            if CORRECT_COUNTER:
                if _sw == 0:
                    enc1.set_count(enc1.ppr * round(enc1.count() / enc1.ppr))

            print("enc1={}, dir={}, rps={:10.3f}, data={}, clk={}, sw={} {}".format(_count, enc1.dir, enc1.rps(), _data, _clk, _sw, enc1.c_debounced_value), end='        \r')
            
        sleep(0.1)

finally:
    try:
        enc1.deinit()
    except:
        pass
