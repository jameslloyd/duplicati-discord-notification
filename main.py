from flask import Flask, request
from discord_webhook import DiscordWebhook, DiscordEmbed

colour = {}
colour['Success'] = '7CFC00'
colour['Unknown'] = '909090'
colour['Warning'] = 'FFBF00'
colour['Error'] = 'FF0000'
colour['FATAL'] = 'FF0000'


app = Flask(__name__)

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
            title = f'Duplicati job {name} {output["MainOperation"]} {output["ParsedResult"]}'
            description=f'{output["MainOperation"]} started at {output["BeginTime"]}\n{output["MainOperation"]} took {output["Duration"]}\nNumber of files {output["ExaminedFiles"]}\nNumber of modified files {output["ModifiedFiles"]}\nSize of backup {output["SizeOfExaminedFiles"]}'
            footer = f'{output["ParsedResult"]}'
            color = colour[output["ParsedResult"]]
            embed = DiscordEmbed(title=title,description=description,color=color)
            embed.set_footer(text=footer)
            webhook.add_embed(embed)
            response = webhook.execute()
    return '{}'

if __name__ == "__main__":
    app.run(host="192.168.6.3")