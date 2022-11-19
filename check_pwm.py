import smbus, time, sys

if len(sys.argv) != 3:
    print("Usage: python3 check_pwm.py <channel> <value>")
    exit(1)

bus = smbus.SMBus(1)
addr = 0x40
channel = int(sys.argv[1])
value = int(sys.argv[2])


def clamp(x, _min, _max):
    return max(min(x, _max), _min)


def servo_init():
    # channel0が0x06からスタートし、1chは4byte
    channel_0_start = 0x06
    reg = 4 * channel + channel_0_start
    bus.write_word_data(addr, reg, 0)
    # bus.write_word_data(addr, channel_reg, round(val))


# この辺の設定が謎
bus.write_byte_data(addr, 0, 0x20)  # enable the chip
time.sleep(0.25)
bus.write_byte_data(addr, 0, 0x10)  # enable Prescale change as noted in the datasheet
time.sleep(0.25)  # delay for reset

# 周波数を50Hzに設定
# 動作周波数: 25MHz
# カウンタの周期: 4096
# を50Hzにするためのプリスケーラの値は
# 25M / (4096 * 50) - 1 = 121(0x79)
bus.write_byte_data(addr, 0xFE, 0x79)
bus.write_byte_data(addr, 0, 0x20)  # enables the chip

servo_init()

# 88からモータが左回転
# 320で停止
# 557までモータが右回転
print("==============================")
print(f"{channel=}, {value=}")
print("==============================")
channel_reg = 4 * channel + 0x08
bus.write_word_data(addr, channel_reg, value)
time.sleep(5)
bus.write_word_data(addr, channel_reg, 0)