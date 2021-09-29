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
    

class Encoder():
    def __init__(self, a, b, ppr=30, x124=2, scale=1, c=None):
        self.a = a
        self.b = b
        self.ppr = ppr
        self.x124 = x124
        self.scale = scale

        self.c = c
        self._rps = 0
        
        self._dir = 0

        self._counter = 0
        self._state = 0
        self._time = ticks_us()

        if x124 == 1:
            self._x = (0, 0, 1, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0) 
        elif x124 == 2:
            self._x = (0, 0, 1, 0, 0, 0, 0, -1, -1, 0, 0, 0, 0, 1, 0, 0)
        elif x124 == 4:
            self._x = (0, -1, 1, 0, 1, 0, 0, -1, -1, 0, 0, 1, 0, 1, -1, 0)
        else:
            raise ValueError("x124 must be from [1, 2, 4]")

        if c is not None:
            self.c_debounced_value = None
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
        ret = 'Encoder(A={}, B={}, mppr={}, x124={}, scale={}'.format(self.a, self.b, self.ppr, self.x124, self.scale)
        if self.c is not None:
            ret += ', C={}'.format(self.c)
        return ret + ')'
    
    def Isr(self, pin):
        _time = ticks_us()
        if self.c is not None:
            c_debounced_value = self.c_debounce.value()
        if (pin == self.a) or (pin == self.b):
            self._state = ((self._state << 2) + (self.b.value() << 1) + self.a.value()) & 0xF
            _dir = self._x[self._state]
            self._counter += _dir
            if (pin == self.b) and (_dir != 0):
                self._dir = _dir
                dt = ticks_diff(_time, self._time)
                self._time = _time
                if dt > 0:
                    self._rps = _dir * 1_000_000 / (self.ppr * self.x124 * dt)

        if self.c is not None:
            if self.c_debounced_value == c_debounced_value:
                if self.c.value() == 0:
                    self._counter = self.ppr * round(self._counter / self.ppr)
            else:
                self.c_debounced_value = c_debounced_value
            
    def dir(self):
        _dir = self._dir
        self._dir = 0
        return _dir

    def counter(self):
        return self._counter
 
    def set_counter(self, counter):
        self._counter = counter

    def rps(self):
        return self._rps
        
    def rpm(self):
        return self._rps * 60

    def position(self, value=None):
        if value is not None:
            self._counter = value // self.scale
        return self._counter * self.scale
