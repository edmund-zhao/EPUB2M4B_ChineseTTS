import glob
import os

import util

outputPath = input('OutPut Path:')

for bookid, item in enumerate(sorted(glob.glob('./output/*.wav'), key=os.path.getmtime)):
    util.wav2mp3(item, outputPath, bookid)