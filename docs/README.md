# ESP32 Conway's Game of Life for Python

MicroPython implementation.

## ESP32-S3-BOX-3

MicroPython + SDL3 - https://github.com/georgik/micropython/tree/experimental/esp32-s3-box-3-sdl3

Use Thonny or other tool to copy `conway.py` to board.

## Desktop

Python 3 implementation with SDL3.

```shell
cd desktop
pip install -r requirements.txt
python3 conway.py
```

## NuttX and Python

Simulator on desktop

```shell
cd nuttx
pip install -r requirements.txt
python simulator.py
```

Running on NuttX:
- change device `/tmp/leds0` to `/dev/leds0`
