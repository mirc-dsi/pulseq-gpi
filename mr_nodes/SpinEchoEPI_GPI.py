from math import pi, ceil, sqrt

import gpi

from mr_gpi.Sequence.sequence import Sequence
from mr_gpi.calcduration import calcduration
from mr_gpi.makeadc import makeadc
from mr_gpi.makeblock import makeblockpulse
from mr_gpi.makedelay import makedelay
from mr_gpi.makesinc import makesincpulse
from mr_gpi.maketrap import maketrapezoid
from mr_gpi.opts import Opts


class ExternalNode(gpi.NodeAPI):
    """
    This Node provides options for setting up the event that needs to be added. Event parameters_params should be set
    to 0 if left unconfigured. Up to 6 simultaneous events can be added in one block. The 'ComputeEvents' button gathers
    the input data into a dict object. The output of this Node (or a chain of AddBlock Nodes) has to be supplied to a
    GenSeq Node.

     Units:
     - duration: s
     - flipAngle : deg
     - flatTime : s
     - riseTime : s
     - dwell : s
     - delay : s
     - sliceThickness : m
     - amplitude : Hz
    """

    def initUI(self):
        # Widgets
        self.addWidget('StringBox', 'Maximum Gradient (mT/m)', placeholder="max_grad")
        self.addWidget('StringBox', 'Maximum Slew Rate (T/m/s)', placeholder="max_slew")
        self.addWidget('StringBox', 'Repetition Time (s)', placeholder="TR")
        self.addWidget('StringBox', 'Echo Time (s)', placeholder="TE")
        self.addWidget('StringBox', 'Field of View', placeholder="fov")
        self.addWidget('StringBox', 'Nx', placeholder="Nx")
        self.addWidget('StringBox', 'Ny', placeholder="Ny")
        self.addWidget('PushButton', 'ComputeEvents', button_title="Compute events")

        # IO Ports
        self.addOutPort('output', 'DICT')

        return 0

    def compute(self):
        if 'ComputeEvents' in self.widgetEvents() or 'input' in self.portEvents():
            self.max_grad = float(self.getVal('Maximum Gradient (mT/m)'))
            self.max_slew = float(self.getVal('Maximum Slew Rate (T/m/s)'))
            self.tr = float(self.getVal('Repetition Time (s)'))
            self.te = float(self.getVal('Echo Time (s)'))
            self.fov = float(self.getVal('Field of View'))
            self.Nx = int(self.getVal('Nx'))
            self.Ny = int(self.getVal('Ny'))
            seq = self.make_se_epi()
            self.setData('output', {'seq': seq})

            return 0

    def make_se_epi(self):
        kwargs_for_opts = {"max_grad": self.max_grad, "grad_unit": "mT/m", "max_slew": self.max_slew,
                           "slew_unit": "T/m/s", "rf_dead_time": 10e-6, "adc_dead_time": 10e-6}
        system = Opts(kwargs_for_opts)
        seq = Sequence(system)

        slice_thickness = 3e-3

        flip = 90 * pi / 180
        kwargs_for_sinc = {"flip_angle": flip, "system": system, "duration": 3e-3, "slice_thickness": slice_thickness,
                           "apodization": 0.5, "time_bw_product": 4}
        rf, gz = makesincpulse(kwargs_for_sinc, 2)
        # plt.plot(rf.t[0], rf.signal[0])
        # plt.show()

        delta_k = 1 / self.fov
        k_width = self.Nx * delta_k
        readout_time = 3.2e-4
        kwargs_for_gx = {"channel": 'x', "system": system, "flat_area": k_width, "flat_time": readout_time}
        gx = maketrapezoid(kwargs_for_gx)
        kwargs_for_adc = {"num_samples": self.Nx, "system": system, "duration": gx.flat_time, "delay": gx.rise_time}
        adc = makeadc(kwargs_for_adc)

        pre_time = 8e-4
        kwargs_for_gxpre = {"channel": 'x', "system": system, "area": -gx.area / 2, "duration": pre_time}
        gx_pre = maketrapezoid(kwargs_for_gxpre)
        kwargs_for_gz_reph = {"channel": 'z', "system": system, "area": -gz.area / 2, "duration": pre_time}
        gz_reph = maketrapezoid(kwargs_for_gz_reph)
        kwargs_for_gy_pre = {"channel": 'y', "system": system, "area": -self.Ny / 2 * delta_k, "duration": pre_time}
        gy_pre = maketrapezoid(kwargs_for_gy_pre)

        dur = ceil(2 * sqrt(delta_k / system.max_slew) / 10e-6) * 10e-6
        kwargs_for_gy = {"channel": 'y', "system": system, "area": delta_k, "duration": dur}
        gy = maketrapezoid(kwargs_for_gy)

        flip = 180 * pi / 180
        kwargs_for_sinc = {"flip_angle": flip, "system": system, "duration": 500e-6}
        rf180 = makeblockpulse(kwargs_for_sinc)
        kwargs_for_gz_spoil = {"channel": 'z', "system": system, "area": gz.area * 2, "duration": 3 * pre_time}
        gz_spoil = maketrapezoid(kwargs_for_gz_spoil)

        TE = self.te
        duration_to_center = (self.Nx / 2 + 0.5) * calcduration(gx) + self.Ny / 2 * calcduration(gy)
        delayTE1 = TE / 2 - calcduration(gz) / 2 - pre_time - calcduration(gz_spoil) - calcduration(rf180) / 2
        delayTE2 = TE / 2 - calcduration(rf180) / 2 - calcduration(gz_spoil) - duration_to_center
        delay1 = makedelay(delayTE1)
        delay2 = makedelay(delayTE2)

        seq.add_block(rf, gz)
        seq.add_block(gx_pre, gy_pre, gz_reph)
        seq.add_block(delay1)
        seq.add_block(gz_spoil)
        seq.add_block(rf180)
        seq.add_block(gz_spoil)
        seq.add_block(delay2)
        for i in range(self.Ny):
            seq.add_block(gx, adc)
            seq.add_block(gy)
            gx.amplitude = -gx.amplitude
        seq.add_block(makedelay(1))

        return seq
