import requests
import json
from datetime import date
from datetime import datetime
from datetime import timedelta

# code_payload = {'clientx_id':client_id, 'redirect_uri':redirect_uri, 'state':state}
# r = requests.get('https://www.wunderlist.com/oauth/authorize', params=code_payload)

# access = {'code':code, 'client_id':client_id, 'client_secret':client_secret}
# post_result = requests.post("https://www.wunderlist.com/oauth/access_token",data = access)
# token = post_result.json().values()[0]

#Application Details
with open('config.json') as json_file:
	config_data = json.load(json_file)

client_id = config_data['client_id']
redirect_uri = config_data['redirect_uri']
client_secret = config_data['client_secret']
state = config_data['state']
code = config_data['code']
token = config_data['token']
mailgun_api = config_data['mailgun_api']
mailgun_key = config_data['mailgun_key']
to_name = config_data['to_name']
to_email = config_data['to_email']

def get_wunderlists():
	list_request = {'client_id':client_id, 
					'client_secret':client_secret, 
					'code':code, 
					'grant_type': 'authorization_code', 
					'redirect_uri':redirect_uri, 
					'access_token':token}
	wunderlists = requests.get("https://a.wunderlist.com/api/v1/lists", params = list_request)
	wunderlist_lists = wunderlists.json()
	return wunderlist_lists

def send_simple_message(api, key, name, email, text):
	return requests.post(
		'https://api.mailgun.net/v3/'+mailgun_api+'/messages',
		auth=("api", mailgun_key),
		data={"from": 'Daily Wunderlist Email <mailgun@'+mailgun_api+'>',
			  "to": [to_name, to_email],
			  "subject":  'Your Daily Wunderlist Digest %s'%todayDatePrint(),
			  "text": text, "html":text})

def get_tasks(list_id):
	task_request = {'client_id':client_id, 
				'client_secret':client_secret, 
				'code':code, 
				'grant_type': 
				'authorization_code', 
				'redirect_uri':redirect_uri, 
				'access_token':token,
				'list_id':list_id}
	tasks = requests.get("https://a.wunderlist.com/api/v1/tasks", params = task_request)
	return tasks.json()

def convertDate(old_date):
	year = old_date[0:4]
	month = old_date[5:7]
	day = old_date[8:10]
	return date(int(year),int(month),int(day))

def todayDatePrint():
	now = datetime.now()
	return str(now.month)+'/'+str(now.day)+'/'+str(now.year)

def todayDate():
	now = datetime.now()
	return date(now.year, now.month, now.day)

list_dict = {}
text = '<html>'

# Pull List name + id from API
mylist = get_wunderlists()
for i in range(0,len(mylist)):
	list_dict[mylist[i]['title']]=mylist[i]['id']

LateTasks = ["Late Tasks"]
TodayTasks  = ["Today's Tasks"]
FutureTasks = ['Upcoming Agenda']

for each in list_dict:
	list_tasks = get_tasks(list_dict[each])
	for j in range(0,len(list_tasks)):
		if 'due_date' in list_tasks[j]:
			task_date = convertDate(list_tasks[j]['due_date'])
			# print "Analyzing Task: ", list_tasks[j]['title'], list_tasks[j]['due_date']
			if task_date < todayDate():
				# print list_tasks[j]['title'], "Task Late!"
				LateTasks.append([each, list_tasks[j]['title'], list_tasks[j]['due_date']])
				# print "Added Late Task"
			elif task_date == todayDate():
				# print list_tasks[j]['title'], "Task Due Today"
				TodayTasks.append([each, list_tasks[j]['title'], list_tasks[j]['due_date']])
				# print "Added Today Task"
			elif (task_date - todayDate()) < timedelta(3):
				# print list_tasks[j]['title'], "Task in Future"
				FutureTasks.append([each, list_tasks[j]['title'], list_tasks[j]['due_date']])
				# print "Added Future Task"


for each in (LateTasks, TodayTasks, FutureTasks):
	text+='<H2>'+each[0]+'</H2>'
	# print each[0]
	# print "Number of Tasks: ", len(each)
	if len(each) > 1:text+='<h3>'+each[1][0]+'</h3>'
	for i in range(1,len(each)):
		if i > 1:
			if each[i][0] == each[i-1][0]:
				text+='<li>'+each[i][1]+'</li>'
			else:
				text+='<h3>'+each[i][0]+'</h3>'
				text+='<li>'+each[i][1]+'</li>'
		else:
			text+='<li>'+each[i][1]+'</li>'

	text+='</UL>'
text+='</HTML>'

text_file = open('TEST_EMAIL.html','w')
text_file.write(text)
text_file.close()

send_simple_message(mailgun_api, mailgun_key, to_name, to_email, text)

# Goes through each list and prints all the tasks - no discrimination!!
# 
# for each in list_dict:
# 	# print each
# 	text+='<h2>'+str(each)+'</h2><ul>'
# 	list_tasks = get_tasks(list_dict[each])
# 	for j in range(0,len(list_tasks)):
# 		if 'due_date' in list_tasks[j]:
# 			task_text = "\t"+list_tasks[j]['title']+"\t"+list_tasks[j]['due_date']
# 			# print task_text
# 			text+='<li>'+str(task_text)+'</li>'
# 		else:
# 			task_text = "\t"+list_tasks[j]['title']
# 			# print task_text
# 			text+='<li>'+str(task_text)+'</li>'
# 	text+='</ul>'
# text+='</html>'