#!/usr/bin/env bash

NTUPLE_LOCATION=$1
RETURN_LOCATION=$PWD

cd $NTUPLE_LOCATION
cmsenv

cmsDriver.py step1 \
    -n 10000 \
    --nThreads 8 \
    --conditions 125X_mcRun4_realistic_v2 \
    --era Phase2C17I13M9 \
    --geometry Extended2026D88 \
    --eventcontent FEVTDEBUGHLT \
    -s RAW2DIGI,L1TrackTrigger,L1 \
    --datatier GEN-SIM-DIGI-RAW-MINIAOD \
    --fileout file:test.root \
    --customise "SLHCUpgradeSimulations/Configuration/aging.customise_aging_1000,Configuration/DataProcessing/Utils.addMonitoring,L1Trigger/Configuration/customisePhase2.addHcalTriggerPrimitives,L1Trigger/Configuration/customisePhase2FEVTDEBUGHLT.customisePhase2FEVTDEBUGHLT,L1Trigger/Configuration/customisePhase2TTNoMC.customisePhase2TTNoMC" \
    --filein "/store/mc/Phase2Fall22DRMiniAOD/TT_TuneCP5_14TeV-powheg-pythia8/GEN-SIM-DIGI-RAW-MINIAOD/PU200_125X_mcRun4_realistic_v2_ext1-v1/30000/000c5e5f-78f7-44ee-95fe-7b2f2c2e2312.root" \
    --mc \
    --customise_commands="process.source.inputCommands = cms.untracked.vstring(\"keep *\", \"drop l1tPFJets_*_*_*\")"

cd $RETURN_LOCATION