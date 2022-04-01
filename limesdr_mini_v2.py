#!/usr/bin/env python3

#
# This file is part of LiteX-LimeSDR-Mini-V2 project.
#
# Copyright (c) 2022 Florent Kermarrec <florent@enjoy-digital.fr>
# SPDX-License-Identifier: BSD-2-Clause

# Build/Use:
# ./limesdr_mini_v2.py --build --load
# litex_term jtag --jtag-config=openocd_limesdr_mini_v2.cfg

from migen import *

import limesdr_mini_v2_platform as limesdr_mini_v2

from litex.build.lattice.trellis import trellis_args, trellis_argdict

from litex.soc.cores.clock import *
from litex.soc.interconnect.csr import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *
from litex.soc.cores.led import LedChaser
from litex.soc.cores.bitbang import I2CMaster

# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.rst = Signal()
        self.clock_domains.cd_sys = ClockDomain()

        # # #

        # Clk.
        clk40 = platform.request("clk40")

        # PLL.
        self.submodules.pll = pll = ECP5PLL()
        self.comb += pll.reset.eq(self.rst)
        pll.register_clkin(clk40, 40e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)

# BoardInfo ----------------------------------------------------------------------------------------

class BoardInfo(Module, AutoCSR):
    def __init__(self, revision_pads):
        self.revision = CSRStorage(fields=[
            CSRField("hardware", size=4, description="Hardware Revision."),
            CSRField("bom",      size=4, description="Bill of Material Revision."),
        ])

        # # #

        self.comb += self.revision.fields.hardware.eq(revision_pads.hardware)
        self.comb += self.revision.fields.bom     .eq(revision_pads.bom)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=int(80e6), toolchain="trellis", with_led_chaser=True, **kwargs):
        platform = limesdr_mini_v2.Platform(toolchain=toolchain)

        # SoCCore -----------------------------------------_----------------------------------------
        kwargs["uart_name"] = "jtag_uart"
        SoCCore.__init__(self, platform, sys_clk_freq, ident="LiteX SoC on LimeSDR-Mini-V2", **kwargs)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq)

        # Info -------------------------------------------------------------------------------------
        self.submodules.info = BoardInfo(platform.request("revision"))

        # I2C Bus ----------------------------------------------------------------------------------
        # - Temperature Sensor (LM72   @ 0x48).
        # - Eeprom             (M24128 @ 0x50) / Not populated.
        self.submodules.i2c = I2CMaster(platform.request("i2c"))

        # Leds -------------------------------------------------------------------------------------
        if with_led_chaser:
            leds_g = Signal(4)
            leds_r = Signal(4)
            self.comb += platform.request_all("led_g_n").eq(~leds_g)
            self.comb += platform.request_all("led_r_n").eq(~leds_r)
            self.submodules.leds = LedChaser(Cat(leds_g, leds_r), sys_clk_freq)

# Build --------------------------------------------------------------------------------------------

def main():
    from litex.soc.integration.soc import LiteXSoCArgumentParser
    parser = LiteXSoCArgumentParser(description="LiteX SoC on LimeSDR-Mini-V2")
    target_group = parser.add_argument_group(title="Target options")
    target_group.add_argument("--build",        action="store_true", help="Build bitstream.")
    target_group.add_argument("--load",         action="store_true", help="Load bitstream.")
    target_group.add_argument("--toolchain",    default="trellis",   help="FPGA toolchain (trellis or diamond).")
    target_group.add_argument("--sys-clk-freq", default=80e6,        help="System clock frequency.")
    builder_args(parser)
    soc_core_args(parser)
    trellis_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(
        sys_clk_freq = int(float(args.sys_clk_freq)),
        toolchain    = args.toolchain,
        **soc_core_argdict(args)
    )
    builder = Builder(soc, **builder_argdict(args))
    builder_kargs = trellis_argdict(args) if args.toolchain == "trellis" else {}
    builder.build(**builder_kargs, run=args.build)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram", ext=".svf")) # FIXME

if __name__ == "__main__":
    main()
