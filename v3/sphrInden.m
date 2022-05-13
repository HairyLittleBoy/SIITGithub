classdef sphrInden < abaqusSimu
    %sphrInden generate Lh curve with interpolation, ANN and FEM methods
    %   
    
    properties 
        LhGenrMethod
    end
    
    methods
        function obj = sphrInden(mlPs,niu,indenterR,penetration,miu,cpuNum,meshSizeCoef,method)
            obj = obj@abaqusSimu(mlPs,niu,indenterR,penetration,miu,cpuNum,meshSizeCoef);
            obj.LhGenrMethod = method;
        end

% ----- LhPrdctWthAnn       
        function [ LhAnn ] = LhCalcAnn(obj)
            % predict Lh with ANN based on power law model
            % indenterR: indenter radius in mm
            netRand1 = randperm(100,2);
            netRand2 = randperm(400,2);
            
            netPath = 'E:\MyPapers\MyMatlabFuncs\SIITPowerLaw\MatLabMatFiles\PrLawNets\';
            
            for i=1:length(netRand1)
                numNet1 = netRand1(i);
                
                load([netPath,'nets_fp1_hdn10_',num2str(numNet1)])
                load([netPath,'nets_fp2_hdn10_',num2str(numNet1)])
                load([netPath,'nets_fp3_hdn10_',num2str(numNet1)])
                load([netPath,'nets_fp4_hdn10_',num2str(numNet1)])
                load([netPath,'nets_fp5_hdn10_',num2str(numNet1)])
                load([netPath,'nets_fp1_hdn40_',num2str(numNet1)])
                load([netPath,'nets_fp2_hdn40_',num2str(numNet1)])
                load([netPath,'nets_fp3_hdn40_',num2str(numNet1)])
                load([netPath,'nets_fp4_hdn40_',num2str(numNet1)])
                load([netPath,'nets_fp5_hdn40_',num2str(numNet1)])
            end
            for i=1:length(netRand2)
                numNet2 = netRand2(i);
                load([netPath,'nets_fp1_hdn30_',num2str(numNet2)])
                load([netPath,'nets_fp2_hdn30_',num2str(numNet2)])
                load([netPath,'nets_fp3_hdn30_',num2str(numNet2)])
                load([netPath,'nets_fp4_hdn30_',num2str(numNet2)])
                load([netPath,'nets_fp5_hdn30_',num2str(numNet2)])
                load([netPath,'nets_fp1_hdn20_',num2str(numNet2)])
                load([netPath,'nets_fp2_hdn20_',num2str(numNet2)])
                load([netPath,'nets_fp3_hdn20_',num2str(numNet2)])
                load([netPath,'nets_fp4_hdn20_',num2str(numNet2)])
                load([netPath,'nets_fp5_hdn20_',num2str(numNet2)])
                
            end
            
            
            fp1Total = 0;
            fp2Total = 0;
            fp3Total = 0;
            fp4Total = 0;
            fp5Total = 0;
            x3 = [obj.modelParas(1)/obj.modelParas(2);obj.modelParas(3)];
            numNN = 1000;               % 用4次多项式拟合h/R-pm曲线，系数作为神经网络的输出。
            % 为了提高神经网络的泛化能力，预测每个系数用1000个小网络
            
            for i = 1:length(netRand1)
                numNet1 = netRand1(i);
                eval(['net1i = nets_fp1_hdn10_',num2str(numNet1),';'])
                eval(['net2i = nets_fp2_hdn10_',num2str(numNet1),';'])
                eval(['net3i = nets_fp3_hdn10_',num2str(numNet1),';'])
                eval(['net4i = nets_fp4_hdn10_',num2str(numNet1),';'])
                eval(['net5i = nets_fp5_hdn10_',num2str(numNet1),';'])
                
                fp1 = net1i(x3);
                fp2 = net2i(x3);
                fp3 = net3i(x3);
                fp4 = net4i(x3);
                fp5 = net5i(x3);
                
                fp1Total = fp1Total + fp1;
                fp2Total = fp2Total + fp2;
                fp3Total = fp3Total + fp3;
                fp4Total = fp4Total + fp4;
                fp5Total = fp5Total + fp5;
            end
            
            for i = 1:length(netRand2)
                numNet2 = netRand2(i);
                eval(['net1i = nets_fp1_hdn30_',num2str(numNet2),';'])
                eval(['net2i = nets_fp2_hdn30_',num2str(numNet2),';'])
                eval(['net3i = nets_fp3_hdn30_',num2str(numNet2),';'])
                eval(['net4i = nets_fp4_hdn30_',num2str(numNet2),';'])
                eval(['net5i = nets_fp5_hdn30_',num2str(numNet2),';'])
                
                fp1 = net1i(x3);
                fp2 = net2i(x3);
                fp3 = net3i(x3);
                fp4 = net4i(x3);
                fp5 = net5i(x3);
                
                fp1Total = fp1Total + fp1;
                fp2Total = fp2Total + fp2;
                fp3Total = fp3Total + fp3;
                fp4Total = fp4Total + fp4;
                fp5Total = fp5Total + fp5;
                
            end
                        
            for i = 1:length(netRand2)
                numNet2 = netRand2(i);
                eval(['net1i = nets_fp1_hdn20_',num2str(numNet2),';'])
                eval(['net2i = nets_fp2_hdn20_',num2str(numNet2),';'])
                eval(['net3i = nets_fp3_hdn20_',num2str(numNet2),';'])
                eval(['net4i = nets_fp4_hdn20_',num2str(numNet2),';'])
                eval(['net5i = nets_fp5_hdn20_',num2str(numNet2),';'])
                
                
                fp1 = net1i(x3);
                fp2 = net2i(x3);
                fp3 = net3i(x3);
                fp4 = net4i(x3);
                fp5 = net5i(x3);
                
                fp1Total = fp1Total + fp1;
                fp2Total = fp2Total + fp2;
                fp3Total = fp3Total + fp3;
                fp4Total = fp4Total + fp4;
                fp5Total = fp5Total + fp5;
            end
            for i = 1:length(netRand1)
                numNet1 = netRand1(i);
                
                eval(['net1i = nets_fp1_hdn40_',num2str(numNet1),';'])
                eval(['net2i = nets_fp2_hdn40_',num2str(numNet1),';'])
                eval(['net3i = nets_fp3_hdn40_',num2str(numNet1),';'])
                eval(['net4i = nets_fp4_hdn40_',num2str(numNet1),';'])
                eval(['net5i = nets_fp5_hdn40_',num2str(numNet1),';'])
                
                fp1 = net1i(x3);
                fp2 = net2i(x3);
                fp3 = net3i(x3);
                fp4 = net4i(x3);
                fp5 = net5i(x3);
                
                fp1Total = fp1Total + fp1;
                fp2Total = fp2Total + fp2;
                fp3Total = fp3Total + fp3;
                fp4Total = fp4Total + fp4;
                fp5Total = fp5Total + fp5;
                
            end
            fpAverageOutput(1) = fp1Total / (2*length(netRand1)+2*length(netRand2));
            fpAverageOutput(2) = fp2Total / (2*length(netRand1)+2*length(netRand2));
            fpAverageOutput(3) = fp3Total / (2*length(netRand1)+2*length(netRand2));
            fpAverageOutput(4) = fp4Total / (2*length(netRand1)+2*length(netRand2));
            fpAverageOutput(5) = fp5Total / (2*length(netRand1)+2*length(netRand2));
                       
            pm(:,1) = linspace(0,0.3,1000);
            pm(:,2) = fpAverageOutput(1).*pm(:,1).^4 + fpAverageOutput(2).*pm(:,1).^3 + ...
                fpAverageOutput(3).*pm(:,1).^2 + fpAverageOutput(4).*pm(:,1) + ...
                fpAverageOutput(5);
            LhAnn(:,1) = pm(:,1).*obj.indenterR;
            LhAnn(:,2) = (obj.modelParas(2)/200).*pm(:,2).*pi.*(obj.indenterR^2 - (obj.indenterR - LhAnn(:,1)).^2);  %在神经网络的训练中，输入是
            %[E/Y,N],而Y被设定为200MPa
            %所以这里要比上200
        end

% ----- LhCalcNumr
        function LhNumr = LhCalcNumr( obj )
            % this function use E, Y, N, R to predict Lh curve，
            % with pm=p1_dim*(a/R)^3+p2_dim*(a/R)^2+p3_dim*(a/R)+p4_dim
            % formula to calculate pm(pm=L/(pi*a^2)),coefficients
            % p1_dim-p4_dim are obtained with FEM and interpolation method
            % it is usually more accurate than ANN
            pene = linspace(0,obj.penetration,1000)';
            EY = obj.modelParas(1)/obj.modelParas(2);
            aR = sqrt(pene.*(2*obj.indenterR-pene))./obj.indenterR;
            
            if length(obj.modelParas) == 3
                load('E:\MyPapers\MyMatlabFuncs\SIITPowerLaw\MatLabMatFiles\p1TOp4PrwLaw.mat', ...
                    'p1_dim','p2_dim','p3_dim','p4_dim');               
                p1_intrp = interp2(XX,YY,p1_dim',obj.modelParas(3),EY,'spline');
                p2_intrp = interp2(XX,YY,p2_dim',obj.modelParas(3),EY,'spline');
                p3_intrp = interp2(XX,YY,p3_dim',obj.modelParas(3),EY,'spline');
                p4_intrp = interp2(XX,YY,p4_dim',obj.modelParas(3),EY,'spline');
                pm_intrp = p1_intrp.*aR.^3+p2_intrp.*aR.^2+p3_intrp.*aR+p4_intrp;
                pm_intrp = pm_intrp.*(obj.modelParas(2)/200);  % 有限元模拟中全部用200MPa为屈服应力，只改变
                % E从而改变E/Y的值，所以这里要用Y/200对pm进行
                % 成倍数缩放
            elseif length(obj.modelParas) == 4          
                AY = obj.modelParas(3)/obj.modelParas(2);
                method = 'interp';
                switch method
                    case 'interp'
                        load('E:\MyPapers\MyMatlabFuncs\SIITPowerLaw\MatLabMatFiles\p1TOp3Voce.mat', ...
                              'p1_dim','p2_dim','p3_dim','XX','YY','ZZ'); 
                        p1_intrp = interp3(XX,YY,ZZ,p1_dim,EY,obj.modelParas(4),AY,'spline');
                        p2_intrp = interp3(XX,YY,ZZ,p2_dim,EY,obj.modelParas(4),AY,'spline');
                        p3_intrp = interp3(XX,YY,ZZ,p3_dim,EY,obj.modelParas(4),AY,'spline');
                        pm_intrp = p1_intrp.*aR.^2+p2_intrp.*aR.^1+p3_intrp;
                        pm_intrp = pm_intrp.*((obj.modelParas(2))/200);
                    case 'Ann'
                        load('E:\MyPapers\MyMatlabFuncs\SIITPowerLaw\MatLabMatFiles\p1TOp3VoceWithAnn.mat', ...
                             'netp1','netp2','netp3')
                        p1_intrp = netp1([obj.modelParas(4);EY;AY]);
                        p2_intrp = netp2([obj.modelParas(4);EY;AY]);
                        p3_intrp = netp3([obj.modelParas(4);EY;AY]);
                        pm_intrp = p1_intrp.*aR.^2+p2_intrp.*aR.^1+p3_intrp;
                        pm_intrp = pm_intrp.*((obj.modelParas(2))/200);                        
                end               
            end
            LhNumr(:,1) = pene';
            LhNumr(:,2) = pm_intrp.*(pi.*aR.^2)./(1/obj.indenterR^2);   % 有限元模拟中全部用R=1mm，所
            % 以这里用1/R^2成倍数缩放

        end
        
% ----- LhGenr
        function Lhdata = LhGenr(obj)
            %LhGenr generate a Lh curve with the method which property 'method'defines
            switch obj.LhGenrMethod
                case 'FEM'
                   jobName = jobNameGenr(obj); % defined in clasee abaqusSimu
                   runPyMain(obj)              % defined in clasee abaqusSimu
                   Lhdata= LhImport(['Lh_',jobName]);
                case 'ANN'
                    Lhdata = LhCalcAnn(obj);
                case 'interp'
                    Lhdata = LhCalcNumr(obj);
            end
        end
    end
end

