import requests
from constants import *
from dotenv import load_dotenv, dotenv_values
import os
import json
load_dotenv()

def genmessage(response, cellcode):
    try:
        celllist = str(cellcode).split(", ")
        json_data = response.json()
        if json_data['status'] == 'SUCCESSFUL':
            # self.locked_cells_by_user.emit(len(self.cells_list))
            # self.success.emit(", ".join(self.cells_list))
            
            text = f'Successful: Locked {len(celllist)} cells.'
            request_status = True
        elif json_data['status'] == 'FAILED':
            answer = [x["msgKey"].replace("MLAS.GENERAL_ERROR_MSG.", "") for x in
                    json_data["returnValue"]]
            answer = ", ".join(list(set(answer)))
            text = f'Unsuccessful: {answer}'
            has_not_reopened = [True for x in json_data["returnValue"] if 'CELL_ID_NOT_REOPEN' in x["msgKey"]]
            if not any(has_not_reopened) or \
                    'CELL_ID_LOCKED' in answer or \
                    'RESULTING_CELLS_NOT_ADJACENT' in answer:
                request_status = False
                if 'RESULTING_CELLS_NOT_ADJACENT' in answer:
                    # self.cell_unavailable.emit(len(self.cells_list))
                    text = f'{len(celllist)} Cell(s) unvailable'
                elif 'CELL_ID_LOCKED' in answer:
                    text = f'{len(celllist)} Cell(s) Locked by others'
                    # self.lock_by_other_count.emit(len(self.cells_list))
            else:
                request_status = None
        else:
            request_status = False
            text = f'Unknown Status: {response.json()}'
        return text
    except Exception as _:
        request_status = False
        if "Session expired" in response.text:
            text = 'Error: Cookies expired. Login required.'
        else:
            text = 'Error: Cookies invalid. Login required.'
        # self.cookies_error.emit()
        return text

######
def unlink_cellids():
    with open('cellids.txt') as file:
        content = file.readlines()
    cellidslocked = "".join(content)

    with open('info.json') as json_file:
        info = json.load(json_file)

    cellcode = os.environ.get("RANDOM_OPEN_CELL")

    with open('headers.json') as json_file:
        headers = json.load(json_file)

    with open('captchaswapper2.txt') as file:
        content = file.readlines()
        captcharesponse = "".join(content).split('uvresp')[1].split(",")[1].replace('"',"").replace("'","")

    payload = PAYLOAD.copy()
    payload['selectedCellIds'] = cellcode
    payload['submitter'] = info['submitter']
    payload['clientNumberId'] = info['clientNumberId']
    payload['clientName'] = info['clientName']
    payload['agentOfList'][0]['clientNumberId'] = info['agentOfList'][0]['clientNumberId']  
    payload['agentOfList'][0]['fullName'] = info['agentOfList'][0]['fullName']  
    payload['agentOfList'][0]['clientIdAndName'] = info['agentOfList'][0]['clientIdAndName']
    payload['revisedSelectedCellIds'] = cellcode
    payload['gRecaptchaResponse'] = captcharesponse
    response = requests.post(
        'https://www.mlas.mndm.gov.on.ca/mlas/mlas/tenure/module/p_canh/module/acmc/lockSelectedCells',
        headers=headers,
        json=payload,
    )

    # print("Cell ID's claims Status:", genmessage(response=response, cellcode=cellcode))
    print("Client", info['clientName'], "has released cell ids:", cellidslocked)
#####

def link_cellids():
    with open('cookieto.txt') as file:
        content = file.readlines()
    cookieto = "".join(content)
    xsrftoken = ""
    for cook in cookieto.split(";"):
        if cook.split("=")[0].strip() == 'XSRF-TOKEN':
            xsrftoken = cook.split("=")[1]


    with open('cellids.txt') as file:
        content = file.readlines()
    cellids = "".join(content)

    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'priority': 'u=1, i',
        'referer': 'https://www.mlas.mndm.gov.on.ca/mlas/index.html',
        'sec-ch-ua': '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': os.environ.get("USER_AGENT"),
        'x-requested-with': 'XMLHttpRequest',
        'x-xsrf-token': xsrftoken,
        'cookie': cookieto,

    }

    response = requests.get(
        'https://www.mlas.mndm.gov.on.ca/mlas/api/prospector/getCurrentClientId',
        # cookies=cookies,
        headers=headers,
    )
    clientid = response.text

    params = {
        'id': clientid,
    }
    response = requests.get(
        'https://www.mlas.mndm.gov.on.ca/mlas/mlas/tenure/module/p_canh/module/acmc/retrieveInitalFormData',
        params=params,
        headers=headers,
    )
    info = response.json()
    # input(info)
    with open('captchaswapper1.txt') as file:
        content = file.readlines()
        captcharesponse = "".join(content).split('uvresp')[1].split(",")[1].replace('"',"").replace("'","")

    # print(captcharesponse)

    payload = PAYLOAD.copy()
    payload['selectedCellIds'] = cellids
    payload['submitter'] = info['submitter']
    payload['clientNumberId'] = info['clientNumberId']
    payload['clientName'] = info['clientName']
    payload['agentOfList'][0]['clientNumberId'] = info['agentOfList'][0]['clientNumberId']  
    payload['agentOfList'][0]['fullName'] = info['agentOfList'][0]['fullName']  
    payload['agentOfList'][0]['clientIdAndName'] = info['agentOfList'][0]['clientIdAndName']
    payload['revisedSelectedCellIds'] = cellids  
    payload['gRecaptchaResponse'] = captcharesponse
    # print(payload)
    # input()
    response = requests.post(
        'https://www.mlas.mndm.gov.on.ca/mlas/mlas/tenure/module/p_canh/module/acmc/lockSelectedCells',
        headers=headers,
        json=payload,
    )
    # print(response.text)
    # print("Cell ID's claims Status:", genmessage(response=response, cellcode=cellids))
    print("cell ids", cellids, "has locked by", info['clientName'])


def main():
    unlink_cellids()
    link_cellids()
if __name__ == '__main__':
    main()