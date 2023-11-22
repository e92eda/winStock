#kabuStStart.py
# Kabu Station auto start
#https://www.stockinvestment.blog/?p=928
# 2023/10/21
# Modified by E.Kunieda

import webbrowser
import pyautogui
import time,os

#pyautogui.FAILSAFE = False

# 開くURL
url = 'http://download.r10.kabu.co.jp/kabustation/KabuStation.application'

# ブラウザの表示モード（0:開いているウィンドウで開く、1:新規ウィンドウで開く、2新しいタブで開く）
window_open_mode = 1

# 開くブラウザを指定
browser = webbrowser.get("'C:/Program Files/internet explorer/iexplore.exe' %s") #IE

#browser = webbrowser.get("'C:\Program Files\Google\Chrome\Application\chrome.exe' %s")
#browser = webbrowser.get("'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe' %s")
print( browser )

browser.open(url ,window_open_mode, True)
print("起動が完了するまで待つ!")
time.sleep(7) #起動が完了するまで待つ。
print("まった!")
pyautogui.typewrite(os.environ.get('KS_PASSWORD'))  #KSパスワード　ログインIDは記録させておくため入力しない
pyautogui.typewrite("\n")
