import gpi


class ExternalNode(gpi.NodeAPI):
    """This Node allows the user to make a ConcatSequence for Jemris."""

    def initUI(self):
        self.parameters = ['Name', 'Observe', 'Aux1', 'Aux2', 'Aux3', 'HardwareMode', 'Repetitions', 'Vector']

        # Widgets
        [self.addWidget('StringBox', label) for label in self.parameters]
        self.addWidget('PushButton', 'ComputeEvents', button_title="Compute events")

        # IO Ports
        # List of port names so that it is easier to get data from ports
        self.input_ports = ['Seq1', 'Seq2', 'Seq3', 'Seq4', 'Seq5', 'Seq6']
        [self.addInPort(port, 'LIST', obligation=gpi.OPTIONAL) for port in self.input_ports]

        self.addOutPort('ConcatSequence Children', 'LIST')

        return 0

    def compute(self):
        if 'ComputeEvents' in self.widgetEvents() or 'input' in self.portEvents():
            # concat_seq_children is a list of ConcatSequence/ AtomicSequence parameters_params making up this
            # ConcatSequence. It is easier to get data from ports
            concat_seq_children = []
            for port in self.input_ports:
                # Port data will be None if no input is supplied
                if self.getData(port) is not None:
                    concat_seq_children.append(self.getData(port))
            concat_params = dict(zip(self.parameters, [self.getVal(label) for label in self.parameters]))
            self.setData('ConcatSequence Children', [concat_params, concat_seq_children])

        return 0
