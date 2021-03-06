from ConfigHandler import progress_led_toggle_adaptor


def memfree():
    from gc import mem_free
    from machine import freq
    return "CPU[Hz]: {}\nGC MemFree[byte]: {}".format(freq(), mem_free())


def gcollect():
    from gc import collect, mem_free
    collect()
    return "GC MemFree[byte]: {}".format(mem_free())


@progress_led_toggle_adaptor
def heartbeat():
    from time import sleep
    sleep(0.1)
    return "<3 heartbeat <3"


def clock():
    from time import localtime
    return localtime()


def ntp():
    try:
        from time import localtime, time
        from ntptime import settime
        from machine import RTC
        from ConfigHandler import cfgget

        # Sync with NTP server
        settime()
        # Get localtime + GMT
        (year, month, mday, hour, minute, second, weekday, yearday) = localtime(time() + int(cfgget('gmttime'))*3600)
        # Create RealTimeClock + Set RTC with time (+timezone)
        RTC().datetime((year, month, mday, 0, hour, minute, second, 0))
        # Print time
        return localtime()
    except Exception as e:
        return "NTP time errer.:{}".format(e)


def module(unload=None):
    from sys import modules
    if unload is None:
        return modules.keys()
    try:
        del modules[unload]
        return "Module unload {} done.".format(unload)
    except Exception as e:
        return "Module unload failed: {}".format(e)


def pwr(mode=None):
    from machine import freq
    if mode is not None and mode.lower().strip() == 'norm':
        freq(80000000)
        return 'LOW MODE: CPU 8Mhz'
    if mode is not None and mode.lower().strip() == 'boost':
        freq(160000000)
        return 'HIGH MODE: CPU 16Mhz'
    return '{} ? boost or norm'.format(mode)


def help():
    return 'memfree', 'gcollect', 'heartbeat', 'clock', 'ntp', 'module', 'pwr'
