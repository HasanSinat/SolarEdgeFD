import  requests
import pandas as pd
import  datetime
import sys
import streamlit as st
import io
import xlsxwriter
from streamlit_lottie import st_lottie
from streamlit_lottie import st_lottie_spinner
import os
import streamlit as st
import math
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 
def check_password():
    """Returns `True` if the user had a correct password."""
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if (
            st.session_state["username"] in st.secrets["passwords"]
            and st.session_state["password"]
            == st.secrets["passwords"][st.session_state["username"]]
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store username + password
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False
    if "password_correct" not in st.session_state:
        # First run, show inputs for username + password.
        
        st.text_input("Username", key="username")
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input("Username",  key="username")
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 User not known or password incorrect")
        return False
    else:
        # Password correct.
        return True
if check_password():
    api_key = st.secrets["SolarEdge_API_KEY"]
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    buffer = io.BytesIO()
    solarEdgePlants = [
        {"id": 2176821, "name": "ABDULLAH YILMAZ GÜNEŞ GES","ins_date": "13.02.2022"},
        {"id": 1061237,"name": "ALKOR GES" },
        {"id": 603955, "name": "CELAL BAYAR ÜNİVERSİTESİ GES"},
        {"id": 2696896, "name": "ERMAS MADENCILIK"},
        {"id": 2205847, "name": "GALETOS GES"},
        {"id": 1824266, "name": "MEGASUT GES"},
        {"id": 2633601, "name": "MESNEVI GIDA GES"},
        {"id": 2416307, "name": "MOSSDECO GES"},
        {"id": 2321791, "name": "OKT 3 GES"},
        {"id": 521013, "name": "TED DENİZLİ KOLEJİ GES"},
        {"id": 2563278, "name": "TRIMLINE/BALOSB GES"},
        ]
    baseUrl="https://monitoringapi.solaredge.com"
    inverterSN = " "
    startTime = "2022-04-01"
    endTime = "2022-04-07"
    inverters = list() #api'den inverterlerin seri no'larını çekip buraya atacak
    frameList = list() #her inverter için gelen veriler ayrı dataframelerde depolanıp en son birleştirilecek
    datelist = list() #girilen uzun tarihler haftalık tarihlere parçalanacak
    inverter_frame_list = list()
    connected_optimizer = 0
    dataTypes=["totalActivePower","dcVoltage","totalEnergy","temperature","L1Data.acCurrent","L1Data.acVoltage","L1Data.apparentPower","L1Data.activePower","L1Data.reactivePower","L1Data.cosPhi","L2Data.acCurrent","L2Data.acVoltage","L2Data.apparentPower","L2Data.activePower","L2Data.reactivePower","L2Data.cosPhi","L3Data.acCurrent","L3Data.acVoltage","L3Data.apparentPower","L3Data.activePower","L3Data.reactivePower","L3Data.cosPhi"]
    if "selectedDataTypes" not in st.session_state:
        st.session_state["selectedDataTypes"] = dataTypes
    @st.experimental_memo(show_spinner=False)
    def get_key(val):
        for plant in solarEdgePlants:
            if plant["name"] == val:
                return plant["id"]
        return "key doesn't exist"
    @st.experimental_memo(show_spinner=False)
    def get_date(val):
        for plant in solarEdgePlants:
            if plant["name"] == val:
                return plant["ins_date"]
    @st.experimental_memo(show_spinner=False)
    def fetchData(siteID,startTime,endTime,inverterSN,api_key, counter,dataTypes):
        
        response_data = requests.get(f"{baseUrl}/equipment/{siteID}/{inverterSN}/data?startTime={startTime} 08:00:00&endTime={endTime} 19:00:00&api_key={api_key}")
        statusCode = response_data.status_code
        response_data = response_data.json()
           #Api'ye json formatında istek atıyorum.
        if statusCode == 200 :
            data = pd.json_normalize(response_data["data"]["telemetries"], )
            data=data[dataTypes + ["date"]  ]
            data["InverterNo"] = f"Inverter {counter}"
            data.fillna(0,inplace=True)
            data = data.groupby(["date", "InverterNo", ]).mean()
        return data
        
    @st.experimental_memo(show_spinner=False)
    def load_lottieurl(url: str):
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    def excelCreator():
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            mixed.to_excel(writer, sheet_name="yield_sheet_Nam")
            writer.save()
            return buffer      
    def csvCreator():
        csv = mixed.to_csv()
        csv = csv.encode('utf-8')
        return csv
    def siteDetailsData (siteID,api_key):
        response = requests.get(f"{baseUrl}/site/{siteID}/details?api_key={api_key}").json()
        data = pd.json_normalize(response["details"])
        return data
    lottie_url_hamster = "https://assets9.lottiefiles.com/packages/lf20_xktjqpi6.json"
    lottie_hamster = load_lottieurl(lottie_url_hamster)

    st.header("SolarEdge Data Sihirbazı 🧙")
    st.header("#")
    with st.form(key="Santral Seçim Forumu"):
        
        selectedPlant= st.selectbox(
                "Santarli Seçiniz",
                ("ABDULLAH YILMAZ GÜNEŞ GES", "ALKOR GES", "CELAL BAYAR ÜNİVERSİTESİ GES","ERMAS MADENCILIK","GALETOS GES","MEGASUT GES","OKT 3 GES","TED DENİZLİ KOLEJİ GES","TRIMLINE/BALOSB GES",)
            )   
        siteID = get_key(val = selectedPlant)
        colx, coly = st.columns(2)
        with colx:
            startTime = st.date_input("Başlangıç Tarihi", max_value=datetime.datetime.now())
        with coly:
            endTime = st.date_input("Btiş Tarihi",max_value=datetime.datetime.now())

        st.session_state["selectedDataTypes"] = st.multiselect(label="Data Tipleri", options=dataTypes , default=dataTypes)
        col1, mid, col2 = st.columns([10,39,10])
        with col1:
            submitted = st.form_submit_button("Submit")
        with  col2:
            sitedetails = st.form_submit_button("Site Details")
    with st.expander("Bilgilendirme"):
        st.info("API'de günlük istek limiti bulunmaktadır, bu limit genel çağrılar için 300, santral numarası ile ile yapılan çağrılar için de ayrıca 300 olarak belirlenmiştir.\n Günlük istek limiti aşıldığıda istek hata döndürecektir.")
        st.warning("API'ın çalışma şekli toplu veri indirmeye uygun olmadığından, veriler her inverter bazında verilen tarih aralığını bir haftalık bloklara bölüp ardından tüm dataları bir araya getirmek suretiyle çalışır, Ornegin 9 inverterli bir tesisten bir aylık data çekmek için her inverter için 4 haftalık data çekilip birleştirilir, seri no'ları çekmek için 1 veriler için 36 olmak üzere toplam 37 istek atılmış olur.")
    with st.expander("Bellek Temizliği"):
        st.error("Lütfen yalnızca gerekli olduğu durumlarda kullanınız..")
        st.info("Bellekteki tüm verileri temizler, aynı tesiste yapılacak art arda istekleklerde kullnılması önerilir.")
        colx,coly,colz = st.columns(3)
        with coly:
            if st.button("Belleği Temizle"):
                st.experimental_memo.clear()
    if submitted:
        try:
            response_inventory = requests.get(f"{baseUrl}/site/{siteID}/inventory?api_key={api_key}").json() #Api'ye json formatında istek atıyorum.
        except:
            sys.exit("Data Alınamadı, Lütfen Sonra Tekrar Deneyiniz.")

        for inverter in response_inventory["Inventory"]["inverters"]:  #inverterlerin seri nolarını çıkarıp ayrı bir listeye ekliyorum.
            inverters.append(inverter["SN"])

            connected_optimizer += inverter["connectedOptimizers"] 
        if endTime - startTime < datetime.timedelta(weeks=1):
            st.info("Aralık Bir Haftadan Kısa Seçilemez, Aralık Uygun olacak şekilde Bitiş Tarihi Güncellenmiştir.")
            startTime = endTime - datetime.timedelta(days=6)

        tarih = pd.date_range(startTime,endTime, freq="6D").to_series()
        tarih = tarih.apply(lambda x: x.strftime("%Y-%m-%d"))
        tarih=tarih.to_list()
        
        counter = 1
        
        try:
            with st_lottie_spinner(lottie_hamster, key="download", height=300, quality="high"):       #inverter listesindeki inverter no'lar ile seçilen tarih aralığını haftalara bölüp istek atıyor ve en son tüm verileri birleştiriyor.
                for sn in inverters:
                    for i in range(len(tarih)-1):
                        startTime=tarih[i]
                        endTime=tarih[i+1]
                        try:
                            data = fetchData(siteID=siteID, startTime=startTime,endTime=endTime,inverterSN=sn,api_key=api_key,counter=counter,dataTypes=st.session_state["selectedDataTypes"])
                        except Exception as e:
                            print(e)
                            pass
                        frameList.append(data)
                    counter +=1   
                mixed = pd.concat(frameList)
                st.write(mixed)
        
        except Exception as e:
            print(e)
            #sys.exit("Data Alınamadı, Lütfen Sonra Tekrar Deneyiniz.")
            mixed = pd.DataFrame()
            pass

        st.header("##")
    
        col1, mid, col2 = st.columns([10,15,7.5])

        if not mixed.empty:
            with col1:
                with st.spinner("CSV Dosyası Hazırlanıyor.."):
                    csv = csvCreator()
                    st.download_button(
                                "Download as CSV",
                                csv,
                                "file.csv",
                                "text/csv",
                                key='download-csv'
                                )
            with col2:
                with st.spinner("Excel Dosyası Hazırlanıyor.."):
                    buffer =excelCreator()
                    st.download_button(
                            label="Download as XLSX",
                            data=buffer,
                            file_name="file_name_Yield.xlsx",
                            mime="application/vnd.ms-excel"
                            )
        else: st.error("Santral Bazında Günlük Limit Aşımı ve / veya Dataların Başlangıç Tarihinden Önce Seçilmiş Başlangıç Tarihi.") 
    if sitedetails: #site details section
        sitedetailsdatas = siteDetailsData(siteID,api_key)
        response_inventory = requests.get(f"{baseUrl}/site/{siteID}/inventory?api_key={api_key}").json() #Api'ye json formatında istek atıyorum.
        for inverter in response_inventory["Inventory"]["inverters"]:
            inverters.append(inverter["SN"])  #inverterlerin seri nolarını çıkarıp ayrı bir listeye ekliyorum.
            connected_optimizer += inverter["connectedOptimizers"] 
        sitePeakPower = sitedetailsdatas["peakPower"]
        pd.to_numeric(sitePeakPower)    
        siteName = sitedetailsdatas["name"].str.cat()
        siteinsDate =sitedetailsdatas["installationDate"].str.cat()
        siteMaxPower = sitedetailsdatas["primaryModule.maximumPower"]
        pd.to_numeric(siteMaxPower) 
        siteCity = sitedetailsdatas["location.city"].str.cat()
        siteTown = sitedetailsdatas["location.address"].str.cat()
        siteImageUrl=sitedetailsdatas["uris.SITE_IMAGE"].str.cat()
        st.header(siteName)
        st.image(f"{baseUrl}{siteImageUrl}?api_key={api_key}" )
        inverterCount = len(inverters)
        maxCall = math.floor(290 / (inverterCount * 4))

        col1, gap1, col2, gap2, col3 = st.columns([3,2,4,2,3])
        with col1:
            st.metric(label = "Peak Power (kWp)" ,value = sitePeakPower)
        with col2:
            st.metric(label = "Installed" ,value = siteinsDate)
        with col3:
            st.metric(label="Connected Optimizers", value=connected_optimizer)
        #st.metric(label = "Site Max Power" ,value = siteMaxPower)
        col1, gap1, col2, gap2, col3 = st.columns([3,2,4,2,3])
        with col1:
            st.metric(label="Inverter Count", value=inverterCount)
        with col2:
            st.metric(label="Max. Request at Once", value=f"{maxCall} Months")
        st.metric(label = "City" ,value = siteCity)
        st.metric(label = "Address" ,value = siteTown)
        
 