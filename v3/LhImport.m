function Lhdata= LhImport(fileName)
%LhImport import the Lh data from .txt file to matlab workspace
%   the first line of Lh.txt file is the header
%   the format of the Lh.txt file should be three columes:
%   the 1st colume (spaces) 2nd colume (spaces) 3rd colume 
%   the runPyMain fuction in abaqusSimu automatically gives Lh file with
%   three columes, if the Lh data to be imported is from experiment, then a
%   arbitrary number should be given to 1st colume artificially 

LhfileToRead = [fileName,'.txt'];


[timeStep,dispp,load] = textread(LhfileToRead,'%f %f %f ',-1 ,'headerlines', 1);
temp = find(abs(load)<1e-4);
timeStep(temp(2:end))=[];
dispp(temp(2:end))=[];
load(temp(2:end))=[];

Lhdata = [-dispp,-load];   
end

