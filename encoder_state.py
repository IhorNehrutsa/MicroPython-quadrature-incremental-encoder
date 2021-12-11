# encoder_state.py

# Copyright (c) 2021 Ihor Nehrutsa
# Released under the MIT License (MIT) - see LICENSE file


class Encoder:
    def __init__(self, phase_a, phase_b, x124=4, scale=1):
        self.pin_a = phase_a
        self.pin_b = phase_b
        self.x124 = x124
        self.scale = scale  # Optionally scale encoder rate to distance/angle etc.

        self._value = 0  # raw counter value

        self._state = 0  # encoder state transitions
        if x124 == 1:
            self._x = (0, 0, 1, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0)
        elif x124 == 2:
            self._x = (0, 0, 1, 0, 0, 0, 0, -1, -1, 0, 0, 0, 0, 1, 0, 0)
        elif x124 == 4:
            self._x = (0, -1, 1, 0, 1, 0, 0, -1, -1, 0, 0, 1, 0, 1, -1, 0)
        else:
            raise ValueError("multiplier x124 must be from [1, 2, 4]")

        try:
            self.pin_a.irq(self._callback, hard=True)
            self.pin_b.irq(self._callback, hard=True)
        except TypeError:
            self.pin_a.irq(self._callback)
            self.pin_b.irq(self._callback)

    def deinit(self):
        # use deinit(), otherwise _callback() will work after exiting the program
        try:
            self.pin_a.irq(None)
        except:
            pass
        try:
            self.pin_b.irq(None)
        except:
            pass

    def __repr__(self):
        return 'Encoder(A={}, B={}, x124={}, scale={})'.format(
            self.pin_a, self.pin_b, self.x124, self.scale)

    def _callback(self, pin):
        self._state = ((self._state << 2) + (self.pin_a() << 1) + self.pin_b()) & 0xF
        self._value += self._x[self._state]

    def get_value(self):
        return self._value

    def value(self, value=None):
        _value = self._value
        if value is not None:
            self._value = value
        return _value

    def scaled(self, scaled=None):
        _scaled = self._value * self.scale
        if scaled is not None:
            self._value = round(scaled / self.scale)
        return _scaled

