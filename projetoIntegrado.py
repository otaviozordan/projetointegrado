import requests
from retrying import retry
from OFDM_64_QAM import *
from colorama import Fore, Style
import json

ip = '196.168.0.103'
token = '/token=teleco2k23g1'
url1 = 'http://' + ip + ':8000' + token
url2 = 'http://' + ip + ':8020' + token

# Função para fazer uma requisição HTTP com tentativas
@retry(wait_fixed=5000, stop_max_attempt_number=3)
def make_request(url):
    print(Fore.BLUE + "Tentando URL:", url + Style.RESET_ALL)
    response = requests.get(url)
    
    if response.status_code != 200:
        raise Exception(Fore.RED + f'Requisição falhou com código de status {response.status_code}' + Style.RESET_ALL)
    
    return response.json()

try:
    CarrierSRS = make_request(url1)
    k = CarrierSRS['k']
    p = CarrierSRS['p']
    cp = CarrierSRS['cp']
    print(Fore.GREEN + f"Obtido JSON de 'CarrierSRS': K={k}, P={p}, CP={cp}" + Style.RESET_ALL)

    ServiceSRS = make_request(url2)
    snr = ServiceSRS['snr']
    service = ServiceSRS['service']
    modulation = ServiceSRS['modulation']
    print(Fore.GREEN + f"Obtido JSON de 'ServiceSRS': SNR={snr}, Service={service}, Modulation={modulation}" + Style.RESET_ALL)

    dicInfo = get_ber(K=int(k), CP=int(cp), P=int(p), SNRdb=int(snr))
    print(Fore.GREEN + "\n\nCálculo de BER concluído:"+ str(dicInfo['BER']) + Style.RESET_ALL)

    if service == '0':
        servico = 'DADOS'
        padrao = 0.33
    elif service == '1':
        servico = 'VOZ'
        padrao = 0.22
    elif service == '2':
        servico = 'CRITICO'
        padrao = 0.05

    mensagem = 'O servico '+servico+' e ' 
    numero_modulacao = ''.join(filter(str.isdigit, modulation))
    numero_modulacao = int(numero_modulacao)
    if numero_modulacao > 64:
        print(Fore.BLUE + 'Modulcacao superior a 64QAM' + Style.RESET_ALL)        
        padrao = padrao * 3/4

    if dicInfo['BER'] <= padrao:
        mensagem += 'apto'
    else: 
        mensagem += 'inviavel'

    print(Fore.GREEN + mensagem + ' para padrao ' + str(padrao) + Style.RESET_ALL)
    jsonResposta = {
        'server': ['CarrierSRS', 'ServiceSRS'],
        'ber': dicInfo['BER'],
        'Potencia RX em dBm': dicInfo['S_Power'],
        'Potencia do ruido em dBm': dicInfo['N_Power'],
        'ber': dicInfo['BER'],
        'servico': servico,
        'mensagem': mensagem,
        'modulacao':modulation
    }

    # Imprimir o JSON identado
    print(Fore.YELLOW + json.dumps(jsonResposta, indent=4) + Style.RESET_ALL)

except Exception as e:
    print(Fore.RED + f'[ERRO] {str(e)}' + Style.RESET_ALL)
