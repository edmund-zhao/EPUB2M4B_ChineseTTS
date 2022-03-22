import glob
import zipfile
import cn2an
import os
from pydub import AudioSegment

def uncompress(path, novelName=None):
    zip_file = zipfile.ZipFile(path)
    zip_list = zip_file.namelist()  # 得到压缩包里所有文件
    if novelName is None:
        novelName = path.split('/')[-1][:-5]
    for f in zip_list:
        zip_file.extract(f, './{}'.format(novelName))  # 循环解压文件到指定目录
    zip_file.close()  # 关闭文件，必须有，释放内存

def num2char(all_list):
    output = []
    for i in all_list:
        output.append(cn2an.transform(i, "an2cn"))
    return output

def wav2mp3(filepath, savepath, bookid=0):
    if not os.path.exists(savepath):
        os.makedirs(savepath, mode = 0o777)
    sourcefile = AudioSegment.from_wav(filepath)
    filename = "%05d.mp3"%bookid 
    #filename = "%05d_"%bookid + filepath.split('/')[-1][:-4] + '.mp3'
    print(filename)
    sourcefile.export(savepath + filename, format="mp3", bitrate='64k')
def getChapterTxt(fileDir):
    times = 0
    text = ""
    for i in sorted(glob.glob(fileDir+'/*.mp3'), key=os.path.getmtime):
        sound_time = times
        h = sound_time // 3600
        m = (sound_time - h * 3600) // 60
        s = (sound_time - h * 3600 - m * 60)
        t = "%02d:%02d:%02.03f "%(h,m,s) + i.split('/')[-1][:-4] + '\n'
        text += t
        sound = AudioSegment.from_file(i)
        times += sound.duration_seconds
    with open('./chapters.txt','w',encoding='utf-8') as f:
        f.write(text)