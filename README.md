# MicroPython quadrature incremental encoder

MicroPython quadrature incremental encoder based on pin interrupts.  
It uses [Quadrature decoder state table](https://en.wikipedia.org/wiki/Incremental_encoder#Quadrature_decoder) and state transitions.

Applicable for hand-driven devices like

![image](https://user-images.githubusercontent.com/70886343/136481028-a9066ee9-d531-4393-8799-ae64ae83eddf.png)

See also encoder problems and code samples at [Incremental encoders](https://github.com/peterhinch/micropython-samples/blob/master/encoders/ENCODERS.md) by Peter Hinch.

Minimal example:
```
from machine import Pin

from encoder_state import Encoder

enc = Encoder(Pin(1), Pin(2))
value = enc.value()
while True:
    val = enc.value()
    if value != val:
        value = val
        print(value)
```

Quick start:
  * Connect encoder to the MicroPython board.
  * Upload the encoder_state.py to the board.
  * Run the encoders_test.py

Tested on ESP32 board.

Needs to be tested on other MicroPython boards.
