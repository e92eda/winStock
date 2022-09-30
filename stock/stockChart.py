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



    def stockLoad(self, symbolToQuery, period=7, period_type='day'):  # Load new values from the net and calculate averages.

        myshare = share.Share(symbolToQuery)
        symbol_data = None
        # get_historical(period_type, period, frequency_type, frequency)
        # period type (share.PERIOD_TYPE_DAY, share.PERIOD_TYPE_WEEK, share.PERIOD_TYPE_MONTH, share.PERIOD_TYPE_YEAR),
        # period (1, 5, 10, etc.), frequency_type (share.FREQUENCY_TYPE_MINUTE, share.FREQUENCY_TYPE_DAY, share.FREQUENCY_TYPE_MONTH, share.FREQUENCY_TYPE_YEAR),
        # and frequency (1, 5, 10, etc.).Only certain combinations of these parameters are allowed.
        if period_type=='day':
            period_type = share.PERIOD_TYPE_DAY
            frequency_type = share.FREQUENCY_TYPE_MINUTE
            freq_interval = 5

        elif period_type=='week':
            period_type = share.PERIOD_TYPE_WEEK
            frequency_type = share.FREQUENCY_TYPE_MINUTE
            freq_interval = 60

        elif period_type=='month':
            period_type = share.PERIOD_TYPE_MONTH
            frequency_type = share.FREQUENCY_TYPE_DAY
            freq_interval = 1

        else:       # if period_type=='year':
            period_type = share.PERIOD_TYPE_YEAR
            frequency_type = share.FREQUENCY_TYPE_DAY
            freq_interval = 1


        try:
            symbol_data = myshare.get_historical( period_type, period, frequency_type, freq_interval)
        except YahooFinanceError as e:
            print(e.message)
            sys.exit(1)

        self.df = pd.DataFrame(symbol_data)
        self.df["datetime"] = pd.to_datetime(self.df.timestamp, unit="ms")  # Readable to human.


    def stockFigure(self, title="Title", arrow = []):  # Draw figure

        plt.rcParams["font.size"] = 18      #　font size 指定

        # attributes of arrow
        arrowsColor = {"Buy": "blue", "Sell": "red"}
        arrowsDirect = {"Buy": -0.1, "Sell": 0.1, "Other": 0.01}

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
        self.axa[acount].set_title(f"<< {title} >>")

        self.axa[acount].hlines([0], xmin, xmax, "blue", linestyles='dashed', alpha=0.4)  # hlines


        # Legends,  handsにはlabelが指定された曲線オブジェクトのリスト、 labsには対応するlabelのリストが入る
        hansa, labsa = self.axa[acount].get_legend_handles_labels()
        hansb, labsb = self.axb[acount].get_legend_handles_labels()

        self.axa[acount].legend(handles=hansa + hansb, labels=labsa + labsb, bbox_to_anchor=(0, 1),
                                loc='upper left')

        # Trade arrows
        for alpoint in arrow:

            # adf = brand.df.loc[brand.df["timestamp"] == alpoint["Timestamp"]]
            # if len(adf.index) == 1:  # if there is a stored timestamp that matches
            #     alIndex = adf.index[0]
            #     ylimimts = self.axb[acount].get_ylim()
            #
                if alpoint['side'] == 1:
                    aKind = 'Sell'
                elif alpoint['side'] == 2:
                    aKind = 'Buy'
                else:
                    aKind = 'Other'

                xminTimestamp = self.df["timestamp"][xmin]
                xmaxTimestamp = self.df["timestamp"][xmax-1]
                xTimestamp = pd.Timestamp(alpoint['x']).value/1000000

                xIndex = int(xmin + (xmax-xmin)/(xmaxTimestamp-xminTimestamp)*(xTimestamp-xminTimestamp))

                if xIndex>=xmin and xIndex<=xmax:


                    self.df["timestamp"]
                    plt.annotate(alpoint['qty'], xy=(xIndex, alpoint['y']), size=15, color=arrowsColor[aKind],arrowprops=dict(shrink=0, width=1, headwidth=8,
                                                 headlength=10, connectionstyle='arc3',
                                                 facecolor=arrowsColor[aKind], edgecolor='gray')
                                  )

                # plt.annotate(alpoint["Logic"] + '!' + str(alpoint["Repeat"]), xy=(alIndex, alpoint["Price"]),
                #              xytext=(alIndex, alpoint["Price"] + arrowsDirect[aKind] * (ylimimts[1] - ylimimts[0])),
                #              arrowprops=dict(shrink=0, width=1, headwidth=8,
                #                              headlength=10, connectionstyle='arc3',
                #                              facecolor=arrowsColor[aKind], edgecolor='gray')
                #              )

        return self.fig



    def beginingOfTheDayIndice(self, df):       #Just for making ticks
        result = [];
        tday = 0        # To make tick at the beginning of a day.


        for i in range(df.shape[0]):
            if tday != df.at[i, "datetime"].day:
                result.append(i)
                tday = df.at[i, "datetime"].day


        size = len(result)
        skip = int(size/ 10)  # reduce the size if too big.
        i = 0
        sresult = []
        while i < size:
            sresult.append(result[i])
            i += skip + 1


        return sresult

    # def drawAllows(self, symbolForDisplay):
    #     # symbolForDisplay = self.kwargs['pk']  # Requestの後に、pK（この場合表示すべき銘柄Symbol）がついている場合
    #     trades = Trade.objects.filter(Symbol=symbolForDisplay).order_by(
    #         '-created_at')  # .filter(user=self.request.user)        return trades


if __name__ == "__main__":

    stockChart = StockChart(display=True)

    stockChart.stockLoad('4385.T')
    figPlt = stockChart.stockFigure()

    figPlt.savefig("img.png")

    exit(0)