from flask import Flask, request, render_template
import requests
from discord_webhook import DiscordWebhook, DiscordEmbed

colour = {}
colour['Success'] = '7CFC00'
colour['Unknown'] = '909090'
colour['Warning'] = 'FFBF00'
colour['Error'] = 'FF0000'
colour['FATAL'] = 'FF0000'
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
            for item in data:
                if item.startswith(tuple(dataitems)):
                    if ':' in item:
                        i = item.split(': ')
                        output[i[0]]=i[1] 
            output['Duration'] = output['Duration'].split(':')
            print(output['Duration'])
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
            title = f'Duplicati job {name} {output["MainOperation"]} {output["ParsedResult"]}'
            footer = f'{output["MainOperation"]} {output["ParsedResult"]}'
            embed = DiscordEmbed(title=title,color=colour[output["ParsedResult"]])
            output["BeginTime"] = output["BeginTime"].split('(')
            embed.set_author(name="Duplicati Discord Notification",url="https://duplicati-notifications.lloyd.ws/", )
            embed.add_embed_field(name='Started', 
                                    value=output["BeginTime"][0]) # 2/7/2022 7:25:05 AM (1644218705)  %-m/%-d/%Y %H:%-M:%S ()
            embed.add_embed_field(name='Time Taken', value=duration) #00:00:00.2887780
            embed.add_embed_field(name='Files', value='{:,}'.format(int(output["ExaminedFiles"]))) # f'{1000000:,}'
            embed.add_embed_field(name='Deleted Files', value='{:,}'.format(int(output["DeletedFiles"])))
            embed.add_embed_field(name='Modified Files', value='{:,}'.format(int(output["ModifiedFiles"])))
            embed.add_embed_field(name='Size', value=size)
            embed.set_footer(text=footer)
            webhook.add_embed(embed)
            webhook.execute()
        if request.args.get('duplicatimonitor'):
            postdata = {'message': message}
            requests.post(request.args.get('duplicatimonitor'), data = postdata)
    return '{}'

if __name__ == "__main__":
    app.run(host="0.0.0.0")