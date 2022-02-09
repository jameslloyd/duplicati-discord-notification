import requests, os
from flask import Flask, request, render_template
from discord_webhook import DiscordWebhook, DiscordEmbed
from google.cloud import secretmanager
from pymongo import MongoClient
import datetime

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

colour = {}
colour['Success'] = '7CFC00'
colour['Unknown'] = '909090'
colour['Warning'] = 'FFBF00'
colour['Error'] = 'FF0000'
colour['FATAL'] = 'FF0000'
icon = {}
icon['Success'] = ':white_check_mark:'
icon['Warning'] = ':warning:'
icon['Error'] = ':no_entry:'
icon['Uknown'] = ':grey_question:'
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

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/report", methods=['POST'])
def report():
    if request.args.get('webhook'):
        webhookurl = request.args.get('webhook')
        message = request.form.get('message')
        if request.args.get('name'):
            name = request.args.get('name')
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
            webhook = DiscordWebhook(url=webhookurl, username=f'{output["MainOperation"]} Notification')
            size = sizeof_fmt(output["SizeOfExaminedFiles"])
            title = f'{icon[output["ParsedResult"]]} Duplicati job {name} {output["MainOperation"]} {output["ParsedResult"]} {icon[output["ParsedResult"]]}'
            footer = f'{output["MainOperation"]} {output["ParsedResult"]}'
            embed = DiscordEmbed(title=title,color=colour[output["ParsedResult"]], description=erroroutput)
            output["BeginTime"] = output["BeginTime"].split('(')
            embed.set_author(name="Duplicati Discord Notification",url="https://duplicati-notifications.lloyd.ws/")
            embed.add_embed_field(name='Started', 
                                    value=output["BeginTime"][0]) # 2/7/2022 7:25:05 AM (1644218705)  %-m/%-d/%Y %H:%-M:%S ()
            embed.add_embed_field(name='Time Taken', value=duration) #00:00:00.2887780
            embed.add_embed_field(name='No. Files', value='{:,}'.format(int(output["ExaminedFiles"])))
            embed.add_embed_field(name='Added Files', value='{:,}'.format(int(output["AddedFiles"])))
            embed.add_embed_field(name='Added Size', value=sizeof_fmt(int(output["SizeOfAddedFiles"]))) # f'{1000000:,}'
            embed.add_embed_field(name='Deleted Files', value='{:,}'.format(int(output["DeletedFiles"])))
            embed.add_embed_field(name='Modified Files', value='{:,}'.format(int(output["ModifiedFiles"])))
            embed.add_embed_field(name='Modified Size', value=sizeof_fmt(int(output["SizeOfModifiedFiles"])))
            embed.add_embed_field(name='Size', value=size)
            embed.set_footer(text=footer)
            webhook.add_embed(embed)
            webhook.execute()
            if DATABASE == 'True' and PROJECTID:
                output['when'] = datetime.datetime.utcnow()
                print('trying to insert')
                collection.insert_one(output)
        if request.args.get('duplicatimonitor'):
            postdata = {'message': message}
            requests.post(request.args.get('duplicatimonitor'), data = postdata)
    return '{}'
    


if __name__ == "__main__":
    app.run(host="0.0.0.0")