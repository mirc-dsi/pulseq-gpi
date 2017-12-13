import numpy as np

from mr_gpi.holder import Holder
from mr_gpi.maketrap import maketrapezoid
from mr_gpi.opts import Opts


def makesincpulse(kwargs, nargout=1):
    """
    Makes a Holder object for an RF pulse Event.

    Parameters
    ----------
    kwargs : dict
        Key value mappings of RF Event parameters_params and values.
    nargout: int
        Number of output arguments to be returned. Default is 1, only RF Event is returned. Passing any number greater
        than 1 will return the Gz Event along with the RF Event.

    Returns
    -------
    Tuple consisting of:
    rf : Holder
        RF Event configured based on supplied kwargs.
    gz : Holder
        Slice select trapezoidal gradient Event.
    """

    flip_angle = kwargs.get("flip_angle")
    system = kwargs.get("system", Opts())
    duration = kwargs.get("duration", 0)
    freq_offset = kwargs.get("freq_offset", 0)
    phase_offset = kwargs.get("phase_offset", 0)
    time_bw_product = kwargs.get("time_bw_product", 4)
    apodization = kwargs.get("apodization", 0)
    max_grad = kwargs.get("max_grad", 0)
    max_slew = kwargs.get("max_slew", 0)
    slice_thickness = kwargs.get("slice_thickness", 0)

    BW = time_bw_product / duration
    alpha = apodization
    N = int(round(duration / 1e-6))
    t = np.zeros((1, N))
    for x in range(1, N + 1):
        t[0][x - 1] = x * system.rf_raster_time
    tt = t - (duration / 2)
    window = np.zeros((1, tt.shape[1]))
    for x in range(0, tt.shape[1]):
        window[0][x] = 1.0 - alpha + alpha * np.cos(2 * np.pi * tt[0][x] / duration)
    signal = np.multiply(window, np.sinc(BW * tt))
    flip = np.sum(signal) * system.rf_raster_time * 2 * np.pi
    signal = signal * flip_angle / flip

    rf = Holder()
    rf.type = 'rf'
    rf.signal = signal
    rf.t = t
    rf.freq_offset = freq_offset
    rf.phase_offset = phase_offset
    rf.dead_time = system.rf_dead_time

    fill_time = 0
    if nargout > 1:
        if slice_thickness == 0:
            raise ValueError('Slice thickness must be provided')

        system.max_grad = max_grad if max_grad > 0 else system.max_grad
        system.max_slew = max_slew if max_slew > 0 else system.max_slew

        amplitude = BW / slice_thickness
        area = amplitude * duration
        kwargs_for_trap = {"channel": 'z', "system": system, "flat_time": duration, "flat_area": area}
        gz = maketrapezoid(kwargs_for_trap)

        fill_time = gz.rise_time
        nfill_time = int(round(fill_time / 1e-6))
        t_fill = np.zeros((1, nfill_time))
        for x in range(1, nfill_time + 1):
            t_fill[0][x - 1] = x * 1e-6
        temp = np.concatenate((t_fill[0], rf.t[0] + t_fill[0][-1]))
        temp = temp.reshape((1, len(temp)))
        rf.t = np.resize(rf.t, temp.shape)
        rf.t[0] = temp
        z = np.zeros((1, t_fill.shape[1]))
        temp2 = np.concatenate((z[0], rf.signal[0]))
        temp2 = temp2.reshape((1, len(temp2)))
        rf.signal = np.resize(rf.signal, temp2.shape)
        rf.signal[0] = temp2

    if fill_time < rf.dead_time:
        fill_time = rf.dead_time - fill_time
        t_fill = np.array([x * 1e-6 for x in range(int(round(fill_time / 1e-6)))])
        rf.t = np.insert(rf.t, 0, t_fill) + t_fill[-1]
        rf.t = np.reshape(rf.t, (1, len(rf.t)))
        rf.signal = np.insert(rf.signal, 0, (np.zeros(t_fill.size)))
        rf.signal = np.reshape(rf.signal, (1, len(rf.signal)))

    # Following 2 lines of code are workarounds for numpy returning 3.14... for np.angle(-0.00...)
    negative_zero_indices = np.where(rf.signal == -0.0)
    rf.signal[negative_zero_indices] = 0

    if nargout > 1:
        return rf, gz
    else:
        return rf
