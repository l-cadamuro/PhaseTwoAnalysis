/*
 * ntupler.cpp
 *
 *  Created on: 24 Aug 2016
 *      Author: jkiesele
 */

#include "interface/ntupler.h"
#include "interface/scaleFactors.h"
//dirty hack
#include "../../../NTupler/src/MiniEvent.cc"
#include "TDirectory.h"

#include "TH1F.h"

void ntupler::analyze(size_t childid /* this info can be used for printouts */){

	d_ana::dBranchHandler<Electron> elecs(tree(),"Electron");
	d_ana::dBranchHandler<HepMCEvent>  event(tree(),"Event");
	d_ana::dBranchHandler<GenParticle> genpart(tree(),"Particle");
	d_ana::dBranchHandler<Jet>         genjet(tree(),"GenJet");
	d_ana::dBranchHandler<Jet>         jetPUPPI(tree(),"JetPUPPI");
	d_ana::dBranchHandler<Jet>         jet(tree(),"Jet");
	d_ana::dBranchHandler<Muon>        muonloose(tree(),"MuonLoose");
	d_ana::dBranchHandler<Muon>        muontight(tree(),"MuonTight");
	d_ana::dBranchHandler<Photon>      photonloose(tree(),"PhotonLoose");
	d_ana::dBranchHandler<Photon>      photontight(tree(),"PhotonTight");
	d_ana::dBranchHandler<MissingET>   metPUPPI(tree(),"PuppiMissingET");
	d_ana::dBranchHandler<MissingET>   met(tree(),"MissingET");
	size_t nevents=tree()->entries();
	if(isTestMode())
		nevents/=100;


	//create output
	TString chilidstr="";
	chilidstr+=childid;
	TFile * outfile= new TFile(getOutDir()+"/p2ntuple_"+(TString)getLegendName()+"_"+chilidstr+".root","RECREATE");
	TDirectory *counterdir = outfile->mkdir("weightCounter");
	counterdir->cd();
	TH1F * h_event_weight = new TH1F("Event_weight","Event_weight",1,0,1);

	outfile->cd();
	TDirectory *ntupledir = outfile->mkdir("ntuple");
	ntupledir->cd();

	MiniEvent_t ev_;
	TTree * t_event_        = new TTree("Event","Event");
	TTree * t_genParts_     = new TTree("Particle","Particle");
	TTree * t_genPhotons_   = new TTree("GenPhoton","GenPhoton");
	TTree * t_vertices_     = new TTree("Vertex","Vertex");
	TTree * t_genJets_      = new TTree("GenJet","GenJet");
	TTree * t_looseElecs_   = new TTree("ElectronLoose","ElectronLoose");
	TTree * t_mediumElecs_  = new TTree("ElectronMedium","ElectronMedium");
	TTree * t_tightElecs_   = new TTree("ElectronTight","ElectronTight");
	TTree * t_looseMuons_   = new TTree("MuonLoose","MuonLoose");
	TTree * t_tightMuons_   = new TTree("MuonTight","MuonTight");
	TTree * t_allTaus_      = new TTree("TauAll","TauAll");
	TString inName = getSampleFile();
	bool hasPU = !inName.Contains("_0PU");
	TTree * t_puppiJets_    = new TTree(hasPU?"JetPUPPI":"Jet",hasPU?"JetPUPPI":"Jet");
	TTree * t_puppiMET_     = new TTree(hasPU?"PuppiMissingET":"MissingET",hasPU?"PuppiMissingET":"MissingET");
	TTree * t_loosePhotons_ = new TTree("PhotonLoose","PhotonLoose");
	TTree * t_tightPhotons_ = new TTree("PhotonTight","PhotonTight");
	createMiniEventTree(t_event_, t_genParts_, t_vertices_, t_genJets_, t_genPhotons_, t_looseElecs_,
			    t_mediumElecs_,t_tightElecs_, t_looseMuons_, t_tightMuons_, 
			    t_allTaus_, t_puppiJets_, t_puppiMET_,
			    t_loosePhotons_, t_tightPhotons_, ev_);


	//load effective corrections for delphes samples vs fullSim
	scaleFactors
	tightelecsf,medelecsf,looseelecsf,
	tightmuonsf,loosemuonsf,
	jetsf,
	tightphotonsf,loosephotonsf,
	metsf;

	TString basepath=getenv("CMSSW_BASE");
	basepath+="/src/PhaseTwoAnalysis/delphesInterface/ntupler/data/";

	tightelecsf.loadTH2D  (basepath+"ElectronTight_PTabsEta.root","FullSimOverDelphes");
	medelecsf.loadTH2D    (basepath+"ElectronMedium_PTabsEta.root","FullSimOverDelphes");
	//looseelecsf.loadTH2D  (cmsswbase+"bla.root","histo");
    //
	tightmuonsf.loadTH2D  (basepath+"MuonTight_PTabsEta.root","FullSimOverDelphes");
	//loosemuonsf.loadTH2D  (cmsswbase+"bla.root","histo");
    //
	//jetsf.loadTH2D        (cmsswbase+"bla.root","histo");
    //
	tightphotonsf.loadTH2D(basepath+"PhotonTight_PTabsEta.root","FullSimOverDelphes");
	//loosephotonsf.loadTH2D(cmsswbase+"bla.root","histo");
    //
	//metsf.loadTH2D        (cmsswbase+"bla.root","histo");

	for(size_t eventno=0;eventno<nevents;eventno++){
		/*
		 * The following two lines report the status and set the event link
		 * Do not remove!
		 */
		reportStatus(eventno,nevents);
		tree()->setEntry(eventno);

		if(event.size()<1)continue;

		h_event_weight->Fill(0.,(double)event.at(0)->Weight);



		std::vector<Photon*>selectedphotonsL;
		for(size_t i=0;i<photonloose.size();i++){
			if(photonloose.at(i)->PT<10)continue;
			if(photonloose.at(i)->IsolationVarRhoCorr / photonloose.at(i)->E > 0.25)
			  continue;
			selectedphotonsL.push_back(photonloose.at(i));
		}

		std::vector<Photon*>selectedphotons;
		for(size_t i=0;i<photontight.size();i++){
			if(photontight.at(i)->PT<10)continue;
			if(photontight.at(i)->IsolationVarRhoCorr / photontight.at(i)->E > 0.25)
				continue;
			selectedphotons.push_back(photontight.at(i));
		}

		std::vector<Electron*>selectedelectrons;
		for(size_t i=0;i<elecs.size();i++){
			if(elecs.at(i)->PT<10)continue;
			selectedelectrons.push_back(elecs.at(i));
		}

		std::vector<Muon*>selectedMuonsT;
		for(size_t i=0;i<muontight.size();i++){
                  if(muontight.at(i)->PT<5)continue;
                  selectedMuonsT.push_back(muontight.at(i));
		}

		std::vector<Muon*>selectedMuonsL;
		for(size_t i=0;i<muonloose.size();i++){
                  if(muonloose.at(i)->PT<5)continue;
                  selectedMuonsL.push_back(muonloose.at(i));
		}


		std::vector<Jet*>selectedjets;
		if (hasPU){
		  for(size_t i=0;i<jetPUPPI.size();i++){
		    if(jetPUPPI.at(i)->PT<10)continue;
		    selectedjets.push_back(jetPUPPI.at(i));
		  }
		}
		else {
		  for(size_t i=0;i<jet.size();i++){
		    if(jet.at(i)->PT<10)continue;
		    selectedjets.push_back(jet.at(i));
		  }
		}
		
		std::vector<Jet*>selectedtaujets;
		for(size_t i=0;i<jet.size();i++){
                  if(jet.at(i)->PT<10)continue;
                  if(jet.at(i)->TauTag!=1) continue;
                  selectedtaujets.push_back(jet.at(i));
		}

            
		ev_.event = event.at(0)->Number;
		ev_.g_nw = 1;
		ev_.g_w[0] = event.at(0)->Weight;


            ev_.ngl=0;

            for(size_t i=0;i<genpart.size();i++){
                  if(ev_.ngl>=MiniEvent_t::maxpart)break;

                  int pid= fabs(genpart.at(i)->PID);

                  if( (pid>16  && pid < 21) ||  pid > 25 ) continue;

                  ev_.gl_pid[ev_.ngl]=genpart.at(i)->PID;
                  ev_.gl_ch[ev_.ngl]=genpart.at(i)->Charge;
                  ev_.gl_st[ev_.ngl]=genpart.at(i)->Status;
                  ev_.gl_p[ev_.ngl]=genpart.at(i)->P;
                  ev_.gl_pz[ev_.ngl]=genpart.at(i)->Pz;
                  ev_.gl_pt[ev_.ngl]=genpart.at(i)->PT;
                  ev_.gl_eta[ev_.ngl]=genpart.at(i)->Eta;
                  ev_.gl_phi[ev_.ngl]=genpart.at(i)->Phi;
                  ev_.gl_mass[ev_.ngl]=genpart.at(i)->Mass;
                  ev_.ngl++;

                  //std::cout<<i<<"   "<<pid<<"    "<<genpart.at(i)->Status<<"  ->"<<genpart.at(i)->M1<<"  "<<genpart.at(i)->M2<<" ;  "<<genpart.at(i)->D1<<"  "<<genpart.at(i)->D2<<std::endl;

            }

            ev_.ngj=0;

            for(size_t i=0;i<genjet.size();i++){
                  if(ev_.ngj>=MiniEvent_t::maxpart)break;

                  ev_.gj_pt[ev_.ngj]=genjet.at(i)->PT;
                  ev_.gj_eta[ev_.ngj]=genjet.at(i)->Eta;
                  ev_.gj_phi[ev_.ngj]=genjet.at(i)->Phi;
                  ev_.gj_mass[ev_.ngj]=genjet.at(i)->Mass;
                  ev_.ngj++;

                  //std::cout<<i<<"   "<<pid<<"    "<<genjet.at(i)->Status<<"  ->"<<genjet.at(i)->M1<<"  "<<genjet.at(i)->M2<<" ;  "<<genjet.at(i)->D1<<"  "<<genjet.at(i)->D2<<std::endl;

            }

            //std::cout<<std::endl;

		ev_.nlp=0;
		for(size_t i=0;i<selectedphotonsL.size();i++){
			if(ev_.nlp>=MiniEvent_t::maxpart)break;
			ev_.lp_eta[ev_.nlp]=selectedphotonsL.at(i)->Eta;
			ev_.lp_pt [ev_.nlp]=selectedphotonsL.at(i)->PT;
			ev_.lp_phi[ev_.nlp]=selectedphotonsL.at(i)->Phi;
			ev_.lp_nrj[ev_.nlp]=selectedphotonsL.at(i)->E;
			ev_.lp_sf[ev_.nlp]=tightphotonsf.getSF(fabs(selectedphotonsL.at(i)->Eta),selectedphotonsL.at(i)->PT);
			ev_.nlp++;
		}

		ev_.ntp=0;
		for(size_t i=0;i<selectedphotons.size();i++){
			if(ev_.ntp>=MiniEvent_t::maxpart)break;
			ev_.tp_eta[ev_.ntp]=selectedphotons.at(i)->Eta;
			ev_.tp_pt [ev_.ntp]=selectedphotons.at(i)->PT;
			ev_.tp_phi[ev_.ntp]=selectedphotons.at(i)->Phi;
			ev_.tp_nrj[ev_.ntp]=selectedphotons.at(i)->E;
			ev_.tp_sf[ev_.ntp]=tightphotonsf.getSF(fabs(selectedphotons.at(i)->Eta),selectedphotons.at(i)->PT);
			ev_.ntp++;
		}

		ev_.nlm=0;
		for(size_t i=0;i<selectedMuonsL.size();i++){
		  if(ev_.nlm>=MiniEvent_t::maxpart)break;
		  ev_.lm_pt    [ev_.nlm] =selectedMuonsL.at(i)->PT;
		  ev_.lm_eta   [ev_.nlm]=selectedMuonsL.at(i)->Eta;
		  ev_.lm_phi   [ev_.nlm]=selectedMuonsL.at(i)->Phi;
		  ev_.lm_mass  [ev_.nlm]=0.105;
		  ev_.lm_relIso[ev_.nlm]=selectedMuonsL.at(i)->IsolationVarRhoCorr; // /selectedMuonsL.at(i)->PT;
		  ev_.lm_sf[ev_.nlm]=tightmuonsf.getSF(fabs(selectedMuonsL.at(i)->Eta),selectedMuonsL.at(i)->PT);
                  //ev_.lm_g     [ev_.nlm] =selectedMuonsL.at(i)->Particle.PID;
		  ev_.nlm++;
		}

		ev_.ntm=0;
		for(size_t i=0;i<selectedMuonsT.size();i++){
		  if(ev_.ntm>=MiniEvent_t::maxpart)break;
		  ev_.tm_pt    [ev_.ntm] =selectedMuonsT.at(i)->PT;
		  ev_.tm_eta   [ev_.ntm]=selectedMuonsT.at(i)->Eta;
		  ev_.tm_phi   [ev_.ntm]=selectedMuonsT.at(i)->Phi;
		  ev_.tm_mass  [ev_.ntm]=0.105;
		  ev_.tm_relIso[ev_.ntm]=selectedMuonsT.at(i)->IsolationVarRhoCorr; // /selectedMuonsT.at(i)->PT;
		  ev_.tm_sf[ev_.ntm]=tightmuonsf.getSF(fabs(selectedMuonsT.at(i)->Eta),selectedMuonsT.at(i)->PT);
                  //ev_.tm_g     [ev_.ntm] =selectedMuonsT.at(i)->Particle.PID;
		  ev_.ntm++;
		  
		}

		ev_.nte=0;
		ev_.nme=0;
		ev_.nle=0;
		for(size_t i=0;i<selectedelectrons.size();i++){
			if(ev_.nle>=MiniEvent_t::maxpart)break;

			ev_.le_pt    [ev_.nle] =selectedelectrons.at(i)->PT;
			ev_.le_eta   [ev_.nle]=selectedelectrons.at(i)->Eta;
			ev_.le_phi   [ev_.nle]=selectedelectrons.at(i)->Phi;
			ev_.le_mass  [ev_.nle]=0.00051;
			ev_.le_relIso[ev_.nle]=selectedelectrons.at(i)->IsolationVarRhoCorr; //  /selectedelectrons.at(i)->PT ;
			ev_.le_sf[ev_.nle]=medelecsf.getSF(fabs(selectedelectrons.at(i)->Eta),selectedelectrons.at(i)->PT);
			ev_.nle++;

			if(ev_.nme>=MiniEvent_t::maxpart)break;

			ev_.me_pt    [ev_.nme] =selectedelectrons.at(i)->PT;
			ev_.me_eta   [ev_.nme]=selectedelectrons.at(i)->Eta;
			ev_.me_phi   [ev_.nme]=selectedelectrons.at(i)->Phi;
			ev_.me_mass  [ev_.nme]=0.00051;
			ev_.me_relIso[ev_.nme]=selectedelectrons.at(i)->IsolationVarRhoCorr; //  /selectedelectrons.at(i)->PT ;
			ev_.me_sf[ev_.nme]=medelecsf.getSF(fabs(selectedelectrons.at(i)->Eta),selectedelectrons.at(i)->PT);
			ev_.nme++;

			ev_.te_pt    [ev_.nte] =selectedelectrons.at(i)->PT;
			ev_.te_eta   [ev_.nte]=selectedelectrons.at(i)->Eta;
			ev_.te_phi   [ev_.nte]=selectedelectrons.at(i)->Phi;
			ev_.te_mass  [ev_.nte]=0.00051;
			ev_.te_relIso[ev_.nte]=selectedelectrons.at(i)->IsolationVarRhoCorr; //  /selectedelectrons.at(i)->PT ;
			ev_.te_sf[ev_.nte]=tightelecsf.getSF(fabs(selectedelectrons.at(i)->Eta),selectedelectrons.at(i)->PT);
			ev_.nte++;


		}

            ev_.ntau=0;
            for(size_t i=0;i<selectedtaujets.size();i++){
                  if(ev_.ntau>=MiniEvent_t::maxjets)break;
                  ev_.tau_pt  [ev_.ntau] =selectedtaujets.at(i)->PT;
                  ev_.tau_eta [ev_.ntau]=selectedtaujets.at(i)->Eta;
                  ev_.tau_phi [ev_.ntau]=selectedtaujets.at(i)->Phi;
                  ev_.tau_mass[ev_.ntau]=selectedtaujets.at(i)->Mass;
                  ev_.tau_ch[ev_.ntau]=selectedtaujets.at(i)->Charge;
                  ev_.tau_dm[ev_.ntau]=selectedtaujets.at(i)->Flavor; // not defined
                  ev_.tau_chargedIso[ev_.ntau]=0; // not defined
                  ev_.tau_sf[ev_.ntau]= 1; // jetsf.getSF(fabs(selectedtaujets.at(i)->Eta),selectedtaujets.at(i)->PT);
                  ev_.ntau++;
            }

		ev_.nj=0;
		for(size_t i=0;i<selectedjets.size();i++){
			if(ev_.nj>=MiniEvent_t::maxjets)break;
			ev_.j_pt  [ev_.nj] =selectedjets.at(i)->PT;
			ev_.j_eta [ev_.nj]=selectedjets.at(i)->Eta;
			ev_.j_phi [ev_.nj]=selectedjets.at(i)->Phi;
			ev_.j_mass[ev_.nj]=selectedjets.at(i)->Mass;

			ev_.j_flav[ev_.nj]=selectedjets.at(i)->Flavor;
			ev_.j_hadflav[ev_.nj]=selectedjets.at(i)->Flavor;

			ev_.j_deepcsv[ev_.nj]=0;
			ev_.j_mvav2[ev_.nj]=0;
			ev_.j_deepcsv[ev_.nj] = selectedjets.at(i)->BTag;
			ev_.j_mvav2[ev_.nj] = selectedjets.at(i)->BTag;
			ev_.j_sf[ev_.nj]=jetsf.getSF(fabs(selectedjets.at(i)->Eta),selectedjets.at(i)->PT);
			ev_.nj++;
		}

		ev_.nmet=0;
		if (hasPU){
		  for(size_t i=0;i<metPUPPI.size();i++){
		    if(ev_.nmet>=MiniEvent_t::maxpart) break;
		    ev_.met_eta[ev_.nmet]=metPUPPI.at(i)->Eta ;
		    ev_.met_pt [ev_.nmet]=metPUPPI.at(i)->MET ;
		    ev_.met_phi[ev_.nmet]=metPUPPI.at(i)->Phi ;
		    ev_.met_sf[ev_.nmet]=metsf.getSF(0,metPUPPI.at(i)->MET);
		    ev_.nmet++;
		  }
		}
		else {
		  for(size_t i=0;i<met.size();i++){
		    if(ev_.nmet>=MiniEvent_t::maxpart) break;
		    ev_.met_eta[ev_.nmet]=met.at(i)->Eta ;
		    ev_.met_pt [ev_.nmet]=met.at(i)->MET ;
		    ev_.met_phi[ev_.nmet]=met.at(i)->Phi ;
		    ev_.met_sf[ev_.nmet]=metsf.getSF(0,met.at(i)->MET);
		    ev_.nmet++;
		  }
		}



		t_event_->Fill();
		t_genParts_->Fill();
		t_genPhotons_->Fill();
		t_vertices_->Fill();
		t_genJets_->Fill();
		t_looseElecs_->Fill();
		t_mediumElecs_->Fill();
		t_tightElecs_->Fill();
		t_looseMuons_->Fill();
		t_tightMuons_->Fill();
		t_allTaus_->Fill();
		t_puppiJets_->Fill();
		t_puppiMET_->Fill();
		t_loosePhotons_->Fill();
		t_tightPhotons_->Fill();

	}

	counterdir->cd();
	h_event_weight->Write();

	ntupledir->cd();
	t_event_        ->Write();
	t_genParts_     ->Write();
	t_genPhotons_   ->Write();
	t_vertices_     ->Write();
	t_genJets_      ->Write();
	t_looseElecs_   ->Write();
	t_mediumElecs_   ->Write();
	t_tightElecs_   ->Write();
	t_looseMuons_   ->Write();
	t_tightMuons_   ->Write();
	t_allTaus_      ->Write();
	t_puppiJets_    ->Write();
	t_puppiMET_     ->Write();
	t_loosePhotons_ ->Write();
	t_tightPhotons_ ->Write();

	outfile->Close();
	/*
	 * Must be called in the end, takes care of thread-safe writeout and
	 * call-back to the parent process
	 */
	processEndFunction();
}



void ntupler::postProcess(){

	/* empty */

}



