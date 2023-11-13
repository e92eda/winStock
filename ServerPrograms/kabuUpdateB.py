# Database kabudb tabbles: postions, orders update
# 2023/10/21,11/5
# E.Kunieda


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
    values = [tuple(apos.values()) for apos in positions]

####Insert update
    sql = ('''
    INSERT INTO stock_stock 
            (ExecutionID, AccountType, Symbol, SymbolName, Exchange, ExchangeName, Price, \
            LeavesQty, HoldQty, Side, CurrentPrice, Valuation, ProfitLoss, ProfitLossRate,\
            holding, period, period_type)
    VALUES 
            (%s, %s, %s, %s, %s,%s, %s, %s, %s, %s,%s, %s, %s, %s\
            ,True, 7, 'day')
    ON DUPLICATE KEY UPDATE CurrentPrice = VALUES(CurrentPrice), Valuation = VALUES(Valuation),
    ProfitLoss = VALUES(ProfitLoss), ProfitLossRate = VALUES(ProfitLossRate)\
    ,holding = VALUES(holding)
    ''')
    cur.executemany(sql, values)
    connection.commit()


# MySQL db table stock_tradeに登録
def insertOrders(connection, orders):
    cur = connection.cursor()
    values = []
    for apos in orders:
        apos.pop('Details')  # Details は邪魔で悪さをする
        values.append(tuple(apos.values()))
    # values = [('20231020A02N44303022', 5, 5, 1, '2023-10-20T09:05:07.598398+09:00', '7752', 'リコー', 9, 'SOR', 1245.0, 100.0, 100.0, '2', 4, 2, 20231020, [1,2])]
    print(values)
    sql = ('''
    INSERT IGNORE INTO stock_trade 
        (ID, State, OrderState, OrdType,RecvTime, Symbol, SymbolName, Exchange, ExchangeName, Price, OrderQty, CumQty, Side, AccountType, DelivType, ExpireDay) 
     VALUES
        (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''')

    cur.executemany(sql, values)
    connection.commit()


##### Main ####

# トークン発行
token_value = generate_token()
# 残高照会
positions = get_positions(token_value)

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

print("***** Tables stock_stock(positions) and orders are updated! ****")
