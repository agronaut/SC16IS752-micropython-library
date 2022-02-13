#  SC16IS752.py is ported from C++ SC16IS752_rsk.cpp to ESP32 Micropython -
#  Library for interfacing with SC16IS752 i2c to serial and gpio port expander with esp32
#  Created by rsk, ported from liamaha/SC16IS752_ESP8266
#  ported to Micro Python by agronaut

from machine import Pin, I2C

# Channel definitions
SC16IS752_CHANNEL_A = const(0x00)
SC16IS752_CHANNEL_B = const(0x01)

#Uart registers
SC16IS752_RHR = const(0x00) #  Recv Holding Register is 0x00 in READ Mode
SC16IS752_THR = const(0x00) #  Xmit Holding Register is 0x00 in WRITE Mode

#GPIO control registers
SC16IS752_IODir = const(0x0A)  # I/O P:ins Direction Register
SC16IS752_IOState = const(0x0B)  # I/O Pins State Register
SC16IS752_IOIntEna = const(0x0C)  # I/O Interrupt Enable Register
SC16IS752_IOControl = const(0x0E)  # I/O Pins Control Register

SC16IS752_IER = const(0x01)  # Interrupt Enable Register

SC16IS752_FCR = const(0x02)  # FIFO Control Register in WRITE Mode
SC16IS752_IIR = const(0x02)  # Interrupt Identification Register in READ Mode

SC16IS752_LCR = const(0x03)  # Line Control Register
SC16IS752_MCR = const(0x04)  # Modem Control Register
SC16IS752_LSR = const(0x05)  # Line status Register
SC16IS752_MSR = const(0x06)  # Modem Status Register
SC16IS752_SPR = const(0x07)  # ScratchPad Register
SC16IS752_TCR = const(0x06)  # Transmission Control Register
SC16IS752_TLR = const(0x07)  # Trigger Level Register
SC16IS752_TXLVL = const(0x08)  # Xmit FIFO Level Register
SC16IS752_RXLVL = const(0x09)  # Recv FIFO Level Register
SC16IS752_EFCR = const(0x0F)  # Extra Features Control Register

#Baud rate divisor registers
SC16IS752_DLL = const(0x00)  # Divisor Latch LSB  0x00
SC16IS752_DLH = const(0x01)  # Divisor Latch MSB  0x01

SC16IS752_EFR = const(0x02) # Enhanced Function Register



"""
baud rate and divisor table
	2400 	48
	3600 	32
	4800 	24
	7200 	16
	9600 	12
	19200 	6
"""

class SC16IS752():
    def __init__(self, i2c, address, channel):
        self._outputRegVal = 0x00
        self._inputRegVal = 0x00
        self._deviceAddress = address
        self._channel = channel
        self._i2c = i2c


    ## -------------------- private functions -----------------------

    def _readRegister(self, regAddress):
        result = self._i2c.readfrom_mem(self._deviceAddress, regAddress << 3 | self._channel << 1, 1)
        #print('READ REGISTER', regAddress, 'RESULT: ', result)
        return result
    

    def _writeRegister(self, regAddress, data):
        if isinstance(data, bytes):
            r = data
        else:
            r = bytes([data])
        
        self._i2c.writeto_mem(self._deviceAddress, regAddress << 3 | self._channel << 1, r)
        #print('WRITE REGISTER: ', regAddress << 3 | self._channel << 1, 'DATA: ', r)


    def _uartConnected(self):
        TEST_CHARACTER = 0x88    
        self._writeRegister(SC16IS752_SPR, TEST_CHARACTER)
        return (self._readRegister(SC16IS752_SPR) == bytes([TEST_CHARACTER]))

    
    def _bitwise_and_bytes(self, a, b):
        result_int = int.from_bytes(a, "big") & int.from_bytes(b, "big")
        return result_int.to_bytes(max(len(a), len(b)), "big")
    
    
    def _bitwise_or_bytes(self, a, b):
        result_int = int.from_bytes(a, "big") | int.from_bytes(b, "big")
        return result_int.to_bytes(max(len(a), len(b)), "big") 


    # -------------------- public functions ---------------------------

    def available(self):
  
        # Get the number of bytes (characters) available for reading.
        # This is data that's already arrived and stored in the receive
        # buffer (which holds 64 bytes).
  
        # This alternative just checks if there's data but doesn't
        # return how many characters are in the buffer:
        # print('LSR register: ', self._readRegister(SC16IS752_LSR))
        # print('The data stored in the receive buffer', self._bitwise_and_bytes(self._readRegister(SC16IS752_LSR), b'\x01'))
        
        return int.from_bytes(self._readRegister(SC16IS752_RXLVL), 'big')


    def txBufferSize(self):
	    #  returns the number of empty spaces in the tx buffer, so 0 means it's full
        print('TEXT BUFFER SIZE: ', self._readRegister(SC16IS752_TXLVL))

        return self._readRegister(SC16IS752_TXLVL)


    def read_byte(self):
        return self._readRegister(SC16IS752_RHR)

    
    # reads the whole transmitted byte sequence
    # if it longer than 64 bytes, surplus bytes queued and can be read by consequent read_buf calls
    def read_buf(self, buf_size=100):
        buf = bytearray(buf_size)
        # this timing is chosen by trial, if less, reading errors occur in the last portion of the read buffer
        # it's only needed when reading is triggered by polling available(), not for interrupts
        # utime.sleep_ms(20)
        self._i2c.readfrom_mem_into(self._deviceAddress, SC16IS752_RHR << 3 | self._channel << 1, buf)
        return buf


    def write(self, value):
	    #   Write byte to UART.
	
        while(self._readRegister(SC16IS752_TXLVL) == 0):
            #  Wait for space in TX buffer, returns the number of spaces in the buffer.
            pass
        self._writeRegister(SC16IS752_THR, value); 


    #  ----------------------------------- added by rsk -------

    def flush(self):
        print('[INFO]:Flushing the buffer...')
        while self.available() > 0:
            self.read_byte()


    def SetBaudrate(self, baudrateDivisor):
        #  uses baud rate divisor from p17 of the datasheet.
        print('[INFO]: Setting baud rate...')
        temp_lcr = self._readRegister(SC16IS752_LCR)
        temp_lcr = self._bitwise_or_bytes(bytes(temp_lcr), b'\x80')

        self._writeRegister(SC16IS752_LCR, temp_lcr[0])
        # write to DLL
        #print('SetBaudrate baudrateDivisor: ', baudrateDivisor)
        self._writeRegister(SC16IS752_DLL, baudrateDivisor)
        # write to DLH
        #print('SetBaudrate baudrateDivisor>>8: ', baudrateDivisor>>8)
        self._writeRegister(SC16IS752_DLH, baudrateDivisor>>8)

        temp_lcr= self._bitwise_and_bytes(bytes(temp_lcr), b'\x7F')
        self._writeRegister(SC16IS752_LCR, temp_lcr[0])


    # does not work for some reason
    # value b'\x08' appears too big to be written to SC16IS752_IOControl
    def ResetDevice(self):

        reg = self._readRegister(SC16IS752_IOControl)
        reg = self._bitwise_or_bytes(bytes(reg), b'\x08')
        # print('REG: ', reg)
        self._writeRegister(SC16IS752_IOControl, reg[0])


    def FIFOEnable(self, fifo_enable):
        print('[INFO]: Enabling FIFO...')
        temp_fcr = self._readRegister(SC16IS752_FCR)

        if fifo_enable == 0:
            temp_fcr = self._bitwise_and_bytes(bytes(temp_fcr), b'\xFE')
        else:
            temp_fcr = self._bitwise_or_bytes(bytes(temp_fcr), b'\x01')
        
        self._writeRegister(SC16IS752_FCR, temp_fcr[0])


    def SetLine(self, data_length, parity_select, stop_length):
        print('[INFO]: Setting the line...')
        temp_lcr = self._readRegister(SC16IS752_LCR)
        temp_lcr = self._bitwise_and_bytes(bytes(temp_lcr), b'\xC0') # Clear the lower six bit of LCR (LCR[0] to LCR[5]

        #print("LCR Register:0x")
        #print(temp_lcr)

        # data length settings
        if data_length == 5:          
            pass
        elif data_length == 6:
            temp_lcr = self._bitwise_or_bytes(bytes(temp_lcr), b'\x01')
        elif data_length == 7:
            temp_lcr = self._bitwise_or_bytes(bytes(temp_lcr), b'\x02')
        elif data_length == 8:
            temp_lcr = self._bitwise_or_bytes(bytes(temp_lcr), b'\x03')
        else:
            temp_lcr = self._bitwise_or_bytes(bytes(temp_lcr), b'\x03')


        if ( stop_length == 2 ):
            temp_lcr = self._bitwise_or_bytes(bytes(temp_lcr), b'\x04')

        if parity_select == 0:           # parity selection length settings
            pass
        elif parity_select == 1:
            temp_lcr = self._bitwise_or_bytes(bytes(temp_lcr), b'\x08')
        elif parity_select == 2:
            temp_lcr = self._bitwise_or_bytes(bytes(temp_lcr), b'\x18')
        elif parity_select == 3:
            temp_lcr = self._bitwise_or_bytes(bytes(temp_lcr), b'\x03')
        elif parity_select == 4:
            pass

        self._writeRegister(SC16IS752_LCR, temp_lcr[0])
        
        # enable firing up the IRQ pin only when some data arrives to the RHR register
        # search manual for "Receive Holding Register interrupt" IER[0]
        self._writeRegister(SC16IS752_IER, b'\x01')

