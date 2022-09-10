# 2022/09/10

import matplotlib.pyplot as plt
from screeninfo import get_monitors  # Screen size

import pandas as pd

import sys
from yahoo_finance_api2 import share
from yahoo_finance_api2.exceptions import YahooFinanceError


class StockChart:

    def __init__(self, split=4, size=1, display=False):  # 初期化
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

    def chartDraw(symbol):
        return

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

    def stockDisplay(self):



if __name__ == "__main__":

    stockChart = StockChart(display=True)

    result = stockChart.stockLoad('4385.T')