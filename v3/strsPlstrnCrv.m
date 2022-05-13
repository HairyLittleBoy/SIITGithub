classdef strsPlstrnCrv
    %STRSPLSTRNCRV 此处显示有关此类的摘要
    %   此处显示详细说明
    
    properties 
        modelParas 
    end
    
    methods
        function obj = strsPlstrnCrv(mlPs)
            obj.modelParas = mlPs;
        end
        
        function strsPlstrnPoints = strsPlstrnPower(obj)
            if length(obj.modelParas) ~= 3
                error('the length of modelParas is not matched ')
            else
            strsPlstrnPoints(:,1) = linspace(0,1,400);            
            disp( 'power law model:[E,Y,n]')
            strsPlstrnPoints(:,2) = obj.modelParas(2).*(1+obj.modelParas(1) ...
                /obj.modelParas(2).*strsPlstrnPoints(:,1)).^obj.modelParas(3);
            end
        end
        
        function strsPlstrnPoints = strsPlstrnVoce(obj)
            if length(obj.modelParas) ~= 4
                error('the length of modelParas is not matched ')
            else
            strsPlstrnPoints(:,1) = linspace(0,1,400);
            disp('voce model:[E,Y,A,m]')
            strsPlstrnPoints(:,2) = obj.modelParas(2)+ ...
                obj.modelParas(3).*(1-exp(-obj.modelParas(4).*strsPlstrnPoints(:,1)));
            end
        end
    end
end

