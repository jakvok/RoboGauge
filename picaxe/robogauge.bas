; RoboGauge v3
; c.2 - button
; c.3 - opto endstop
; c.4 - serial in

setfreq m8

symbol ms1=b.3
symbol ms2=b.4
symbol ms3=b.5
symbol ena=b.2
symbol stp=c.0
symbol dir=c.1

symbol counter = w0
symbol lsb = b2
symbol hsb = b3
symbol steps = w2

; setup fullstep
low ms1
low ms2
low ms3
low ena

pause 2000

reference:

low dir	;up direction

;go up until optoendstop
do
	pulsout stp,1
	pauseus 20
	if pinc.3 = 1 then exit
loop
pause 200

;go back 2mm down
high dir
for counter = 1 to 50
	pulsout stp,1
	pauseus 20
next counter
pause 200

;go SLOW up, until optoendstop
low dir
do
	pulsout stp,1
	pauseus 200
	if pinc.3 = 1 then exit
loop
pause 200

; go down 2mm at Z-zero
high dir
for counter = 1 to 50
	pulsout stp,1
	pauseus 20
next counter


main:

serin C.4,T2400,("p001"),lsb,hsb ; wait for serial input calls p001

steps = hsb * 256 + lsb

sertxd("steps:", #steps, 13, 10,"lsb:",#lsb,13,10,"hsb:",#hsb,13,10)

steps = steps max 6750


high dir
for counter = 1 to steps
	pulsout stp,1
	pauseus 20
	if pinc.2 = 1 then goto reference
next counter
do
	if pinc.2 = 1 then exit
	pause 100
loop
goto reference
