import FWCore.ParameterSet.Config as cms

ntuple = cms.EDAnalyzer('MiniFromPatnoEGamma',
        pileup        = cms.uint32(200),
        vertices      = cms.InputTag("offlineSlimmedPrimaryVertices"),
        # electrons     = cms.InputTag("phase2Electrons"),
        # photons       = cms.InputTag("phase2Photons"),
        beamspot      = cms.InputTag("offlineBeamSpot"),
        conversions   = cms.InputTag("reducedEgamma", "reducedConversions", "PAT"),
        muons         = cms.InputTag("slimmedMuons"),
        taus          = cms.InputTag("slimmedTaus"),
        jets          = cms.InputTag("slimmedJetsPuppi"),
        mets          = cms.InputTag("slimmedMETsPuppi"),
        genParts      = cms.InputTag("packedGenParticles"),
        genJets       = cms.InputTag("slimmedGenJets"),
)
