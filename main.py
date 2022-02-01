from flask import Flask, request
import requests
from discord_webhook import DiscordWebhook, DiscordEmbed

colour = {}
colour['Success'] = '7CFC00'
colour['Unknown'] = '909090'
colour['Warning'] = 'FFBF00'
colour['Error'] = 'FF0000'
colour['FATAL'] = 'FF0000'


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
    return 'OK'

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
                if ':' in item:
                    i = item.split(': ')
                    output[i[0]]=i[1]
            webhook = DiscordWebhook(url=webhookurl)
            size = sizeof_fmt(output["SizeOfExaminedFiles"])
            title = f'Duplicati job {name} {output["MainOperation"]} {output["ParsedResult"]}'
            description=f'{output["MainOperation"]} started at {output["BeginTime"]}\n{output["MainOperation"]} took {output["Duration"]}\nNumber of files {output["ExaminedFiles"]}\nNumber of modified files {output["ModifiedFiles"]}\nSize of backup {size}'
            footer = f'{output["ParsedResult"]}'
            color = colour[output["ParsedResult"]]
            embed = DiscordEmbed(title=title,description=description,color=color)
            embed.set_footer(text=footer)
            webhook.add_embed(embed)
            response = webhook.execute()
        if request.args.get('duplicatimonitor'):
            postdata = {'message': message}
            requests.post(request.args.get('duplicatimonitor'), data = postdata)

    return '{}'

if __name__ == "__main__":
    app.run(host="192.168.6.3")