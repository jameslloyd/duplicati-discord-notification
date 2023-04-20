import requests, os, datetime, json
from flask import Flask, request, render_template, abort
from discord_webhook import DiscordWebhook, DiscordEmbed
from google.cloud import secretmanager
from pymongo import MongoClient
import logging

def access_secret_version(secret_id, PROJECT_ID, version_id="latest"):
    # Create the Secret Manager client.
    client = secretmanager.SecretManagerServiceClient()
    # Build the resource name of the secret version.
    name = f"projects/{PROJECT_ID}/secrets/{secret_id}/versions/{version_id}"
    # Access the secret version.
    response = client.access_secret_version(name=name)
    # Return the decoded payload.
    return response.payload.data.decode('UTF-8')

DATABASE = os.getenv('DATABASE',False)
PROJECTID = os.getenv('PROJECTID',False)
if DATABASE == 'True' and PROJECTID:
    client = MongoClient(access_secret_version('mongodburl',PROJECTID))
    db = client.duplicati
    collection = db.duplicati

versionurl ='https://updates.duplicati.com/beta/latest-installers.js'

colour = {}
colour['Success'] = 8190976
colour['Unknown'] = 9474192
colour['Warning'] = 16760576
colour['Error'] = 16711680
colour['FATAL'] = 16711680
icon = {}
icon['Success'] = ':white_check_mark:'
icon['Warning'] = ':warning:'
icon['Error'] = ':no_entry:'
icon['Unknown'] = ':grey_question:'
icon['FATAL'] = ':fire:'

dataitems = ['DeletedFiles','DeletedFolders','ModifiedFiles','ExaminedFiles','OpenedFiles','AddedFiles','SizeOfModifiedFiles','SizeOfAddedFiles','SizeOfExaminedFiles','SizeOfOpenedFiles','NotProcessedFiles','AddedFolders','TooLargeFiles','FilesWithError','ModifiedFolders','ModifiedSymlinks','AddedSymlinks','DeletedSymlinks','PartialBackup','Dryrun','MainOperation','ParsedResult','Version','EndTime','BeginTime','Duration','MessagesActualLength','WarningsActualLength','ErrorsActualLength']
app = Flask(__name__)

def sizeof_fmt(num, suffix="B"):
    num = int(num)
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"

def get_url(url):
    r = requests.get(url)
    if r.status_code == 200:
        return r.text
    else:
        print(r.status_code)
        return False

def get_json(text):
    obj = text[text.find('{') : text.rfind('}')+1]
    return json.loads(obj)

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/report", methods=['POST'])
def report():
    if request.args.get('webhook'):
        webhookurl = request.args.get('webhook', '')
        message = request.form.get('message','')
        if request.args.get('level'):
            if request.args.get('level') == 'w':
                notification_level = ['Unknown','Warning','Error','FATAL']
            elif request.args.get('level') == 'e':
                notification_level = ['Unknown','Error','FATAL']
            else:
                notification_level = ['Success','Unknown','Warning','Error','FATAL']
        else:
            notification_level = ['Success','Unknown','Warning','Error','FATAL']
            
        if request.args.get('name'):
            name = request.args.get('name').replace(" ", "_")
            data = message.split('\n')
            output = {}
            output['ip'] = request.remote_addr
            output['name'] = name
            output['webhook'] = webhookurl
            errors = []
            for item in data:
                if item.startswith(tuple(dataitems)):
                    if ':' in item:
                        i = item.split(': ')
                        output[i[0]]=i[1]
                else:
                    if 'Access to the path' in item:
                        error = item.split('Access to the path ')
                        errors.append(error[1])
            errors = list(dict.fromkeys(errors))
            erroroutput = ''
            for e in errors[:2]:
                erroroutput = f'{erroroutput}\n Access to path {e}'
            output['Duration'] = output['Duration'].split(':')
            duration = ''
            if output['Duration'][0] != '00':
                duration = f"{duration} {output['Duration'][0]} Hrs "
            if output['Duration'][1] != '00':
                duration = f"{duration} {output['Duration'][1]} Mins "
            if output['Duration'][2] != '00':
                seconds = int(round(float(output['Duration'][2]),1))
                duration = f"{duration} {seconds} Secs "        

            # duplicati version check
            #latest_duplicati_versions = get_json(get_url(versionurl))
            #latest_version = latest_duplicati_versions['version']
            #current_version = output['Version'].split(' ')
            #current_version = current_version[0]
            #if current_version != latest_version:
            #    erroroutput = f"{erroroutput} \n :warning: Duplicati isn't running on the latest version :warning:"

            #webhook = DiscordWebhook(url=webhookurl, username=f'{output["MainOperation"]} Notification')
            size = sizeof_fmt(output["SizeOfExaminedFiles"])
            title = f'{icon[output["ParsedResult"]]} Duplicati job {name} {output["MainOperation"]} {output["ParsedResult"]} {icon[output["ParsedResult"]]}'
            footer = f'{output["MainOperation"]} {output["ParsedResult"]}'
            #embed = DiscordEmbed(title=title,color=colour[output["ParsedResult"]], description=erroroutput)
            output["BeginTime"] = output["BeginTime"].split('(')
            #embed.set_author(name="Duplicati Discord Notification",url=f"https://duplicati-notifications.lloyd.ws/chart?name={name}&webhook={webhookurl}")
            #embed.add_embed_field(name='Started',       value=output["BeginTime"][0]) # 2/7/2022 7:25:05 AM (1644218705)  %-m/%-d/%Y %H:%-M:%S ()
            #embed.add_embed_field(name='Time Taken',    value=duration) #00:00:00.2887780
            #embed.add_embed_field(name='No. Files',     value='{:,}'.format(int(output["ExaminedFiles"])))
            #embed.add_embed_field(name='Added Files',   value='{:,}'.format(int(output["AddedFiles"])))
            #embed.add_embed_field(name='Added Size',    value=sizeof_fmt(int(output["SizeOfAddedFiles"]))) # f'{1000000:,}'
            #embed.add_embed_field(name='Deleted Files', value='{:,}'.format(int(output["DeletedFiles"])))
            #embed.add_embed_field(name='Modified Files',value='{:,}'.format(int(output["ModifiedFiles"])))
            #embed.add_embed_field(name='Modified Size', value=sizeof_fmt(int(output["SizeOfModifiedFiles"])))
            #embed.add_embed_field(name='Size', value=size)
            #embed.set_footer(text=footer)
            #webhook.add_embed(embed)
            #response = webhook.execute()
    
            #if response.status_code == 200:
            #    logging.info(f'[WEBHOOK] Success to {webhookurl}')
            #else:
            #    logging.warning(f'[WEBHOOK] Failed to {webhookurl}')

            jsondata= {
                 "embeds": [
                    {
                    "title": title,
                    "color": colour[output["ParsedResult"]],
                    "fields": [
                        {
                        "name": "Started",
                        "value": output["BeginTime"][0],
                        "inline": 'true'
                        },
                        {
                        "name": "Time Taken",
                        "value": duration,
                        "inline": 'true'
                        },
                        {
                        "name": "No. Files",
                        "value": '{:,}'.format(int(output["ExaminedFiles"])),
                        "inline": 'true'
                        },
                        {
                        "name": "Added Files",
                        "value": '{:,}'.format(int(output["AddedFiles"])),
                        "inline": 'true'
                        },
                        {
                        "name": "Added Size",
                        "value": sizeof_fmt(int(output["SizeOfAddedFiles"])),
                        "inline": 'true'
                        },
                        {
                        "name": "Deleted Files",
                        "value": '{:,}'.format(int(output["DeletedFiles"])),
                        "inline": 'true'
                        },
                        {
                        "name": "Modified Files",
                        "value": '{:,}'.format(int(output["ModifiedFiles"])),
                        "inline": 'true'
                        },
                        {
                        "name": "Modified Files Size",
                        "value": sizeof_fmt(int(output["SizeOfModifiedFiles"])),
                        "inline": 'true'
                        },
                        {
                        "name": "Size",
                        "value": size,
                        "inline": 'true'
                        }
                    ],
                    "author": {
                        "name": "Duplicati Discord Notification",
                        "url": f"https://duplicati-notifications.lloyd.ws/chart?name={name}&webhook={webhookurl}",
                        "icon_url": "https://www.duplicati.com/images/duplicati-fb-share-v1.png"
                    }
                    }
                ]
                }
            if output["ParsedResult"] in notification_level:
                webhookresult = requests.post(webhookurl,json = jsondata)
            #print(webhookresult)

            if DATABASE == 'True' and PROJECTID:
                output['when'] = datetime.datetime.utcnow()
                print('trying to insert')
                collection.insert_one(output)
        if request.args.get('duplicatimonitor'):
            postdata = {'message': message}
            requests.post(request.args.get('duplicatimonitor'), data = postdata)
    return '{}'

@app.route("/chart", methods=['GET'])
def chart():
    name = request.args.get('name','')
    webhook = request.args.get('webhook','')
    length = int(request.args.get('length',30))
    height = int(request.args.get('height',100))
    if name == '' or webhook == '':
        abort(404)
    query = [
        {
            '$match': {
                'name': name, 
                'webhook': webhook
            }
        }, {
            '$sort': {
                'when': -1
            }
        }, {
            '$limit': length
        }
    ]
    data = list(collection.aggregate(query))
    if len(data) < 1:
        abort(404)
    addedfiles = []
    when = []
    modifiedfiles = []
    deletedfiles = []
    timetaken = []
    size =[]
    backups = list(collection.distinct("name",{"webhook" : webhook}))
    for d in data:
        timetaken.append((int(d['Duration'][0])*60*60) + (int(d['Duration'][1])*60) + float(d['Duration'][2]))
        size.append(float(d['SizeOfExaminedFiles'])/1073741824)
        addedfiles.append(d['AddedFiles'])
        deletedfiles.append(d['DeletedFiles'])
        modifiedfiles.append(d['ModifiedFiles'])
        when.append(d['when'].strftime('%Y-%m-%dT%H:%M:%SZ'))  #2017-01-07 18:00:00
    return render_template('chart.html', when=when,addedfiles=addedfiles,modifiedfiles=modifiedfiles,deletedfiles=deletedfiles,size=size,timetaken=timetaken,backups=backups,height=height)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8888)