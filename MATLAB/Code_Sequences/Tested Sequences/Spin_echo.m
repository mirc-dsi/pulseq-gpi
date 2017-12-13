%% This file demonstrates the generation of a .seq file and corresponding toppe files for GE impl.
% Author: Sneha Potdar
% Date: 17th July 2017
%% File Location 
Pulseq = uigetdir('Pick your Pulseq source code directory');
Pulseq = [Pulseq,'/.'];
addpath(genpath('.'));
addpath(genpath(Pulseq));
os = 'pc';
%% System limits
seq=mr.Sequence();
fov=256e-3;
Nx=256; Ny=256;
TE=100e-3;
TR=2000e-3;
dt_GE = 4e-6; %seconds
system = mr.opts('MaxGrad',33,'GradUnit','mT/m',...
        'MaxSlew',100,'SlewUnit','T/m/s','ADCdeadtime',10e-6,...
        'RFdeadTime',10e-6);

%% Implementation of RF 90 degree pulse and Gz slice selelction
deltak=1/fov;
kWidth = Nx*deltak;
readoutTime = Nx*dt_GE;  % Nx*dwelltime, here dwelltime is kept as 4e-6
[rf, gz] = mr.makeSincPulse(pi/2,system,'Duration',2.5e-3,...
    'SliceThickness',3e-3,'apodization',0.5,'timeBwProduct',4);

%% Implementation of Gx Frequency encoding, ADC
gx = mr.makeTrapezoid('x',system,'FlatArea',kWidth,'FlatTime',readoutTime);
adc = mr.makeAdc(Nx,system,'Duration',gx.flatTime,'Delay',gx.riseTime);

%% Implementation of GxPre, GzReph
% gxPre = mr.makeTrapezoid('x',system,'Area',gx.area/2,'Duration',readoutTime./2);
gxPre = mr.makeTrapezoid('x',system,'Area',-gx.area/2,'Duration',2.5e-3);
gzReph = mr.makeTrapezoid('z',system,'Area',-gz.area/2,'Duration',2.5e-3);

%% Implementation of RF180 degree, Gz180 slice selelction
[rf180, gz180] = mr.makeSincPulse(pi,system,'Duration',2.5e-3,...
  'SliceThickness',3e-3,'apodization',0.5,'timeBwProduct',4);

%% Calculating Delays
delayTE1=TE/2-mr.calcDuration(gzReph)-mr.calcDuration(rf)- mr.calcDuration(rf180)/2;
delayTE2=TE/2-mr.calcDuration(gx)./2-mr.calcDuration(rf180)/2;
delayTE3=TR-TE-mr.calcDuration(gx);

%%
phaseAreas = ((0:Ny-1)-Ny/2)*deltak;
for i=1:Ny
    seq.addBlock(rf,gz);
    gyPre = mr.makeTrapezoid('y',system,'Area',phaseAreas(i),'Duration',2.5e-3);
    seq.addBlock(gxPre,gyPre,gzReph);
    seq.addBlock(mr.makeDelay(delayTE1));
    seq.addBlock(rf180,gz180);
    seq.addBlock(mr.makeDelay(delayTE2));
    seq.addBlock(gx,adc);
    seq.addBlock(mr.makeDelay(delayTE3));
end
%%
seq.plot('TimeRange',[0 TR]);
fname = [date,'SE Pulseq.seq'];
seq.write(fname);
