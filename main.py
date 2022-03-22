import util
import re
import glob
import TTSM
from bs4 import BeautifulSoup

def exact_p_tag(path):
    all_list = []
    # repc = re.compile('<p+.*?>([\s\S]*?)</p*?>')
    # rept = re.compile('<title+.*?>([\s\S]*?)</title*?>')
    xhtml_file = open(path, 'r', encoding='utf-8')
    xhtml_handle = xhtml_file.read()
    soup = BeautifulSoup(xhtml_handle, 'lxml')
    title = soup.find_all('h1')

    p_list = soup.find_all('p')
    for t in title:
        all_list.append(t.get_text())
    for p in p_list:
        all_list.append(p.get_text())

    xhtml_file.close()

    # 由于模型原因，需要将数字转化为中文
    all_list = util.num2char(all_list)
    print(all_list[0])
    return all_list

filePath = '变身反派女主的我被美少女们纠缠.epub'
fileName = '变身反派女主的我被美少女们纠缠'
util.uncompress(filePath, fileName)

for xhtml in sorted(glob.glob(fileName+'/EPUB/chapter*.xhtml')):
    text_list = exact_p_tag(xhtml)
    TTSM.run(text_list)
