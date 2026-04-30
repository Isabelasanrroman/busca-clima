import os
from datetime import datetime, timedelta

import requests


def fahrenheit_to_celsius(temp):
    if temp is not None:
        celsius = (temp - 32) / 1.8
        return round(celsius, 2)
    return None

def mph_to_kmph(v_mph):
    if v_mph is not None:
        v_kmph = v_mph * 1.6090
        return round(v_kmph, 2)
    return None

def validar_nome_cidade(cidade):
    if not cidade or not isinstance(cidade, str):
        return 'O nome da cidade é obrigatório.'
    if len(cidade.strip()) < 2:
        return 'O nome da cidade deve ter pelo menos 2 caracteres'
    return None

def transformar_dados_clima(dados_clima):
    clima_atual = dados_clima.get('currentConditions', {})
    dias = dados_clima.get('days', [])[:7]

    data_atual = datetime.now().strftime('%d/%m/%Y')

    dados_processados = {
        'data': data_atual,
        'hora': clima_atual.get('datetime'),
        'cidade': dados_clima.get('resolvedAddress'),
        'temperatura': fahrenheit_to_celsius(clima_atual.get('temp')),
        'umidade': clima_atual.get('humidity'),
        'vento': mph_to_kmph(clima_atual.get('windspeed')),
        'precipitacao': clima_atual.get('precip'),
        'icon': clima_atual.get('icon'),
        'previsao': []
    }

    for dia in dias:
        dia_processado = {
            'data': datetime.strptime(dia['datetime'], "%Y-%m-%d").strftime('%d/%m/%Y'),
            'temperatura_max': fahrenheit_to_celsius(dia.get('tempmax')),
            'temperatura_min': fahrenheit_to_celsius(dia.get('tempmin')),
            'umidade': dia.get('humidity'),
            'vento': mph_to_kmph(dia.get('windspeed')),
            'precipitacao': dia.get('precip'),
            'icon': dia.get('icon')
        }

        dados_processados['previsao'].append(dia_processado)

    return dados_processados

def buscar_clima_por_cidade(cidade):
    msg_erro = validar_nome_cidade(cidade)
    if msg_erro:
        return {
            'error': True,
            'message': msg_erro,
            'status': 400
        }

    base_url = os.getenv("BASE_URL_VISUAL_CROSSING")
    api_key = os.getenv("VISUAL_CROSSING_API_KEY")

    if not base_url or not api_key:
        return {
            'error': True,
            'message': 'Configurações de API ausentes.',
            'status': 500
        }
    data_inicial = datetime.now().strftime('%Y-%m-%d')
    data_final = (datetime.now() + timedelta(days=6)).strftime('%Y-%m-%d')

    url = f"{base_url}{cidade}/{data_inicial}/{data_final}?key={api_key}&unitGroup=us&include=days,current"

    try:
        response = requests.get(url, timeout=10)

        if response.status_code == 404:
            return {
                'error': True,
                'message': f"Cidade '{cidade}' não encontrada.",
                'status': 404
            }
        response.raise_for_status()

        dados_response = response.json()

        return {
            'error': False,
            'data': transformar_dados_clima(dados_response),
            'status': 200
        }

    except requests.exceptions.Timeout:
        return {
            'error': True,
            'message': 'Tempo de resposta excedido.',
            'status': 504
        }

    except requests.exceptions.RequestException as ex:
        return {
            'error': True,
            'message': f"Erro de conexão: {str(ex)}",
            'status': 502
        }

    except Exception as ex:
        return {
            'error': True,
            'message': f"Erro inesperado: {str(ex)}",
            'status': 500
        }



