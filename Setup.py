import sys
import os
answer = ''
os.system('@echo off')
for i in sys.path:
    if i and '.' not in i:
        this = ''
        os.chdir(i)
        print(i)
        this += os.popen('python -m pip install --upgrade pip -i https://pypi.douban.com/simple').read()
        this += os.popen('python -m pip install pygame pygame-pgu -i https://pypi.douban.com/simple').read()
        this += os.popen('python -m pip install pygame pygame-pgu -i https://pypi.douban.com/simple --upgrade').read()
        answer += this
        if '不是' not in this:
            print(this)
        if 'Requirement already' in answer:
            break
print('OK') 
os.system('pause')
