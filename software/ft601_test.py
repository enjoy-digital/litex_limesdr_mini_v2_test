#!/usr/bin/env python3

#
# This file is part of LiteX-LimeSDR-Mini-V2 project.
#
# Copyright (c) 2022 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

import time
import ctypes

import ftd3xx
from ftd3xx._ftd3xx_linux import *

class FT601:
    channel = 0 # FIXME: Add Channel config?
    def open(self):
        self.device = device = ftd3xx.create(id_str=0, flags=FT_OPEN_BY_INDEX)
        if device is None:
            raise OSError("Unable to find FTD601 device, please check Hardware/OS config.")
        device.flushPipe(self.channel)

    def close(self):
        if hasattr(self, "device"):
            self.device.close()
            del self.device

    def write(self, data, timeout=1e-1):
        if not isinstance(data, bytes):
            data = bytes(data)
        xfer_bytes =  self.device.writePipe(
            channel = self.channel,
            data    = data,
            datalen = len(data),
            timeout = int(timeout*1e3),
        )
        return xfer_bytes

    def read(self, length=1, timeout=1e-1):
        data = ctypes.c_buffer(length)
        xfer_bytes = self.device.readPipe(
            channel = self.channel,
            data    = data,
            datalen = length,
            timeout = int(timeout*1e3),
        )
        return list(data[:xfer_bytes])

ft601 = FT601()
ft601.open()
for _ in range(8):
    ft601.write([i%256 for i in range(64)])
    time.sleep(0.1)
    print(ft601.read(64, timeout=1e-1))
    time.sleep(0.5)
    #print(ft601.device.getReadQueueStatus(0))
ft601.close()
