#約定メールfileから読み込み 国内　Kabucom
# 2022/10/4
# 起動 変数を設定 [ $filePath; 値:Get(ファイルパス) ] レイアウト切り替え [ 「Transactions」 (Transactions) ]

import glob
import re

tranMailFolder = "/Users/kunieda/Dropbox/StockExecute/tranMail/*.txt"       # Text files

class StockMail():
    def getFromText(self, text):
        result={}
        trade=Trade()
        matchObject = re.search("\d\d\d\d/\d\d/\d\d",text)
        result['tdate'] = matchObject.group()
        text = text[matchObject.end():]

        matchObject = re.search("\d\d:\d\d:\d\d", text)
        result['ttime'] = matchObject.group()
        text = text[matchObject.end():]

        matchObject = re.search("\d\d\d\d", text)
        result['symbol'] = matchObject.group()
        text = text[matchObject.end():]

        matchObject = re.search("／.+\n", text)
        result['symbolName'] = matchObject.group()[1:-1]
        text = text[matchObject.end():]

        matchObject = re.search(".+／", text)
        result['sellbuy'] = matchObject.group()[:-1]
        text = text[matchObject.end():]

        matchObject = re.search("[\d,]+", text)
        result['price'] = matchObject.group().replace(',','')
        text = text[matchObject.end():]

        matchObject = re.search("[\d,]+", text)
        result['qty'] = matchObject.group().replace(',','')
        text = text[matchObject.end():]

        matchObject = re.search("[\d,]+", text)
        result['total'] = matchObject.group().replace(',','')
        text = text[matchObject.end():]


        return result


    def getFromMailSave(self, folderName):
        # フォルダーにあるすべてのファイルをレコードに読み込む
        files = glob.glob(folderName)
        for file in files:
            print(file)
            f=open(file,"r")
            fileContent = f.read()
            # 取り出し



if __name__ == "__main__":
    f= open("./test.txt","r")
    itext = f.read()
    stockMail=StockMail()
    # stockMail.getFromMailSave(tranMailFolder)
    aa = stockMail.getFromText(itext)
    print (aa)
#
# フィールドへ移動 [ Transactions::Tinput ]
# 変数を設定 [ $MailText; 値:Trim ( Transactions::Tinput) ] If [ Left ( $MailText;12) = "約定アラートメールです。" ]
# #マネックスの取引
# 変数を設定 [ $message; 値:"Manex" ]
# スクリプト実行 [ 「GetFromMailManex」 ]
# スクリプト実行 [ 「subLog」; 引数: Left ( $message & " : " & $MailText;12) ]
# レコード/検索条件/ページへ移動
# [ 次の; 最後まできたら終了 ]
# Else If [ Left ( $MailText;12) = "■【auKabucom】" ] #株コムの取引
# 変数を設定 [ $message; 値:"KabKom" ]
# スクリプト実行 [ 「GetFromMailKcom」 ]
# スクリプト実行 [ 「subLog」; 引数: Left ( $MailText;12) ]
# レコード/検索条件/ページへ移動
# [ 次の; 最後まできたら終了 ]
# Else
# End If End Loop
# // カスタムダイアログを表示 [ タイトル: $message; メッセージ: Transactions::銘柄名 & " " & Transactions::取引 & " " & Transactions::数量; デフォルトボタン: 「OK」, 確定: 「はい」 ]
#      #取引のファイルでないので消去
# レコード/検索条件削除
# [ ダイアログなし ]
# スクリプト実行 [ 「subLog」; 引数: "No Trade file!" ] Exit Loop If [ Get (対象レコード数) = 0 ]
# 2022年10月3日 6:06:38 StockTrade.fmp12 - GetFromMailSave -1-
#
#
# GetFromMailKcom
# #カブコム約定メールから読み込みサブスクリプト
# フィールドへ移動 [ Transactions::Tinput ]
# 変数を設定 [ $MailText; 値:Trim ( Transactions::Tinput) ]
# #約定日
# // 変数を設定 [ $MailText; 値:Middle ( $MailText ; Position ( $MailText ; "[約定結果]" ; 1 ; 1 );1000) ] 変数を設定 [ $MailText; 値:Middle ( $MailText ; Position ( $MailText ; "約定しました。" ; 1 ; 1 );1000) ] 変数を設定 [ $MailText; 値:Middle ( $MailText ; Position ( $MailText ; "20" ; 1 ; 1 );1000) ]
# 変数を設定 [ $dateText; 値:Left ( $MailText ; 10 ) ]
# フィールド設定 [ Transactions::約定日; GetAsDate ( $dateText ) ]
# #”/”を基準にCode、銘柄を取得
# // 変数を設定 [ $textPos; 値:Position ( $MailText ; "/" ; 2 ; 1 ) ]
# // 変数を設定 [ $MailText; 値:Middle ( $MailText ; Position ( $MailText ; "[銘柄]" ; 1 ; 1 );1000) ]
# フィールド設定 [ Transactions::銘柄コード; MiddleWords ( $MailText ; 4 ; 1 ) ]
# フィールド設定 [ Transactions::銘柄名; MiddleWords ( $MailText ; 5 ; 1 ) ]
# フィールド設定 [ Transactions::取引; MiddleWords ( $MailText ; 6 ; 1 ) ]
# 変数を設定 [ $MailText; 値:Middle ( $MailText ; Position ( $MailText ; "単価" ; 1 ; 1 )+2;1000) ] フィールド設定 [ Transactions::単価; MiddleWords ( $MailText ; 1 ; 1 ) ]
# 変数を設定 [ $MailText; 値:Middle ( $MailText ; Position ( $MailText ; "数量" ; 1 ; 1 )+2;1000) ] フィールド設定 [ Transactions::数量; MiddleWords ( $MailText ; 1 ; 1 ) ]
# 変数を設定 [ $MailText; 値:Middle ( $MailText ; Position ( $MailText ; "金額" ; 1 ; 1 );1000) ] フィールド設定 [ Transactions::受渡金額; MiddleWords ( $MailText ; 2 ; 1 ) ]
# If [ Transactions::取引 = "現物買" ]
# フィールド設定 [ Transactions::受渡金額; Transactions::受渡金額  * -1 ] End If
# #Set the values
# フィールド設定 [ Transactions::商品; "株式" ] フィールド設定 [ Transactions::Account; "KabuKom" ]
#             2022年10月3日 6:00:27 StockTrade.fmp12 - GetFromMailKcom -1-
#
