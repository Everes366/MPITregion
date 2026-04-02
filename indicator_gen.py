import datetime
import requests
import random
import time


def send_indicator_values(url, device_number, start_date, start_value):
    body = {
        'key': 'fcff5cf3-723b-4a83-943f-8badbe6e33a1',
        'number': device_number,
    }
    for _ in range(10):
        start_value += random.randint(1, 100)
        body['date'] = start_date.strftime('%d.%m.%Y')
        body['value'] = start_value
        result = requests.post(url, json=body)
        if result.status_code == 201 or result.status_code == 200:
            print(f'Данные за {datetime.datetime.strftime(start_date, "%d.%m.%Y")} успешно отправлены!')
            print(result.json())
        else:
            print(f'ОШИБКА! Данные за {datetime.datetime.strftime(start_date, "%d.%m.%Y")} не отправлены!')
        start_date += datetime.timedelta(days=1)
        time.sleep(2)



if __name__ == '__main__':
    url = 'http://127.0.0.1:5000/setindicator'
    device_number = 'abc abc abc'
    start_date = datetime.date(day=1, month=1, year=2026)
    start_value = 100
    send_indicator_values(url, device_number, start_date, start_value)


    