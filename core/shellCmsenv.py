import os

if 'bash' in os.environ['SHELL']:
    cmsenvCommand = 'eval `scramv1 runtime -sh`'
elif 'tcsh' in os.environ['SHELL']:
    cmsenvCommand = 'eval `scramv1 runtime -csh`'
else:
    raise RuntimeError("Unknown shell")