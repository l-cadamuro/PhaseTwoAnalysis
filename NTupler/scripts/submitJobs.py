def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

#!/usr/bin/env python
import os, re
import commands
import math, time
import sys

print 
print 'START'
print 
########   YOU ONLY NEED TO FILL THE AREA BELOW   #########
########   customization  area #########

####### force to have 1 job / 1 file
# NumberOfJobs = 182 # number of jobs to be submitted
# interval     = 1  # number files to be processed in a single job, take care to split your file so that you run on all files. The last job might be with smaller number of files (the ones that remain).
# ScriptName   = "produceNtuples_cfg_jetsOnly.py" # script to be used with cmsRun
ScriptName   = "clean_produce_Ntuples.py"

# OutputFileNames = "TTbar_PU0_ntuple" # base of the output file name, they will be saved in res directory
# FileList     = "TTbar_PU0_filelist.txt" # list with all the file directories

OutputFileNames = "GG_HH_4B_PU200_UpdBTag_ntuple_resub" # base of the output file name, they will be saved in res directory
FileList        = "filelists/GG_HH_4B_PU200_v2_filelist.txt" # list with all the file directories
tag             = "GG_HH_4B_PU200_UpdBTag_ntuple_resub"
odir            = "/eos/cms/store/user/lcadamur/DelphesPhaseIITreesFullSim"

# OutputFileNames = "VBF_HH_4B_PU200_UpdBTag_ntuple" # base of the output file name, they will be saved in res directory
# FileList     = "filelists/VBF_HH_4B_PU200_comb_filelist.txt" # list with all the file directories


# OutputFileNames = "TTbar_PU200_ntuple" # base of the output file name, they will be saved in res directory
# FileList     = "TTbar_PU200_ext_filelist.txt" # list with all the file directories

queue = "8nh" # give bsub queue -- 8nm (8 minutes), 1nh (1 hour), 8nh, 1nd (1day), 2nd, 1nw (1 week), 2nw 

# rerunJECs = True

nfiles = file_len(FileList)

# if NumberOfJobs*interval < nfiles:
#    print "** WARNING: with the current setting you can process up to", NumberOfJobs, "*", interval, '=', NumberOfJobs*interval, "files, while list contains", nfiles
#    print "... I am exiting (comment the exit command if you really want to proceed"
#    sys.exit()  

interval = 1
NumberOfJobs = nfiles

print '... Will execute', NumberOfJobs, "jobs each running on", interval, 'files'

########   customization end   #########

path = os.getcwd()
print
# print 'do not worry about folder creation:'
# os.system("rm -r tmp")
# os.system("mkdir tmp")
# os.system("mkdir res")

full_odir   = "%s/%s" % (odir, tag)
full_jobdir = "jobs_%s" % (tag)

print "Output dir is : ", full_odir
print "Job dir is : ", full_jobdir

os.system("mkdir %s" % full_odir)
os.system("mkdir %s" % full_jobdir)

# xrootx proxy
proxynamebase = 'x509up_u63159'
homebase = '/afs/cern.ch/user/l/lcadamur/' ## keep trailing /
proxyname = '/tmp/'+proxynamebase
homename = homebase + proxynamebase
print "..... proxy in", homename
if not os.path.isfile(proxyname):
   print "NO PROXY FOUND"
   sys.exit()
os.system('cp %s %s' % (proxyname, homebase))
print

#### jecs are already applied when using the default
# jecs_text = ''
# if rerunJECs:
#    jecs_text = 'updateJEC=./PhaseIIFall17_V3_MC.db'
# print '... rerunning JECs?', rerunJECs

##### loop for creating and sending jobs #####
for x in range(1, int(NumberOfJobs)+1):
   ##### creates directory and file list for job #######
   # os.system("mkdir tmp/"+str(x))
   # os.chdir("tmp/"+str(x))

   thisdir = "%s/%i" % (full_jobdir, x) 
   os.system("mkdir %s" % thisdir)
   # os.chdir("tmp/"+str(x))
   os.chdir("%s" % (thisdir))
   os.system("sed '"+str(1+interval*(x-1))+","+str(interval*x)+"!d' ../../"+FileList+" > list.txt ")
   
   ##### creates jobs #######
   with open('job.sh', 'w') as fout:
      fout.write("#!/bin/sh\n")
      fout.write("echo\n")
      fout.write("echo\n")
      fout.write("export X509_USER_PROXY=%s\n" % homename)
      fout.write("echo 'START---------------'\n")
      fout.write("echo 'WORKDIR ' ${PWD}\n")
      fout.write("source /afs/cern.ch/cms/cmsset_default.sh\n")
      fout.write("cd "+str(path)+"\n")
      fout.write("cmsenv\n")
      # fout.write("cmsRun "+ScriptName+" outFilename='res/"+OutputFileNames+"_"+str(x)+".root' inputFiles_clear inputFiles_load='tmp/"+str(x)+"/list.txt'\n")
      # fout.write("cmsRun "+ScriptName+" outFilename='res/"+OutputFileNames+"_"+str(x)+".root' inputFiles_load='tmp/"+str(x)+"/list.txt' %s\n" % jecs_text)
      # fout.write("cmsRun "+ScriptName+" outFilename='res/"+OutputFileNames+"_"+str(x)+".root' inputFiles_load='tmp/"+str(x)+"/list.txt'\n")
      fout.write("cmsRun "+ScriptName+" outFilename='" + full_odir + "/"+OutputFileNames+"_"+str(x)+".root' inputFiles_load='" + thisdir + "/list.txt'\n")
      fout.write("echo 'STOP---------------'\n")
      fout.write("echo\n")
      fout.write("echo\n")
   os.system("chmod 755 job.sh")
   
   ###### sends bjobs ######
   os.system("bsub -q "+queue+" -o logs job.sh")
   print "job nr " + str(x) + " submitted"
   
   os.chdir("../..")
   
print
print "your jobs:"
os.system("bjobs")
print
print 'END'
print