classdef abaqusSimu < strsPlstrnCrv
    % generate L-h curve with abaqus
    %   
    
    properties 
        indenterR
        penetration
        niu        % poission's ratio
        miu       % fricCoef
        cpuNum
        meshSizeCoef
    end
    
    methods
        function obj = abaqusSimu(mlPs,niu,indenterR,penetration,miu,cpuNum,meshSizeCoef)

            obj = obj@strsPlstrnCrv(mlPs);
            obj.niu = niu;
            obj.indenterR = indenterR;
            obj.penetration = penetration;
            obj.miu = miu;
            obj.cpuNum = cpuNum;
            obj.meshSizeCoef = meshSizeCoef;
        end
%% -----jobNameGenr
        function jobName = jobNameGenr(obj)
            % generate the jobName of FEM simulation
            Ename = num2str(obj.modelParas(1)/1000);
            Rname = num2str(obj.indenterR);
            Yname = num2str(obj.modelParas(2),10);
            miuname = num2str(obj.miu);

            Ename(Ename=='.')='p';
            Rname(Rname=='.')='p';
            Yname(Yname=='.')='p';
            miuname(miuname=='.')='p';


            if length(obj.modelParas) == 3
                Nname = num2str(obj.modelParas(3),10);
                Nname(Nname=='.')='p';
                jobName = ['R',Rname,'E',Ename,'Y',Yname,'N',Nname,'fc',miuname];
            elseif length(obj.modelParas) == 4
                Aname = num2str(obj.modelParas(3),10);
                mname = num2str(obj.modelParas(4),10);
                Aname(Aname=='.')='p';
                mname(mname=='.')='p';
                jobName = ['R',Rname,'E',Ename,'Y',Yname,'A',Aname,'m',mname,'fc',miuname];
            end
        end
 %% -----rewrtPyMain
        function rewrtPyMain(obj)
            % write the .py file for abaqus
            
            % rewrtPyMain function write a .py file for abaqus, this .py
            % file is the input of abaqus. It contains three lines like
            % below:
            %
            % from SIIT import *	
            % SIITFEM(indenterR = 0.5,penetration = -0.5, elasModulus = 120000,
            %         poission = 0.3, yiled = 200, hardIndx = 0.1, fricCoef = 0,jobName = 'ppp',
            %         cpuNum = 2,meshSizeCoef = 10)	
            % SIITFEMPost(jobName = 'ppp', indenterR = 0.5)	
            % 
            % the SIIT.py is a python module and SIITFEM and
            % SIITFEMPost are functions inside the module,which conduct the FEM and
            % post pocess the result,outputs the L-h curve and indent
            % profile
            
            jobName = jobNameGenr(obj);
            ElsMdls  =obj.modelParas(1);
            yld = obj.modelParas(2);
            if length(obj.modelParas) == 3
                disp('---mssge from rewrtPyMain: powerlaw model ''sig=yiled*(1.0+E/Y*epsP)**N''')

                hardIndx = obj.modelParas(3);
                % write the pymain script which calls the functions in SIIT
                
                newline{1} = {'from SIIT import *'};
                newline{2} = {['SIITFEM(indenterR = ',num2str(obj.indenterR),',penetration = ', ...
                    num2str(-obj.penetration),', elasModulus = ',num2str(ElsMdls), ...
                    ',poission = ',num2str(obj.niu),', yiled = ',num2str(yld), ...
                    ', hardIndx = ',num2str(hardIndx),', fricCoef = ',num2str(obj.miu), ...
                    ',jobName = ''',jobName,''', cpuNum = ',num2str(obj.cpuNum), ...
                    ',meshSizeCoef = ',num2str(obj.meshSizeCoef),')']};
                newline{3} = {['SIITFEMPost(jobName = ''',jobName,''', indenterR = ',num2str(obj.indenterR),')']};
            elseif length(obj.modelParas) == 4
                disp('---mssge from rewrtPyMain: Voce model ''sig=Y+A*(1.0-exp(-m*epsP))''')
                AVoce = obj.modelParas(3);
                mVoce = obj.modelParas(4);
                newline{1} = {'from SIIT import *'};
                newline{2} = {['SIITFEMVoce(indenterR = ',num2str(obj.indenterR),',penetration = ', ...
                    num2str(-obj.penetration),', elasModulus = ',num2str(ElsMdls), ...
                    ',poission = ',num2str(obj.niu),', yiled = ',num2str(yld), ...
                    ', AVoce = ',num2str(AVoce),', mVoce = ',num2str(mVoce),', fricCoef = ',num2str(obj.miu), ...
                    ',jobName = ''',num2str(jobName),''', cpuNum = ',num2str(obj.cpuNum), ...
                    ',meshSizeCoef = ',num2str(obj.meshSizeCoef),')']};
                newline{3} = {['SIITFEMPost(jobName = ''',jobName,''', indenterR = ',num2str(obj.indenterR),')']};
            else
                error('strs pl strn model is not supported by rewrtPyMain function in abaqusSimu class')
            end
            
            fileID = fopen(['pymain_',jobName,'.py'],'w+');       % create pymain.py in current direction
            for k=1:length(newline)
                fprintf(fileID,'%s\t\n',char(newline{k}));
            end
            fclose(fileID);
            
        end
 %% -----runpyMain
        function runPyMain(obj)
            % run pymain_jobName in abaqus
            
            jobName = jobNameGenr(obj);
            rewrtPyMain(obj);
            
            mkdir(jobName);
            copyfile( 'E:\MyPapers\MyMatlabFuncs\SIITPowerLaw\v3\SIIT.py', jobName);
            copyfile( ['pymain_',jobName,'.py'], jobName,'f');
            cd(jobName);
            
            system(['abaqus cae noGUI=','pymain_',jobName,'.py']);
            cd ..
            movefile( [jobName,'\Lh_',jobName,'.txt'])
            movefile( [jobName,'\UnldSrfNdsCrd_',jobName,'.txt'])
            
            rmdir(jobName,'s');
        end
    end
end









