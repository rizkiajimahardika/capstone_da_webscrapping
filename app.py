from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
url_get = requests.get('https://www.exchange-rates.org/history/IDR/USD/T')
soup = BeautifulSoup(url_get.content,"html.parser")

#find your right key here
table = soup.find('table', attrs={'class':'table'})
row = table.find_all('tr')

row_length = len(row)

temp = [] #initiating a tuple

for i in range(1, row_length):

    # using key tr to take information
    row = table.find_all('tr')[i]
    
    # get date
    date = row.find_all('td')[0].text
    date = date.strip()
    
    # get kurs
    kurs = row.find_all('td')[2].text
    kurs = kurs.strip()
    
    temp.append((date,kurs))
    

temp = temp[::-1]

#change into dataframe
df = pd.DataFrame(temp, columns = ('date','kurs'))

#data wrangling process

# to get rid of the string 'IDR'
df['kurs'] = df['kurs'].str.replace('IDR','')

# to get rid of the string ','
df['kurs'] = df['kurs'].str.replace(',','')

# to change the data type in column date to datetime64

df['date'] = df['date'].astype('datetime64')

# to change the data type in column kurs to float
df['kurs'] = df['kurs'].astype('float')


# make new column to get contain month
df['month'] = df['date'].dt.to_period('M')

# using groupby to get mean in every month
df_mean = df.groupby('month').mean().round(2)

#end of data wrangling 

@app.route("/")
def index(): 
	
	card_data = f'{df["kurs"].mean().round(2)}' #be careful with the " and ' 

	# generate plot
	ax = df_mean.plot(figsize = (12,6)) 
	
	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]

	# render to html
	return render_template('index.html',
		card_data = card_data, 
		plot_result=plot_result
		)


if __name__ == "__main__": 
    app.run(debug=True)