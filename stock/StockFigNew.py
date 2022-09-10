#
# Stock disply
# 2021/06/01

import matplotlib.pyplot as plt
import time, datetime
import Brandd
import json
import os
from screeninfo import get_monitors  # Screen size
import globals



class StockFigNew:

    stopSw = False  # Class variable
    figSize = 0     # Figure size

    def __init__(self, interval = 300, days = 7, split = 4, size = 1, display = True):  # 初期化
        self.interval = interval
        self.days = days
        self.split = split
        self.fig = False        # When Display mode, this variable will be set later.
        if split not in [1, 2, 4, 6,9]:
            print ( f"split {split} is wrong!")
            exit()

        self.triger = interval / 5  # Triger timing from the each repeat period.

        for m in get_monitors():
            print(m.name, m.width, m.height)

        # figures set
        if display!= None:
            plt.ion()  # Set pyplot to interactive mode
            self.fig = plt.figure(figsize=(int(m.width / 100 * size), int(m.height / 100 * size)), dpi=100
                             )  # Create a figure

            self.fig.canvas.manager.set_window_title(f' debug:{globals.debug}')      # Title

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

        self.done = False  # flag for triger
        self.count = 0
        self.scount = 0
        self.wcount = 0
        self.first = True
        self.preTimer = 0

        StockFigs.stopSw = not display      # Class variable

    def close(self):
        plt.close()


    def reflesh(self, inputf = "./data/_stockbrands.json"):

        acount = self.scount % self.split     # Axis count for figures

        if globals.debug:
            print (f"Refresh at {datetime.datetime.now()}!! count:{self.count}, scount:{self.scount}, acount:{acount}, wcount:{self.wcount}, preTImer:{self.preTimer:.2f}")
        else:
            print('.', end='')

        if self.first or not self.done and (time.time() % self.interval) > self.triger:   # Once in the interval, request read data.

            self.count += 1
            print(" Do Load and Culc! Count:", self.count, time.ctime(time.time()))

            (jsonData,jsonTrade) = self.jsonRoadsTwo(inputf)    # Read brands and Trades

            # update bland list
            jcodeList = [j['code'] for j in jsonData]

            for brandData in jsonData:
                found = False
                for b in Brandd.Brand.brandslist:
                    if b.code == brandData['code']:
                        Brandd.Brand.update(b, brandData)  # the brand exist in the list, so update it.
                        found = True
                if not found:
                    br=Brandd.Brand(brandData)         # Create a new instance and append it to the list.
                    message = f'Brand {br.code}:{br.name}  appended to the list.'
                    print(message)
                    if not globals.debug and globals.linesend:
                        globals.lineSend(message)

                tlist = []
                for brand in Brandd.Brand.brandslist:
                    if brand.code in jcodeList:
                        tlist.append(brand)
                    else:
                        message = f"Remove {brand.code}"
                        print(message)
                        if not globals.debug and globals.linesend:
                            globals.lineSend(message)

                Brandd.Brand.brandslist = tlist


            for brand in Brandd.Brand.brandslist:

                #if brand.operationTime() or globalvals.debug or self.first:  # Check Market operation time.
                now = datetime.datetime.now()
                miniutesNow = now.minute
                if globals.debug or not brand.slowMode or miniutesNow % 30 < self.interval/60: # check the state every 30 minutes. self.interval is in sccond

                    brand.loadAndCalc(period_day=self.days)    # Get data from the net and calculate averages.

                    if brand.timeStampSame():
                        print("The timestamp is different from the previous one. Get into the slowMode.")
                        brand.slowMode = True
                    else:
                        brand.slowMode = False

                    brand.StockAlarm(jsonTrade) # Check alert conditions.

                else:
                    #if globalvals.debug:
                    print ( f'{now} Brand {brand.name} is in slowMode.')



            ############# Currently not used.
            # # Load jsonTrade data
            # for jTrade in jsonTrade:
            #     print (jTrade)

            self.scount = 0     # Counter for the stock to draw.
            self.wcount = 0     # Alternative counter for waiting for a while.
            self.done = True
            self.first = False

        # For every path
        if self.scount >= len(Brandd.Brand.brandslist):     #Reset self.scount
            self.scount = 0

        brand = Brandd.Brand.brandslist[self.scount]    # Deploy a brand to process

        if not StockFigs.stopSw:     #If the class variable Sw is TRUE, do not draw figures
            # Draw figure
            self.drawFigure(brand, acount)

# Counters increment
        if (acount >= self.split -1) and self.wcount < 4:
            self.wcount += 1        # Wait for 3 paths

        else:
            self.wcount = 0
            self.scount += 1
            if self.scount >= len(Brandd.Brand.brandslist):
                self.scount = 0

# Timer reset.
        ctimer = time.time() % self.interval
 #       print ("ctimer, prev:", ctimer,self.preTimer)
        if ctimer < self.preTimer:  # Reset timer
            self.done = False
            print("Reset timer!")

        self.preTimer = ctimer
        print(end=".")



    def drawFigure(self, brand, acount, title=""):     # Draw figure
        # attributes of arrow
        arrowsColor = {"Buy":"yellow","Sell":"red"}
        arrowsDirect = {"Buy":-0.1,"Sell":0.1,"Other":0.01}

        xmin, xmax = 0, brand.df.shape[0]

        xTickList = self.beginingOfTheDayIndice(brand.df)


        self.axa[acount].cla()
        self.axb[acount].cla()


        self.axb[acount].plot(brand.df["close"], color="black")     # Stock price
        dPlotb = [str(a) + "hAv" for a in brand.searchHour]
        for dd in dPlotb: #Average plot
            self.axb[acount].plot(brand.df[dd], alpha=0.6,  label=dd)

        dPlota = [str(a) + "hAvD" for a in brand.searchHour]     # Data to plot
        for dd in dPlota: #Parameters plot
            self.axa[acount].plot(brand.df[dd], ls=":", alpha=0.4, label=dd)

        # Draw ticks
        self.axa[acount].set_xticks(xTickList)
        self.axa[acount].set_xticklabels(
            str(brand.df.at[i, "datetime"].month) + str(brand.df.at[i, "datetime"].day) for i in xTickList)
        self.axa[acount].tick_params(axis='both', which='both', length=0)

        # Title
        self.axa[acount].set_title(f"{brand.code} {brand.name}:{brand.remainCash} + {brand.stockVolume} * {brand.currentPrice} = {brand.remainCash + brand.stockVolume * brand.currentPrice}")

        self.axa[acount].hlines([0], xmin, xmax, "blue", linestyles='dashed', alpha=0.4)  # hlines


        # # Limit lines
        # for ll in brand.limits:
        #     self.axb[acount].hlines([ll], xmin, xmax, "red", linestyles='dashed', alpha=0.4)  # hlines

        # Sell over line !!!!Not in use!!
        #self.axb[acount].hlines(brand.sellOver, xmin, xmax, "yellow", linestyles='dashdot', alpha=0.6, label="Sell over")  # hlines

        # Buy under line !!!!Not in use!!
        #self.axb[acount].hlines(brand.buyUnder, xmin, xmax, "magenta", linestyles='dashdot', alpha=0.6, label="Buy under")  # hlines

        # Legends,  handsにはlabelが指定された曲線オブジェクトのリスト、 labsには対応するlabelのリストが入る
        hansa, labsa = self.axa[acount].get_legend_handles_labels()
        hansb, labsb = self.axb[acount].get_legend_handles_labels()

        self.axa[acount].legend(handles=hansa+hansb, labels=labsa+labsb,bbox_to_anchor=(0, 1), loc='upper left')

        #Alert arrows
        for alpoint in brand.alertList:
            #altimestamp, alvalue, aKindFull, repeat = alpoint

            adf = brand.df.loc[brand.df["timestamp"]==alpoint["Timestamp"]]
            if len(adf.index) == 1:     # if there is a stored timestamp that matches
                alIndex = adf.index[0]
                ylimimts = self.axb[acount].get_ylim()

                if 'Buy' in alpoint["Logic"]:
                    aKind = 'Buy'
                elif 'Sell' in alpoint["Logic"]:
                    aKind = 'Sell'
                else:
                    aKind = 'Other'

                plt.annotate(alpoint["Logic"]+'!'+str(alpoint["Repeat"]), xy=(alIndex,alpoint["Price"]), xytext=(alIndex,alpoint["Price"] + arrowsDirect[aKind] * (ylimimts[1]-ylimimts[0])),
                             arrowprops=dict(shrink=0, width=1, headwidth=8,
                                             headlength=10, connectionstyle='arc3',
                                             facecolor=arrowsColor[aKind], edgecolor='gray')
                             )


        plt.pause(.001)


    def beginingOfTheDayIndice(self, df):       #Just for making ticks
        result = [];
        tday = 0

        for i in range(df.shape[0]):
            if tday != df.at[i, "datetime"].day:
                result.append(i)
                tday = df.at[i, "datetime"].day

        return result


    def jsonRoadsTwo(self, filename):       #Read brand data and trade data from two files.

    # jsonTradeの形式
    # {"Tid":"2021/09/29 6:48:18","code":"6113.T","limit":1180,"logic":"ImSell","mode":"","name":"アマダ","repeat":0,"volume":1300}


        jsonData = self.jsonRead(filename)

        jsonTrade = self.jsonRead(filename.replace(".json", "T.json"))  # Trade conditions

        for brandData in jsonData:
            # marge trade conditions to the jsonData
            brandData["condList"] = [cc
                                     for cc in jsonTrade if
                                     cc['code'] == brandData['code']]  # marge trade conditions to the jsonData

        return (jsonData, jsonTrade)


    def jsonRead(self, filename):       # Read blands
        if os.path.isfile(filename):
            os.chmod(filename, 444)     # Read only

            json_open = open(filename, 'r')
            json_load = json.load(json_open)
            json_open.close()

            os.chmod(filename, 666)     # Read write
        else:
            print (f'File {filename} dose not exit!')
            exit(1)

        return json_load


    def operationTime(self):        # In market operation time?

        now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))  # 日本時刻
        r = (9<= now.hour <15) and now.weekday()<5
        return r

    def stopResume(self):     # Stop and resume disply reflesh
        self.stopSw = not self.stopSw


if __name__ == "__main__":

