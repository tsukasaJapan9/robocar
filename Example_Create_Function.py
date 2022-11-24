import smbus, time

bus = smbus.SMBus(1)
addr = 0x40


def clamp(x, _min, _max):
    return max(min(x, _max), _min)


def servo_init(channel):
    # channel0が0x06からスタートし、1chは4byte
    channel_0_start = 0x06
    channel_reg = 4 * channel + channel_0_start
    bus.write_word_data(addr, channel_reg, 0)


def servo_pos(channel, pos):
    channel_0_end = 0x08
    channel_reg = 4 * channel + channel_0_end
    pos = clamp(pos, -90, 90)

    # Mapping Servo Position
    #   209 = 0 deg
    #   312 = 45 deg
    #   416 = 90 deg
    deg_0_pulse = 297.96
    deg_90_pulse = 491.52
    deg_minus_90_pulse = 102.4
    # pos_end_byte = lambda x: (deg_max - deg_0) / deg_range * x + deg_0
    if pos >= 0:
        val = (deg_90_pulse - deg_0_pulse) * pos / 90 + deg_0_pulse
    else:
        val = (deg_0_pulse - deg_minus_90_pulse) * (90 + pos) / 90 + deg_minus_90_pulse

    bus.write_word_data(addr, channel_reg, round(val))


# Running this program will move the servo to 0, 45,
# and 90 degrees with 5 second pauses in between with a 50 Hz PWM signal.
# Configure 50Hz PWM Output

# この辺の設定が謎
bus.write_byte_data(addr, 0, 0x20)  # enable the chip
time.sleep(0.25)
bus.write_byte_data(addr, 0, 0x10)  # enable Prescale change as noted in the datasheet
time.sleep(0.25)  # delay for reset

# 動作周波数: 25MHz
# カウンタの周期: 4096
# を50Hzにするためのプリスケーラの値は
# 25M / (4096 * 50) - 1 = 121(0x79)
bus.write_byte_data(
    addr, 0xFE, 0x79
)  # changes the Prescale register value for 50 Hz, using the equation in the datasheet.
bus.write_byte_data(addr, 0, 0x20)  # enables the chip

# Initialize Channel (sets start time for channel)
servo_init(0)
servo_init(1)

# Run Loop
while True:
    time.sleep(1)
    servo_pos(1, 0)
    # time.sleep(0.5)
    # servo_pos(3, 90, 0)  # chl 3 end time = 1.0ms (0 degrees)
    # time.sleep(0.5)
    # servo_pos(3, 90, 45)  # chl 3 end time = 1.5ms (45 degrees)
    # time.sleep(0.5)
    # servo_pos(3, 90, 0)  # chl 3 end time = 1.0ms (0 degrees)
    # time.sleep(0.5)
    # servo_pos(3, 90, 90)  # chl 3 end time = 2.0ms (90 degrees)
