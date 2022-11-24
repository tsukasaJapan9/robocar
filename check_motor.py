import smbus, time, sys

if len(sys.argv) != 4:
    print("Usage: python3 check_motor.py <channel> <speed> <interval>")
    exit(1)

bus = smbus.SMBus(1)
addr = 0x40
arg_channel = int(sys.argv[1])
arg_speed = int(sys.argv[2])
arg_interval = int(sys.argv[3])


def clamp(x, _min, _max):
    return max(min(x, _max), _min)


def servo_init(channel):
    # channel0が0x06からスタートし、1chは4byte
    channel_0_start = 0x06
    reg = 4 * channel + channel_0_start
    bus.write_word_data(addr, reg, 0)


def move_servo(channel, speed):
    channel_0_end = 0x08
    reg = 4 * channel + channel_0_end
    speed = clamp(speed, -100, 100)

    speed_0_pulse = 320
    speed_100_pulse = 550
    speed_minus_100_pulse = 88
    if speed >= 0:
        val = (speed_100_pulse - speed_0_pulse) * speed / 100 + speed_0_pulse
    else:
        val = (speed_0_pulse - speed_minus_100_pulse) * (100 + speed) / 100 + speed_minus_100_pulse

    print(f"{reg=}, {speed=}, {val=}")
    bus.write_word_data(addr, reg, round(val))


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

servo_init(0)

print("==============================")
print(f"{arg_channel=}, {arg_speed=}")
print("==============================")

for _ in range(3):
    move_servo(arg_channel, arg_speed)
    time.sleep(arg_interval)
    move_servo(arg_channel, -arg_speed)
    time.sleep(arg_interval)
