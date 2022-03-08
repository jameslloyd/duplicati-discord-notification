import requests

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
icon['Uknown'] = ':grey_question:'
icon['FATAL'] = ':fire:'

def sizeof_fmt(num, suffix="B"):
    num = int(num)
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"

output = {
    "_id": { "$oid": "6204747a8961f9f5d2fac759" },
    "ip": "127.0.0.1",
    "name": "Home Backup to Backblaze",
    "webhook": "https://discord.com/api/webhooks/932532069626695692/spYLGG9QGItAThgVHt77PoFa4tFavss_4cl6quodEKSKKMeS3sXtFDQTgaP-BWN9FeEZ",
    "DeletedFiles": "0",
    "DeletedFolders": "0",
    "ModifiedFiles": "26",
    "ExaminedFiles": "167832",
    "OpenedFiles": "27",
    "AddedFiles": "1",
    "SizeOfModifiedFiles": "78288426",
    "SizeOfAddedFiles": "438",
    "SizeOfExaminedFiles": "656766671821",
    "SizeOfOpenedFiles": "78426596",
    "NotProcessedFiles": "0",
    "AddedFolders": "0",
    "TooLargeFiles": "0",
    "FilesWithError": "0",
    "ModifiedFolders": "0",
    "ModifiedSymlinks": "0",
    "AddedSymlinks": "0",
    "DeletedSymlinks": "0",
    "PartialBackup": "False",
    "Dryrun": "False",
    "MainOperation": "Backup",
    "ParsedResult": "Success",
    "Version": "2.0.6.3 (2.0.6.3_beta_2021-06-17)",
    "EndTime": "2/10/2022 2:12:07 AM (1644459127)",
    "BeginTime": ["2/10/2022 2:00:00 AM ", "1644458400)"],
    "Duration": ["00", "12", "07.8836510"],
    "MessagesActualLength": "29",
    "WarningsActualLength": "0",
    "ErrorsActualLength": "0",
    "when": {
        "$date": "2022-02-10T02:12:10.281Z"
    }
}


webhookurl = 'https://discord.com/api/webhooks/931137345456066620/xJbBeXzqxAzpgNs6YEABoPxSZrGz52S6EjqfN7s3s9xcW3amdOQJuyXxwDcYTJEarxVj'
name = "Home-Back-blaze"
size = sizeof_fmt(output["SizeOfExaminedFiles"])
title = icon[output['ParsedResult']] + " Duplicati job " + name + " " + output['MainOperation'] + " " + output['ParsedResult'] + " " + icon[output['ParsedResult']]
footer = f'{output["MainOperation"]} {output["ParsedResult"]}'

duration = ''
if output['Duration'][0] != '00':
    duration = f"{duration} {output['Duration'][0]} Hrs "
if output['Duration'][1] != '00':
    duration = f"{duration} {output['Duration'][1]} Mins "
if output['Duration'][2] != '00':
    seconds = int(round(float(output['Duration'][2]),1))
    duration = f"{duration} {seconds} Secs "        
print(title)
jsondata= {
"content": 'yo yo yo',
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

result = requests.post(webhookurl,json = jsondata)
print(result.status_code)