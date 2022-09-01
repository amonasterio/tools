import requests, pandas as pd
from xml.etree import ElementTree as ET
from datetime import  datetime



def convierteFechaSistrix(fecha):
    #dejamos los 10 primeros caracteres
    date=fecha[0:10]
    formato_entrada='%Y-%m-%d'
    formato_salida='%d-%m-%Y'
    date_time_obj = datetime.strptime(date,formato_entrada)
    return date_time_obj.strftime(formato_salida)


def getCreditsResponse(url):
    credits=-1
    response=requests.get(url)
    if response.status_code==200:
        root=ET.fromstring(response.content)
        for child in root.findall('.//credits'):
            if child.attrib['value']!=None:
                credits=str(child.attrib['value'])
                break
    return credits   

def getCredits(api_key):
    url='https://api.sistrix.com/credits?api_key='+api_key
    credits=getCreditsResponse(url)
    return credits

def getDataFrameResponse(url,es_mobile,tipo_consulta,pais):
    response=requests.get(url)
    dct_arr=[]
    df=None
    if response.status_code==200:
        root=ET.fromstring(response.content)
    
        for child in root.findall('.//sichtbarkeitsindex'):
            dict={}
            if tipo_consulta =='domain':
                dict['domain']=child.attrib['domain']
            elif tipo_consulta =='host':
                dict['domain']=child.attrib['host']
            elif tipo_consulta =='path':
                dict['domain']=child.attrib['path']
            if es_mobile:
                dict['dispositivo']='mobile'
            else:
                dict['dispositivo']='desktop'
            dict['date']=convierteFechaSistrix(child.attrib['date'])
            if child.attrib['value']!=None:
                dict['value']=str(child.attrib['value']).replace('.',',')
            else:
                if len(dct_arr)>1:
                    dict['value']=dct_arr[len(dct_arr)-1].get('value')
                else:
                    dict['value']=''
            dict['country']=pais
            dct_arr.append(dict)
        dct_arr.reverse()
        df = pd.DataFrame(dct_arr)
    return df  

def getUltimasSemanas(num_semanas, dominio, pais, es_mobile,es_host, api_key):
    url='https://api.sistrix.com/domain.sichtbarkeitsindex?api_key='+api_key
    if not es_host:
        url+='&domain='+dominio
    else:
        url+='&host='+dominio
    url+='&country='+pais+'&history=true&num='+str(num_semanas)
    if es_mobile:
        url+='&mobile=true'
    df=getDataFrameResponse(url,es_mobile,es_host)
    return df




def getUltimosDias(num_dias, dominio, pais, es_mobile,tipo_consulta, api_key):
    url='https://api.sistrix.com/domain.sichtbarkeitsindex?api_key='+api_key
    if tipo_consulta =='domain':
        url+='&domain='+dominio
    elif tipo_consulta=='host':
        url+='&host='+dominio
    elif tipo_consulta=='path':
        url+='&path='+dominio
    url+='&country='+pais+'&history=true&num='+str(num_dias)
    if es_mobile:
        url+='&mobile=true'
    url+='&daily=true'
    print(url)
    df=getDataFrameResponse(url,es_mobile,tipo_consulta,pais)
    return df

def getUltimasSemanas(num_semanas, dominio, pais, es_mobile,tipo_consulta, api_key):
    url='https://api.sistrix.com/domain.sichtbarkeitsindex?api_key='+api_key
    if tipo_consulta =='domain':
        url+='&domain='+dominio
    elif tipo_consulta =='host':
        url+='&host='+dominio
    elif tipo_consulta=='path':
        url+='&path='+dominio
    url+='&country='+pais+'&history=true&num='+str(num_semanas)
    if es_mobile:
        url+='&mobile=true'
    df=getDataFrameResponse(url,es_mobile,tipo_consulta,pais)
    return df
