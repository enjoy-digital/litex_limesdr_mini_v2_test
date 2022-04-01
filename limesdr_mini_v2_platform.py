#
# This file is part of LiteX-LimeSDR-Mini-V2 project.
#
# Copyright (c) 2022 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

from litex.build.generic_platform import *
from litex.build.lattice import LatticePlatform
from litex.build.lattice.programmer import OpenOCDJTAGProgrammer

# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk.
    ("clk40", 0, Pins("A9"), IOStandard("LVCMOS33")),

    # Leds.
    ("led_g", 0, Pins("R16"), IOStandard("LVCMOS25"), Misc("OPENDRAIN=ON")),
    ("led_g", 1, Pins("M18"), IOStandard("LVCMOS25"), Misc("OPENDRAIN=ON")), # Shared with FPGA_GPIO4.
    ("led_g", 2, Pins("T17"), IOStandard("LVCMOS25"), Misc("OPENDRAIN=ON")), # Shared with FPGA_GPIO6.
    ("led_r", 0, Pins("V17"), IOStandard("LVCMOS25"), Misc("OPENDRAIN=ON")),
    ("led_r", 1, Pins("R18"), IOStandard("LVCMOS25"), Misc("OPENDRAIN=ON")), # Shared with FPGA_GPIO5.
    ("led_r", 2, Pins("R17"), IOStandard("LVCMOS25"), Misc("OPENDRAIN=ON")), # Shared with FPGA_GPIO7.

    # Revision.
    ("revision", 0,
        Subsignal("hardware", Pins("D4 M2 N4 J3")),
        Subsignal("bom",      Pins("N1 M1 N2")),
        IOStandard("LVCMOS25")
    ),

    # I2C.
    ("i2c", 0,
        Subsignal("scl", Pins("C10"), Misc("OPENDRAIN=ON")),
        Subsignal("sda", Pins("B9"), Misc("OPENDRAIN=ON")),
        IOStandard("LVCMOS33"),
    ),
]

# Platform -----------------------------------------------------------------------------------------

class Platform(LatticePlatform):
    default_clk_name   = "clk40"
    default_clk_period = 1e9/40e6

    def __init__(self, device="LFE5U", toolchain="trellis", **kwargs):
        assert device in ["LFE5U"]
        LatticePlatform.__init__(self, device + "-45F-8MG285C", _io, toolchain=toolchain, **kwargs)

    def create_programmer(self):
        return OpenOCDJTAGProgrammer("openocd_limesdr_mini_v2.cfg")

    def do_finalize(self, fragment):
        self.add_period_constraint(self.lookup_request("clk40", loose=True), 1e9/40e6)
