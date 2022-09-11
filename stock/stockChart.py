# 2022/09/10

import matplotlib.pyplot as plt
from screeninfo import get_monitors  # Screen size

import pandas as pd

import sys
from yahoo_finance_api2 import share
from yahoo_finance_api2.exceptions import YahooFinanceError

import base64
from io import BytesIO


class StockChart:

    # get data and return chart image.

    def get(self, symbol):
        self.stockLoad(symbol)
        return self.stockFigure()


    def __init__(self, split=1, size=1, display=False):  # 初期化
        self.split = split

        for m in get_monitors():
            print(m.name, m.width, m.height)

        if display:
            plt.ion()  # Set pyplot to interactive mode
            self.fig = plt.figure(figsize=(int(m.width / 100 * size), int(m.height / 100 * size)), dpi=100
                             )  # Create a figure

            self.fig.canvas.manager.set_window_title('Chart')  # Title

            if self.split == 1:
                rows, columns = 1, 1
            elif self.split == 2:
                rows, columns = 1, 2
            elif self.split == 4:
                rows, columns = 2, 2
            elif self.split == 6:
                rows, columns = 2, 3
            elif self.split == 9:
                rows, columns = 3, 3

            self.axa = [self.fig.add_subplot(rows, columns, i + 1) for i in range(self.split)]

            self.axb = [self.axa[i].twinx() for i in range(self.split)]


    def close(self):
        plt.close()



    def stockLoad(self, symbolToQuery, period_day=7, freq_interval=5):  # Load new values from the net and calculate averages.

        myshare = share.Share(symbolToQuery)
        symbol_data = None

        try:
            symbol_data = myshare.get_historical( share.PERIOD_TYPE_DAY, period_day,
                share.FREQUENCY_TYPE_MINUTE, freq_interval)
        except YahooFinanceError as e:
            print(e.message)
            sys.exit(1)

        # print(symbol_data)

        self.df = pd.DataFrame(symbol_data)
        self.df["datetime"] = pd.to_datetime(self.df.timestamp, unit="ms")  # Readable to human.

        # Calculate moving averages and their differntials.
        # rowNo = self.df.shape[0]  # 0 for number for index
        #
        # for avhur in self.searchHour:  # Average in {avh} hours
        #     # Append columns for each avt hour-avarage
        #     for row in range(0, rowNo):  # for all rows
        #         average = self.df.loc[range(max(0, row - int(60 / freq_interval * avhur)), row + 1), "close"].mean()
        #         self.df.loc[row, str(avhur) + "hAv"] = average
        #
        # difinterval = 10
        # for ii in range(len(self.searchHour)):  # Average differential
        #     avhur = self.searchHour[ii]
        #     for row in range(difinterval, rowNo):  # for row 1 to the end
        #         diff = self.df.loc[row, str(avhur) + "hAv"] - self.df.loc[row - difinterval, str(avhur) + "hAv"]
        #         self.df.loc[row, str(avhur) + "hAvD"] = diff
        #
        # dif2interval = 30
        # for avhur in self.searchHour:  # Average differential
        #     for row in range(dif2interval, rowNo):  # for row 1 to the end
        #         diff = self.df.loc[row, str(avhur) + "hAvD"] - self.df.loc[row - dif2interval, str(avhur) + "hAvD"]
        #         self.df.loc[row, str(avhur) + "hAvD2"] = diff

        return


    def stockFigure(self, title=""):  # Draw figure
        # attributes of arrow
        arrowsColor = {"Buy": "yellow", "Sell": "red"}
        arrowsDirect = {"Buy": -0.1, "Sell": 0.1, "Other": 0.01}

        xmin, xmax = 0, self.df.shape[0]

        xTickList = self.beginingOfTheDayIndice(self.df)

        acount = 0      # Temporally this time.

        self.axa[acount].cla()      # Clear axis a, b
        self.axb[acount].cla()

        self.axb[acount].plot(self.df["close"], color="black")  # Stock price
        # dPlotb = [str(a) + "hAv" for a in brand.searchHour]
        # for dd in dPlotb:  # Average plot
        #     self.axb[acount].plot(self.df[dd], alpha=0.6, label=dd)
        #
        # dPlota = [str(a) + "hAvD" for a in brand.searchHour]  # Data to plot
        # for dd in dPlota:  # Parameters plot
        #     self.axa[acount].plot(self.df[dd], ls=":", alpha=0.4, label=dd)

        # Draw ticks
        self.axa[acount].set_xticks(xTickList)
        self.axa[acount].set_xticklabels(
            str(self.df.at[i, "datetime"].month) + str(self.df.at[i, "datetime"].day) for i in xTickList)
        self.axa[acount].tick_params(axis='both', which='both', length=0)

        # Title
        self.axa[acount].set_title(
            f"{title}  Title")

        self.axa[acount].hlines([0], xmin, xmax, "blue", linestyles='dashed', alpha=0.4)  # hlines

        # # Limit lines
        # for ll in brand.limits:
        #     self.axb[acount].hlines([ll], xmin, xmax, "red", linestyles='dashed', alpha=0.4)  # hlines

        # Sell over line !!!!Not in use!!
        # self.axb[acount].hlines(brand.sellOver, xmin, xmax, "yellow", linestyles='dashdot', alpha=0.6, label="Sell over")  # hlines

        # Buy under line !!!!Not in use!!
        # self.axb[acount].hlines(brand.buyUnder, xmin, xmax, "magenta", linestyles='dashdot', alpha=0.6, label="Buy under")  # hlines

        # Legends,  handsにはlabelが指定された曲線オブジェクトのリスト、 labsには対応するlabelのリストが入る
        hansa, labsa = self.axa[acount].get_legend_handles_labels()
        hansb, labsb = self.axb[acount].get_legend_handles_labels()

        self.axa[acount].legend(handles=hansa + hansb, labels=labsa + labsb, bbox_to_anchor=(0, 1),
                                loc='upper left')

        # Alert arrows
        # for alpoint in brand.alertList:
        #     # altimestamp, alvalue, aKindFull, repeat = alpoint
        #
        #     adf = brand.df.loc[brand.df["timestamp"] == alpoint["Timestamp"]]
        #     if len(adf.index) == 1:  # if there is a stored timestamp that matches
        #         alIndex = adf.index[0]
        #         ylimimts = self.axb[acount].get_ylim()
        #
        #         if 'Buy' in alpoint["Logic"]:
        #             aKind = 'Buy'
        #         elif 'Sell' in alpoint["Logic"]:
        #             aKind = 'Sell'
        #         else:
        #             aKind = 'Other'
        #
        #         plt.annotate(alpoint["Logic"] + '!' + str(alpoint["Repeat"]), xy=(alIndex, alpoint["Price"]),
        #                      xytext=(alIndex, alpoint["Price"] + arrowsDirect[aKind] * (ylimimts[1] - ylimimts[0])),
        #                      arrowprops=dict(shrink=0, width=1, headwidth=8,
        #                                      headlength=10, connectionstyle='arc3',
        #                                      facecolor=arrowsColor[aKind], edgecolor='gray')
        #                      )

        plt.pause(.001)

        return self.Output_Graph()

    def beginingOfTheDayIndice(self, df):       #Just for making ticks
        result = [];
        tday = 0

        for i in range(df.shape[0]):
            if tday != df.at[i, "datetime"].day:
                result.append(i)
                tday = df.at[i, "datetime"].day

        return result

    #プロットしたグラフを画像データとして出力するための関数
    def Output_Graph(self):
        buffer = BytesIO()                   #バイナリI/O(画像や音声データを取り扱う際に利用)
        plt.savefig(buffer, format="png")    #png形式の画像データを取り扱う
        buffer.seek(0)                       #ストリーム先頭のoffset byteに変更
        img = buffer.getvalue()            #バッファの全内容を含むbytes
        graph = base64.b64encode(img)        #画像ファイルをbase64でエンコード
        graph = graph.decode("utf-8")        #デコードして文字列から画像に変換
        buffer.close()
        return graph




if __name__ == "__main__":


    stockChart = StockChart(display=True)
    #
    # stockChart.stockLoad('4385.T')
    # figData = stockChart.stockFigure()

    stockChart.get('4385.T')

    print()

    exit(0)