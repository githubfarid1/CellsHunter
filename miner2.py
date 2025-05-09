from camoufox.sync_api import Camoufox
from dotenv import load_dotenv, dotenv_values
import sys
import os
from utils.time_helper import get_sync_time, get_time_with_timezone_and_offset, \
    get_time_object_with_timezone_and_offset, get_current_day_with_timezone_and_offset, \
    run_by_time, get_request_time, get_time_from_params
from browserforge.fingerprints import Screen
from datetime import datetime, timedelta, date, time
from pytz import timezone, utc
import requests
import json
from dateutil import tz
from constants import *
from concurrent.futures import ThreadPoolExecutor, wait, as_completed
import argparse
from utils.rotation_logger import setup_logger
from time import sleep

logger = setup_logger(__name__)
__version__ = '1.0'

logger.info(f'CellHunter started at {datetime.now().strftime("%D %T")}. Version {__version__}')

load_dotenv()
# USER = os.environ.get("USER")
# PASSWORD = os.environ.get("PASSWORD")
HEADLESS = (os.getenv('HEADLESS', 'False') == 'True')
# CLICKTIME = os.environ.get("CLICKTIME")
CELLIDS = os.environ.get("CELLIDS")
UNTILSECOND = float(os.environ.get("UNTILSECOND"))
SLEEPSECOND = float(os.environ.get("SLEEPSECOND"))
# breakpoint()
est = timezone("US/Eastern")
PROXY = None
# breakpoint()
if os.environ.get("PROXY_SERVER") != '':
    PROXY={
            'server': os.environ.get("PROXY_SERVER"),
            'username': os.environ.get("PROXY_USERNAME"),
            'password': os.environ.get("PROXY_PASSWORD")
        }


def gettimenow():
    time_synced = False
    selected_timezone = 'US/Eastern'
    try:
        time_offset = get_sync_time()[1]
        time_synced = True
    except:
        time_offset = 0.0
        print('Time Sync Required!','Server problem with get NTP time.\nRestart an app required.')
        time_synced = False
    finally:
        if time_offset != 0.0:
            time_offset_str = f'{time_offset:.2f}'
            message = (f'Your local clock is {time_offset_str} seconds fast.'
                if time_offset > 0 else f'Your local clock is {time_offset_str} seconds slow.')
            # print(message)
        else:
            if time_synced:
                print(f'Your local clock is in perfect sync')
            else:
                print(f'Time sync server issue. Display local time.')

    print(f"Timezone: {selected_timezone}")
    return get_current_day_with_timezone_and_offset(selected_timezone, time_offset)
def intercept_request(request, cellcode):
    if "retrieveInitalFormData" in request.url:
        headers = request.all_headers()
        with open('headers.json', 'w') as f:
            json.dump(headers, f)        
    
    return request    

def intercept_response(response, cellcode):
    if "retrieveInitalFormData" in response.url:
        info = response.json()
        with open("info.json", "w") as f:
            json.dump(info, f)
    
    return response    

def main():
    parser = argparse.ArgumentParser(description="Cells Hunter")
    parser.add_argument('-d', '--date', type=str,help="Date Click")
    parser.add_argument('-t', '--time', type=str,help="Time Click")
    parser.add_argument('-c', '--cellids', type=str,help="Cell IDs")
    parser.add_argument('-u', '--user', type=str,help="User")
    parser.add_argument('-p', '--password', type=str,help="Password")

    args = parser.parse_args()
    try:
        date.fromisoformat(args.date)
    except ValueError:
        message = "Incorrect date format, should be YYYY-MM-DD"
        logger.exception(message)
        raise ValueError(message)
        
    try:
        time.fromisoformat(args.time)
    except ValueError:
        message = "Incorrect time format, should be HH:MM:SS.MS"
        logger.exception(message)
        raise ValueError(message)


    clear = lambda: os.system('cls')
    clear()
    # breakpoint()
    selected_timezone = 'US/Eastern'
    clickdate = args.date
    clicktime = args.time
    # breakpoint()
    clickme = datetime(int(clickdate.split("-")[0]), int(clickdate.split("-")[1]), int(clickdate.split("-")[2]), 
                       int(clicktime.split(":")[0]), int(clicktime.split(":")[1]), int(clicktime.split(":")[2].split(".")[0]), int(clicktime.split(":")[2].split(".")[1]), tzinfo = tz.gettz(selected_timezone))
    
    clickmestr= " ".join([clickdate, clicktime])
    cellcode = args.cellids
    user = args.user
    password = args.password
    print("User:", user)
    print("Password:", password)

    print("CELL IDs:", cellcode)
    print("Click execute time at:", clickmestr)

    try:
        session = requests.Session()
        constrains = Screen(max_width=1280, max_height=720)
        with Camoufox(headless=HEADLESS, screen=constrains, os="windows", geoip=True,  locale="en-US") as playwright:
            # await run(playwright)
            if PROXY == None:
                context = playwright.new_context(no_viewport=True)
            else:
                context = playwright.new_context(no_viewport=True, proxy=PROXY)

            page = context.new_page()
            # breakpoint()
            url = "https://signin.ontario.ca/"
            print(f"Goto {url}" , "... ", end="", flush=True)
            page.goto(url, wait_until="networkidle", timeout=120000)
            print("PASSED")
            print("Waiting for Login", "... ", end="", flush=True)
            page.wait_for_selector("input[name='identifier']", timeout=30000)
            page.fill("input[name='identifier']", user)
            page.fill("input[name='credentials.passcode']", password)
            # breakpoint()
            
            # page.click("input[value='Sign in']", timeout=20000)
            page.click("input[value='Sign in']", timeout=60000, force=True)
            menu = page.wait_for_selector("article.chiclet--article", timeout=60000)
            print("PASSED")
            print("Opening Mining Lands Administration", "... ", end="", flush=True)

            menu.click()
            page2 = page.wait_for_event("popup")
            page2.on("request", lambda request: intercept_request(request, cellcode=cellcode))
            page2.on("response", lambda response: intercept_response(response, cellcode=cellcode))
            print("PASSED")
            print("Opening menu Register a minning Claim", "... ", end="", flush=True)
            page2.wait_for_selector("dshb-bulletin-dtv", timeout=60000)
            
            
            # page2.goto("https://www.mlas.mndm.gov.on.ca/mlas/index.html#/p_CanhAcmcAcquireMiningClaim", wait_until="networkidle")


            menu = page2.locator("li.menu").nth(4)
            menu.click()
            page.wait_for_timeout(500)
            menu.click()
            
            next = page2.wait_for_selector("input[name='declarationChkbox']")
            page2.wait_for_timeout(2000)
            next.click()

            next = page2.wait_for_selector("button#nextBtnId")
            # page2.wait_for_timeout(random.randint(1000, 3000))

            next.click()
            print("PASSED")
            print("Input Cell ID's", "... ", end="", flush=True)
            
            page2.fill("textarea#selectedGeoMapIds", cellcode, timeout=90000)
            print("PASSED")
            waittime = clickme - timedelta(seconds=SLEEPSECOND)
            opencaptchatime = clickme - timedelta(seconds=10)
            print("Sleep until", waittime.strftime("%m/%d/%Y, %H:%M:%S"), "...", end="", flush=True)
            while True:
                gt = datetime.now(est)
                if gt.timestamp() > waittime.timestamp():
                    break
            
            print("PASSED")
            time_offset = 0
            while True:
                try:
                    time_offset = get_sync_time()[1]
                    if time_offset != 0:
                        break
                except:
                    print("time offset failed, try again")
                    continue
            
            time_offset_str = f'{time_offset:.2f}'
            message = (f'Your local clock is {time_offset_str} seconds fast.'
                if time_offset > 0 else f'Your local clock is {time_offset_str} seconds slow.')
            # print(message)
            print("Waiting click time at", clickmestr.split(" ")[1], "....")
            
            with open('headers.json') as json_file:
                headers = json.load(json_file)
            readstatus  = False
            tokenlist = []
            while True:
                gt = datetime.now(est)
                gt = gt + timedelta(seconds=time_offset)
                print("Now:", gt.strftime("%H:%M:%S.%f"))
                if gt.timestamp() >= opencaptchatime.timestamp() and not readstatus:
                    readstatus = True
                    # print("read captcha token..")
                    try:
                        with open('captcharesponse1.txt') as file:
                            content = file.readlines()
                            captcharesponse = "".join(content).split('uvresp')[1].split(",")[1].replace('"',"").replace("'","")
                            tokenlist.append(captcharesponse)
                    except:
                        pass
                    try:    
                        with open('captcharesponse2.txt') as file:
                            content = file.readlines()
                            captcharesponse = "".join(content).split('uvresp')[1].split(",")[1].replace('"',"").replace("'","")
                            tokenlist.append(captcharesponse)
                    except:
                        pass
                    try:    
                        with open('captcharesponse3.txt') as file:
                            content = file.readlines()
                            captcharesponse = "".join(content).split('uvresp')[1].split(",")[1].replace('"',"").replace("'","")
                            tokenlist.append(captcharesponse)
                    except:
                        pass

                    
                    payload = PAYLOAD.copy()
                    with open('info.json') as json_file:
                        info = json.load(json_file)
                    payload['selectedCellIds'] = cellcode
                    payload['submitter'] = info['submitter']
                    payload['clientNumberId'] = info['clientNumberId']
                    payload['clientName'] = info['clientName']
                    payload['agentOfList'][0]['clientNumberId'] = info['agentOfList'][0]['clientNumberId']  
                    payload['agentOfList'][0]['fullName'] = info['agentOfList'][0]['fullName']  
                    payload['agentOfList'][0]['clientIdAndName'] = info['agentOfList'][0]['clientIdAndName']
                    payload['revisedSelectedCellIds'] = cellcode  
                    # payload['gRecaptchaResponse'] = captcharesponse



                if gt.timestamp() >= clickme.timestamp():
                    break

            def genmessage(response):
                try:
                    celllist = str(cellcode).split(", ")
                    json_data = response.json()
                    if json_data['status'] == 'SUCCESSFUL':
                        # self.locked_cells_by_user.emit(len(self.cells_list))
                        # self.success.emit(", ".join(self.cells_list))
                        text = f'Successful: Locked {len(celllist)} cells.'
                        with open("cellids.txt", "w") as f:
                            f.write(cellcode)
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
            
            def do_request(token):
                gt = datetime.now(est)
                gt = gt + timedelta(seconds=time_offset)
                starttime = gt.strftime("%H:%M:%S.%f")
                payload['gRecaptchaResponse'] = token
                response = session.post(
                    'https://www.mlas.mndm.gov.on.ca/mlas/mlas/tenure/module/p_canh/module/acmc/lockSelectedCells',
                    headers=headers,
                    json=payload,
                )
                print("Cell ID's claims Status:", genmessage(response), ", executed at:",starttime)

            gt = datetime.now(est)
            gt = gt + timedelta(seconds=time_offset)
            print("Bot is trying to Claims Cell IDs", cellcode)
            with ThreadPoolExecutor() as executor:
                # futures = [executor.submit(do_request) for i in range(0, 3)]
                futures = []
                for token in tokenlist:
                    sleep(0.1)
                    futures.append(executor.submit(do_request, token))
                for i, future in enumerate(as_completed(futures)):
                    try:
                        future.result()  # Ensure the task has completed without errors
                    
                    except Exception as e:
                        logger.exception(f"Error in thread: {str(e)}")
                        print(f"Error in thread: {e}")
            input("go to next page manually...")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type,fname,exc_tb.tb_lineno)
        logger.exception(" ".join([str(exc_type), str(fname), str(exc_tb.tb_lineno)]) )

if __name__ == "__main__":
    main()