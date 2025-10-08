import smbus
import time

MPU6050_ADDR = 0x68
bus = smbus.SMBus(1)

bus.write_byte_data(MPU6050_ADDR, 0x6B, 0)

def read_word(reg):
    high = bus.read_byte_data(MPU6050_ADDR, reg)
    low = bus.read_byte_data(MPU6050_ADDR, reg + 1)
    value = (high << 8) + low
    if value >= 0x8000:
        return -((65535 - value) + 1)
    else:
        return value

def get_accel_data():
    accel_x = read_word(0x3B) / 16384.0
    accel_y = read_word(0x3D) / 16384.0
    accel_z = read_word(0x3F) / 16384.0
    return (accel_x, accel_y, accel_z)

def get_gyro_data():
    gyro_x = read_word(0x43) / 131.0
    gyro_y = read_word(0x45) / 131.0
    gyro_z = read_word(0x47) / 131.0
    return (gyro_x, gyro_y, gyro_z)


