# 2022/9/2, by ek

import urllib.request
import json, pprint, requests
import pandas as pd

host_ = '18080' # 本番環境
pass_ = 'KABUSTATIONで設定時に決めたパスワード'

# 認証用のトークンを作成する関数
def generate_token():

    obj = {'APIPassword': pass_}
    json_data = json.dumps(obj).encode('utf8')
    url = f'http://localhost:{host_}/kabusapi/token'
    req = urllib.request.Request(url, json_data, method='POST')
    req.add_header('Content-Type', 'application/json')

    try:
        with urllib.request.urlopen(req) as res:
            content = json.loads(res.read())
        token_value = content.get('Token')
        return token_value

    except urllib.error.HTTPError as e:
        print(e)
        return e


#注文一覧を取得

def get_order(token,order_type=0):
    url = f'http://localhost:18080/kabusapi/orders?product={order_type}'
    response = requests.get(url, headers={'X-API-KEY': token,})

    orders = json.loads(response.text)

    data = []

    for order in orders:

        state = order['State']

        if state >= 4:  # 1,2,3: 待機,処理中,処理済

            continue

        price = order['Price']

        if price == 0.0:

            price = '成行  '

        side = order['Side']

        if side == '2':

            side = '買'

        elif side == '1':

            side = '売'

        board = get_priceinfo(1, order['Symbol'], token)

        current_price = board["CurrentPrice"]

        if current_price == None:

            current_price = "---"

        data.append(
            [order['ID'],
             order['Symbol'],
             order['symbolName'],
             price,
             side,
             order['OrderQty'],
             current_price,
             order['ExpireDay'],])

    return pd.DataFrame(data, columns=['注文ID','コード','銘柄', '注文価格','売/買','注文数','現在価格','期限'])

# ポジションを確認する関数
def get_position(token, product=0):
    url = f'http://localhost:18080/kabusapi/positions?product={product}'
    response = requests.get(url, headers={'X-API-KEY': token,})
    positions = json.loads(response.text)
    data = []
    for position in positions:
        #print(position)
        if position['Side'] == '2':
            side = '買'
        elif position['Side'] == '1':
            side = '売'
        try:
            typeid = position['MarginTradeType']
            ordertype = '信用'
        except:
            typeid = -1
            ordertype = '現物'
        data.append(
                [ordertype,typeid,
                 position['ExecutionID'],
                 position['Symbol'],
                 position['symbolName'],
                 side,
                 position['Price'],
                 position['LeavesQty'],
                 position['CurrentPrice'],
                 position['ProfitLoss']]
                )
    return pd.DataFrame(data, columns=['注文種別','信用注文タイプ','ポジションID','コード','銘柄', '売買','注文価格','注文数','現在価格', '損益'])


if __name__ == '__main__':
    # 関数を実行してトークンを発行
    token = generate_token()
    print(token)

    currentOrders = get_order(token)

    print(currentOrders)
