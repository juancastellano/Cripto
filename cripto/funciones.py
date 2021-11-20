import sys
import time
import requests
import pandas as pd


# Funcion para obtener valores de todas las cotizaciones en una lista
# Llama a funcion de obtener valor de una cotizacion concreta con cada
# par de la lista
def getCotizaciones(lista_divisas, startDate, endDate):
    Cotizaciones = pd.DataFrame()
    print('Obteniendo valores de Criptodivisas ... ')
    for cotizacion in lista_divisas:
        data = getKrakenTradeData(cotizacion, startDate, endDate)
        Cotizaciones = Cotizaciones.append(data.reset_index(),
                                           ignore_index=True)
    return Cotizaciones


# Funcion que recibe tres argumentos, una divisa cripto
# y un intervalo de tiempo
# Usa la api publica de Kraken
# Importante, hay un delay de casi 1 segundo entre peticiones,
# como solo devuelve 1000 registros en cada llamada,
# obtener mas de 8 horas de historico lleva tiempo.

def getKrakenTradeData(pair, startDate, endDate):
    try:
        endpoint = 'https://api.kraken.com/0/public/Trades'
        result = pd.DataFrame()
        result_tmp = pd.DataFrame()
        # conversion a entero de la fecha
        startTime = int(time.mktime(startDate.timetuple())) * 1000000000
        endTime = int(time.mktime(endDate.timetuple())) * 1000000000

        timeLoaded = startTime
        print('Obtener cotizacion ', pair)
        # vamos sacando bloques de 1000 registros hasta llegar
        # a los margenes indicados
        while timeLoaded < endTime:
            payLoad = {'pair': pair, 'since': timeLoaded}
            response = requests.get(url=endpoint, params=payLoad)
            data = response.json()['result']
            tradesRaw = data[pair]
            timeLoaded = int(data["last"])
            tradeData = pd.DataFrame.from_records(tradesRaw,
                                                  columns=['Price', 'Volume',
                                                           'Time', 'BuySell',
                                                           'MarketLimit',
                                                           'Misc'])

            tradeData['Time'] = pd.to_datetime(tradeData['Time'], unit='s')
            result_tmp = result_tmp.append(tradeData.reset_index(),
                                           ignore_index=True)
            time.sleep(0.88)

        # ahora acumular por segundo los datos
        result_tmp['Date'] = pd.to_datetime(result_tmp['Time'],
                                            unit='s').round('1s')

        # agregamos quedandonos con el utimo precio dentro del mismo segundo
        result_tmp = result_tmp.groupby('Date').last()
        # calculamos el VWAP
        tradeData = VWAP(result_tmp, 20)
        # separar siglas de la moneda de la divisa para poder filtrar
        tradeData['valor'] = pair[-3:]
        tradeData['cripto'] = pair[:5]
        result = result.append(tradeData.reset_index(), ignore_index=True)

    except Exception:
        print('Error al obtener valores de divisas ', sys.exc_info()[1])
    return result


# funcion que calcula el VWAP, admite ventana de N valores para su calculo
# se multiplica el precio por el volumen y se hace una suma de ese valor
# por agrupacion de ventana. Idem para el volumen , el resultado del
# cociente de dichas operaciones es el vwap
def VWAP(df, tam_ventana):
    df['pv'] = df['Price'].astype(float) * df['Volume'].astype(float)
    precio = df['pv'].rolling(window=tam_ventana).sum()
    volumen = df['Volume'].rolling(window=tam_ventana).sum()
    return df.assign(vwap=precio / volumen)
