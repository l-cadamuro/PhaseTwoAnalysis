## this is the piece at DESY

MAIN_PATH="/store/group/upgrade/delphes_output/YR_Delphes/Delphes342pre14" ### con '/' iniziale, senza '/' finale
XRDSRVR="root://cms-xrd-global.cern.ch/"
for d in \
    QCD_bEnriched_HT200to300_TuneCUETP8M1_14TeV-madgraphMLM-pythia8_200PU \
    QCD_bEnriched_HT300to500_TuneCUETP8M1_14TeV-madgraphMLM-pythia8_200PU \
    QCD_bEnriched_HT500to700_TuneCUETP8M1_14TeV-madgraphMLM-pythia8_200PU \
    QCD_bEnriched_HT1500to2000_TuneCUETP8M1_14TeV-madgraphMLM-pythia8_200PU \
    QCD_bEnriched_HT2000toInf_TuneCUETP8M1_14TeV-madgraphMLM-pythia8_200PU ; \
do 
   echo "... running on dataset $d"
   ONAME="filelist_${d}.dat"
   rm ${ONAME}
   touch ${ONAME}
   # while read linea ; do echo ${XRDSRVR}${MAIN_PATH}/${d}/${linea} >> ${ONAME}; done < <(gfal-ls srm://dcache-se-cms.desy.de/pnfs/desy.de/cms/tier2${MAIN_PATH}/${d});
   while read linea ; do echo ${MAIN_PATH}/${d}/${linea} >> ${ONAME}; done < <(gfal-ls srm://dcache-se-cms.desy.de/pnfs/desy.de/cms/tier2${MAIN_PATH}/${d});
done


## tbis is the peice at fermilab
MAIN_PATH="/store/user/snowmass/noreplica/YR_Delphes/Delphes342pre15"  ### con '/' iniziale, senza '/' finale
XRDSRVR="root://cmseos.fnal.gov/"
for d in \
  QCD_bEnriched_HT1000to1500_TuneCUETP8M1_14TeV-madgraphMLM-pythia8_200PU \
  QCD_bEnriched_HT700to1000_TuneCUETP8M1_14TeV-madgraphMLM-pythia8_200PU ; \
do  
  echo "... running on dataset $d"
  ONAME="filelist_${d}.dat"
  rm ${ONAME}
  touch ${ONAME}
  # while read linea ; do echo ${XRDSRVR}${MAIN_PATH}/${d}/${linea} >> ${ONAME}; done < <(eos ${XRDSRVR} ls ${MAIN_PATH}/${d}/*.root) ;
  while read linea ; do echo ${MAIN_PATH}/${d}/${linea} >> ${ONAME}; done < <(eos ${XRDSRVR} ls ${MAIN_PATH}/${d}/*.root) ;
done