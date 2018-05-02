import FWCore.ParameterSet.Config as cms
from FWCore.ParameterSet.VarParsing import VarParsing
from Configuration.StandardSequences.Eras import eras

############################################################
rerun_btag = True # for the latest PhaseII developments - NB: increases the runtime

############################################################


options = VarParsing ('python')
options.register('outFilename', 'MiniEvents.root',
                 VarParsing.multiplicity.singleton,
                 VarParsing.varType.string,
                 "Output file name"
                 )

options.inputFiles = []
options.parseArguments()

standardjec='PhaseTwoAnalysis/NTupler/data/PhaseIIFall17_V3_MC.db'
standardjec_tag='PhaseIIFall17_V3_MC'

# process = cms.Process("MiniAnalysis")
process = cms.Process("MiniAnalysis", eras.Phase2)

# Geometry, GT, and other standard sequences
process.load('Configuration.Geometry.GeometryExtended2023D17Reco_cff')
process.load("Configuration.StandardSequences.MagneticField_cff")
process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('Configuration.StandardSequences.MagneticField_AutoFromDBCurrent_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_condDBv2_cff')
process.load("TrackingTools/TransientTrack/TransientTrackBuilder_cfi")

from Configuration.AlCa.GlobalTag_condDBv2 import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, '93X_upgrade2023_realistic_v2', '')

# Log settings
process.load("FWCore.MessageService.MessageLogger_cfi")
process.MessageLogger.cerr.FwkReport.reportEvery = 1000
#process.MessageLogger.cerr.threshold = 'INFO'
# process.MessageLogger.categories.append('MyAna')
# process.MessageLogger.cerr.INFO = cms.untracked.PSet(
#         limit = cms.untracked.int32(0)
# )

# Input
process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(-1)
) 

process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring(
        'root://cms-xrd-global.cern.ch//store/mc/PhaseIITDRFall17MiniAOD/DiPhotonJetsBox_MGG-80toInf_14TeV-Sherpa/MINIAODSIM/PU200_93X_upgrade2023_realistic_v2-v1/150000/E01EFC0F-13B7-E711-A90B-FA163E4C681C.root'
    ),
    # secondaryFileNames = cms.untracked.vstring('root://cms-xrd-global.cern.ch//store/mc/PhaseIITDRFall17DR/DiPhotonJetsBox_MGG-80toInf_14TeV-Sherpa/GEN-SIM-RECO/PU200_93X_upgrade2023_realistic_v2-v1/150000/24BB7BB2-A9B4-E711-9DC9-FA163E7FFB3C.root')
)
if options.inputFiles:
    process.source.fileNames = cms.untracked.vstring(options.inputFiles)

process.options   = cms.untracked.PSet(
    wantSummary = cms.untracked.bool(True),
    allowUnscheduled = cms.untracked.bool(True) ### likely useless in CMSSW 9_3_2: https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideUnscheduledExecution
)


##### set JECs
from CondCore.DBCommon.CondDBSetup_cfi import *
process.jec = cms.ESSource("PoolDBESSource",CondDBSetup,
                            connect = cms.string('sqlite_fip:'+standardjec),
                            toGet =  cms.VPSet(
                                cms.PSet(record = cms.string("JetCorrectionsRecord"),
                                         tag = cms.string("JetCorrectorParametersCollection_"+standardjec_tag+"_AK4PFPuppi"),
                                         label = cms.untracked.string("AK4PFPuppi"))
                                )
                            )
process.es_prefer_jec = cms.ESPrefer("PoolDBESSource","jec")

#############
# nutplize
process.ntuple = cms.EDAnalyzer("MiniFromPat_jetonly")
process.load("PhaseTwoAnalysis.NTupler.MiniFromPat_jetonly_cfi")


##### re apply b tag and JECs
from PhysicsTools.PatAlgos.tools.jetTools import updateJetCollection

if rerun_btag:
    print "... I will update the jet collection and rerun the btag"
    updateJetCollection(process,
                        jetSource = cms.InputTag('slimmedJetsPuppi'),
                        postfix = 'UpdatedJECAK4PFPuppi',
                        jetCorrections = ('AK4PFPuppi', ['L1FastJet','L2Relative','L3Absolute'], 'None'),
                        ###### re-run the b tag discriminators
                        pfCandidates       = cms.InputTag('packedPFCandidates'),
                        btagDiscriminators = ['pfDeepCSVJetTags:probb', 'pfDeepCSVJetTags:probbb'],
                        )
    process.ntuple.jets = "selectedUpdatedPatJetsUpdatedJECAK4PFPuppi"
else:
    print "... I will only update the jet collection (no btag)"
    updateJetCollection(process,
                        jetSource = cms.InputTag('slimmedJetsPuppi'),
                        postfix = 'UpdatedJECAK4PFPuppi',
                        jetCorrections = ('AK4PFPuppi', ['L1FastJet','L2Relative','L3Absolute'], 'None'),
                        )
    process.ntuple.jets = "updatedPatJetsUpdatedJECAK4PFPuppi"


# from PhysicsTools.PatAlgos.tools.helpers import *
# process.reJECTask = getPatAlgosToolsTask(process)
# print process.patAlgosToolsTask

# print "... appending by hand the task elements to the process"
# myJECpath = cms.Path()
# for elem in process.patAlgosToolsTask:
#     myJECpath += elem

# print "... done"

#### output file
process.TFileService = cms.Service("TFileService",
                                   fileName = cms.string(options.outFilename)
                                   )


# from FWCore.ParameterSet.Utilities import convertToUnscheduled
# convertToUnscheduled(process)

# process.p = cms.Path(
#     process.patJetCorrFactorsUpdatedJECAK4PFPuppi *
#     process.updatedPatJetsUpdatedJECAK4PFPuppi *
#     process.ntuple
# )

# process.p = myJECpath
# process.p += process.ntuple

#Trick to make it work in 9_1_X
# for mod in process.producers_().itervalues():
#     process.tsk.add(mod)
# for mod in process.filters_().itervalues():
#     process.tsk.add(mod)

process.p = cms.Path(
    process.ntuple,
    process.patAlgosToolsTask
)
