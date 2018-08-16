#!/usr/bin/env python
import subprocess
import os,sys
import optparse
import commands
import math
import random

#python submitProdCondor.py -o /afs/cern.ch/work/a/amagnan/public/UPSGAna/180804/

usage = 'usage: %prog [options]'
parser = optparse.OptionParser(usage)
parser.add_option('-q', '--queue'  ,    dest='queue'             , help='batch queue'             , default='2nd')
parser.add_option('-o', '--out'         ,    dest='out'                , help='output directory'             , default=os.getcwd() )
parser.add_option('-n', '--numEvts' ,  dest='numEvts'  , help='Number of events to process' , default=0)

parser.add_option('-S', '--no-submit'   ,    action="store_true",  dest='nosubmit'           , help='Do not submit batch job.')
(opt, args) = parser.parse_args()

pulist = ['200PU']

inputlistdir = 'filelists/180716/split/'
#inputlistdir = 'filelists/test/'

#sampleShort=['ST_tch_top']
#bkgshort=['ST_s-channel','ST_tW_antitop','ST_tW_top','TT']

#bkgshort2=['DY1Jets_MLL-50','EWKWMinus2Jets','EWKZ2Jets_ZToLL','EWKZ2Jets_ZToNuNu','W0JetsToLNu','W1JetsToLNu','W3JetsToLNu','ZJetsToNuNu_HT-100To200']
#bkgshort3=['DY3Jets_MLL-50','QCD_Mdijet-1000toInf']
#bkgshort4=['DYJetsToLL_M-50_HT-100to200','DYJetsToLL_M-50_HT-1200to2500','DYJetsToLL_M-50_HT-200to400','DYToLL-M-50_3J']
#,'DYJetsToLL_M-50_HT-2500toInf','DYJetsToLL_M-50_HT-400to600','DYJetsToLL_M-50_HT-600to800','DYJetsToLL_M-50_HT-70to100','DYJetsToLL_M-50_HT-800to1200','DYToLL-M-50_0J','DYToLL-M-50_1J','DYToLL-M-50_2J']

#siglist=['VBF_HToInvisible_M125_14TeV_powheg_pythia8']
#sigshort=['VBFH']


runDir=os.getcwd()
#os.system('xrdcp -f root://cmseos.fnal.gov//store/user/snowmass/DelphesSubmissionLPCcondor/scripts/EOSSafeUtils.py '+runDir)
execfile(runDir+'/EOSSafeUtils.py')

os.system('echo "pu size: %s"'%len(pulist))
#os.system('export X509_USER_PROXY=${HOME}/.gridproxy.pem')
os.environ['X509_USER_PROXY'] = "%s/.gridproxy.pem"%(os.environ['HOME'])
os.system('echo $X509_USER_PROXY')
os.system('voms-proxy-init --valid 168:00')
os.system('voms-proxy-info')

for pu in pulist :
    os.system('echo " - pu %s"'%pu)

    for inputlist in os.listdir(inputlistdir):
        lastchar=inputlist.rfind(".dat")
        print "%s %d"%(inputlist,lastchar)
        sample=inputlist[0:lastchar]
        os.system('echo " -- sample: %s"'%(sample))
        outDir='%s/%s_%s'%(opt.out,sample,pu)
        os.system('mkdir -p %s'%outDir)

    #wrapper
        scriptFile = open('%s/runJob.sh'%(outDir), 'w')
        scriptFile.write('#!/bin/bash\n')
        scriptFile.write('export BASEDIR=$PWD \n')
        scriptFile.write('export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch \n')
        scriptFile.write('source $VO_CMS_SW_DIR/cmsset_default.sh \n')
        scriptFile.write('cd /afs/cern.ch/work/a/amagnan/CMSSW_9_3_5/src/PhaseTwoAnalysis/delphesInterface/ \n')
        scriptFile.write('eval `scramv1 runtime -sh` \n')
        scriptFile.write('source env.sh\n')
        scriptFile.write('cd $BASEDIR\n')
        scriptFile.write('pwd\n')
        scriptFile.write('voms-proxy-info\n')
        scriptFile.write('mkdir outputdir\n')
        scriptFile.write('echo "running with input filelist: %s/%s/%s"\n'%(os.getcwd(),inputlistdir,inputlist))
        scriptFile.write('cp %s/%s/%s .\n'%(os.getcwd(),inputlistdir,inputlist))
        #scriptFile.write('xrdcp %s%s_%s/DY1Jets_MLL-50_TuneCUETP8M1_14TeV-madgraphMLM-pythia8_1_0.root $PWD/test.root\n'%(sampleDir,sampleList[sample],pu))
        #scriptFile.write('ls -l test.root\n')
        scriptFile.write('%s/ntupler %s/config.txt | tee output.out\n'%(os.getcwd(),outDir))
        scriptFile.write('cp output.out %s/output.out\n'%(outDir))
        scriptFile.write('echo " -- Delphes to ntuple done."\n')
    #copy output to eos
        scriptFile.write('cd /afs/cern.ch/work/a/amagnan/CMSSW_9_3_5/src/\n')
        scriptFile.write('eval `scramv1 runtime -sh` \n')
        scriptFile.write('cd $BASEDIR \n')
        scriptFile.write('echo $ROOTSYS \n')
        scriptFile.write('pwd\n')
        scriptFile.write('hadd outputdir/%s.root outputdir/p2ntuple*.root\n'%sample)
        scriptFile.write('if (( "$?" == "0" )); then\n')
        scriptFile.write('eos mkdir -p /eos/cms/store/group/phys_higgs/future/amagnan/%s/\n'%pu)
        scriptFile.write('eos cp outputdir/%s.root /eos/cms/store/group/phys_higgs/future/amagnan/%s/%s.root\n'%(sample,pu,sample))
        scriptFile.write('ls *\n')
        scriptFile.write('cp outputdir/delphesNtuple.root %s/\n'%(outDir))
        scriptFile.write('echo " -- hadd ntuples done."\n')
        #run light tree maker
        scriptFile.write('mkdir filelists\n')
        scriptFile.write('echo outputdir/%s.root > filelists/%s_%s.dat\n'%(sample,sample,pu))
        scriptFile.write('/afs/cern.ch/work/a/amagnan/UPSGAna/HinvPhaseTwoNtupleAnalysis/Analysis/bin/simpleTree ./ %s %s filelists %d | tee runTree.log\n'%(sample,pu,opt.numEvts))
        scriptFile.write('cp runTree.log %s/runTree.log\n'%(outDir))
        scriptFile.write('mv HistosFile* %s/\n'%(outDir))
        scriptFile.write('ls * \n')
        scriptFile.write('echo " -- ntuple to lighttree done"\n')
        scriptFile.write('else\n')
        scriptFile.write('echo "-- problem with hadd...."\n')
        scriptFile.write('cp -r outputdir %s/.\n'%(outDir))
        scriptFile.write('fi\n')
        scriptFile.write('echo " -- All done"\n')
        scriptFile.close()
        
        #get dir from filelist
        #tmpDir=subprocess.check_output(['head','-n 1','%s/%s.dat'%(inputlistdir,sample)])
        #lastchar=tmpDir.rfind("/")
        #sampleDir=tmpDir[0:lastchar]
        #print "Sample dir is: %s"%sampleDir

        configFile = open('%s/config.txt'%(outDir), 'w')
        configFile.write('[config-begin]\n')
        configFile.write('Outputdir  = outputdir/\n')
        configFile.write('Outputfile = delphesNtuple.root\n')
        configFile.write('Lumi       = 3000\n')
        configFile.write('Testmode   = false\n')
        configFile.write('Maxchilds  = 6\n')
        configFile.write('Samplesdir = root:/\n')
        configFile.write('RunOnOutputOnly = false\n')
        configFile.write('[config-end]\n')
        configFile.write('[inputfiles-begin]\n')
        #configFile.write('%s_%s/DY1Jets_MLL-50_TuneCUETP8M1_14TeV-madgraphMLM-pythia8_1_0.root, %s, 1, 1, auto, 1\n'%(sampleList[sample],pu,sampleShort[sample]))
        configFile.write('%s.dat, %s, 1, 1, auto, 1\n'%(sample,sample))
        configFile.write('[inputfiles-end]\n')
        configFile.close()
        

        print 'Getting proxy'
        subprocess.check_output(['voms-proxy-info','-path'])

        proxyPath=os.popen('voms-proxy-info -path')
        proxyPath=proxyPath.readline().strip()
        os.system('chmod u+rwx %s/runJob.sh'%outDir)

        condorFile = open('%s/condorSubmit.sub'%(outDir), 'w')
        condorFile.write('use_x509userproxy = true\n')
        condorFile.write('universe = vanilla\n')
        condorFile.write('+JobFlavour = "nextweek"\n')
        condorFile.write('Executable = %s/runJob.sh\n'%outDir)
        condorFile.write('Output = %s/condor.out\n'%outDir)
        condorFile.write('Error = %s/condor.err\n'%outDir)
        condorFile.write('Log = %s/condor.log\n'%outDir)
        condorFile.write('Queue 1\n')
        condorFile.close()

    #submit
        if opt.nosubmit :
            os.system('echo condor_submit %s/condorSubmit.sub'%(outDir))
            #os.system('echo bsub -q %s %s/runJob.sh'%(opt.queue,outDir))
            #os.system('cat %s/runJob.sh'%(outDir))
            #os.system('cat %s/config.txt'%(outDir))
            #os.system('cat %s/condorSubmit.sub'%(outDir))
        else: 
            #os.system("bsub -q %s \'%s/runJob.sh\'"%(opt.queue,outDir))
            os.system('condor_submit %s/condorSubmit.sub'%(outDir))
