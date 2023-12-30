import allsky_shared as s
import os
import math
import board
import busio
import adafruit_tsl2591
import adafruit_tsl2561

metaData = {
    "name": "AllSky Light Meter",
    "description": "Estimates sky brightness",
    "module": "allsky_light",
    "version": "v1.0.0",
    "events": ["periodic"],
    "experimental": "false",
    "arguments": {
        "type": "",
        "i2caddress": "",
        "tsl2591gain": "25x",
        "tsl2591integration": "100ms",
        "tsl2561gain": "Low",
        "tsl2561integration": "101ms"
    },
    "argumentdetails": {
        "type": {
            "required": "false",
            "description": "Sensor Type",
            "help": "The type of sensor that is being used.",
            "type": {
                "fieldtype": "select",
                "values": "None,TSL2591,TSL2561",
                "default": "None"
            }
        },
        "i2caddress": {
            "required": "false",
            "description": "I2C Address",
            "help": "Override the standard i2c address (0x29) for the sensor. NOTE: This value must be hex i.e. 0x76"
        },
        "tsl2591gain": {
            "required": "false",
            "description": "TSL2591 Gain",
            "help": "The gain for the TSL2591 sensor.",
            "tab": "TSL2591",
            "type": {
                "fieldtype": "select",
                "values": "1x,25x,428x,9876x",
                "default": "25x"
            }
        },
        "tsl2591integration": {
            "required": "false",
            "description": "TSL2591 Integration time",
            "help": "The integration time for the TSL2591 sensor.",
            "tab": "TSL2591",
            "type": {
                "fieldtype": "select",
                "values": "100ms,200ms,300ms,400ms,500ms,600ms",
                "default": "100ms"
            }
        },
        "tsl2561gain": {
            "required": "false",
            "description": "TSL2561 Gain",
            "help": "The gain for the TSL2561 sensor.",
            "tab": "TSL2561",
            "type": {
                "fieldtype": "select",
                "values": "Low,High",
                "default": "Low"
            }
        },
        "tsl2561integration": {
            "required": "false",
            "description": "TSL2561 Integration time",
            "help": "The integration time for the TSL2561 sensor.",
            "tab": "TSL2561",
            "type": {
                "fieldtype": "select",
                "values": "13.7ms,101ms,402ms",
                "default": "101ms"
            }
        }
    },
    "enabled": "false"
}

def adjust_gain_tsl2591(sensor, lux):
    if lux < 10:
        sensor.gain = adafruit_tsl2591.GAIN_MAX
    elif lux < 100:
        sensor.gain = adafruit_tsl2591.GAIN_HIGH
    elif lux < 1000:
        sensor.gain = adafruit_tsl2591.GAIN_MED
    else:
        sensor.gain = adafruit_tsl2591.GAIN_LOW

def adjust_gain_tsl2561(sensor, lux):
    if lux < 10:
        sensor.gain = 1  # High Gain
    elif lux < 1000:
        sensor.gain = 0  # Low Gain
    else:
        sensor.gain = 0  # Low Gain

def readTSL2591(params):
    i2c = board.I2C()
    sensor = adafruit_tsl2591.TSL2591(i2c)

    # Ustawienie początkowego wzmocnienia i czasu integracji
    sensor.gain = adafruit_tsl2591.GAIN_MED
    sensor.integration_time = adafruit_tsl2591.INTEGRATIONTIME_100MS

    # Automatyczna regulacja wzmocnienia
    lux = sensor.lux
    adjust_gain_tsl2591(sensor, lux)

    # Ponowny odczyt wartości po dostosowaniu wzmocnienia
    lux = sensor.lux
    infrared = sensor.infrared
    visible = sensor.visible

    return lux, infrared, visible

def readTSL2561(params):
    i2c = busio.I2C(board.SCL, board.SDA)
    sensor = adafruit_tsl2561.TSL2561(i2c)

    # Ustawienie początkowego wzmocnienia i czasu integracji
    sensor.gain = 0
    sensor.integration_time = 1

    # Automatyczna regulacja wzmocnienia
    lux = sensor.lux
    adjust_gain_tsl2561(sensor, lux)

    # Ponowny odczyt wartości po dostosowaniu wzmocnienia
    visible = sensor.broadband
    infrared = sensor.infrared
    lux = sensor.lux
    if lux is None:
        lux = 0

    return lux, infrared, visible

def sqm_to_bortle(sqm):
    if sqm >= 21.75:
        return 1  # Excellent dark-sky site
    elif sqm >= 21.6:
        return 2  # Typical truly dark site
    elif sqm >= 21.3:
        return 3  # Rural sky
    elif sqm >= 20.8:
        return 4  # Brighter rural
    elif sqm >= 20.3:
        return 4.5  # Semi-Suburban/Transition sky
    elif sqm >= 19.25:
        return 5  # Suburban sky
    elif sqm >= 18.5:
        return 6  # Bright suburban sky
    elif sqm >= 18.0:
        return 7  # Suburban/urban transition
    elif sqm < 18.0:
        return 8  # City sky
    else:
        return 9  # Inner-city sky

def light(params, event):
    result = ''
    sensor = params["type"].lower()
    if sensor != "None":
        if sensor == "tsl2591":
            lux, infrared, visible = readTSL2591(params)
        elif sensor == "tsl2561":
            lux, infrared, visible = readTSL2561(params)

        sqm = math.log10(lux / 108000) / -0.4
        bortle = sqm_to_bortle(sqm)
        nelm = 7.93 - 5.0 * math.log10((pow(10, (4.316 - (sqm / 5.0))) + 1.0))
        lux2 = round(lux, 7)
        nelm2 = round(nelm, 2)
        sqm2 = round(sqm, 2)

        extraData = {}
        extraData["AS_LIGHTLUX"] = str(lux2)
        extraData["AS_LIGHTNELM"] = str(nelm2)
        extraData["AS_LIGHTSQM"] = str(sqm2)
        extraData["AS_LIGHTBORTLE"] = str(bortle)
        s.saveExtraData("allskylight.json", extraData)
        result = f"Lux {lux2}, NELM {nelm2}, SQM {sqm2},  Bortle {bortle}"
        s.log(4, f"INFO: {result}")
    else:
        s.deleteExtraData("allskylight.json")
        result = "No sensor defined"
        s.log(0, f"ERROR: {result}")

    return result

def light_cleanup():
    moduleData = {
        "metaData": metaData,
        "cleanup": {
            "files": {
                "allskylight.json"
            },
            "env": {}
        }
    }
    s.cleanupModule(moduleData)

# Możesz tutaj dodać dodatkowy kod, jeśli jest potrzebny
