import requests
import matplotlib.pyplot as plt
import pandas as pd

def get_traffic_data(resource_id,geohash_value,limit=500):
    url=f"https://data.ibb.gov.tr/api/3/action/datastore_search?resource_id={resource_id}&limit={limit}&q={geohash_value}"
    response=requests.get(url)
    #url'ye istek attık, response olarak kaydettik
    if response.status_code==200:
        #eğer başarılıysa data değişkenine json olarak kaydettik
        data = response.json()

        #datadan result'u çektik eğer bir şey yoksa boş dict döndürdük
        result= data.get("result",{})
        #resulttan recordu çektik eğer yoksa boş liste döndürdük
        records= result.get("records",[])


        #eğer records varsa bunu pandas df kullanarak dataframe'e kaydettik
        if records:
            df= pd.DataFrame(records)
            return df
        #eğer yoksa da records yok yazdırdık
        else:
            print("there is no records")

    #status code 200 değilse erroru yazdırık
    else:
        print("error: ", response.status_code, response.text)
        return None


geohash_value = "sxk9u7"
resource_id="914cb0b9-d941-4408-98eb-f378519c26f4"

df= get_traffic_data(geohash_value=geohash_value,resource_id=resource_id)
df.head()

print("Check number of rows: ", df.shape[0] == 720)
#fonksiyonu tamamladık şimdi de sıra trafik yoğunluğunu hesaplayıp bunu df'ye sütun olarak kaydetmede


df["NUMBER_OF_VEHICLES"]=pd.to_numeric(df["NUMBER_OF_VEHICLES"])
df["AVERAGE_SPEED"]=pd.to_numeric(df["AVERAGE_SPEED"])
#sütunları numerik değere çevirdik


df["TRAFFIC_DENSITY"]=df["NUMBER_OF_VEHICLES"]/(df["AVERAGE_SPEED"])**2
df["TRAFFIC_DENSITY"]=pd.to_numeric(df["TRAFFIC_DENSITY"])
#yeni sütun ekledik ve onu da numerik değer yaptık



#her bir saat için ort hızı ve yoğunluğu gir


df["DATE_TIME"]=pd.to_datetime(df["DATE_TIME"], errors="coerce")
#date time sütununu date time(tarih-saat) formatına çevirdik

df["HOUR"]=df["DATE_TIME"].dt.hour
#date_time sütunundan saati çektik

hourly_stat= df.groupby("HOUR").agg(
average_density=("TRAFFIC_DENSITY", "mean"),
#saat saat alarak traffic densitydeki yoğunlukların ortalamasını alıyoz
average_speed=("AVERAGE_SPEED", "mean")
).reset_index()

hourly_stat.head()




#matplotlib.pyplot kullanarak grafik çizeceğiz

#2 satır ve 1 sütundan oluşan 2 tane subplot oluşturduk, figsize grafiğin boyutunu, gridspace grafiklerin oranlarını belirtir. sharex=true kısmı ise x eksenlerinin ortak olmasını sağlar, yani ikisi de saati ortak olarak alır
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), gridspec_kw={'height_ratios': [1, 1]}, sharex=True)


#x= hour ve y=average speed olacak şekilde bir çizgi grafiği çizer
ax1.plot(hourly_stat["HOUR"], hourly_stat["average_speed"], color='blue')
#grafiğin başlığı
ax1.set_title("Traffic Density and Average Vehicle Speed by Hour")
#çizgi grafiğinin adı
ax1.set_ylabel("Average Speed")




#x=hour ve y=average density olacak şekilde bar grafiği oluşturur, renk olacağı için değişkene atadık
bars = ax2.bar(hourly_stat["HOUR"], hourly_stat["average_density"], color='green')
#saat kısmı
ax2.set_xlabel("Hour of Day")
#bar grafiğinin adı
ax2.set_ylabel("Traffic Density")


average_density_value = hourly_stat["average_density"].mean()

#yeşil mi sarı mı kırmızı mı olacak
for bar in bars:
    traffic_density = bar.get_height()


    if traffic_density > average_density_value:
        bar.set_color('red')

    elif traffic_density<average_density_value:
        if abs(traffic_density-average_density_value)<(average_density_value*0.10):
            bar.set_color('orange')


plt.subplots_adjust(hspace=0)



plt.show()





