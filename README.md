# MicroPython MCP79410

MicroPython driver for the [MCP79410](https://www.microchip.com/en-us/product/mcp79410) real-time clock IC.

## Usage

The `MCP79410` constructor accepts an I2C instance.

```python
import time
from machine import Pin, I2C
from mcp79410 import MCP79410, DateTime, ALARM_MASK_ALL

i2c = I2C(0, sda=Pin(16), scl=Pin(17), freq=100000)

mcp = MCP79410(i2c)

# Update clock and start oscillator.
mcp.write_time_and_date(DateTime(14, 30, 50, 1, 30, 8, 2024), start_oscillator=1)

time.sleep(1)

# Get current time.
mcp.read_time_and_date()

# Configure alarm on complete match of the provided date-time (about one minute in the future).
# The alarm generates an interrupt on the MFP pin (not covered here).
mcp.write_alarm(0, DateTime(14, 31, 50, 1, 30, 8, 2024), ALARM_MASK_ALL, 1)
mcp.wirte_control(alarm_0_enable=1)
```
