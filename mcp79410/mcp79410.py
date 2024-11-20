from micropython import const
from collections import namedtuple

_RTCSEC = const(0x00)
_RTCMIN = const(0x01)
_RTCHOUR = const(0x02)
_RTCWDAY = const(0x03)
_RTCDATE = const(0x04)
_RTCMTH = const(0x05)
_RTCYEAR = const(0x06)
_CONTROL = const(0x07)
_OSCTRIM = const(0x08)
_EEUNLOCK = const(0x09)
_ALM0SEC = const(0x0a)
_ALM0MIN = const(0x0b)
_ALM0HOUR = const(0x0c)
_ALM0WDAY = const(0x0d)
_ALM0DATE = const(0x0e)
_ALM0MTH = const(0x0f)
_ALM1SEC = const(0x11)
_ALM1MIN = const(0x12)
_ALM1HOUR = const(0x13)
_ALM1WDAY = const(0x14)
_ALM1DATE = const(0x15)
_ALM1MTH = const(0x16)

_ALMxSEC = const(_ALM0SEC - _ALM0SEC)
_ALMxMIN = const(_ALM0MIN - _ALM0SEC)
_ALMxHOUR = const(_ALM0HOUR - _ALM0SEC)
_ALMxWDAY = const(_ALM0WDAY - _ALM0SEC)
_ALMxDATE = const(_ALM0DATE - _ALM0SEC)
_ALMxMTH = const(_ALM0MTH - _ALM0SEC)

_RTCSEC_ST = const(7)

_RTCWDAY_OSCRUN = const(5)

_RTCHOUR_1224 = const(6)

_CONTROL_SQWFS0 = const(0)
_CONTROL_SQWFS1 = const(1)
_CONTROL_CRSTRIM = const(2)
_CONTROL_EXTOSC = const(3)
_CONTROL_ALM0EN = const(4)
_CONTROL_ALM1EN = const(5)
_CONTROL_SQWEN = const(6)
_CONTROL_OUT = const(7)

_ALMxWDAY_IF = const(3)
_ALMxWDAY_MSK0 = const(4)
_ALMxWDAY_MSK1 = const(5)
_ALMxWDAY_MSK2 = const(6)
_ALMxWDAY_ALMPOL = const(7)

_EPOCH = const(2000)

ALARM_MASK_SECONDS = 0x00
ALARM_MASK_MINUTES = 0x01
ALARM_MASK_HOURS = 0x02
ALARM_MASK_DAY_OF_WEEK = 0x03
ALARM_MASK_DATE = 0x04
ALARM_MASK_ALL = 0x07

DateTime = namedtuple('DateTime', ('second', 'minute', 'hour', 'week_day', 'day', 'month', 'year'))

def read_bcd(value):
    return ((value >> 4) * 10) + (value & 0x0f)

def write_bcd(value):
    return ((value // 10) << 4) | (value % 10)

class MCP79410:
    _BUFFER_8 = bytearray(1)
    _BUFFER_48 = bytearray(6)
    _BUFFER_56 = bytearray(7)

    def __init__(self, i2c, rtcc_address=0x6f, eeprom_address=0x57):
        self._i2c = i2c
        self._rtcc_address = rtcc_address
        self._eeprom_address = eeprom_address

    def write_time_and_date(self, datetime, start_oscillator=1):
        # Disable oscillator to avoid rollover issues
        self._BUFFER_8[0] = 0
        self._i2c.writeto_mem(self._rtcc_address, _RTCSEC, self._BUFFER_8)

        for _ in range(5):
            # Wait for the oscillator run status bit to clear
            self._i2c.readfrom_mem_into(self._rtcc_address, _RTCWDAY, self._BUFFER_8)
            oscrun = self._BUFFER_8[0] & (1 << _RTCWDAY_OSCRUN)

            if not oscrun:
                break
        else:
            raise OSError('oscillator bit did not clear')

        # Load new time and date values
        self._BUFFER_56[_RTCSEC] = write_bcd(datetime.second)
        self._BUFFER_56[_RTCMIN] = write_bcd(datetime.minute)
        self._BUFFER_56[_RTCHOUR] = write_bcd(datetime.hour) | (0 << _RTCHOUR_1224) # 24-hour format
        self._BUFFER_56[_RTCWDAY] = write_bcd(datetime.week_day)
        self._BUFFER_56[_RTCDATE] = write_bcd(datetime.day)
        self._BUFFER_56[_RTCMTH] = write_bcd(datetime.month)
        self._BUFFER_56[_RTCYEAR] = write_bcd(datetime.year - _EPOCH)

        self._i2c.writeto_mem(self._rtcc_address, _RTCSEC, self._BUFFER_56)

        if start_oscillator:
            # Re-enable oscillator if requested
            self._BUFFER_8[0] = write_bcd(datetime.second) | (start_oscillator << _RTCSEC_ST)
            self._i2c.writeto_mem(self._rtcc_address, _RTCSEC, self._BUFFER_8)

    def read_time_and_date(self):
        self._i2c.readfrom_mem_into(self._rtcc_address, _RTCSEC, self._BUFFER_56)

        return DateTime(
            read_bcd(self._BUFFER_56[_RTCSEC] & 0b01111111),
            read_bcd(self._BUFFER_56[_RTCMIN] & 0b01111111),
            read_bcd(self._BUFFER_56[_RTCHOUR] & 0b00011111),
            read_bcd(self._BUFFER_56[_RTCWDAY] & 0b00000111),
            read_bcd(self._BUFFER_56[_RTCDATE] & 0b00111111),
            read_bcd(self._BUFFER_56[_RTCMTH] & 0b00011111),
            read_bcd(self._BUFFER_56[_RTCYEAR]) + _EPOCH)

    def write_control(self,
            square_wave_frequency=0,
            coarse_trim_enable=0,
            external_oscillator=0,
            alarm_0_enable=0,
            alarm_1_enable=0,
            square_wave_enable=0,
            mfp_output=0):
        self._BUFFER_8[0] = ((mfp_output << _CONTROL_OUT)
            | (square_wave_enable << _CONTROL_SQWEN)
            | (alarm_1_enable << _CONTROL_ALM1EN)
            | (alarm_0_enable << _CONTROL_ALM0EN)
            | (external_oscillator << _CONTROL_EXTOSC)
            | (coarse_trim_enable << _CONTROL_CRSTRIM)
            | (square_wave_frequency << _CONTROL_SQWFS0))
        self._i2c.writeto_mem(self._rtcc_address, _CONTROL, self._BUFFER_8)

    def write_alarm(self, n, datetime, mask, interrupt_polarity):
        alarm_offset = (_ALM1SEC - _ALM0SEC) * n

        self._BUFFER_48[_ALMxSEC] = write_bcd(datetime.second)
        self._BUFFER_48[_ALMxMIN] = write_bcd(datetime.minute)
        self._BUFFER_48[_ALMxHOUR] = write_bcd(datetime.hour)
        self._BUFFER_48[_ALMxWDAY] = (write_bcd(datetime.week_day)
            | (interrupt_polarity << _ALMxWDAY_ALMPOL)
            | (mask << _ALMxWDAY_MSK0)
            | (0 << _ALMxWDAY_IF)) # Clear interrupt flag bit
        self._BUFFER_48[_ALMxDATE] = write_bcd(datetime.day)
        self._BUFFER_48[_ALMxMTH] = write_bcd(datetime.month)

        self._i2c.writeto_mem(self._rtcc_address, _ALM0SEC + alarm_offset, self._BUFFER_48)

    def write_alarm_interrupt_polarity(self, interrupt_polarity):
        self._i2c.readfrom_mem_into(self._rtcc_address, _ALM0WDAY, self._BUFFER_8)
        self._BUFFER_8[0] &= ~(1 << _ALMxWDAY_ALMPOL) # Clear polarity bit
        self._BUFFER_8[0] |= (1 << _ALMxWDAY_ALMPOL)
        self._i2c.writeto_mem(self._rtcc_address, _ALM0WDAY, self._BUFFER_8)
