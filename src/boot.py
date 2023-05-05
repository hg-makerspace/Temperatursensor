# This file is executed on every boot (including wake-boot from deepsleep)

import gc
#import esp
#import webrepl

#esp.osdebug(None)
#webrepl.start()
gc.collect()
