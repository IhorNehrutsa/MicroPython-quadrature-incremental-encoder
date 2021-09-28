# quad_irq.py

from utime import ticks_ms, ticks_us, ticks_diff

DEBOUNCE_MS = 20  # ms

class Debounce():
    def __init__(self, pin, debounce_ms=DEBOUNCE_MS):
        self.prev_value = pin.value()
        self._time = ticks_ms()
        self.stable_value = self.prev_value
        
        self.pin = pin
        self.debounce_ms = debounce_ms
        
    def __repr__(self):
        return 'Debounce({}, debounce_ms={})'.format(self.pin, self.debounce_ms)
    
    def value(self):
        _value = self.pin.value()
        _time = ticks_ms()
        if self.prev_value != _value:
            self.prev_value = _value
            self._time = _time
        else:
            dt = ticks_diff(_time, self._time)
            if dt <= 0:
                dt = self.debounce_ms
                
            if dt >= self.debounce_ms:
               self.stable_value = _value
               
        return self.stable_value
    

class ClockMultiplier:
    x1 = 1
    x2 = 2
    x4 = 4


class QUAD():
    _x1 = (0, 0, 1, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0) 
    _x2 = (0, 0, 1, 0, 0, 0, 0, -1, -1, 0, 0, 0, 0, 1, 0, 0)
    _x4 = (0, -1, 1, 0, 1, 0, 0, -1, -1, 0, 0, 1, 0, 1, -1, 0)

    def __init__(self, a, b, ppr=30, x124=ClockMultiplier.x2, c=None):
        self.a = a
        self.b = b
        self.x124 = x124
        
        self.c = c
        self.ppr = ppr
        self._rps = 0
        
        self.dir = 0

        self._count = 0
        self._state = 0
        self._time = ticks_us()

        if x124 == ClockMultiplier.x1:
            self._x = self._x1
        elif x124 == ClockMultiplier.x2:
            self._x = self._x2
        elif x124 == ClockMultiplier.x4:
            self._x = self._x4
        else:
            raise ValueError("x124 must be from [1, 2, 4]")

        self.c_debounced_value = None
        if c is not None:
            self.c_debounce = Debounce(c)
            self.c_debounced_value = self.c_debounce.value()
            self.c.irq(self.Isr)
        self.a.irq(self.Isr)
        self.b.irq(self.Isr)
        
    def deinit(self):
        try:
            self.a.irq(None)
        except:
            pass
        try:
            self.b.irq(None)
        except:
            pass
        try:
            if self.c is not None:
                self.c.irq(None)
        except:
            pass
    
    def __del__(self):
        self.deinit()

    def __repr__(self): 
        ret = 'QUAD(A={}, B={}, x124={}'.format(self.a, self.b, self.x124)
        if self.c is not None:
            ret += ', C={}, ppr={}'.format(self.c, self.ppr)
        return ret + ')'
    
    def Isr(self, pin):
        c_debounced_value = self.c_debounce.value()
        if (pin == self.a) or (pin == self.b):
            self._state = ((self._state << 2) + (self.b.value() << 1) + self.a.value()) & 0xF
            self.dir = self._x[self._state]
            self._count += self.dir
            if (pin == self.b) and (self.dir != 0):
                _time = ticks_us()
                dt = ticks_diff(_time, self._time)
                self._time = _time
                if dt > 0:
                    self._rps = self.dir * 1_000_000 / (self.ppr * self.x124 * dt)

        if self.c_debounced_value == c_debounced_value:
            if self.c.value() == 0:
                self._count = self.ppr * round(self._count / self.ppr)
        else:
            self.c_debounced_value = c_debounced_value

    def count(self):
        return self._count
 
    def set_count(self, count):
        self._count = count

    def rps(self):
        return self._rps
        
    def rpm(self):
        return self._rps * 60
    