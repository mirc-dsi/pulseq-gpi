%% This file demonstrates the generation of a .seq file and corresponding toppe files for GE impl.
% Author: Sairam Geethanath
% Modified: Sneha Potdar
% Date: 24th July 2017
% Latest Modified: Sneha Potdar
% Date: 11th August 2017
%% Add path
Pulseq = uigetdir('Pick your Pulseq source code directory');
Pulseq = [Pulseq,'/.'];
addpath(genpath('.'));
addpath(genpath(Pulseq));
os = 'pc';
%% Provide system parameters
system = mr.opts('MaxGrad',33,'GradUnit','mT/m', 'MaxSlew',100,'SlewUnit','T/m/s');
seq=mr.Sequence(system);
TR = 20e-3; %s 
TE = 10e-3; %s 
fov=256e-3;
Nx=256; Ny=256;
dt_GE = 4e-6; %seconds
sliceThickness=3e-3;  
flip=15*pi/180;
[rf, gz] = mr.makeSincPulse(flip,'system',system,'Duration',2.5e-3,...
    'SliceThickness',sliceThickness,'apodization',0.5,'timeBwProduct',4);

%% Calculate parameters
deltak=1/fov;
kWidth = Nx*deltak;
readoutTime = Nx*dt_GE;  % Nx*dwelltime, here dwelltime is kept as 4e-6
gx = mr.makeTrapezoid('x',system,'FlatArea',kWidth,'FlatTime',readoutTime);
adc=mr.makeAdc(Nx, 'Dwell', dt_GE, 'Delay',gx.riseTime) ; % This is to ensure dt of 4e-6, number of readout points increase through - harmless but for BW
gxPre = mr.makeTrapezoid('x',system,'Area',-gx.area/2,'Duration',2.5e-3);
gzReph = mr.makeTrapezoid('z',system,'Area',-gz.area/2,'Duration',2.5e-3);
phaseAreas = ((0:Ny-1)-Ny/2)*deltak;

%% Calculate delays required
delayTE=TE - mr.calcDuration(gxPre) - mr.calcDuration(rf)/2 ...
    - mr.calcDuration(gx)/2;
delayTR=TR - mr.calcDuration(gxPre) - mr.calcDuration(rf) ...
    - mr.calcDuration(gx) - delayTE;
delay1 = mr.makeDelay(delayTE);
delay2 = mr.makeDelay(delayTR);

%% Play sequence per TR
for i=1:Ny
    seq.addBlock(rf, gz);
    gyPre = mr.makeTrapezoid('y',system,'Area',phaseAreas(i),'Duration',2.5e-3);
    seq.addBlock(gxPre,gyPre,gzReph);
    seq.addBlock(delay1);
    seq.addBlock(gx,adc);
    seq.addBlock(delay2)
end
seq.plot('TimeRange',[0 TR]);
fname = [date,'GRE Pulseq.seq'];
seq.write(fname);
