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




    def __init__(self, split=1, size=1, display=True):  # 初期化
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


    def getChart(self, symbol): # Not in use.
        self.stockLoad(self, symbol)
        return self.stockFigure()


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



    def stockFigure(self, title=""):  # Draw figure
        # attributes of arrow

        xmin, xmax = 0, self.df.shape[0]

        xTickList = self.beginingOfTheDayIndice(self.df)

        acount = 0      # Temporally this time.

        self.axa[acount].cla()      # Clear axis a, b
        self.axb[acount].cla()

        self.axb[acount].plot(self.df["close"], color="black")  # Stock price

        # Draw ticks
        self.axa[acount].set_xticks(xTickList)
        self.axa[acount].set_xticklabels(
            str(self.df.at[i, "datetime"].month) + '/' + str(self.df.at[i, "datetime"].day) for i in xTickList)
        self.axa[acount].tick_params(axis='both', which='both', length=0)

        # Title
        self.axa[acount].set_title(f"{title}  Title", title)

        self.axa[acount].hlines([0], xmin, xmax, "blue", linestyles='dashed', alpha=0.4)  # hlines


        # Legends,  handsにはlabelが指定された曲線オブジェクトのリスト、 labsには対応するlabelのリストが入る
        hansa, labsa = self.axa[acount].get_legend_handles_labels()
        hansb, labsb = self.axb[acount].get_legend_handles_labels()

        self.axa[acount].legend(handles=hansa + hansb, labels=labsa + labsb, bbox_to_anchor=(0, 1),
                                loc='upper left')


        # plt.pause(.001)

        return self.fig



    def beginingOfTheDayIndice(self, df):       #Just for making ticks
        result = [];
        tday = 0

        for i in range(df.shape[0]):
            if tday != df.at[i, "datetime"].day:
                result.append(i)
                tday = df.at[i, "datetime"].day

        return result





if __name__ == "__main__":

    stockChart = StockChart(display=True)

    stockChart.stockLoad('4385.T')
    figPlt = stockChart.stockFigure()

    figPlt.savefig("img.png")

    exit(0)