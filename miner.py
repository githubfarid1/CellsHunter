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
from playsound import playsound
from concurrent.futures import ThreadPoolExecutor, wait, as_completed
import argparse

load_dotenv()
USER = os.environ.get("USER")
PASSWORD = os.environ.get("PASSWORD")
HEADLESS = (os.getenv('HEADLESS', 'False') == 'True')
# CLICKTIME = os.environ.get("CLICKTIME")
CELLIDS = os.environ.get("CELLIDS")
UNTILSECOND = float(os.environ.get("UNTILSECOND"))
SLEEPSECOND = float(os.environ.get("SLEEPSECOND"))
# breakpoint()
est = timezone("US/Eastern")
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
    args = parser.parse_args()
    try:
        date.fromisoformat(args.date)
    except ValueError:
        raise ValueError("Incorrect date format, should be YYYY-MM-DD")
        
    try:
        time.fromisoformat(args.time)
    except ValueError:
        raise ValueError("Incorrect time format, should be HH:MM:SS.MS")


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
    # cellcode = input("Selected Cell IDs: ")
    cellcode = args.cellids
    print("CELL IDs:", cellcode)
    print("Click execute time at:", clickmestr)
    try:
        session = requests.Session()
        constrains = Screen(max_width=1280, max_height=720)
        # with Camoufox(headless=HEADLESS, humanize=(0.5, 1.0), screen=constrains, os="windows") as playwright:
        with Camoufox(headless=HEADLESS, screen=constrains, os="windows", geoip=True,  locale="en-US") as playwright:

            # await run(playwright)
            context = playwright.new_context(no_viewport=True)
            page = context.new_page()
            # breakpoint()
            url = "https://signin.ontario.ca/"
            print(f"Goto {url}" , "... ", end="", flush=True)
            page.goto(url, wait_until="networkidle", timeout=120000)
            print("PASSED")
            print("Waiting for Login", "... ", end="", flush=True)
            page.wait_for_selector("input[name='identifier']", timeout=20000)
            page.fill("input[name='identifier']", USER)
            page.fill("input[name='credentials.passcode']", PASSWORD)
            # breakpoint()
            
            # page.click("input[value='Sign in']", timeout=20000)
            page.click("input[value='Sign in']", timeout=30000, force=True)
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
            print("Sleep until", waittime.strftime("%m/%d/%Y, %H:%M:%S"), "...", end="", flush=True)
            while True:
                gt = datetime.now(est)
                if gt.timestamp() > waittime.timestamp():
                    break
            
            print("PASSED")
            # playsound("sound1.wav")
            # input("pause")
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

            while True:
                gt = datetime.now(est)
                gt = gt + timedelta(seconds=time_offset)
                print("Now:", gt.strftime("%m/%d/%Y, %H:%M:%S"))
                if gt.timestamp() >= clickme.timestamp():
                    break

            with open('headers.json') as json_file:
                headers = json.load(json_file)
            
            with open('captcharesponse.txt') as file:
                content = file.readlines()
            captcharesponse = content[3].split(",")[1].replace('"',"").replace("'","")

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
            payload['gRecaptchaResponse'] = captcharesponse
            def do_request():
                response = session.post(
                    'https://www.mlas.mndm.gov.on.ca/mlas/mlas/tenure/module/p_canh/module/acmc/lockSelectedCells',
                    headers=headers,
                    json=payload,
                )
                result = response.json()
                print("Cell ID's claims Status:", result['status'])

            gt = datetime.now(est)
            endtime = gt + timedelta(seconds=time_offset+UNTILSECOND)
            while True:
                with ThreadPoolExecutor(max_workers=10) as executor:
                    futures = [executor.submit(do_request) for i in range(0, 10)]
                    for i, future in enumerate(as_completed(futures)):
                        try:
                            future.result()  # Ensure the task has completed without errors
                        except Exception as e:
                            print(f"Error in thread: {e}")

                
                gt = datetime.now(est)
                gt = gt + timedelta(seconds=time_offset)
                if gt.timestamp() > endtime.timestamp():
                    break
            input("go to next page manually...")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type,fname,exc_tb.tb_lineno)

if __name__ == "__main__":
    main()