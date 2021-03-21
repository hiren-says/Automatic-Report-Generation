# ----------------------------------------------------------------------------------------
#       Importing Necessary libaries
# ----------------------------------------------------------------------------------------
import os
import numpy as np
import datetime
import pandas as pd
import mysql.connector
from mysql.connector import Error

# ----------------------------------------------------------------------------------------
#                     Check Latex files (main.tex $ structure.tex) 
# ----------------------------------------------------------------------------------------
with open('main.tex') as f:
    tmplt = f.read()

# ----------------------------------------------------------------------------------------
#                    Dictionary for Months
# ----------------------------------------------------------------------------------------
monthlist = { "01":'Janauary',
    "02":'February',
    "03":'March',
    "04":'April',
    "05":'May',
    "06":'June',
    "07":'July',
    "08":'August',
    "09":'September',
    "10":'October',
    "11":'November',
    "12":'December'   }

x = datetime.datetime.now()

# ----------------------------------------------------------------------------------------
#               Billing details Updating 
# ----------------------------------------------------------------------------------------
date = x.strftime("%d") + '-' +  x.strftime("%m") + '-' + x.strftime("%Y")

#------------------Connecting to database------------
mydb = mysql.connector.connect(
host='host_name',
database='database_name',
user='user_name',
password='password')
mycursor = mydb.cursor()



dates = '' # Useful for bar plot
datewithvalues = '' # useful for bar plot
gpt = 0 #total generator power 
dpt = 0 #total diesel power
ceg = 0
ced = 0

total = 0
ceg = 0
ced = 0
billcycle = 0

#----------------------------------------------------------------------------------------------
#                   Flat Nos
# ----------------------------------------------------------------------------------------

flat_no=["Flat1","Flat2"]


# ----------------------------------------------------------------------------------------
#                   Bill generation betweeen dates
# ----------------------------------------------------------------------------------------
# todate = input('Enter to date in ''DD-MM-YYYY'' format')
prev_date='2020-04-02'
fromdate = '02-04-2020'
todate = '24-04-2020'
start = datetime.datetime.strptime(fromdate, '%d-%m-%Y')
end = datetime.datetime.strptime(todate, '%d-%m-%Y')
month1 = (str(start.date()).split('-'))[1]
month2 = (str(end.date()).split('-'))[1]
step = datetime.timedelta(days=1)

# ----------------------------------------------------------------------------------------
#			Previous month readings
#-----------------------------------------------------------------------------------------
for i in range(len(flat_no)):

	query_prev_g="SELECT min(energy) FROM ft_data WHERE meter_id = '"+flat_no[i]+"g'"+" AND date(tstamp) = '" + prev_date+"'"
	print(query_prev_g)
	mycursor.execute(query_prev_g)
	result_g = (mycursor.fetchall()[0][0])
	print(result_g)
	peg=round(result_g,2)
	prevgp=peg


	query_prev_d="SELECT min(energy) FROM ft_data WHERE meter_id = '"+flat_no[i]+"d'"+" AND date(tstamp) = '" + prev_date+"'"
	print(query_prev_d)
	mycursor.execute(query_prev_d)
	result_d = (mycursor.fetchall()[0][0])
	print(result_d)
	ped=round(result_d,2)
	prevdp=ped


	while start<=end:
	  var = start.date()
	  var = "'"+str(var)+"'"
	  k = (str(start.date()).split('-'))[2] 
	  print(var)

	  #Retriving max energy values from databse and storing in variables day wise
	  query="SELECT max(energy) FROM ft_data WHERE meter_id = '"+flat_no[i]+"g'"+" AND date(tstamp) =" + str(var)
	  print(query)

	  mycursor.execute(query)
	  gp = (mycursor.fetchall()[0][0]) #Temporary variable 
	  if gp == None:
		gp = 0
		ceg = ceg
	  else:
		ceg = gp #Updating in loop for replacing current reading in latex file
	  query1=query="SELECT max(energy) FROM ft_data WHERE meter_id = '"+flat_no[i]+"d'"+" AND date(tstamp) =" + str(var)

	  mycursor.execute(query1)
	  dp = (mycursor.fetchall()[0][0]) #Temporary variable
	  if dp == None:
		dp = 0
		ced = ced #Updating in loop for replacing current reading in latex file 
	  else:
		ced = dp

	  #Operations
	  if gp == 0:
		todaygp = 0
		prevgp = prevgp
	  else:
		todaygp = gp - prevgp
		prevgp = gp

	  if dp == 0:
		todaydp = 0
		prevdp = prevdp
	  else:
		todaydp = dp - prevdp
		prevdp = dp

	  # Calculating total power utilized in current duration 
	  gpt = gpt + todaygp 
	  dpt = dpt + todaydp 

	  #Calculating day wise diesel & grid power utilzation
	  total = round( todaydp+todaygp , 2)  

	  # Bar plot requirements
	  dates = dates + k+','
	  datewithvalues = datewithvalues + '('+k+','+ str(total) +')'

	  start += step #date counter
	  billcycle = billcycle + 1
	#End of loop
	# ----------------------------------------------------------------------------------------
	# If bill is generated between days in two successive months
	# ----------------------------------------------------------------------------------------
	if monthlist[month1] == monthlist[month2]:
	  month = monthlist[month2]
	else :
	  month = monthlist[month1] + '-' +  monthlist[month2]


	# ----------------------------------------------------------------------------------------
	#Replacing dates & months 
	# ----------------------------------------------------------------------------------------
	tmplt = tmplt.replace('--billdate--', date)
	tmplt = tmplt.replace('--month--', month)
	tmplt = tmplt.replace('--year--', (str(end.date()).split('-'))[0])
	tmplt = tmplt.replace('--fromdate--', fromdate)
	tmplt = tmplt.replace('--todate--', todate)
	tmplt = tmplt.replace('--billcycle--', str(billcycle))

	# ----------------------------------------------------------------------------------------
	#Replacing values for bar plot
	# ----------------------------------------------------------------------------------------
	dates = dates[:-1] # removing last comma 
	tmplt = tmplt.replace('--dates--', dates)
	tmplt = tmplt.replace('--datewithvalues--', datewithvalues )

	# ----------------------------------------------------------------------------------------
	#Replacing curent values of energy consumption in latex file
	# ----------------------------------------------------------------------------------------
	tmplt = tmplt.replace('-ceg-' , str(round(ceg,2)))
	tmplt = tmplt.replace('-ced-' , str(round(ced,2)))

	# ----------------------------------------------------------------------------------------
	#Replaceing previous values of energy consumption in latex file 
	# ----------------------------------------------------------------------------------------
	tmplt = tmplt.replace('-peg-' , str(round(peg,2)))
	tmplt = tmplt.replace('-ped-' , str(round(ped,2)))

	# ----------------------------------------------------------------------------------------
	#Replacing energy utilisation in current bill duration
	# ----------------------------------------------------------------------------------------
	tmplt = tmplt.replace('-eg-' , str(round(gpt,2)))
	tmplt = tmplt.replace('-ed-' , str(round(dpt,2))) 
	tmplt = tmplt.replace('-tec-' , str(round(gpt+dpt,2)))

	# ----------------------------------------------------------------------------------------
	# Replacing values of previous months values 
	# ----------------------------------------------------------------------------------------
	tmplt = tmplt.replace('--minus1--', monthlist['0'+str(int(month1)-3)])
	tmplt = tmplt.replace('--minus2--', monthlist['0'+str(int(month1)-2)])
	tmplt = tmplt.replace('--minus3--', monthlist['0'+str(int(month1)-1)])
	# tmplt = tmplt.replace('--todate--', todate)

	d = x.strftime("%d") + '_' +  x.strftime("%m") + '_' + x.strftime("%Y")
	filename=flat_no[i]+"-"+month+"-"+ x.strftime("%Y")
	print(filename)
	with open(filename + '.tex', 'w') as f:
		f.write(tmplt)

	# ----------------------------------------------------------------------------------------
	#File operations
	# ----------------------------------------------------------------------------------------
	os.system('pdflatex ' + filename + '.tex')
	os.system('rm ' + filename + '.aux')
	os.system('rm ' + filename + '.log')
	os.system('rm ' + filename + '.tex')
