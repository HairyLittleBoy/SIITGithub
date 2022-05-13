classdef material
    %MATERIAL 此处显示有关此类的摘要
    %   此处显示详细说明
    
    properties (Access = private)
        elasticModulus
        poissionRatio
        strsPlstrn
    end
    
    methods
        function obj = material(E,niu,sPs)
            obj.elasticModulus = E;
            obj.poissionRatio = niu;
            obj.strsPlstrn = sPs;
        end
        
        function outputArg = method1(obj,inputArg)
            %METHOD1 此处显示有关此方法的摘要
            %   此处显示详细说明
            outputArg = obj.Property1 + inputArg;
        end
    end
end

