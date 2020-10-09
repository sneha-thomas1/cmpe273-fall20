import yaml
import sys
import schedule
from datetime import datetime
import requests
import operator
import calendar
import time

input_filename=sys.argv[1]
with open(input_filename,"r") as file:
    input_file = yaml.full_load(file)


def job():
    steps=input_file['Scheduler']['step_id_to_execute']
    data=None
    for x in range(len(steps)):
        execute_step(steps[x],data)


def http_call(config):
    if config['method']=='GET':
        r = requests.get(config['url'])
    else :
        print("Invalid method")
    return r

##evaluate conditional statement
def evaluate_condition(condition,response):
    if list(condition.keys())[0]=='if':
            operator=list(condition['if'].keys())[0]
            left=condition['if'][f'{operator}']['left']
            right=condition['if'][f'{operator}']['right']
            if left=="http.response.code":
                left=response.status_code
            else :
                print("Invalid value")
            if operator =='equal':
                if left ==right:
                    return True
                else :
                    return False
    else :
        print("Invalid statement")
    return False

##execute steps
def execute_step(step,data):
    actions=input_file['Steps'][int(step)-1][int(step)]
    if actions['type'] == 'HTTP_CLIENT':
        action_url=actions['outbound_url']
        if action_url.startswith("::input"):
            if action_url[action_url.rindex(":")+1:]=='data':
                url=data
        else:
            url=actions['outbound_url']   
        config={
            'method' : actions['method'],
            'url': f'{url}'
        }
        response=http_call(config)
        condition=actions['condition']
        condition_value=evaluate_condition(condition,response)
        if condition_value :
            action=condition['then']['action']
            data=condition['then']['data']
        else:
            action=condition['else']['action']
            data=condition['else']['data']
        execute_action(action,data,response)
    else :
        print("Invalid type")

##execute action based on condition 
def execute_action(action,data,response):
    now = datetime.now()
    response_values={
        'http.response.code':response.status_code,
        'http.response.body':response.text,
        'http.response.headers.content-type':response.headers['Content-Type'],
        'http.response.headers.X-Ratelimit-Limit':response.headers.get('X-RateLimit-Limit',None)
    }
    if action.partition("::")[2].startswith('print'):
        print (response_values.get(data,data))
    elif action.partition("::")[2].startswith('invoke'):
        step_to_execute=action[action.rindex(":")+1:]
        execute_step(step_to_execute,data)
    else:
        print("Invalid action")

        
##sceduler
def scheduler():
    when=input_file['Scheduler']['when']
    mm=when.split()[0]
    hour=when.split()[1]
    day=when.split()[2]
    if day!='*':
        day=int(day)

    if mm=='*' and hour=='*' and day=='*':
        schedule.every().minutes.do(job)

    elif day=='*' and hour=='*' :
        schedule.every(int(mm)).minutes.do(job)

    elif mm=='*' and hour=='*' :
        if day==0:
            schedule.every().sunday.at("00:00").do(job)
        elif day==1:
            schedule.every().monday.at("00:00").do(job)
        elif day==2:
            schedule.every().tueday.at("00:00").do(job)
        elif day==3:
            schedule.every().at("00:00").do(job)
        elif day==4:
            schedule.every().thursday.at("00:00").do(job)
        elif day==5:
            schedule.every().friday.at("00:00").do(job)
        elif day==6:
            schedule.every().saturday.at("00:00").do(job)
        else:
            print("Invalid weekday")

    elif day=='*' and mm=='*' :
        time_str=hour+":00"
        time_obj=str(datetime.strptime(time_str, '%H:%M').time())
        schedule.every().day.at(time_obj).do(job)

    elif day=='*':
        time_str=hour+":"+mm
        time_obj=str(datetime.strptime(time_str, '%H:%M').time())
        schedule.every().day.at(time_obj).do(job)

    elif mm=='*':
        if day==0:
            schedule.every().sunday.at(int(hour)).do(job)
        elif day==1:
            schedule.every().monday.at(int(hour)).do(job)
        elif day==2:
            schedule.every().tueday.at(int(hour)).do(job)
        elif day==3:
            schedule.every().wednesday.at(int(hour)).do(job)
        elif day==4:
            schedule.every().thursday.at(int(hour)).do(job)
        elif day==5:
            schedule.every().friday.at(int(hour)).do(job)
        elif day==6:
            schedule.every().saturday.at(int(hour)).do(job)
        else:
            print("Invalid weekday")

    elif hour=='*':
        time_str="00:"+mm
        time_obj=str(datetime.strptime(time_str, '%H:%M').time())
        if day==0:
            schedule.every().sunday.at(time_obj).do(job)
        elif day==1:
            schedule.every().monday.at(time_obj).do(job)
        elif day==2:
            schedule.every().tueday.at(time_obj).do(job)
        elif day==3:
            schedule.every().wednesday.at(time_obj).do(job)
        elif day==4:
            schedule.every().thursday.at(time_obj).do(job)
        elif day==5:
            schedule.every().friday.at(time_obj).do(job)
        elif day==6:
            schedule.every().saturday.at(time_obj).do(job)
        else:
            print("Invalid weekday")

    else:
        time_str=hour+":"+mm
        time_obj=str(datetime.strptime(time_str, '%H:%M').time())
        if day==0:
            schedule.every().sunday.at(time_obj).do(job)
        elif day==1:
            schedule.every().monday.at(time_obj).do(job)
        elif day==2:
            schedule.every().tueday.at(time_obj).do(job)
        elif day==3:
            schedule.every().wednesday.at(time_obj).do(job)
        elif day==4:
            schedule.every().thursday.at(time_obj).do(job)
        elif day==5:
            schedule.every().friday.at(time_obj).do(job)
        elif day==6:
            schedule.every().saturday.at(time_obj).do(job)
        else:
            print("Invalid weekday")


scheduler()


while True:
    schedule.run_pending()
    time.sleep(1)




