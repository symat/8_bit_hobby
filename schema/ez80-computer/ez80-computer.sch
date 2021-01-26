EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 1 1
Title ""
Date ""
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
Text GLabel 1000 1000 0    50   Output ~ 0
+3V3
Text GLabel 1000 1400 0    50   Output ~ 0
Ground
Text GLabel 1000 2500 0    50   Output ~ 0
ZDI_A
Text GLabel 1000 2400 0    50   Output ~ 0
ZDI_CL
Wire Wire Line
	1100 2400 1000 2400
Wire Wire Line
	1100 2500 1000 2500
Wire Wire Line
	1100 1000 1000 1000
Wire Wire Line
	1100 1400 1000 1400
$Comp
L symat_8_bit_hobby:Rapsberry_PI_GPIO_connector_(40_pin) J?
U 1 1 6012D4D4
P 1500 1950
F 0 "J?" H 1500 3125 50  0000 C CNN
F 1 "Rapsberry_PI_GPIO_connector_(40_pin)" H 1500 3034 50  0000 C CNN
F 2 "" H 1450 2000 50  0001 C CNN
F 3 "~" H 1450 2000 50  0001 C CNN
	1    1500 1950
	1    0    0    -1  
$EndComp
$EndSCHEMATC
