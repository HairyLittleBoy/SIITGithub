function [ bestYN ,localYN, lnrCoef, errorOpt] = LOFMethod(sphrIndenObj,LhExpObj,numOfLocal,maxIterOpt,MatParaIni)
%LOFMethod identify the Y and N in power law with LOF method
%   sphrIndenObj: obj of sphrInden class
%   LhExpObj: obj of LhCurve class
%   numOfLocal: num Of Local domains
%   maxIter: maxIter in optimization
%   MatParaIni: initial guess of Y and N
Nlocal = linspace(0.8*MatParaIni(2),1.25*MatParaIni(2),numOfLocal);
errorOpt = zeros(numOfLocal,1);
numInLocal = 10;
for i = 1:length(Nlocal)
    nfix = Nlocal(i);
    sp = [MatParaIni(1), nfix,];
    lb = [0.2*MatParaIni(1), 0.8*nfix,];
    ub = [5*MatParaIni(1), 1.25*nfix,];
    
    options = optimset('Algorithm','interior-point','Disp','iter','MaxIter', maxIterOpt);
    problem = createOptimProblem('fmincon','objective',@(x)errorLh( x, sphrIndenObj, LhExpObj),'x0',sp,...
        'lb',lb,'ub',ub,'options',options);
    ms = MultiStart;
    ms.UseParallel = 'always';
    [x,funcValue] = run(ms,problem,numInLocal);
    
    localYN.YOpt(i) = x(1);
    localYN.nOpt(i) = x(2); 
    errorOpt(i) = funcValue;
    disp(['the ',num2str(i),'th local domain is done'])
end
ft = fittype( 'poly2' );
[fitresult, ~] = fit( localYN.nOpt', errorOpt, ft );
bestYN.nBest = (-fitresult.p2/2/fitresult.p1);
if fitresult.p1<0 
    bestYN.nBest = min(localYN.nOpt);
end

[fitresult, ~] = fit( localYN.YOpt', errorOpt, ft );
bestYN.YBest = -fitresult.p2/2/fitresult.p1;
if fitresult.p1<0
    bestYN.YBest = min(localYN.YOpt);
end

% ----------------------------------------------------------------
ft = fittype( 'poly1' );
[rlt, ~] = fit( localYN.nOpt', localYN.YOpt', ft );
lnrCoef.p1 = rlt.p1;
lnrCoef.p2 = rlt.p2;
if bestYN.nBest<min(localYN.nOpt)
    [~,Np] = min(errorOpt);
    Nlocal = linspace(0.5*localYN.nOpt(Np),1.5*localYN.nOpt(Np),numOfLocal);
    Ylocal = rlt.p1.*Nlocal+rlt.p2;
elseif bestYN.nBest>max(localYN.nOpt)
    [~,Np] = min(errorOpt);
    Nlocal = linspace(0.6*localYN.nOpt(Np),2*localYN.nOpt(Np),numOfLocal);
    Ylocal = rlt.p1.*Nlocal+rlt.p2;
else
    Ylocal = rlt.p1.*Nlocal+rlt.p2;
end


sphrIndenObj.LhGenrMethod = 'FEM';
parfor i = 1:20
    errorOpt(i) = errorPower( [Ylocal(i),Nlocal(i)], sphrIndenObj, LhExpObj);
end
% localYN.YOpt = Ylocal;
% localYN.nOpt = Nlocal;
bestYNtry.YBest = Ylocal(find(errorOpt==min(errorOpt)));
bestYNtry.nBest = Nlocal(find(errorOpt==min(errorOpt)));

options = optimoptions('patternsearch');
options = optimoptions(options,'AccelerateMesh', true);
options = optimoptions(options,'UseCompletePoll', true);
options = optimoptions(options,'UseCompleteSearch', true);
options = optimoptions(options,'Display', 'Iter');
options = optimoptions(options,'UseVectorized', false);
options = optimoptions(options,'UseParallel', true);
options = optimoptions(options,'MaxFunctionEvaluations',50);

Aeq = [-1,rlt.p1];
beq=-rlt.p2;
lb = [Ylocal(end),Nlocal(1)];
ub = [Ylocal(1),Nlocal(end)];
sp = [bestYNtry.YBest,bestYNtry.nBest];
[x,fval,~,~] = patternsearch(@(x)errorLh( x, sphrIndenObj, LhExpObj),sp, ...
                  [],[],Aeq,beq,lb,ub,[],options);

bestYN.YBest = x(1);  
bestYN.nBest = x(2); 
errorOpt = fval;

end

