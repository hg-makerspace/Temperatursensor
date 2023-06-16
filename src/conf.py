def loadconfig():
    # defaults with all config options
    config_data = {'use_network': True,
                   'wlan_name': "meinwlan",
                   'wlan_passwort': "meinwlanpasswort",
                   'mqtt_server': "example.com",
                   'mqtt_topic': "iot_hg/json"
                   }
    try:
        with open("conf.txt") as f:
            for line in f.readlines():
                if line.strip().startswith('#') or not '=' in line:
                    continue
                linesplit = line.split('=', 1)
                key = linesplit[0].strip()
                value = linesplit[1].strip()
                if key in config_data and len(value) > 0:
                    config_data[key] = value
                else:
                    raise ValueError
    except OSError:
        print("config file not found")
        config_data = None
    except ValueError:
        print("config file parse error")
        config_data = None
    return config_data
