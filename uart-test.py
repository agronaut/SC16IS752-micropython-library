from machine import Pin, I2C
#import SC16IS752
import utime

SC16IS752_IIR = const(0x02)  # Interrupt Identification Register in READ Mode

i2c_qq = I2C(0, scl=Pin(18, pull=Pin.PULL_UP), sda=Pin(19, pull=Pin.PULL_UP), freq=10000)

if len(i2c_qq.scan()) > 0:
    device_address = i2c_qq.scan()[0]
else:
    device_address = 72

# initializing the device
uart1 = SC16IS752(i2c_qq, device_address, 0)
# uart1.ResetDevice() # does not work
uart1.FIFOEnable(1)
uart1.SetBaudrate(12)
uart1.SetLine(8,0,1)
uart1.flush()
utime.sleep_ms(10)

qq_pin = 0
last_irq_time = utime.time()

def handle_i2c_interrupt(pin):
    global qq_pin
    global last_irq_time
    now_time = utime.time()
    # avoid IRQ dribbling (do not fire faster than 1 second interval)
    if now_time - last_irq_time >= 1:
        last_irq_time = now_time
        qq_pin = 1
    else:
        qq_pin = 0

# initializing interrupt pin 17
qq_code_pin = Pin(17, Pin.IN, pull=Pin.PULL_UP)
qq_code_pin.irq(trigger=Pin.IRQ_FALLING, handler=handle_i2c_interrupt)

while True:
    if qq_pin != 0:
    #if uart1.available() > 0:
        #iir = i2c_qq.readfrom_mem(device_address, SC16IS752_IIR << 3, 1)
        #print('Interrupt!', bin(int.from_bytes(iir, "big")))
        qq_pin = 0
    
        # this timing is chosen by trial, if less, reading errors occur (in the last portion of the read buffer)
        # utime.sleep_ms(20)
        s = uart1.read_buf()
        print('RECIEVED SEQUENCE: \n', s.decode('utf-8'))
        uart1.flush()
