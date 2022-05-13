function imprintProfile = imprtImport(fileName)
%imprtImport import the imprint profile from imprintProfile.txt
%   the 1st row is the header
%   the format of imprintProfile.txt is 4 comlumes:
%   initialCoordListX(spaces)initialCoordListY(spaces)finalCoordListX(spaces)finalCoordListY

ImprtfileToRead = [fileName,'.txt'];
[initialCoordListX,initialCoordListY,finalCoordListX,finalCoordListY] = ...
    textread(ImprtfileToRead,'%f %f %f %f',-1 ,'headerlines', 1);
imprintProfile.InitlCoord = [initialCoordListX, initialCoordListY];
imprintProfile.FinlCoord = [finalCoordListX, finalCoordListY];
end

