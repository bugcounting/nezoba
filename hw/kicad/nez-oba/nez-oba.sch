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
Wire Wire Line
	5100 1500 4850 1500
Wire Wire Line
	5100 1950 4850 1950
Wire Wire Line
	5100 2400 4850 2400
Wire Wire Line
	5100 2850 4850 2850
Wire Wire Line
	6200 1500 5950 1500
Wire Wire Line
	6200 1950 5950 1950
Wire Wire Line
	6200 2400 5950 2400
Wire Wire Line
	6200 2850 5950 2850
Wire Wire Line
	7200 1500 7000 1500
Wire Wire Line
	7200 1950 7000 1950
Wire Wire Line
	7200 2400 7000 2400
Wire Wire Line
	7200 2850 7000 2850
Wire Wire Line
	2800 3700 2800 3650
Wire Wire Line
	3150 3700 3150 3550
Text Label 3150 3650 0    50   ~ 0
S.+
Text Label 2800 3650 0    50   ~ 0
S.-
Text Label 4900 1500 0    50   ~ 0
S.left
Text Label 4900 1950 0    50   ~ 0
S.down
Text Label 4900 2400 0    50   ~ 0
S.right
Text Label 4900 2850 0    50   ~ 0
S.up
Text Label 6000 1500 0    50   ~ 0
S.A
Text Label 6000 1950 0    50   ~ 0
S.B
Text Label 6000 2400 0    50   ~ 0
S.X
Text Label 6000 2850 0    50   ~ 0
S.Y
Text Label 7050 1500 0    50   ~ 0
S.L
Text Label 7050 1950 0    50   ~ 0
S.R
Text Label 7050 2400 0    50   ~ 0
S.ZL
Text Label 7050 2850 0    50   ~ 0
S.ZR
$Comp
L power:GND #PWR0111
U 1 1 619230D5
P 7800 1500
F 0 "#PWR0111" H 7800 1250 50  0001 C CNN
F 1 "GND" H 7805 1327 50  0000 C CNN
F 2 "" H 7800 1500 50  0001 C CNN
F 3 "" H 7800 1500 50  0001 C CNN
	1    7800 1500
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR0112
U 1 1 6192339D
P 7800 1950
F 0 "#PWR0112" H 7800 1700 50  0001 C CNN
F 1 "GND" H 7805 1777 50  0000 C CNN
F 2 "" H 7800 1950 50  0001 C CNN
F 3 "" H 7800 1950 50  0001 C CNN
	1    7800 1950
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR0113
U 1 1 6192365F
P 7800 2400
F 0 "#PWR0113" H 7800 2150 50  0001 C CNN
F 1 "GND" H 7805 2227 50  0000 C CNN
F 2 "" H 7800 2400 50  0001 C CNN
F 3 "" H 7800 2400 50  0001 C CNN
	1    7800 2400
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR0114
U 1 1 619238F3
P 7800 2850
F 0 "#PWR0114" H 7800 2600 50  0001 C CNN
F 1 "GND" H 7805 2677 50  0000 C CNN
F 2 "" H 7800 2850 50  0001 C CNN
F 3 "" H 7800 2850 50  0001 C CNN
	1    7800 2850
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR0115
U 1 1 61923E46
P 2800 4300
F 0 "#PWR0115" H 2800 4050 50  0001 C CNN
F 1 "GND" H 2805 4127 50  0000 C CNN
F 2 "" H 2800 4300 50  0001 C CNN
F 3 "" H 2800 4300 50  0001 C CNN
	1    2800 4300
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR0116
U 1 1 61924138
P 3150 4300
F 0 "#PWR0116" H 3150 4050 50  0001 C CNN
F 1 "GND" H 3155 4127 50  0000 C CNN
F 2 "" H 3150 4300 50  0001 C CNN
F 3 "" H 3150 4300 50  0001 C CNN
	1    3150 4300
	1    0    0    -1  
$EndComp
$Comp
L power:+5V #PWR0123
U 1 1 61962C42
P 1950 1800
F 0 "#PWR0123" H 1950 1650 50  0001 C CNN
F 1 "+5V" V 1965 1928 50  0000 L CNN
F 2 "" H 1950 1800 50  0001 C CNN
F 3 "" H 1950 1800 50  0001 C CNN
	1    1950 1800
	0    1    1    0   
$EndComp
Text Label 5750 4150 0    50   ~ 0
cfg.b1
Text Label 5750 4050 0    50   ~ 0
cfg.b2
Text Label 5750 3950 0    50   ~ 0
cfg.b3
Text Label 5750 3850 0    50   ~ 0
cfg.b4
$Comp
L power:GND #PWR0124
U 1 1 619B2A9D
P 5100 3850
F 0 "#PWR0124" H 5100 3600 50  0001 C CNN
F 1 "GND" V 5105 3722 50  0000 R CNN
F 2 "" H 5100 3850 50  0001 C CNN
F 3 "" H 5100 3850 50  0001 C CNN
	1    5100 3850
	0    1    1    0   
$EndComp
$Comp
L power:GND #PWR0125
U 1 1 619B323C
P 5100 3950
F 0 "#PWR0125" H 5100 3700 50  0001 C CNN
F 1 "GND" V 5105 3822 50  0000 R CNN
F 2 "" H 5100 3950 50  0001 C CNN
F 3 "" H 5100 3950 50  0001 C CNN
	1    5100 3950
	0    1    1    0   
$EndComp
$Comp
L power:GND #PWR0127
U 1 1 619B36EB
P 5100 4150
F 0 "#PWR0127" H 5100 3900 50  0001 C CNN
F 1 "GND" V 5105 4022 50  0000 R CNN
F 2 "" H 5100 4150 50  0001 C CNN
F 3 "" H 5100 4150 50  0001 C CNN
	1    5100 4150
	0    1    1    0   
$EndComp
Wire Wire Line
	3900 1650 4150 1650
Wire Wire Line
	3900 1750 4150 1750
Wire Wire Line
	3900 1850 4150 1850
Wire Wire Line
	3900 1950 4150 1950
Wire Wire Line
	3900 2050 4150 2050
Wire Wire Line
	3900 2150 4150 2150
Wire Wire Line
	3900 2250 4150 2250
Wire Wire Line
	3900 2350 4150 2350
Wire Wire Line
	2700 1650 2450 1650
Wire Wire Line
	2700 1750 2450 1750
Wire Wire Line
	2700 1850 2450 1850
Wire Wire Line
	2700 1950 2450 1950
Wire Wire Line
	2700 2050 2450 2050
Wire Wire Line
	2700 2150 2450 2150
Wire Wire Line
	2700 2250 2450 2250
Wire Wire Line
	2700 2350 2450 2350
Text Label 3950 2350 0    50   ~ 0
S.X
Text Label 3950 2250 0    50   ~ 0
S.Y
Text Label 3950 1950 0    50   ~ 0
S.B
Text Label 3950 1850 0    50   ~ 0
S.L
Text Label 3950 1750 0    50   ~ 0
S.R
$Comp
L power:GND #PWR0101
U 1 1 61BC70FF
P 3900 2750
F 0 "#PWR0101" H 3900 2500 50  0001 C CNN
F 1 "GND" V 3905 2622 50  0000 R CNN
F 2 "" H 3900 2750 50  0001 C CNN
F 3 "" H 3900 2750 50  0001 C CNN
	1    3900 2750
	0    -1   -1   0   
$EndComp
$Comp
L power:GND #PWR0106
U 1 1 61BCBF1E
P 3900 2850
F 0 "#PWR0106" H 3900 2600 50  0001 C CNN
F 1 "GND" V 3905 2722 50  0000 R CNN
F 2 "" H 3900 2850 50  0001 C CNN
F 3 "" H 3900 2850 50  0001 C CNN
	1    3900 2850
	0    -1   -1   0   
$EndComp
$Comp
L power:GND #PWR0118
U 1 1 61BCC5B2
P 3900 2950
F 0 "#PWR0118" H 3900 2700 50  0001 C CNN
F 1 "GND" V 3905 2822 50  0000 R CNN
F 2 "" H 3900 2950 50  0001 C CNN
F 3 "" H 3900 2950 50  0001 C CNN
	1    3900 2950
	0    -1   -1   0   
$EndComp
Text Label 3950 1650 0    50   ~ 0
S.up
Text Label 2500 1850 0    50   ~ 0
S.+
Text Label 2500 2350 0    50   ~ 0
S.home
Text Label 2500 1950 0    50   ~ 0
S.left
Text Label 2500 2050 0    50   ~ 0
S.down
Text Label 2500 2250 0    50   ~ 0
cfg.b4
$Comp
L power:GND #PWR0119
U 1 1 61BCFF22
P 2700 2550
F 0 "#PWR0119" H 2700 2300 50  0001 C CNN
F 1 "GND" V 2705 2422 50  0000 R CNN
F 2 "" H 2700 2550 50  0001 C CNN
F 3 "" H 2700 2550 50  0001 C CNN
	1    2700 2550
	0    1    1    0   
$EndComp
$Comp
L power:+5V #PWR0120
U 1 1 61BD5645
P 2700 2450
F 0 "#PWR0120" H 2700 2300 50  0001 C CNN
F 1 "+5V" V 2715 2578 50  0000 L CNN
F 2 "" H 2700 2450 50  0001 C CNN
F 3 "" H 2700 2450 50  0001 C CNN
	1    2700 2450
	0    -1   -1   0   
$EndComp
Text Label 3700 3650 0    50   ~ 0
S.home
Wire Wire Line
	3700 3700 3700 3550
Wire Wire Line
	5700 3850 5950 3850
Wire Wire Line
	5700 3950 5950 3950
Wire Wire Line
	5700 4050 5850 4050
Wire Wire Line
	5700 4150 5950 4150
Wire Wire Line
	1950 2000 2150 2000
Text Label 650  1900 0    50   ~ 0
cfg.b2
Text Label 650  2000 0    50   ~ 0
cfg.b3
Wire Wire Line
	950  2000 600  2000
Wire Wire Line
	950  1900 600  1900
Text Label 2000 2000 0    50   ~ 0
cfg.b1
$Comp
L power:GND #PWR0121
U 1 1 61C7AB94
P 3700 4300
F 0 "#PWR0121" H 3700 4050 50  0001 C CNN
F 1 "GND" H 3705 4127 50  0000 C CNN
F 2 "" H 3700 4300 50  0001 C CNN
F 3 "" H 3700 4300 50  0001 C CNN
	1    3700 4300
	1    0    0    -1  
$EndComp
Text Label 3950 2050 0    50   ~ 0
S.A
Text Label 2500 2150 0    50   ~ 0
S.right
NoConn ~ 950  1600
NoConn ~ 950  1700
NoConn ~ 950  2100
NoConn ~ 1950 1600
NoConn ~ 1950 1700
NoConn ~ 3900 2450
NoConn ~ 3900 2550
NoConn ~ 2700 2650
NoConn ~ 2700 2950
$Comp
L power:+5V #PWR0122
U 1 1 61CA0D0B
P 3900 2650
F 0 "#PWR0122" H 3900 2500 50  0001 C CNN
F 1 "+5V" V 3915 2778 50  0000 L CNN
F 2 "" H 3900 2650 50  0001 C CNN
F 3 "" H 3900 2650 50  0001 C CNN
	1    3900 2650
	0    1    1    0   
$EndComp
$Comp
L power:GND #PWR0117
U 1 1 61CA8EB6
P 950 1800
F 0 "#PWR0117" H 950 1550 50  0001 C CNN
F 1 "GND" V 955 1672 50  0000 R CNN
F 2 "" H 950 1800 50  0001 C CNN
F 3 "" H 950 1800 50  0001 C CNN
	1    950  1800
	0    1    1    0   
$EndComp
$Comp
L power:GND #PWR0126
U 1 1 61D0885A
P 5100 4050
F 0 "#PWR0126" H 5100 3800 50  0001 C CNN
F 1 "GND" V 5105 3922 50  0000 R CNN
F 2 "" H 5100 4050 50  0001 C CNN
F 3 "" H 5100 4050 50  0001 C CNN
	1    5100 4050
	0    1    1    0   
$EndComp
$Comp
L power:GND #PWR0102
U 1 1 61D091F3
P 5700 1500
F 0 "#PWR0102" H 5700 1250 50  0001 C CNN
F 1 "GND" H 5705 1327 50  0000 C CNN
F 2 "" H 5700 1500 50  0001 C CNN
F 3 "" H 5700 1500 50  0001 C CNN
	1    5700 1500
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR0103
U 1 1 61D0EF10
P 5700 1950
F 0 "#PWR0103" H 5700 1700 50  0001 C CNN
F 1 "GND" H 5705 1777 50  0000 C CNN
F 2 "" H 5700 1950 50  0001 C CNN
F 3 "" H 5700 1950 50  0001 C CNN
	1    5700 1950
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR0104
U 1 1 61D0F4DF
P 5700 2400
F 0 "#PWR0104" H 5700 2150 50  0001 C CNN
F 1 "GND" H 5705 2227 50  0000 C CNN
F 2 "" H 5700 2400 50  0001 C CNN
F 3 "" H 5700 2400 50  0001 C CNN
	1    5700 2400
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR0105
U 1 1 61D0F91D
P 5700 2850
F 0 "#PWR0105" H 5700 2600 50  0001 C CNN
F 1 "GND" H 5705 2677 50  0000 C CNN
F 2 "" H 5700 2850 50  0001 C CNN
F 3 "" H 5700 2850 50  0001 C CNN
	1    5700 2850
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR0107
U 1 1 61D10314
P 6800 2850
F 0 "#PWR0107" H 6800 2600 50  0001 C CNN
F 1 "GND" H 6805 2677 50  0000 C CNN
F 2 "" H 6800 2850 50  0001 C CNN
F 3 "" H 6800 2850 50  0001 C CNN
	1    6800 2850
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR0108
U 1 1 61D107E5
P 6800 2400
F 0 "#PWR0108" H 6800 2150 50  0001 C CNN
F 1 "GND" H 6805 2227 50  0000 C CNN
F 2 "" H 6800 2400 50  0001 C CNN
F 3 "" H 6800 2400 50  0001 C CNN
	1    6800 2400
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR0109
U 1 1 61D10CC4
P 6800 1950
F 0 "#PWR0109" H 6800 1700 50  0001 C CNN
F 1 "GND" H 6805 1777 50  0000 C CNN
F 2 "" H 6800 1950 50  0001 C CNN
F 3 "" H 6800 1950 50  0001 C CNN
	1    6800 1950
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR0110
U 1 1 61D111E7
P 6800 1500
F 0 "#PWR0110" H 6800 1250 50  0001 C CNN
F 1 "GND" H 6805 1327 50  0000 C CNN
F 2 "" H 6800 1500 50  0001 C CNN
F 3 "" H 6800 1500 50  0001 C CNN
	1    6800 1500
	1    0    0    -1  
$EndComp
$Comp
L nez-symbols:TrinketM0 Trinket1
U 1 1 61CF1130
P 950 2100
F 0 "Trinket1" H 1450 1335 50  0000 C CNN
F 1 "TrinketM0" H 1450 1426 50  0000 C CNN
F 2 "nez-footprints:Trinket_M0" H 1800 2200 50  0001 L CNN
F 3 "https://www.adafruit.com/product/3500#description" H 1800 2100 50  0001 L CNN
F 4 "ADAFRUIT - 3500 - ADAFRUIT TRINKET M0 - FOR USE WITH CIRCUITPYTHON & ARDUINO IDE" H 1800 2000 50  0001 L CNN "Description"
F 5 "2.75" H 1800 1900 50  0001 L CNN "Height"
F 6 "Adafruit" H 1800 1800 50  0001 L CNN "Manufacturer_Name"
F 7 "3500" H 1800 1700 50  0001 L CNN "Manufacturer_Part_Number"
F 8 "1528-2361-ND" H 950 2100 50  0001 C CNN "Digi-Key Part Number"
F 9 "https://www.digikey.be/en/products/detail/adafruit-industries-llc/3500/7623049" H 950 2100 50  0001 C CNN "Digi-Key Product Page"
	1    950  2100
	1    0    0    1   
$EndComp
$Comp
L nez-symbols:SW_DIP_x04 CFG1
U 1 1 61CFBE06
P 5400 4050
F 0 "CFG1" H 5400 4425 50  0000 C CNN
F 1 "SW_DIP_x04" H 5400 4426 50  0001 C CNN
F 2 "nez-footprints:SW_DIP_SPSTx04_Slide_6.7x11.72mm_W7.8mm_P2.54mm" H 5400 4050 50  0001 C CNN
F 3 "https://www.citrelay.com/Catalog%20Pages/SwitchCatalog/KG.pdf" H 5400 4050 50  0001 C CNN
F 4 "CIT Relay and Switch" H 5400 4050 50  0001 C CNN "Manufacturer_Name"
F 5 "KG04E" H 5400 4050 50  0001 C CNN "Manufacturer_Part_Number"
F 6 "2449-KG04E-ND" H 5400 4050 50  0001 C CNN "Digi-Key Part Number"
F 7 "https://www.digikey.be/en/products/detail/cit-relay-and-switch/KG04E/15294210" H 5400 4050 50  0001 C CNN "Digi-Key product page"
	1    5400 4050
	1    0    0    -1  
$EndComp
$Comp
L nez-symbols:R_US R.4.7k2
U 1 1 61D062A7
P 2150 2950
F 0 "R.4.7k2" V 2263 2950 50  0000 C CNN
F 1 "R_US" V 2354 2950 50  0000 C CNN
F 2 "nez-footprints:R_LDR_P12mm_narrow" V 2190 2940 50  0001 C CNN
F 3 "https://www.te.com/commerce/DocumentDelivery/DDEController?Action=srchrtrv&DocNm=1773271&DocType=DS&DocLang=English" H 2150 2950 50  0001 C CNN
F 4 "TE Connectivity Passive Product" H 2150 2950 50  0001 C CNN "Manufacturer_Name"
F 5 "ROX1SJ4K7" H 2150 2950 50  0001 C CNN "Manufacturer_Part_Number"
F 6 "A131473CT-ND" H 2150 2950 50  0001 C CNN "Digi-Key Part Number"
F 7 "https://www.digikey.be/en/products/detail/te-connectivity-passive-product/ROX1SJ4K7/8603603" H 2150 2950 50  0001 C CNN "Digi-Key Product Page"
	1    2150 2950
	0    1    1    0   
$EndComp
$Comp
L power:+5V #PWR0128
U 1 1 61D06FE9
P 2000 2950
F 0 "#PWR0128" H 2000 2800 50  0001 C CNN
F 1 "+5V" V 2015 3078 50  0000 L CNN
F 2 "" H 2000 2950 50  0001 C CNN
F 3 "" H 2000 2950 50  0001 C CNN
	1    2000 2950
	0    -1   -1   0   
$EndComp
$Comp
L nez-symbols:MCP23017-E_SP MCP1
U 1 1 61CFFC40
P 2700 1650
F 0 "MCP1" H 3300 1915 50  0000 C CNN
F 1 "MCP23017-E_SP" H 3300 1824 50  0000 C CNN
F 2 "nez-footprints:DIP-28_W7.62mm" H 3750 1750 50  0001 L CNN
F 3 "http://www.microchip.com/mymicrochip/filehandler.aspx?ddocname=en023709" H 3750 1650 50  0001 L CNN
F 4 "2" H 3750 1450 50  0001 L CNN "Height"
F 5 "Microchip Technology" H 3750 1350 50  0001 L CNN "Manufacturer_Name"
F 6 "MCP23017-E/SP" H 3750 1250 50  0001 L CNN "Manufacturer_Part_Number"
F 7 "MCP23017-E/SP-ND" H 2700 1650 50  0001 C CNN "Digi-Key Part Number"
F 8 "https://www.digikey.be/en/products/detail/microchip-technology/MCP23017-E-SP/894272" H 2700 1650 50  0001 C CNN "Digi-Key Product Page"
	1    2700 1650
	1    0    0    -1  
$EndComp
Text Label 2000 1900 0    50   ~ 0
sda
Wire Wire Line
	1950 1900 2150 1900
Wire Wire Line
	2700 2850 2450 2850
Wire Wire Line
	2450 2950 2450 2850
Text Label 2500 2850 0    50   ~ 0
sda
Wire Wire Line
	1950 2100 2150 2100
Text Label 2000 2100 0    50   ~ 0
scl
$Comp
L nez-symbols:R_US R.4.7k1
U 1 1 61D299B0
P 2150 2650
F 0 "R.4.7k1" V 1945 2650 50  0000 C CNN
F 1 "R_US" V 2036 2650 50  0000 C CNN
F 2 "nez-footprints:R_LDR_P12mm_narrow" V 2190 2640 50  0001 C CNN
F 3 "https://www.te.com/commerce/DocumentDelivery/DDEController?Action=srchrtrv&DocNm=1773271&DocType=DS&DocLang=English" H 2150 2650 50  0001 C CNN
F 4 "TE Connectivity Passive Product" H 2150 2650 50  0001 C CNN "Manufacturer_Name"
F 5 "ROX1SJ4K7" H 2150 2650 50  0001 C CNN "Manufacturer_Part_Number"
F 6 "A131473CT-ND" H 2150 2650 50  0001 C CNN "Digi-Key Part Number"
F 7 "https://www.digikey.be/en/products/detail/te-connectivity-passive-product/ROX1SJ4K7/8603603" H 2150 2650 50  0001 C CNN "Digi-Key Product Page"
	1    2150 2650
	0    1    1    0   
$EndComp
$Comp
L power:+5V #PWR0129
U 1 1 61D299BA
P 2000 2650
F 0 "#PWR0129" H 2000 2500 50  0001 C CNN
F 1 "+5V" V 2015 2778 50  0000 L CNN
F 2 "" H 2000 2650 50  0001 C CNN
F 3 "" H 2000 2650 50  0001 C CNN
	1    2000 2650
	0    -1   -1   0   
$EndComp
Wire Wire Line
	2300 2750 2300 2650
Wire Wire Line
	2300 2750 2700 2750
Wire Wire Line
	2300 2950 2450 2950
Text Label 2500 2750 0    50   ~ 0
scl
$Comp
L nez-symbols:SW_DIP_x01_tactile SW.-1
U 1 1 61D51309
P 2800 4000
F 0 "SW.-1" V 2800 3871 50  0000 R CNN
F 1 "SW_DIP_x01_tactile" V 2845 3871 50  0001 R CNN
F 2 "nez-footprints:SW_SPST_B3S-1000" H 2800 4000 50  0001 C CNN
F 3 "https://www.we-online.de/katalog/datasheet/430476085716.pdf" H 2800 4000 50  0001 C CNN
F 4 "Würth Elektronik" H 2800 4000 50  0001 C CNN "Manufacturer_Name"
F 5 "430476085716" H 2800 4000 50  0001 C CNN "Manufacturer_Part_Number"
F 6 "430476085716-ND" H 2800 4000 50  0001 C CNN "Digi-Key Part Number"
F 7 "https://www.digikey.be/en/products/detail/w%C3%BCrth-elektronik/430476085716/5209048" H 2800 4000 50  0001 C CNN "Digi-Key Product Page"
	1    2800 4000
	0    1    1    0   
$EndComp
$Comp
L nez-symbols:SW_DIP_x01_tactile SW.+1
U 1 1 61D56461
P 3150 4000
F 0 "SW.+1" V 3150 4130 50  0000 L CNN
F 1 "SW_DIP_x01_tactile" V 3195 4130 50  0001 L CNN
F 2 "nez-footprints:SW_SPST_B3S-1000" H 3150 4000 50  0001 C CNN
F 3 "https://www.we-online.de/katalog/datasheet/430476085716.pdf" H 3150 4000 50  0001 C CNN
F 4 "Würth Elektronik" H 3150 4000 50  0001 C CNN "Manufacturer_Name"
F 5 "430476085716" H 3150 4000 50  0001 C CNN "Manufacturer_Part_Number"
F 6 "430476085716-ND" H 3150 4000 50  0001 C CNN "Digi-Key Part Number"
F 7 "https://www.digikey.be/en/products/detail/w%C3%BCrth-elektronik/430476085716/5209048" H 3150 4000 50  0001 C CNN "Digi-Key Product Page"
	1    3150 4000
	0    1    1    0   
$EndComp
$Comp
L nez-symbols:SW_DIP_x01_tactile SW.home1
U 1 1 61D579B1
P 3700 4000
F 0 "SW.home1" V 3700 4130 50  0000 L CNN
F 1 "SW_DIP_x01_tactile" V 3745 4130 50  0001 L CNN
F 2 "nez-footprints:SW_SPST_B3S-1000" H 3700 4000 50  0001 C CNN
F 3 "https://www.we-online.de/katalog/datasheet/430476085716.pdf" H 3700 4000 50  0001 C CNN
F 4 "Würth Elektronik" H 3700 4000 50  0001 C CNN "Manufacturer_Name"
F 5 "430476085716" H 3700 4000 50  0001 C CNN "Manufacturer_Part_Number"
F 6 "430476085716-ND" H 3700 4000 50  0001 C CNN "Digi-Key Part Number"
F 7 "https://www.digikey.be/en/products/detail/w%C3%BCrth-elektronik/430476085716/5209048" H 3700 4000 50  0001 C CNN "Digi-Key Product Page"
	1    3700 4000
	0    1    1    0   
$EndComp
$Comp
L nez-symbols:SW_DIP_x01_Kailh_Choc_Red SW.right1
U 1 1 61D69FA4
P 5400 2400
F 0 "SW.right1" H 5400 2575 50  0000 C CNN
F 1 "SW_DIP_x01_Kailh_Choc_Red" H 5400 2576 50  0001 C CNN
F 2 "nez-footprints:Kailh_Choc_LowProfile_CPG135001D02" H 5400 2400 50  0001 C CNN
F 3 "https://cdn-shop.adafruit.com/product-files/5113/CHOC+keyswitch_Kailh-CPG135001D01_C400229.pdf" H 5400 2400 50  0001 C CNN
F 4 "Adafruit Industries LLC" H 5400 2400 50  0001 C CNN "Manufacturer_Name"
F 5 "5113" H 5400 2400 50  0001 C CNN "Manufacturer_Part_Number"
F 6 "1528-5113-ND" H 5400 2400 50  0001 C CNN "Digi-Key Part Number"
F 7 "https://www.digikey.be/en/products/detail/adafruit-industries-llc/5113/14671668" H 5400 2575 50  0001 C CNN "Digi-Key Product Page"
	1    5400 2400
	1    0    0    -1  
$EndComp
$Comp
L nez-symbols:SW_DIP_x01_Kailh_Choc_Red SW.up1
U 1 1 61D6A46E
P 5400 2850
F 0 "SW.up1" H 5400 3025 50  0000 C CNN
F 1 "SW_DIP_x01_Kailh_Choc_Red" H 5400 3026 50  0001 C CNN
F 2 "nez-footprints:Kailh_Choc_LowProfile_CPG135001D02" H 5400 2850 50  0001 C CNN
F 3 "https://cdn-shop.adafruit.com/product-files/5113/CHOC+keyswitch_Kailh-CPG135001D01_C400229.pdf" H 5400 2850 50  0001 C CNN
F 4 "Adafruit Industries LLC" H 5400 2850 50  0001 C CNN "Manufacturer_Name"
F 5 "5113" H 5400 2850 50  0001 C CNN "Manufacturer_Part_Number"
F 6 "1528-5113-ND" H 5400 2850 50  0001 C CNN "Digi-Key Part Number"
F 7 "https://www.digikey.be/en/products/detail/adafruit-industries-llc/5113/14671668" H 5400 3025 50  0001 C CNN "Digi-Key Product Page"
	1    5400 2850
	1    0    0    -1  
$EndComp
$Comp
L nez-symbols:SW_DIP_x01_Kailh_Choc_Red SW.A1
U 1 1 61D6AA16
P 6500 1500
F 0 "SW.A1" H 6500 1675 50  0000 C CNN
F 1 "SW_DIP_x01_Kailh_Choc_Red" H 6500 1676 50  0001 C CNN
F 2 "nez-footprints:Kailh_Choc_LowProfile_CPG135001D02" H 6500 1500 50  0001 C CNN
F 3 "https://cdn-shop.adafruit.com/product-files/5113/CHOC+keyswitch_Kailh-CPG135001D01_C400229.pdf" H 6500 1500 50  0001 C CNN
F 4 "Adafruit Industries LLC" H 6500 1500 50  0001 C CNN "Manufacturer_Name"
F 5 "5113" H 6500 1500 50  0001 C CNN "Manufacturer_Part_Number"
F 6 "1528-5113-ND" H 6500 1500 50  0001 C CNN "Digi-Key Part Number"
F 7 "https://www.digikey.be/en/products/detail/adafruit-industries-llc/5113/14671668" H 6500 1675 50  0001 C CNN "Digi-Key Product Page"
	1    6500 1500
	1    0    0    -1  
$EndComp
$Comp
L nez-symbols:SW_DIP_x01_Kailh_Choc_Red SW.B1
U 1 1 61D6B292
P 6500 1950
F 0 "SW.B1" H 6500 2125 50  0000 C CNN
F 1 "SW_DIP_x01_Kailh_Choc_Red" H 6500 2126 50  0001 C CNN
F 2 "nez-footprints:Kailh_Choc_LowProfile_CPG135001D02" H 6500 1950 50  0001 C CNN
F 3 "https://cdn-shop.adafruit.com/product-files/5113/CHOC+keyswitch_Kailh-CPG135001D01_C400229.pdf" H 6500 1950 50  0001 C CNN
F 4 "Adafruit Industries LLC" H 6500 1950 50  0001 C CNN "Manufacturer_Name"
F 5 "5113" H 6500 1950 50  0001 C CNN "Manufacturer_Part_Number"
F 6 "1528-5113-ND" H 6500 1950 50  0001 C CNN "Digi-Key Part Number"
F 7 "https://www.digikey.be/en/products/detail/adafruit-industries-llc/5113/14671668" H 6500 2125 50  0001 C CNN "Digi-Key Product Page"
	1    6500 1950
	1    0    0    -1  
$EndComp
$Comp
L nez-symbols:SW_DIP_x01_Kailh_Choc_Red SW.down1
U 1 1 61D699EF
P 5400 1950
F 0 "SW.down1" H 5400 2125 50  0000 C CNN
F 1 "SW_DIP_x01_Kailh_Choc_Red" H 5400 2126 50  0001 C CNN
F 2 "nez-footprints:Kailh_Choc_LowProfile_CPG135001D02" H 5400 1950 50  0001 C CNN
F 3 "https://cdn-shop.adafruit.com/product-files/5113/CHOC+keyswitch_Kailh-CPG135001D01_C400229.pdf" H 5400 1950 50  0001 C CNN
F 4 "Adafruit Industries LLC" H 5400 1950 50  0001 C CNN "Manufacturer_Name"
F 5 "5113" H 5400 1950 50  0001 C CNN "Manufacturer_Part_Number"
F 6 "1528-5113-ND" H 5400 1950 50  0001 C CNN "Digi-Key Part Number"
F 7 "https://www.digikey.be/en/products/detail/adafruit-industries-llc/5113/14671668" H 5400 2125 50  0001 C CNN "Digi-Key Product Page"
	1    5400 1950
	1    0    0    -1  
$EndComp
$Comp
L nez-symbols:SW_DIP_x01_Kailh_Choc_Red SW.left1
U 1 1 61D638A4
P 5400 1500
F 0 "SW.left1" H 5400 1675 50  0000 C CNN
F 1 "SW_DIP_x01_Kailh_Choc_Red" H 5400 1676 50  0001 C CNN
F 2 "nez-footprints:Kailh_Choc_LowProfile_CPG135001D02" H 5400 1500 50  0001 C CNN
F 3 "https://cdn-shop.adafruit.com/product-files/5113/CHOC+keyswitch_Kailh-CPG135001D01_C400229.pdf" H 5400 1500 50  0001 C CNN
F 4 "Adafruit Industries LLC" H 5400 1500 50  0001 C CNN "Manufacturer_Name"
F 5 "5113" H 5400 1500 50  0001 C CNN "Manufacturer_Part_Number"
F 6 "1528-5113-ND" H 5400 1500 50  0001 C CNN "Digi-Key Part Number"
F 7 "https://www.digikey.be/en/products/detail/adafruit-industries-llc/5113/14671668" H 5400 1675 50  0001 C CNN "Digi-Key Product Page"
	1    5400 1500
	1    0    0    -1  
$EndComp
$Comp
L nez-symbols:SW_DIP_x01_Kailh_Choc_Red SW.Y1
U 1 1 61D6BC24
P 6500 2850
F 0 "SW.Y1" H 6500 3025 50  0000 C CNN
F 1 "SW_DIP_x01_Kailh_Choc_Red" H 6500 3026 50  0001 C CNN
F 2 "nez-footprints:Kailh_Choc_LowProfile_CPG135001D02" H 6500 2850 50  0001 C CNN
F 3 "https://cdn-shop.adafruit.com/product-files/5113/CHOC+keyswitch_Kailh-CPG135001D01_C400229.pdf" H 6500 2850 50  0001 C CNN
F 4 "Adafruit Industries LLC" H 6500 2850 50  0001 C CNN "Manufacturer_Name"
F 5 "5113" H 6500 2850 50  0001 C CNN "Manufacturer_Part_Number"
F 6 "1528-5113-ND" H 6500 2850 50  0001 C CNN "Digi-Key Part Number"
F 7 "https://www.digikey.be/en/products/detail/adafruit-industries-llc/5113/14671668" H 6500 3025 50  0001 C CNN "Digi-Key Product Page"
	1    6500 2850
	1    0    0    -1  
$EndComp
$Comp
L nez-symbols:SW_DIP_x01_Kailh_Choc_Red SW.X1
U 1 1 61D6B6F7
P 6500 2400
F 0 "SW.X1" H 6500 2575 50  0000 C CNN
F 1 "SW_DIP_x01_Kailh_Choc_Red" H 6500 2576 50  0001 C CNN
F 2 "nez-footprints:Kailh_Choc_LowProfile_CPG135001D02" H 6500 2400 50  0001 C CNN
F 3 "https://cdn-shop.adafruit.com/product-files/5113/CHOC+keyswitch_Kailh-CPG135001D01_C400229.pdf" H 6500 2400 50  0001 C CNN
F 4 "Adafruit Industries LLC" H 6500 2400 50  0001 C CNN "Manufacturer_Name"
F 5 "5113" H 6500 2400 50  0001 C CNN "Manufacturer_Part_Number"
F 6 "1528-5113-ND" H 6500 2400 50  0001 C CNN "Digi-Key Part Number"
F 7 "https://www.digikey.be/en/products/detail/adafruit-industries-llc/5113/14671668" H 6500 2575 50  0001 C CNN "Digi-Key Product Page"
	1    6500 2400
	1    0    0    -1  
$EndComp
$Comp
L nez-symbols:SW_DIP_x01_Kailh_Choc_Red SW.L1
U 1 1 61D6FAA0
P 7500 1500
F 0 "SW.L1" H 7500 1675 50  0000 C CNN
F 1 "SW_DIP_x01_Kailh_Choc_Red" H 7500 1676 50  0001 C CNN
F 2 "nez-footprints:Kailh_Choc_LowProfile_CPG135001D02" H 7500 1500 50  0001 C CNN
F 3 "https://cdn-shop.adafruit.com/product-files/5113/CHOC+keyswitch_Kailh-CPG135001D01_C400229.pdf" H 7500 1500 50  0001 C CNN
F 4 "Adafruit Industries LLC" H 7500 1500 50  0001 C CNN "Manufacturer_Name"
F 5 "5113" H 7500 1500 50  0001 C CNN "Manufacturer_Part_Number"
F 6 "1528-5113-ND" H 7500 1500 50  0001 C CNN "Digi-Key Part Number"
F 7 "https://www.digikey.be/en/products/detail/adafruit-industries-llc/5113/14671668" H 7500 1675 50  0001 C CNN "Digi-Key Product Page"
	1    7500 1500
	1    0    0    -1  
$EndComp
$Comp
L nez-symbols:SW_DIP_x01_Kailh_Choc_Red SW.R1
U 1 1 61D70161
P 7500 1950
F 0 "SW.R1" H 7500 2125 50  0000 C CNN
F 1 "SW_DIP_x01_Kailh_Choc_Red" H 7500 2126 50  0001 C CNN
F 2 "nez-footprints:Kailh_Choc_LowProfile_CPG135001D02" H 7500 1950 50  0001 C CNN
F 3 "https://cdn-shop.adafruit.com/product-files/5113/CHOC+keyswitch_Kailh-CPG135001D01_C400229.pdf" H 7500 1950 50  0001 C CNN
F 4 "Adafruit Industries LLC" H 7500 1950 50  0001 C CNN "Manufacturer_Name"
F 5 "5113" H 7500 1950 50  0001 C CNN "Manufacturer_Part_Number"
F 6 "1528-5113-ND" H 7500 1950 50  0001 C CNN "Digi-Key Part Number"
F 7 "https://www.digikey.be/en/products/detail/adafruit-industries-llc/5113/14671668" H 7500 2125 50  0001 C CNN "Digi-Key Product Page"
	1    7500 1950
	1    0    0    -1  
$EndComp
$Comp
L nez-symbols:SW_DIP_x01_Kailh_Choc_Red SW.ZL1
U 1 1 61D705A8
P 7500 2400
F 0 "SW.ZL1" H 7500 2575 50  0000 C CNN
F 1 "SW_DIP_x01_Kailh_Choc_Red" H 7500 2576 50  0001 C CNN
F 2 "nez-footprints:Kailh_Choc_LowProfile_CPG135001D02" H 7500 2400 50  0001 C CNN
F 3 "https://cdn-shop.adafruit.com/product-files/5113/CHOC+keyswitch_Kailh-CPG135001D01_C400229.pdf" H 7500 2400 50  0001 C CNN
F 4 "Adafruit Industries LLC" H 7500 2400 50  0001 C CNN "Manufacturer_Name"
F 5 "5113" H 7500 2400 50  0001 C CNN "Manufacturer_Part_Number"
F 6 "1528-5113-ND" H 7500 2400 50  0001 C CNN "Digi-Key Part Number"
F 7 "https://www.digikey.be/en/products/detail/adafruit-industries-llc/5113/14671668" H 7500 2575 50  0001 C CNN "Digi-Key Product Page"
	1    7500 2400
	1    0    0    -1  
$EndComp
$Comp
L nez-symbols:SW_DIP_x01_Kailh_Choc_Red SW.ZR1
U 1 1 61D70B3C
P 7500 2850
F 0 "SW.ZR1" H 7500 3025 50  0000 C CNN
F 1 "SW_DIP_x01_Kailh_Choc_Red" H 7500 3026 50  0001 C CNN
F 2 "nez-footprints:Kailh_Choc_LowProfile_CPG135001D02" H 7500 2850 50  0001 C CNN
F 3 "https://cdn-shop.adafruit.com/product-files/5113/CHOC+keyswitch_Kailh-CPG135001D01_C400229.pdf" H 7500 2850 50  0001 C CNN
F 4 "Adafruit Industries LLC" H 7500 2850 50  0001 C CNN "Manufacturer_Name"
F 5 "5113" H 7500 2850 50  0001 C CNN "Manufacturer_Part_Number"
F 6 "1528-5113-ND" H 7500 2850 50  0001 C CNN "Digi-Key Part Number"
F 7 "https://www.digikey.be/en/products/detail/adafruit-industries-llc/5113/14671668" H 7500 3025 50  0001 C CNN "Digi-Key Product Page"
	1    7500 2850
	1    0    0    -1  
$EndComp
Text Label 2500 1750 0    50   ~ 0
S.-
Text Label 2500 1650 0    50   ~ 0
S.ZR
Text Label 3950 2150 0    50   ~ 0
S.ZL
$EndSCHEMATC
