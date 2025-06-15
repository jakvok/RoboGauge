#!/usr/bin/python3

import serial
from tkinter import messagebox

class Gauge:
    '''
    Class represents tool robotic gauge for tool presetting
    pitch: pitch of driving thread rod [mm]
    stp_rev: steps per revolution of driving stepper motor [1/rev]
    max_travel: max. position of gauge travel [mm]
    min_travel: min. position of gauge travel, default=0 [mm]
    comport: serial port of device <string>
    '''
    def __init__(self, pitch, stp_rev, comport, max_travel, min_travel=0) -> None:
        try:
            self.pitch = float(pitch)
            self.stp_rev = float(stp_rev)
            self.max_travel = float(max_travel)
            self.min_travel = float(min_travel)
            self.comport = comport
        except:
            print('Parameters nust be <float> type.')
    
    def send(self, val):
        '''
        Converts desired position[mm] to 2bytes variable position[steps]
        and
        sends bytes to PIC via serial port:
            bytes1 = allways 'p001'
            byte2 = lower byte of position
            byte3 = upper byte of position
        Returns: False if input value out of range or communication unsuccessful,
                True if value in range and communication succesfull
        '''
        val = int(val * self.stp_rev / self.pitch) # mm -> steps
        # is desired value in range?
        if val < (self.min_travel / self.pitch * self.stp_rev) or val > (self.max_travel / self.pitch * self.stp_rev):
            messagebox.showwarning(title='WARNING!', message='Value out of range.')
            return False

        h_val = (val >> 8) & 0xFF # get upper byte from value
        l_val = val & 0xFF # get lower byte from value
        
        # testing output
        print('int steps: ', val)
        print('hex steps: ', hex(val))
        print('bin steps: ', bin(val))
        print('lower byte: ', l_val, '   upper byte: ',  h_val)
        print('lower bin: ', bin(l_val), '   upper bin: ', bin(h_val))
        output = ('p001' + chr(l_val) + chr(h_val))
        print('ser output: ', output)
        for n in output:
            print('byte: ', ord(n))
        print('upperByte*256+lowerByte= ', (h_val * 256 + l_val))

        try:
            # test output to file
            #with open('test_output.txt', 'w', encoding='utf-8') as f:
            #    f.write('p001' + chr(l_val) + chr(h_val))
            #  baudrate 4800 only when PICAXE run on 8Mhz, standard is 2400@4Mhz
            # serial port output
            with serial.Serial(self.comport, 4800, timeout = 0) as ser:
                ser.write(b'p001' + bytes([l_val, h_val]))
            return True
        except:
            messagebox.showwarning(title='WARNING!', message='Serial communication failed.')
            return False
        
        
if __name__ == '__main__':
    pass