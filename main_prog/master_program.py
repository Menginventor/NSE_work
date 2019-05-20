#This is master program.
#Master program will call main_program.py

import importlib
import atexit
import os
import importlib
import time
import main_program
def exit_handler():

    debugger_log("Master Program exit...")
    
def debugger_log(line,timestamp = True,end = '\r\n'):
    gmt_str = time.strftime("%Y-%m-%d %H:%M:%S : ", time.gmtime())
    print(gmt_str,line,end = end)
    try:
        with open('/home/pi/main_prog/debugger.txt', 'a') as f:
            if timestamp:
                
                f.write(gmt_str)
            f.write(line+end)
    except Exception as e:
        with open('/home/pi/main_prog/unexpected_error.txt', 'a') as f:
            gmt_str = time.strftime("%Y-%m-%d %H:%M:%S : ", time.gmtime())
            f.write(gmt_str)
            f.write("debugger_log error opening file!\r\n")
            f.write(gmt_str)
            f.write(str(e)+'\r\n')
def init():
    atexit.register(exit_handler)
    print('Master program start')
    debugger_log("##################",timestamp = False)
    debugger_log("Excute Master Program...")
    
   
def manual_motor():
    err = False
    statement = ''
    debugger_log("GPIO setup...")
    err,statement = main_program.GPIO_setup()
    if err:
        return err,statement
    else:
        debugger_log("GPIO setup sucessful!")
    #motor setup
    debugger_log("Motor setup...")
    err,statement = main_program.motor_setup()
    if err:
        return err,statement
    else:
        debugger_log("Motor setup sucessful!")
    #Motor manual
    debugger_log("Excute motor_manual program")
    err,statement = main_program.motor_manual()
    if err:
        debugger_log("motor_manual program error!")
        return err,statement
    else:
        debugger_log("motor_manual program sucessful!")
def experiment():
    err = False
    statement = ''
    debugger_log("Initiate experiment program...")
    debugger_log("GPIO setup...")
    err,statement = main_program.GPIO_setup()
    if err:
        return err,statement
    else:
        debugger_log("GPIO setup sucessful!")
    #motor setup
    debugger_log("Motor setup...")
    err,statement = main_program.motor_setup()
    if err:
        return err,statement
    else:
        debugger_log("Motor setup sucessful!")
    #Camera setup
    debugger_log("Camera setup...")
    err,statement = main_program.cam_setup()
    if err:
        debugger_log("Camera setup error!")
        return err,statement
    else:
        debugger_log("Camera setup sucessful!")
    #Start experiment
    debugger_log("Start experiment program")
    err,statement = main_program.experiment()
    if err:
        debugger_log("Experiment program error!")
        return err,statement
    else:
        debugger_log("Experiment program sucessful!")
    err = False
    statement = ''
    return err,statement
def main():
    init()
    err,statement = experiment()
    if err:
        debugger_log("experiment error")
        debugger_log(statement)
    debugger_log("terminating experiment program")
    
main()
