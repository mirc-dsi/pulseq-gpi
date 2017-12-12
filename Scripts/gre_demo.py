"""
This is starter code to demonstrate a working example of the Gradient Recalled Echo as a pure Python implementation.
"""
from math import pi

import numpy as np

from mr_gpi.Sequence.sequence import Sequence
from mr_gpi.calcduration import calcduration
from mr_gpi.makeadc import makeadc
from mr_gpi.makedelay import makedelay
from mr_gpi.makesinc import makesincpulse
from mr_gpi.maketrap import maketrapezoid
from mr_gpi.opts import Opts

"""
GRE:
flip: 0.2617993877991494
delays: 0.002775, 0.004775
-gx.area/2 = -145.681818
-gz.area/2 = -403
gx.flat_time = 0.0064
gx.rise_time = 1e-5
"""
kwargs_for_opts = {"max_grad": 33, "grad_unit": "mT/m", "max_slew": 100, "slew_unit": "T/m/s"}
system = Opts(kwargs_for_opts)
seq = Sequence(system)

fov = 256e-3
Nx = 256
Ny = 256
slice_thickness = 5e-3

flip = 15 * pi / 180
kwargs_for_sinc = {"flip_angle": flip, "system": system, "duration": 2.5e-3, "slice_thickness": slice_thickness,
                   "apodization": 0.5, "time_bw_product": 4}
rf, gz = makesincpulse(kwargs_for_sinc, 2)
# plt.plot(rf.t[0], rf.signal[0])
# plt.show()

delta_k = 1 / fov
kWidth = Nx * delta_k
readoutTime = 6.4e-3
kwargs_for_gx = {"channel": 'x', "system": system, "flat_area": kWidth, "flat_time": readoutTime}
gx = maketrapezoid(kwargs_for_gx)
kwargs_for_adc = {"num_samples": Nx, "duration": gx.flat_time, "delay": gx.rise_time}
adc = makeadc(kwargs_for_adc)

kwargs_for_gxpre = {"channel": 'x', "system": system, "area": -gx.area / 2, "duration": 2e-3}
gx_pre = maketrapezoid(kwargs_for_gxpre)
kwargs_for_gz_reph = {"channel": 'z', "system": system, "area": -gz.area / 2, "duration": 2e-3}
gz_reph = maketrapezoid(kwargs_for_gz_reph)
phase_areas = np.array(([x for x in range(0, Ny)]))
phase_areas = (phase_areas - Ny / 2) * delta_k

TE, TR = 10e-3, 20e-3
delayTE = TE - calcduration(gx_pre) - calcduration(rf) / 2 - calcduration(gx) / 2
delayTR = TR - calcduration(gx_pre) - calcduration(rf) - calcduration(gx) - delayTE
delay1 = makedelay(delayTE)
delay2 = makedelay(delayTR)

for i in range(Ny):
    seq.add_block(rf, gz)
    kwargsForGyPre = {"channel": 'y', "system": system, "area": phase_areas[i], "duration": 2e-3}
    gyPre = maketrapezoid(kwargsForGyPre)
    seq.add_block(gx_pre, gyPre, gz_reph)
    seq.add_block(delay1)
    seq.add_block(gx, adc)
    seq.add_block(delay2)

# Display 1 TR
seq.plot(time_range=(0, TR))

# Display entire plot
# seq.plot()

# The .seq file will be available inside the /gpi/<user>/pulseq-gpi folder
# seq.write("gre_python.seq")
