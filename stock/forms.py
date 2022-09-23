import os

from django import forms
from django.core.mail import EmailMessage
from .models import Stock, Trade

import csv
import io
from django import forms
from django.core.validators import FileExtensionValidator

import datetime


sideTable = ('','売', '買')       # 1:売 2:買　sideを数値で

class InquiryForm(forms.Form):
    name = forms.CharField(label='お名前', max_length=30)
    email = forms.EmailField(label='メールアドレス')
    title = forms.CharField(label='タイトル', max_length=30)
    message = forms.CharField(label='メッセージ', widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['name'].widget.attrs['class'] = 'form-control'
        self.fields['name'].widget.attrs['placeholder'] = 'お名前をここに入力してください。'

        self.fields['email'].widget.attrs['class'] = 'form-control'
        self.fields['email'].widget.attrs['placeholder'] = 'メールアドレスをここに入力してください。'

        self.fields['title'].widget.attrs['class'] = 'form-control'
        self.fields['title'].widget.attrs['placeholder'] = 'タイトルをここに入力してください。'

        self.fields['message'].widget.attrs['class'] = 'form-control'
        self.fields['message'].widget.attrs['placeholder'] = 'メッセージをここに入力してください。'

    def send_email(self):
        name = self.cleaned_data['name']
        email = self.cleaned_data['email']
        title = self.cleaned_data['title']
        message = self.cleaned_data['message']

        subject = 'お問い合わせ {}'.format(title)
        message = '送信者名: {0}\nメールアドレス: {1}\nメッセージ:\n{2}'.format(name, email, message)
        from_email = os.environ.get('FROM_EMAIL')
        to_list = [
            os.environ.get('FROM_EMAIL')
        ]
        cc_list = [
            email
        ]

        message = EmailMessage(subject=subject, body=message, from_email=from_email, to=to_list, cc=cc_list)
        message.send()


class StockCreateForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ('title', 'comment', 'photo1', 'photo2', 'photo3',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'



class CSVUploadForm(forms.Form):
    file = forms.FileField(
        label='CSVファイル',
        help_text='※拡張子csvのファイルをアップロードしてください。',
        validators=[FileExtensionValidator(allowed_extensions=['csv'])]
    )
    # print("File name:",file)
    def clean_file(self):
        file = self.cleaned_data['file']

        # csv.readerに渡すため、TextIOWrapperでテキストモードなファイルに変換
        csv_file = io.TextIOWrapper(file, encoding='shift_jis')
        reader = csv.reader(csv_file)

        # 各行から作った保存前のモデルインスタンスを保管するリスト
        self._instances = []

        if 'Account' in file.name:      # 現有残高　読み込み
            try:
                lcount = 0
                for row in reader:  # Skip 2 rows
                    if lcount > 1:
                        post = Stock(title=row[0], SymbolName=row[0], Symbol=row[1], LeavesQty=row[3],
                                     CurrentPrice=row[4], Price=row[5], Valuation=row[6], ProfitLoss=row[8],
                                     ProfitLossRate=row[9], user_id=1, holding=True)  # user_id をとりあえず１へ　
                        self._instances.append(post)

                    lcount += 1

            except UnicodeDecodeError:
                raise forms.ValidationError('ファイルのエンコーディングや、正しいCSVファイルか確認ください。')

        elif 'TradeKabu' in file.name:  # 売買履歴　読み込み
            # Bulk.create では、iD の連番生成ができないため、datetimeを元に、３桁追加して作成
            t_delta = datetime.timedelta(hours=9)
            JST = datetime.timezone(t_delta, 'JST')
            now = datetime.datetime.now(JST)
            dtimestring = now.strftime('%Y%m%d %H%M%S')

            try:
                lcount = 0
                for row in reader:  # Skip 1 rows
                    if lcount > 0:
                        symbolSerach = row[4]
                        try:
                            stockMatch = Stock.objects.get(Symbol=symbolSerach)
                        except Exception as e:     # Muched stock does not exist
                            print(f'Error!! {symbolSerach} :Corresponding Stock does not exits. {e} ')

                            stockMatch = Stock(Symbol=symbolSerach, SymbolName='Dummy', user_id=1)     # So, this is dummy., user_id=1
                            stockMatch.save()

                        post = Trade(ExecutionDay=row[0].replace('/', '-'), DeliveryDay=row[1].replace('/', '-'), ExchangeName=row[2], SymbolName=row[3],
                                     Symbol=row[4], Side= sideTable.index(row[5]), Qty=row[6], Price=row[7], Valuation=row[8], PointUse=row[9],
                                     Commission=row[10],  ProfitLoss=row[12], stock_record=stockMatch, user_id=1,
                                     id = dtimestring + f'{lcount:03}'  # 年から秒までと、0埋めで3文字)       #AccountType=row[11],
                                     )
                        self._instances.append(post)

                    lcount += 1

            except UnicodeDecodeError:
                raise forms.ValidationError('ファイルのエンコーディングや、正しいCSVファイルか確認ください。')

        return file

    def save_stocks(self):
        #まず、現有しているかどうかのKey：　holding = Falseとする。
        templist = []
        for stock in Stock.objects.all():
            stock.holding = False
            templist.append(stock)

        Stock.objects.bulk_update(templist, fields=['holding'])

        # 現有の場合、Key：　holding　はTrue
        Stock.objects.bulk_create(self._instances, ignore_conflicts=True)  # Initially ignore_conflicts=True
        Stock.objects.bulk_update(self._instances, fields=['LeavesQty', 'CurrentPrice', 'Price', 'Valuation',
                                                           'ProfitLoss', 'ProfitLossRate', 'holding'])


    def save_trades(self):      # Trades save

        #
        Trade.objects.bulk_create(self._instances, ignore_conflicts=False)  # Initially ignore_conflicts=True
        # Trade.objects.bulk_update(self._instances, fields=['Qty', 'CurrentPrice', 'Price', 'Valuation','ProfitLoss'])



class ChoiceForm(forms.Form):
    selected_time = forms.fields.ChoiceField(
        choices=(
            ('XXXX', '10:00'),
            ('XXXX', '10:30')
        ),
        label = '予約時間',
        required = True,
        widget = forms.widgets.RadioSelect
    )

