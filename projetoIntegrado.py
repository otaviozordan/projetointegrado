import math
import requests
import json
from retrying import retry
from colorama import Fore, Style

# Importa funções personalizadas de OFDM_64_QAM
from OFDM_64_QAM import *

# Configuração de endereços IP e tokens
ip = '196.168.0.103'
token = '/token=teleco2k23g5'
url1 = 'http://' + ip + ':8000' + token
url2 = 'http://' + ip + ':8020' + token

# Função para fazer uma requisição HTTP com tentativas
@retry(wait_fixed=2000, stop_max_attempt_number=3)
def make_request(url):
    print(Fore.BLUE + "Tentando URL:", url + Style.RESET_ALL)
    response = requests.get(url)
    print(response.content)
    if response.status_code != 200:
        raise Exception(Fore.RED + f'Requisição falhou com código de status {response.status_code}' + Style.RESET_ALL)
    
    return response.json()

try:
    # Faz uma requisição para 'CarrierSRS' e obtém informações
    CarrierSRS = make_request(url1)
    k = CarrierSRS['k']
    p = CarrierSRS['p']
    cp = CarrierSRS['cp']
    print(Fore.GREEN + f"Obtido JSON de 'CarrierSRS': K={k}, P={p}, CP={cp}" + Style.RESET_ALL)

    # Faz uma requisição para 'ServiceSRS' e obtém informações
    ServiceSRS = make_request(url2)
    snr = ServiceSRS['snr']
    service = ServiceSRS['service']
    modulation = ServiceSRS['modulation']
    print(Fore.GREEN + f"Obtido JSON de 'ServiceSRS': SNR={snr}, Service={service}, Modulation={modulation}" + Style.RESET_ALL)

    # Calcula a BER usando os parâmetros obtidos
    dicInfo = get_ber(K=int(k), CP=int(cp), P=int(p), SNRdb=int(snr))
    print(Fore.GREEN + "\n\nCálculo de BER concluído:"+ str(dicInfo['BER']) + Style.RESET_ALL)

    # Determina o serviço com base na resposta e define um padrão de BER
    if service == '0':
        servico = 'DADOS'
        padrao = 0.33
    elif service == '1':
        servico = 'VOZ'
        padrao = 0.22
    elif service == '2':
        servico = 'CRITICO'
        padrao = 0.05

    # Verifica se a modulação é superior a 64QAM e ajusta o padrão de BER
    numero_modulacao = ''.join(filter(str.isdigit, modulation))
    numero_modulacao = int(numero_modulacao)
    if numero_modulacao > 64:
        print(Fore.BLUE + 'Modulação superior a 64QAM' + Style.RESET_ALL)        
        padrao = padrao * 3/4

    # Determina se o serviço é viável com base na BER calculada
    if dicInfo['BER'] <= padrao:
        mensagem = 'apto'
        usavel = True
    else: 
        mensagem = 'inviável'
        usavel = False

    # Função para converter Watts em dBm
    def watts_to_dbm(watts):
        dbm = 10 * math.log10(watts * 1000)
        return dbm

    # Cria um JSON de resposta com informações relevantes
    jsonResposta = {
        'server': ['CarrierSRS', 'ServiceSRS'],
        'Potencia_RX': str(watts_to_dbm(float(dicInfo['S_Power'])))+ ' [dBm]',
        'Potencia_do_ruido': str(watts_to_dbm(float(dicInfo['N_Power'])))+' [dbm]',
        'ber': dicInfo['BER'],
        'servico': servico,
        'usavel':usavel,
        'mensagem': mensagem,
        'modulacao':modulation
    }

    # Imprime o JSON identado
    print(Fore.YELLOW + json.dumps(jsonResposta, indent=4) + Style.RESET_ALL)

except Exception as e:
    # Lida com exceções e cria um JSON de resposta de erro
    print(Fore.RED + f'[ERRO] {str(e)}' + Style.RESET_ALL)
    jsonResposta = {
        'mensagem': f'[ERRO] {str(e)}',
    }

    # Imprime o JSON identado
    print(Fore.YELLOW + json.dumps(jsonResposta, indent=4) + Style.RESET_ALL) 
