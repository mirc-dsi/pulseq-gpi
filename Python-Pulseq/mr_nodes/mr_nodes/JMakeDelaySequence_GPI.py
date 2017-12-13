import gpi


class ExternalNode(gpi.NodeAPI):
    """This Node provides allows the user to make a DelaySequence for Jemris."""

    def initUI(self):
        # Widgets
        self.delay_labels = ['Name', 'Observe', 'ADCs', 'Aux1', 'Aux2', 'Aux3', 'Delay', 'DelayType', 'HardwareMode',
                             'PhaseLock', 'StartSeq', 'StopSeq', 'Vector']
        [self.addWidget('StringBox', label) for label in self.delay_labels]
        self.addWidget('PushButton', 'ComputeEvents', button_title="Compute events")

        # IO Ports
        self.addOutPort('DelaySequence', 'LIST')

        return 0

    def compute(self):
        if 'ComputeEvents' in self.widgetEvents() or '_INIT_EVENT_' in self.getEvents():
            delay_seq = {'DelaySequence': True}
            for label in self.delay_labels:
                if self.getVal(label) != '':
                    delay_seq[label] = self.getVal(label)
            self.setData('DelaySequence', [delay_seq])

        return 0
