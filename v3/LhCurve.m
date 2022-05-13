classdef LhCurve
    %LHCURVE 此处显示有关此类的摘要
    %   此处显示详细说明
    
    properties 
        LhPoints
    end

    methods
        function obj = LhCurve(LhP)
            %LhPoints
            %   LhPoints is n x 2 matrix, the 1st colume is penetration in
            %   mm and the 2nd is load in N
            obj.LhPoints = LhP;
        end
        
        function [ Lhloading, Lhunloading ] = LhDivide( obj )
            % divide the Lh curve into loading and unloading parts
            
            % the input "LhCurveMatrix" is a matrix whose first colume is the
            % penetration and the second is load
            LhCurveMatrixU = unique(obj.LhPoints,'rows','stable');
            [~,peakloadloc] = max(LhCurveMatrixU(:,2));
            Lhloading = LhCurveMatrixU(1:peakloadloc,:);
            Lhunloading = LhCurveMatrixU(peakloadloc:end,:);
            
        end
        function elasModu = Pharr(obj)
            %  estimate the elastic modulue the Pharr method
        end
    end
end

