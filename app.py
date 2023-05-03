from math import comb
from xml import dom
import streamlit as st
import sistrix_functions as sf
import pandas as pd
import time
import datetime
from functools import reduce
import logging
logging.basicConfig(filename='tools_log.log')


#lista de dataframes a combinar indicando el nombre de la columna que se tiene como referenca
def combinarDataFrames(l_df,column_name):
    df_salida=None
    columnas=['date']
    for df in l_df:
        dominio=df['domain'].iloc[0]
        pais=df['country'].iloc[0]
        device=df['dispositivo'].iloc[0]
        nombre=dominio+"_"+pais+"_"+device
        columnas.append(nombre)
    try:
        df_merged = reduce(lambda  left,right: pd.merge(left,right,on=[column_name],
                                                how='outer'), l_df).fillna('0').reset_index(drop=True)
    except pd.errors.MergeError as e: 
        logging.error("Error al combinar data frames: "+e.args[0])
        st.error("Error al combinar data frames: "+e.args[0])    
    else:  
        logging.info("DataFrames combinados correctamente")
        #Seleccionamos las columnas que nos interesan
        deja_columnas=[2]
        i=1
        while i<=len(l_df):
            deja_columnas.append(4*i-1)
            i+=1
        df_salida=df_merged.iloc[:,deja_columnas]
        #convertimos el formato de 'date' en el dataframe a formato de fecha para poder ordenar
        df_salida['date']=pd.to_datetime(df["date"],format='%d-%m-%Y')
        df_salida=df_salida.sort_values(by='date',ascending=True).reset_index(drop=True)
        #Cambiamos al formato que utilizaremos en el sheet
        df_salida['date']=df_salida['date'].dt.strftime('%d-%m-%Y')
        #renombramos las columnas
        df_salida.columns=columnas
        return df_salida

@st.cache(suppress_st_warning=True)
def getVisibilidadSemanal(df,num_semanas,api_key):
    l_df=[]
    for index in range(len(df)):
        dominio=df['domain'].iloc[index]
        tipo_consulta=df['type'].iloc[index]
        pais=df['country'].iloc[index].strip()
        device=df['device'].iloc[index]
        if device=='mobile':
            es_mobile=True
        else:
            es_mobile=False
        l_df.append(sf.getUltimasSemanas(num_semanas,dominio,pais,es_mobile,tipo_consulta,api_key))
        time.sleep(0.5)
    df_merged = combinarDataFrames(l_df,'date')      
    return df_merged

@st.cache(suppress_st_warning=True)
def getVisibilidadDiaria(df,num_dias,api_key):
    l_df=[]
    for index in range(len(df)):
        dominio=df['domain'].iloc[index]
        tipo_consulta=df['type'].iloc[index]
        pais=df['country'].iloc[index].strip()
        device=df['device'].iloc[index]
        if device=='mobile':
            es_mobile=True
        else:
            es_mobile=False
        l_df.append(sf.getUltimosDias(num_dias,dominio,pais,es_mobile,tipo_consulta,api_key))
        time.sleep(0.5)
    df_merged = combinarDataFrames(l_df,'date')                
    return df_merged

st.set_page_config(
   page_title="Resultados Sistrix",
   layout="wide"
)

st.title("Resultados Sistrix")
api_key= st.text_input('API key de Sistrix', '')
if api_key!='':
    creditos=sf.getCredits(api_key)
    st.write('Créditos semanales restantes: '+creditos)
    if int(creditos) >= 1000:
        dominios_analizar=st.file_uploader('CSV con dominios a analizar', type='csv')
        if dominios_analizar is not None:
            df_entrada=pd.read_csv(dominios_analizar)
            st.write(df_entrada)
            
            num_semanas=st.slider('Últimas semanas a obtener', value=5, min_value=1, max_value=100)   

            btn_sem = st.button('Obtener visibilidad semanal', disabled=False, key='1')
            if btn_sem:
                df_salida=getVisibilidadSemanal(df_entrada,num_semanas,api_key)
                if not df_salida.empty:
                    st.write(df_salida)
                    st.download_button(
                    label="Descargar como CSV",
                    data=df_salida.to_csv(index=False, sep=",").encode('utf-8'),
                    file_name='visibilidad_semanal.csv',
                    mime='text/csv'
                    )
                else:
                    creditos=sf.getCredits(api_key)
                    st.write('Créditos semanales restantes: '+creditos)

            num_dias=st.slider('Últimos días a obtener', value=30, min_value=1, max_value=40)
            btn_d = st.button('Obtener visibilidad diaria', disabled=False, key='3')
            if btn_d:
                df_salida=getVisibilidadDiaria(df_entrada,num_dias,api_key)
                if not df_salida.empty:
                    st.write(df_salida)
                    st.download_button(
                    label="Descargar como CSV",
                    data=df_salida.to_csv(index=False, sep=",").encode('utf-8'),
                    file_name='visibilidad_diaria.csv',
                    mime='text/csv'
                    )
                else:
                    creditos=sf.getCredits(api_key)
                    st.error("Se ha producido un error al recuperar los datos")
                st.write('Créditos semanales restantes: '+sf.getCredits(api_key))
    else:
        st.write('Volumen de créditos bajo. No usar hasta tener más')