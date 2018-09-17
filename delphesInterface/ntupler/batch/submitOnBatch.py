### launch this script from the batch/ folder

import re

def tryint(s):
    try:
        return int(s)
    except:
        return s

def alphanum_key(s):
    """ Turn a string into a list of string and number chunks.
        "z23a" -> ["z", 23, "a"]
    """
    return [ tryint(c) for c in re.split('([0-9]+)', s) ]

def sort_alphanum(l):
    """ Sort the given list in the way that humans expect.
    """
    l.sort(key=alphanum_key)

def dispatch (line, flist, dispatch_format=None):
    """ dispatch the line to all the files in the flist for writing. If dispatch_format is passed, each line will be formatted by ots entries """
    for idx, f in enumerate(flist):
        thisline = line
        if dispatch_format:
            # print '..', thisline
            # print '--', dispatch_format[idx]
            try              : thisline = thisline.format(dispatch_format[idx])
            except IndexError: thisline = thisline.format(*dispatch_format[idx])

        f.write(thisline)

def parseInputFileList (fileName) :
    filelist = []
    with open (fileName) as fIn:
        for line in fIn:
            line = (line.split("#")[0]).strip()
            if line:
                filelist.append(line)
    return filelist

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i+n]

def splitInBlocks (l, n):
    """split the list l in n blocks of equal size"""
    k = len(l) / n
    r = len(l) % n

    i = 0
    blocks = []
    while i < len(l):
        if len(blocks)<r:
            blocks.append(l[i:i+k+1])
            i += k+1
        else:
            blocks.append(l[i:i+k])
            i += k

    return blocks

#############################

import os
import sys
import glob
import argparse
import subprocess

parser = argparse.ArgumentParser(description='Command line parser of skim options')
parser.add_argument('--location' , dest='location', help='where is the sample located? (fnal, cern, desy)', required=True)
parser.add_argument('--njobs'    , dest='njobs',    help='number of jobs', type=int, default=100)
parser.add_argument('--input'    , dest='input',    help='input directory or filelist', required=True)
parser.add_argument('--output'   , dest='output',   help='output directory', default="/eos/cms/store/user/lcadamur/DelphesPhaseIITrees")
parser.add_argument('--tag'      , dest='tag',      help='tag name pf this production', required=True)
parser.add_argument('--directWrite' , dest='directwrite',  help='directly write the output on the destination instead of xrdcp after execution', action='store_true', default=False)
parser.add_argument('--dry-run' , dest='dryrun',  help='do not submit jobs', action='store_true', default=False)
args = parser.parse_args()

cfg_template  = 'TEMPLATE_CFG.txt'

# location      = 'cern' ## fnal, cern, desy
# njobs         = 100 # only applies on .dat input filelists 
location = args.location
njobs    = args.njobs

# input_dir     = '/eos/cms/store/group/upgrade/delphes_output/LHEGEN_SMbackgrounds/Delphes342pre07_hadd/TT_TuneCUETP8M2T4_14TeV-powheg-pythia8_200PU' 
# output_dir    = '/eos/cms/store/user/lcadamur/DelphesPhaseIITrees' ## tag will be appended
# tag           = 'TT_genjets'

# input_dir     = '/eos/cms/store/user/lcadamur/DelphesNtuples/delphes-master-updBTag-28Apr/GG_HH_4B_GEN_SIM_RECO_PU0_fullProd_200PU' 
# output_dir    = '/eos/cms/store/user/lcadamur/DelphesPhaseIITrees' ## tag will be appended
# tag           = 'GG_HH_4B_updBTag'

# input_dir     = '/eos/cms/store/user/lcadamur/DelphesNtuples/delphes-master-btagMTD-8Mag/GG_HH_4B_GEN_SIM_RECO_PU0_fullProd_200PU'
# output_dir    = '/eos/cms/store/user/lcadamur/DelphesPhaseIITrees' ## tag will be appended
# tag           = 'GG_HH_4B_btagMTD_res'

# input_dir     = '/afs/cern.ch/work/l/lcadamur/private/YR_bbbb_analysis/CMSSW_9_3_2/src/PhaseTwoAnalysis/delphesInterface/ntupler/config/filelists/SM_gg_HH_bbbb.dat'
# output_dir    = '/eos/cms/store/user/lcadamur/DelphesPhaseIITrees' ## tag will be appended
# tag           = 'gg_HH_4b_31Ago2018_trees_res2_6childsTest'

input_dir  = args.input
output_dir = args.output
tag        = args.tag

queue = "1nh" # give bsub queue -- 8nm (8 minutes), 1nh (1 hour), 8nh, 1nd (1day), 2nd, 1nw (1 week), 2nw
force = False

#######################################################################################################

if location.lower() == 'fnal':
    xrootd_srv_name = 'root://cmseos.fnal.gov/'
elif location.lower() == 'cern':
    xrootd_srv_name = 'root://eoscms.cern.ch/'
elif location.lower() == 'desy':
    xrootd_srv_name = 'root://cms-xrd-global.cern.ch/'
else:
    print "I cannot determine the location that you passed:", location
    sys.exit()

## for some reason, the batch jobs must be launched with all set up (couldn't make the setup in the script work)
if not 'DANALYSISPATH' in os.environ or not "CMSSW_BASE" in os.environ:
    print "please make the setup of the analysis framework before launching"
    sys.exit()

## enable the possibility to input a filelist
## in the framework this needs to be a .dat file, so let's rely on the same criterion
input_is_filelist = True if input_dir.endswith(".dat") else False
print "... is this an input filelist as .dat file?", input_is_filelist

if not input_dir[-1] == '/' and not input_is_filelist: input_dir += '/'
if not output_dir[-1]  == '/': output_dir += '/'
output_dir += tag
# output_tmp_dir_proto = '/tmp/lcadamur/' + tag + '/dir_{0}' ## for the temporary output of the job. Format the out dir with the job nr so that it does not interfere when copying outputs
output_tmp_dir_proto = '/pool/lcadamur/' + tag + '/dir_{0}' ## for the temporary output of the job. Format the out dir with the job nr so that it does not interfere when copying outputs

job_folder = 'jobs_' + tag
if os.path.isdir(job_folder) and not force:
    print 'jobs folder', job_folder, 'already exists, aborting'
    sys.exit()
os.system('mkdir %s' % job_folder)


if os.path.isdir(output_dir) and not force:
    print 'output folder', output_dir, 'already exists, aborting'
    sys.exit()
os.system('mkdir %s' % output_dir)

print " ******************************** "
print " ** Input   : ", input_dir
print " ** Output  : ", output_dir
print " ** Jobs    : ", job_folder
print " ** Loc     : ", location
if not args. directwrite: print " ** Tmp out : ", output_tmp_dir_proto
print " ******************************** "

if input_is_filelist:
    outListNameBareProto   = 'filelist_{0}.dat'
    outListNameProto = (job_folder + '/' + outListNameBareProto)
    all_files = []
    
    all_single_files = parseInputFileList(input_dir)
    if njobs > len(all_single_files): njobs = len(all_single_files) ## at most 1 job per file
    # now merge the individual files into bunches to be processed by each job, saving the filelist into the jobsdir
    fileblocks = splitInBlocks (all_single_files, njobs)
    if njobs != len(fileblocks):
        print "** ERROR: length of file lists and njobs do not match, something went wrong"
        sys.exit()
    for n in range(0, njobs):
        outListName = outListNameProto.format(n)
        jobfilelist = open(outListName, 'w')
        for f in fileblocks[n]: jobfilelist.write(f+"\n")
        jobfilelist.close()
        all_files.append('batch/' + outListName)
else:
    all_files = glob.glob(input_dir + '*.root')
    all_files = [os.path.basename(x) for x in all_files] ## file name only - the rest is in the folder name
sort_alphanum(all_files)

# for l in all_files: print l
# print '... will submit', len(all_files), 'jobs (one per file)'
print '... will submit', len(all_files), 'jobs'
if input_is_filelist: print "... input was specified as a filelist"
else:                 print "... input was specified as the file folder"

os.chdir(job_folder)
print '... working inside', os.getcwd()

cfg_template_full = '../../config/%s' % cfg_template ## update from working folder
if not os.path.exists(cfg_template_full):
    print 'cfg template not found in', cfg_template_full
    sys.exit()

cfgname_proto = "config_{0}.txt"
configs = [None] * len(all_files)
for i in range(len(all_files)):
    configs[i] = open(cfgname_proto.format(i), 'w')

### prepare the dictionary for replacement
# repl = {
#     'XXX_OUTPUTDIR_XXX'  : output_dir ,
#     'XXX_OUTPUTFILE_XXX' : 'ntuple_{}.root' ,
#     'XXX_SAMPLESDIR_XXX' : input_dir ,
#     'XXX_FILENAME_XXX'   : '{}' ,
#     'XXX_FILETAG_XXX'    : tag + '_{}' ,
# }

repl = {
    'XXX_OUTPUTDIR_XXX'  : (output_dir if args.directwrite else output_tmp_dir_proto),
    'XXX_OUTPUTFILE_XXX' : 'ntuple_{}.root' ,
    'XXX_FILENAME_XXX'   : '{}' ,
    'XXX_FILETAG_XXX'    : tag + '_{}' ,
}


if input_is_filelist: ## if a filelist, just use the name of the server to access the file
    repl['XXX_SAMPLESDIR_XXX'] = xrootd_srv_name
else: ## if it is a folder, instead use the full path to the directory
    repl['XXX_SAMPLESDIR_XXX'] = input_dir


####### fill the cfgs
template = open(cfg_template_full)

f_idxs = range(len(all_files))

for line in template:
    dispatch_format = None
    if 'XXX_' in line and '_XXX' in line:
        for key, value in repl.items():
            if key in line:
                ## special cases
                if   key == 'XXX_OUTPUTDIR_XXX' and not args.directwrite: dispatch_format = f_idxs
                if   key == 'XXX_OUTPUTFILE_XXX': dispatch_format = f_idxs
                elif key == 'XXX_FILENAME_XXX'  : dispatch_format = zip(all_files, f_idxs) ### two values must be passed to "format" and FILENAME and FILETAG are on the same line
                line = line.replace(key, value)

    dispatch(line, configs, dispatch_format)

for f in configs:
    f.close()


##############################################################
# launch he jobs

proxynamebase = 'x509up_u63159'
homebase = '/afs/cern.ch/user/l/lcadamur/' ## keep trailing /
proxyname = '/tmp/'+proxynamebase
myproxyname = homebase + proxynamebase

regenerate_proxy = False
if not os.path.isfile(myproxyname): ## proxy file does not exist
    print "... proxy file does not exist"
    regenerate_proxy = True
else:
    lifetime = subprocess.check_output(['voms-proxy-info', '--file', myproxyname, '--timeleft']) ## in seconds
    lifetime = float(lifetime)
    lifetime = lifetime / (60*60)
    print "... proxy lifetime is ", lifetime, "hours"
    if lifetime < 10.0: ## at least 10 hours
        print "... proxy has expired"
        regenerate_proxy = True
if regenerate_proxy:
    print "... regenerating proxy"
    redone_proxy = False
    while not redone_proxy:
        status = os.system('voms-proxy-init -voms cms')
        if os.WEXITSTATUS(status) == 0:
            redone_proxy = True
        else:
            print "... something when wrong with proxy regeneration, please try again"
    print "... copying proxy" , proxyname, "to ", homebase
    os.system('cp %s %s' % (proxyname, homebase))  


#### copy the proxy to the home area, so that it can be used by the job to run xrootd
#### se lancio piu volte questo script, e un job sta gia girando, puo fallire se sostituisco il file di proxy?
#### per essere sicuro, dovrei copiare il proxy solo se piu vecchio di XXXX tempo
#### voms-proxy-info --file /afs/cern.ch/user/l/lcadamur/x509up_u63159 --timeleft ==> stampa il tempo rimanente del proxy in secondi
#### si puo usare nelllo script e nel caso copiare il file (e.g. se il tempo e' 0 o troppo corto)
#### da capire qual e' il valore di ritorno se il proxy e' scaduto
#### + aggiungi check se il proxy proprio non esiste
# os.system('cp %s %s' % (proxyname, homebase))

execute_in = os.getcwd() + '/../..' ## I am two levels below where ntupler is
##### creates jobs #######
jname_proto = 'job_{0}.sh'
log_proto   = 'job_{0}.log'
err_proto   = 'job_{0}.err'
for i in range(len(all_files)):
    jname = jname_proto.format(i)
    with open(jname, 'w') as fjob:
        fjob.write("#!/bin/sh\n")
        fjob.write("echo\n")
        fjob.write("echo\n")
        fjob.write("export X509_USER_PROXY=%s\n" % myproxyname)
        fjob.write("echo 'START---------------'\n")
        fjob.write('echo "... start job at" `date "+%Y-%m-%d %H:%M:%S"`\n')
        fjob.write("echo 'WORKDIR ' ${PWD}\n")
        fjob.write("source /afs/cern.ch/cms/cmsset_default.sh\n")
        fjob.write("cd "+str(execute_in)+"\n")
        # fjob.write('echo "cmssw base $CMSSW_BASE"\n')
        fjob.write("cmsenv\n")
        # fjob.write('echo "cmssw base $CMSSW_BASE"\n')
        fjob.write("cd ..\n")
        # fjob.write('echo "I am in"\n')
        # fjob.write('pwd\n')
        # fjob.write('ls\n')
        # fjob.write('echo "var is $DANALYSISPATH"\n')
        # fjob.write("source env.sh\n")
        fjob.write(". ./env.sh\n")
        # fjob.write('echo "var is $DANALYSISPATH"\n')
        fjob.write("pwd\n")
        # fjob.write("ls\n")
        ### /tmp area is per maching. So let each job create and handle its own are
        if not args.directwrite:
            output_tmp_dir = output_tmp_dir_proto.format(i)
            fjob.write('echo ">> creating the tmp folder in %s"\n' % output_tmp_dir)
            fjob.write('mkdir -p %s\n' % output_tmp_dir)
            fjob.write('echo ">> tmp folder created"\n')
            ### some checks for debug
            fjob.write('echo ">> touching file"\n')
            fjob.write('touch %s/test_%i\n' % (output_tmp_dir, i))
            fjob.write('echo ">> listing file"\n')
            fjob.write('ls %s\n' % output_tmp_dir)
        fjob.write('echo "launching the delphes command ..."\n')
        # fjob.write("cmsRun "+ScriptName+" outFilename='res/"+OutputFileNames+"_"+str(x)+".root' inputFiles_clear inputFiles_load='tmp/"+str(x)+"/list.txt'\n")
        # fjob.write("cmsRun "+ScriptName+" outFilename='res/"+OutputFileNames+"_"+str(x)+".root' inputFiles_load='tmp/"+str(x)+"/list.txt' %s\n" % jecs_text)
        # fjob.write("cmsRun "+ScriptName+" outFilename='res/"+OutputFileNames+"_"+str(x)+".root' inputFiles_load='tmp/"+str(x)+"/list.txt'\n")
        fjob.write('./ntupler batch/%s/%s\n' % (job_folder, cfgname_proto.format(i)))
        fjob.write('echo "... job ended with status $?"\n')
        if not args.directwrite: ## also add xrdcp directives
            xrd_output_dir = output_dir
            if '/eos/cms' in xrd_output_dir:
                xrd_output_dir = xrd_output_dir.replace('/eos/cms', 'root://eoscms.cern.ch/')
            fjob.write('xrdcp -s %s/p2ntuple_*.root %s\n' % (output_tmp_dir, xrd_output_dir))
            fjob.write('echo "... xrdcp copy ended with status $?"\n')
            fjob.write('echo "... cleaning up the tmp space"\n')
            fjob.write('rm -r %s\n' % output_tmp_dir)
            fjob.write('echo "... deletion done with status $?"\n')
        fjob.write("echo 'STOP---------------'\n")
        fjob.write('echo "... end job at" `date "+%Y-%m-%d %H:%M:%S"`\n')
        fjob.write("echo\n")
        fjob.write("echo\n")
    os.system("chmod 755 %s" % jname)

###### sends bjobs ######
if not args.dryrun:
    for i in range(len(all_files)):
        os.system("bsub -q "+queue+" -o %s -e %s %s" % (log_proto.format(i), err_proto.format(i), jname_proto.format(i)))
        print "job nr " + str(i) + " submitted"

