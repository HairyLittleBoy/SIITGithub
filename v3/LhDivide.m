function [ Lhloading, Lhunloading ] = LhDivide( LhCurveMatrix )
% this function divide the Lh curve into loading and unloading parts

% the input "LhCurveMatrix" is a matrix whose first colume is the
% penetration and the second is load
LhCurveMatrixU = unique(LhCurveMatrix,'rows','stable');
[~,peakloadloc] = max(LhCurveMatrixU(:,2));
Lhloading = LhCurveMatrixU(1:peakloadloc,:);
Lhunloading = LhCurveMatrixU(peakloadloc:end,:);

end

