classdef material
    %MATERIAL �˴���ʾ�йش����ժҪ
    %   �˴���ʾ��ϸ˵��
    
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
            %METHOD1 �˴���ʾ�йش˷�����ժҪ
            %   �˴���ʾ��ϸ˵��
            outputArg = obj.Property1 + inputArg;
        end
    end
end

