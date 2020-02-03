import SensorMonitor.Manager.spiManagement as spi
import RPi.GPIO as GPIO

ScanMode = 0

# gain channel
ADS1256_GAIN_E = {'ADS1256_GAIN_1': 0,  # GAIN   1
                  'ADS1256_GAIN_2': 1,  # GAIN   2
                  'ADS1256_GAIN_4': 2,  # GAIN   4
                  'ADS1256_GAIN_8': 3,  # GAIN   8
                  'ADS1256_GAIN_16': 4,  # GAIN  16
                  'ADS1256_GAIN_32': 5,  # GAIN  32
                  'ADS1256_GAIN_64': 6,  # GAIN  64
                  }

# data rate
ADS1256_DRATE_E = {'ADS1256_30000SPS': 0xF0,  # reset the default values
                   'ADS1256_15000SPS': 0xE0,
                   'ADS1256_7500SPS': 0xD0,
                   'ADS1256_3750SPS': 0xC0,
                   'ADS1256_2000SPS': 0xB0,
                   'ADS1256_1000SPS': 0xA1,
                   'ADS1256_500SPS': 0x92,
                   'ADS1256_100SPS': 0x82,
                   'ADS1256_60SPS': 0x72,
                   'ADS1256_50SPS': 0x63,
                   'ADS1256_30SPS': 0x53,
                   'ADS1256_25SPS': 0x43,
                   'ADS1256_15SPS': 0x33,
                   'ADS1256_10SPS': 0x20,
                   'ADS1256_5SPS': 0x13,
                   'ADS1256_2d5SPS': 0x03
                   }

# registration definition
REG_E = {'REG_STATUS': 0,  # x1H
         'REG_MUX': 1,  # 01H
         'REG_ADCON': 2,  # 20H
         'REG_DRATE': 3,  # F0H
         'REG_IO': 4,  # E0H
         'REG_OFC0': 5,  # xxH
         'REG_OFC1': 6,  # xxH
         'REG_OFC2': 7,  # xxH
         'REG_FSC0': 8,  # xxH
         'REG_FSC1': 9,  # xxH
         'REG_FSC2': 10,  # xxH
         }

# command definition
CMD = {'CMD_WAKEUP': 0x00,  # Completes SYNC and Exits Standby Mode 0000  0000 (00h)
       'CMD_RDATA': 0x01,  # Read Data 0000  0001 (01h)
       'CMD_RDATAC': 0x03,  # Read Data Continuously 0000   0011 (03h)
       'CMD_SDATAC': 0x0F,  # Stop Read Data Continuously 0000   1111 (0Fh)
       'CMD_RREG': 0x10,  # Read from REG rrr 0001 rrrr (1xh)
       'CMD_WREG': 0x50,  # Write to REG rrr 0101 rrrr (5xh)
       'CMD_SELFCAL': 0xF0,  # Offset and Gain Self-Calibration 1111    0000 (F0h)
       'CMD_SELFOCAL': 0xF1,  # Offset Self-Calibration 1111    0001 (F1h)
       'CMD_SELFGCAL': 0xF2,  # Gain Self-Calibration 1111    0010 (F2h)
       'CMD_SYSOCAL': 0xF3,  # System Offset Calibration 1111   0011 (F3h)
       'CMD_SYSGCAL': 0xF4,  # System Gain Calibration 1111    0100 (F4h)
       'CMD_SYNC': 0xFC,  # Synchronize the A/D Conversion 1111   1100 (FCh)
       'CMD_STANDBY': 0xFD,  # Begin Standby Mode 1111   1101 (FDh)
       'CMD_RESET': 0xFE,  # Reset to Power-Up Values 1111   1110 (FEh)
       }


class ADS1256:
    def __init__(self):
        self.rst_pin = spi.RST_PIN
        self.cs_pin = spi.CS_PIN
        self.drdy_pin = spi.DRDY_PIN

    # Hardware reset
    def ads1256_reset(self):
        spi.digital_write(self.rst_pin, GPIO.HIGH)
        spi.delay_ms(200)
        spi.digital_write(self.rst_pin, GPIO.LOW)
        spi.delay_ms(200)
        spi.digital_write(self.rst_pin, GPIO.HIGH)

    def ads1256_write_cmd(self, reg):
        spi.digital_write(self.cs_pin, GPIO.LOW)  # cs  0
        spi.spi_write_byte([reg])
        spi.digital_write(self.cs_pin, GPIO.HIGH)  # cs 1

    def ads1256_write_reg(self, reg, data):
        spi.digital_write(self.cs_pin, GPIO.LOW)  # cs  0
        spi.spi_write_byte([CMD['CMD_WREG'] | reg, 0x00, data])
        spi.digital_write(self.cs_pin, GPIO.HIGH)  # cs 1

    def ads1256_read_data(self, reg):
        spi.digital_write(self.cs_pin, GPIO.LOW)  # cs  0
        spi.spi_write_byte([CMD['CMD_RREG'] | reg, 0x00])
        data = spi.spi_read_bytes(1)
        spi.digital_write(self.cs_pin, GPIO.HIGH)  # cs 1

        return data

    def ads1256_wait_drdy(self):
        for i in range(0, 400000, 1):
            if spi.digital_read(self.drdy_pin) == 0:
                break
        if i >= 400000:
            print("Time Out ...\r\n")

    def ads1256_read_chip_id(self):
        self.ads1256_wait_drdy()
        _id = self.ads1256_read_data(REG_E['REG_STATUS'])
        _id = _id[0] >> 4
        # print 'ID',id
        return _id

    # The configuration parameters of ADC, gain and data rate
    def ads1256_config_adc(self, gain, drate):
        self.ads1256_wait_drdy()
        buf = [0, 0, 0, 0, 0, 0, 0, 0]
        buf[0] = (0 << 3) | (1 << 2) | (0 << 1)
        buf[1] = 0x08
        buf[2] = (0 << 5) | (0 << 3) | (gain << 0)
        buf[3] = drate

        spi.digital_write(self.cs_pin, GPIO.LOW)  # cs  0
        spi.spi_write_byte([CMD['CMD_WREG'] | 0, 0x03])
        spi.spi_write_byte(buf)

        spi.digital_write(self.cs_pin, GPIO.HIGH)  # cs 1
        spi.delay_ms(1)

    def ads1256_set_channel(self, channel):
        if channel > 7:
            return 0
        self.ads1256_write_reg(REG_E['REG_MUX'], (channel << 4) | (1 << 3))

    def ads1256_set_diff_channel(self, channel):
        if channel == 0:
            self.ads1256_write_reg(REG_E['REG_MUX'], (0 << 4) | 1)  # DiffChannel  AIN0-AIN1
        elif channel == 1:
            self.ads1256_write_reg(REG_E['REG_MUX'], (2 << 4) | 3)  # DiffChannel   AIN2-AIN3
        elif channel == 2:
            self.ads1256_write_reg(REG_E['REG_MUX'], (4 << 4) | 5)  # DiffChannel    AIN4-AIN5
        elif channel == 3:
            self.ads1256_write_reg(REG_E['REG_MUX'], (6 << 4) | 7)  # DiffChannel   AIN6-AIN7

    def ads1256_set_mode(self, mode):
        ScanMode = mode

    def ads1256_init(self):
        if spi.module_init() != 0:
            return -1
        self.ads1256_reset()
        _id = self.ads1256_read_chip_id()
        if _id == 3:
            print("ID Read success  ")
        else:
            print("ID Read failed   ")
            return -1
        self.ads1256_config_adc(ADS1256_GAIN_E['ADS1256_GAIN_1'], ADS1256_DRATE_E['ADS1256_30000SPS'])
        return 0

    def ads1256_read_adc_data(self):
        self.ads1256_wait_drdy()
        spi.digital_write(self.cs_pin, GPIO.LOW)  # cs  0
        spi.spi_write_byte([CMD['CMD_RDATA']])
        # config.delay_ms(10)

        buf = spi.spi_read_bytes(3)
        spi.digital_write(self.cs_pin, GPIO.HIGH)  # cs 1
        read = (buf[0] << 16) & 0xff0000
        read |= (buf[1] << 8) & 0xff00
        read |= (buf[2]) & 0xff
        if read & 0x800000:
            read &= 0xF000000
        return read

    def ads1256_get_channel_value(self, channel):
        if ScanMode == 0:  # 0  Single-ended input  8 channel1 Differential input  4 channel
            if channel >= 8:
                return 0
            self.ads1256_set_channel(channel)
            self.ads1256_write_cmd(CMD['CMD_SYNC'])
            # config.delay_ms(10)
            self.ads1256_write_cmd(CMD['CMD_WAKEUP'])
            # config.delay_ms(200)
            value = self.ads1256_read_adc_data()
        else:
            if channel >= 4:
                return 0
            self.ads1256_set_diff_channel(channel)
            self.ads1256_write_cmd(CMD['CMD_SYNC'])
            # config.delay_ms(10)
            self.ads1256_write_cmd(CMD['CMD_WAKEUP'])
            # config.delay_ms(10)
            value = self.ads1256_read_adc_data()
        return value

    def ads1256_get_channel_value_in_volt(self, channel):
        return self.ads1256_get_channel_value(channel) * 5.0 / 0x7fffff

    def ads1256_get_all(self):
        adc_value = [0, 0, 0, 0, 0, 0, 0, 0]
        for i in range(0, 8, 1):
            adc_value[i] = self.ads1256_get_channel_value(i)
        return adc_value
