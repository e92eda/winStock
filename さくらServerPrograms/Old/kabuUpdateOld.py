# Database kabudb tabbles: postions, orders update
# 2023/10/21,11/5,15
#               E.Kunieda


#  MySQL へ接続
# !pip install PyMySQL

import pymysql

import urllib.request
import json, os
import pprint
import time, datetime


def generate_token():  # Kabu Station API トークン発行
    obj = {'APIPassword': 'e2092eda'}
    json_data = json.dumps(obj).encode('utf8')

    url = 'http://localhost:18080/kabusapi/token'
    req = urllib.request.Request(url, json_data, method='POST')
    req.add_header('Content-Type', 'application/json')

    try:
        with urllib.request.urlopen(req) as res:
            content = json.loads(res.read())
            token_value = content.get('Token')
            pprint.pprint(token_value)
    except urllib.error.HTTPError as e:
        print(e)
        content = json.loads(e.read())
        pprint.pprint(content)
    return token_value


def get_positions(token):  # 残高照会
    url_symbol = 'http://localhost:18080/kabusapi/positions'
    req_symbol = urllib.request.Request(url_symbol, method='GET')
    req_symbol.add_header('X-API-KEY', token)

    try:
        with urllib.request.urlopen(req_symbol) as res_symbol:
            content_symbol = json.loads(res_symbol.read())
    #            pprint.pprint(content_symbol)
    except urllib.error.HTTPError as e_symbol:
        print(e_symbol)
        content_symbol = json.loads(e_symbol.read())
    return content_symbol


def get_orders(token):  # 注文約定照会
    url_symbol = 'http://localhost:18080/kabusapi/orders'
    req_symbol = urllib.request.Request(url_symbol, method='GET')
    req_symbol.add_header('X-API-KEY', token)

    try:
        with urllib.request.urlopen(req_symbol) as res_symbol:
            content_symbol = json.loads(res_symbol.read())
    #            pprint.pprint(content_symbol)
    except urllib.error.HTTPError as e_symbol:
        print(e_symbol)
        content_symbol = json.loads(e_symbol.read())
    return content_symbol


# 　MySQL db table posittions すべて消す
# def deletePositions(connection):
#     cur = connection.cursor()
#     sql = "TRUNCATE TABLE `stock_stock`"
#     cur.execute(sql)
#     result = cur.fetchall()


# MySQL db table stock_stockにpositionsリスト更新登録
def insertPositions(connection, positions):
    cur = connection.cursor()
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

    # Kabu Stationから
    values = []
    for apos in positions:
        apost = tuple(apos.values())
        apostt = apost + (True, 7, "day", 1, now, now)

        values.append(apostt)

####Insert update
    sql = ('''
    INSERT INTO stock_stock 
            (ExecutionID, AccountType, Symbol, SymbolName, Exchange, ExchangeName, Price, LeavesQty, HoldQty, Side, CurrentPrice, Valuation, ProfitLoss, ProfitLossRate,holding, period,period_type,user_id,
            created_at, updated_at)
    VALUES 
            (%s,%s,%s,%s,%s, %s,%s,%s,%s,%s, %s,%s,%s,%s,%s, %s,%s,%s,%s,%s)

    ON DUPLICATE KEY UPDATE CurrentPrice = VALUES(CurrentPrice), Valuation = VALUES(Valuation),
    ProfitLoss = VALUES(ProfitLoss), ProfitLossRate = VALUES(ProfitLossRate)\
    ,holding = VALUES(holding), updated_at = VALUES(updated_at)
    ''')

    cur.executemany(sql, values)
    connection.commit()


# MySQL db table stock_Orderに登録
def insertOrders(connection, orders):
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

    cur = connection.cursor()
    values = []
    for apos in orders:
        details = apos.pop('Details')  # Details は邪魔で悪さをする。抜き出す。
        meanPrice = meanPriceGet( details)  #   Price, 'Qty から平均価格をget
        apos['Price'] = meanPrice           # Price に戻す。
        values.append(tuple(apos.values())+(now, now))

    print(values)
    sql = ('''
    INSERT INTO stock_order 
            (ID, State, OrderState, OrdType, RecvTime, Symbol, SymbolName, Exchange, ExchangeName, Price, OrderQty, CumQty, Side, AccountType, DelivType, ExpireDay,
            created_at, updated_at)
    VALUES 
            (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
            %s,%s)
    ON DUPLICATE KEY UPDATE
            State = VALUES(State),
            OrderState= VALUES(OrderState), 
            OrdType = VALUES(OrdType), 
            RecvTime = VALUES(RecvTime), Price = VALUES(Price), OrderQty = VALUES(OrderQty), CumQty = VALUES(CumQty), Side = VALUES(Side), DelivType = VALUES(DelivType),
            ExpireDay = VALUES(ExpireDay),
            updated_at = VALUES(updated_at)
    ''')

    cur.executemany(sql, values)
    connection.commit()

def meanPriceGet( details ):
    sumPrice = 0
    sumQty = 0
    for det in details:
        if det['Price'] != 0.:
            sumPrice += det['Price'] * det['Qty']
            sumQty += det['Qty']

        if sumQty == 0:
            meanPrice = 0.
        else:
            meanPrice = sumPrice/sumQty
    return meanPrice

##### Main ####

# トークン発行
token_value = generate_token()
# 残高照会
positions = get_positions(token_value)

# Order query
orders = get_orders(token_value)

# 　mySQL stockdbローカル接続
connection = pymysql.connect(host='localhost',
                             user='kunieda',
                             password=os.environ.get('DB_PASSWORD'),
                             db='stockdb',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

# Positions hundling
# deletePositions(connection)
insertPositions(connection, positions)

insertOrders(connection, orders)

print("***** Tables stock_stock(positions) and orders are updated! ****")
