import RPi.GPIO as GPIO
import time
import motor
from picamera import PiCamera
import os
import csv
import subprocess
#CMD for video convert sudo MP4Box -add video_log.h264 -fps 30 output.mp4
lamp_pin = 20#Pin for control light
#Command signal
On_pin = 7
Off_pin = 12
uG_pin = 16
#Onboard LED
led1_pin = 18
led2_pin = 25
led3_pin = 8
On_event_flag = False
Off_event_flag = False
uG_event_flag = False
def On_event(pin):
    global On_event_flag
    On_event_flag = True
    print('On signal')
    
def Off_event(pin):
    global Off_event_flag
    Off_event_flag = True
    print('Off signal')
def uG_event(pin):
    global uG_event_flag
    uG_event_flag = True
    print('uG signal')

def debugger_log(line,timestamp = True,end = '\r\n'):
    gmt_str = time.strftime("%Y-%m-%d %H:%M:%S : ", time.gmtime())
    with open('/home/pi/main_prog/experiment_log.txt', 'a') as f:
        if timestamp:
            f.write(gmt_str)
        f.write(line+end)
def GPIO_setup():
    err = False
    statement = None
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup([lamp_pin], GPIO.OUT)
        GPIO.setup([On_pin,Off_pin,uG_pin], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup([led1_pin,led2_pin,led3_pin], GPIO.OUT)
        GPIO.add_event_detect(On_pin, GPIO.FALLING,On_event)
        GPIO.add_event_detect(Off_pin, GPIO.FALLING,Off_event)
        GPIO.add_event_detect(uG_pin, GPIO.FALLING,uG_event)
        led_control(1,1,1)
    except Exception as e:
        err = True
        statement = str(e)
    
    return err,statement
def cam_setup():
    err = False
    statement = ''
    global camera
    try :
        camera = PiCamera()
        camera.framerate = 30
        camera.resolution = (1296,972)
    except Exception as e:
        statement = e
        err = True
    return err,statement
        
def led_control(led1,led2,led3):
    GPIO.output(led1_pin, led1)
    GPIO.output(led2_pin, led2)
    GPIO.output(led3_pin, led3)
    
def lamp_control(status):
    GPIO.output(lamp_pin, status)
def blink_lamp():
    GPIO_setup()
    print("Start blink..")
    for i in range(10):
        print(i)
        lamp_control(1)
        time.sleep(0.5)
        lamp_control(0)
        time.sleep(0.5)
def motor_setup():
    motor.serial_port.port = '/dev/serial0'
    motor.serial_port.baudrate = 57600
    motor.serial_port.timeout = 1
    motor.serial_port.open()
    motor.motor_id = 1
    err = motor.motor_off()
    statement = ''
    if err:
        statement = 'motor fail to setup.'
    return err,statement
def motor_manual():
    motor.velocity_mode()
    err = False
    statement = ""
    err_count = 0
    err_max_retry = 5
    while True:
        ret_err = False
        if  GPIO.input(On_pin) == 0:
            ret_err = motor.send_goal_RPM(80)
        elif  GPIO.input(uG_pin) == 0:
            ret_err = motor.send_goal_RPM(-80)
        elif GPIO.input(Off_pin) == 0:
            break
        else:
            ret_err = motor.send_goal_RPM(0)
        if ret_err:
            err_count += 1
            if err_count > err_max_retry:
                err = True
                statement = 'error connecting to motor.'
                break
            else:
                time.sleep(0.5)
        else:
            if err_count != 0:
                err_count = 0
        
    led_control(0,0,0)
    return err,statement
    
            
def experiment():
    global On_event_flag
    global Off_event_flag
    global uG_event_flag
    experiment_state = 'Sleep'
    timer = time.time()
    err_count = 0
    max_err_count = 5
    err = False
    statement = ''
    log_dir = ''
    still_img_count = 0
    motor_rpm = -80
    experiment_start_time = 0
    debugger_log('start experiment program')
    print('start experiment program')
    try:
        while True:
            if time.time() - timer > 0.1:
                timer += 0.1
                experiment_time = time.time() - experiment_start_time
                if experiment_state == 'Sleep':
                    led_control(1,1,1)
                    lamp_control(1)
                    err = motor.motor_off()
                    if err:
                        err_count += 1
                        if err_count>max_err_count:
                            err = True
                            statement = 'motor comunication error'
                            break
                    else:
                        err_count = 0
                    if On_event_flag:
                        experiment_state = 'Stanby'
                        debugger_log('experiment state = Stanby')
#stanby
                elif experiment_state == 'Stanby':
                    led_control(0,0,1)
                    lamp_control(0)
                    if uG_event_flag:
                        experiment_state = 'Run'
                        experiment_start_time = time.time()
                        gmt = time.strftime("%Y-%m-%d,%H:%M:%S", time.gmtime())
                        log_dir = '/home/pi/main_prog/log/'+gmt
                        # Create target Directory if don't exist
                        
                        debugger_log('create directory '+log_dir)
                        try:
                            if not os.path.exists('/home/pi/main_prog/log'):
                                os.mkdir('/home/pi/main_prog/log')
                            if not os.path.exists(log_dir):
                                os.mkdir(log_dir)
                        except Exception as e:
                            err = True
                            statement = str(e)
                            debugger_log('Fail to directory '+e)
                            break
                        debugger_log('Taking still image')
                        try:
                            camera.capture(log_dir+'/still_img'+str(still_img_count)+'.bmp')
                            still_img_count += 1
                        except Exception as e:
                            err = True
                            statement = str(e)
                            debugger_log('Fail to take still image')
                            break
                        debugger_log('Recording video')
                        try:
                            camera.start_recording(log_dir+'/video_log.h264')
                        except Exception as e:
                            err = True
                            statement = str(e)
                            debugger_log('Fail to take video')
                            break
                        motor.velocity_mode()
                        motor.send_goal_RPM(motor_rpm)
                        
                        
                    if Off_event_flag:
                        experiment_state = 'Sleep'
                        
                elif experiment_state == 'Run':
                    led_control(0,1,1)
                    #motor.send_goal_RPM(motor_rpm)
                    motor_current = motor.read_current_milliamp()
                    if experiment_time<5:
                        motor.send_goal_RPM(0)
                    elif experiment_time<120:
                        motor.send_goal_RPM(motor_rpm)
                    else:
                        motor.send_goal_RPM(0)
                        
                    if motor_current == None:
                        time.sleep(1)
                        motor.velocity_mode()
                    else:
                        with open(log_dir+'/log.csv', 'a', newline='') as csvfile:
                            writer = csv.writer(csvfile, delimiter=',',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
                            writer.writerow([experiment_time,motor_current])
                    if Off_event_flag:
                        experiment_state = 'Sleep'
                        camera.stop_recording()
                        motor.motor_off()
                        lamp_control(1)
                        led_control(0,0,0)
                        break
                        
                else:
                            experiment_state = 'Sleep'
                On_event_flag = False
                Off_event_flag = False
                uG_event_flag = False

            
    except Exception as e:
        err = True
        statement = str(e)
    debugger_log("terminate experiment")
    return err,statement


