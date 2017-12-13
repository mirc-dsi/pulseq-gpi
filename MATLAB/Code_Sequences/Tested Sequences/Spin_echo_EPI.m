%% This file demonstrates the generation of a .seq file and corresponding toppe files for GE impl.
% Author: Sneha Potdar
% Date: 17th July 2017
%% File Location 
Pulseq = uigetdir('Pick your Pulseq source code directory');
Pulseq = [Pulseq,'/.'];
addpath(genpath('.'));
addpath(genpath(Pulseq));
os = 'pc';
%% Set system limits
seq=mr.Sequence();              % Create a new sequence object
fov=220e-3; Nx=128; Ny=128;     % Define FOV and resolution
TE=200e-3;                       % 70 ms, 200ms for 64 and 500 ms and 120 ms for 96
TR=1000e-3;
dt_GE = 4e-6; %seconds
system = mr.opts('MaxGrad',33,'GradUnit','mT/m',...
    'MaxSlew',110,'SlewUnit','T/m/s','ADCdeadtime',10e-6,...
    'RFdeadTime',10e-6,'ADCdeadTime',10e-6);  
%% Create 90 degree slice selection pulse and gradient
[rf, gz] = mr.makeSincPulse(pi/2,system,'Duration',2.5e-3,...
    'SliceThickness',3e-3,'apodization',0.5,'timeBwProduct',4);

%% Define other gradients and ADC events
deltak=1/fov;
kWidth = Nx*deltak;
readoutTime = Nx*dt_GE;  % Nx*dwelltime, here dwelltime is kept as 4e-6
gx = mr.makeTrapezoid('x',system,'FlatArea',kWidth,'FlatTime',readoutTime);
Nx = ceil(gx.flatTime/dt_GE); %to ensure adc dwell time is considered
adc=mr.makeAdc(Nx, 'Dwell', dt_GE, 'Delay',gx.riseTime) ; % This is to ensure dt of 4e-6, number of readout points increase through - harmless but for BW

%%  Pre-phasing gradients
preTime=8e-4;
gxPre = mr.makeTrapezoid('x',system,'Area',gx.area/2-deltak/2,'Duration',preTime);
gzReph = mr.makeTrapezoid('z',system,'Area',-gz.area/2,'Duration',preTime);
gyPre = mr.makeTrapezoid('y',system,'Area',Ny/2*deltak,'Duration',preTime);

%% Phase blip in shortest possible time
dur = ceil(2*sqrt(deltak/system.maxSlew)/10e-6)*10e-6;
gy = mr.makeTrapezoid('y',system,'Area',deltak,'Duration',dur);

%% Refocusing pulse with spoiling gradients
rf180 = mr.makeBlockPulse(pi,system,'Duration',2.5e-3);
gzSpoil = mr.makeTrapezoid('z',system,'Area',gz.area*2,'Duration',3*preTime);

%% Calculate delay time
durationToCenter = (Nx/2+0.5)*mr.calcDuration(gx) + Ny/2*mr.calcDuration(gy);
delayTE1=TE/2 - mr.calcDuration(gz)/2 - preTime - mr.calcDuration(gzSpoil) - mr.calcDuration(rf180)/2;
delayTE2=TE/2 - mr.calcDuration(rf180)/2 - mr.calcDuration(gzSpoil) - durationToCenter;

%% Define sequence blocks
Averages =4;
for S=1:Averages
seq.addBlock(rf,gz);
seq.addBlock(gxPre,gyPre,gzReph);
seq.addBlock(mr.makeDelay(delayTE1));
seq.addBlock(gzSpoil);
seq.addBlock(rf180);
seq.addBlock(gzSpoil);
seq.addBlock(mr.makeDelay(delayTE2));
for i=1:Ny
    seq.addBlock(gx,adc);           % Read one line of k-space
    seq.addBlock(gy);               % Phase blip
    gx.amplitude = -gx.amplitude;   % Reverse polarity of read gradient
end
seq.addBlock(mr.makeDelay(1));
 end
%%
seq.plot('TimeRange',[0 TR]);

%% 
fname = [date,'SE-EPI_Pulseq.seq'];
seq.write(fname);


