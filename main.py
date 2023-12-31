import requests
import re
import os
import json
from time import sleep
import datetime
import concurrent.futures
import traceback
import pause
from termcolor import colored
from selenium import webdriver
from selenium.webdriver.common.by import By

# Getting path to account.json file
file = "accounts.json"
working_dir = os.path.dirname(__file__)
path_to_accounts = working_dir + "/" + file

facility_map = {
    "Tennis SRC": "1TS26",
    "MPF1": "1F124",
    "MPF2": "1F224",
}
booking_code_map = {
    "Tennis SRC": "1TS2TS0",
    "MPF1": "1F12F10",
    "MPF2": "1F22F20",
}


def get_timing_hash(facility_type):
    if facility_type == "Tennis SRC":
        return {
            "1": "0700-0800",
            "2": "0800-0900",
            "3": "0900-1000",
            "4": "1000-1100",
            "5": "1100-1200",
            "6": "1200-1300",
            "7": "1300-1400",
            "8": "1400-1500",
            "9": "1500-1600",
            "10": "1600-1700",
            "11": "1700-1800",
            "12": "1800-1900",
            "13": "1900-2000",
            "14": "2000-2100",
            "15": "2100-2200",
        }
    else:
        return {
            "1": "0830-1000",
            "2": "1000-1130",
            "3": "1130-1300",
            "4": "1300-1430",
            "5": "1430-1600",
            "6": "1600-1730",
            "7": "1730-1900",
        }


def main():
    facility_type = input("Choose Facility: 1-Tennis SRC, 2-MPF1, 3-MPF2\n")
    if facility_type == "1":
        facility_type = "Tennis SRC"
    elif facility_type == "2":
        facility_type = "MPF1"
    elif facility_type == "3":
        facility_type = "MPF2"

    print(f"Booking for {facility_type}...")

    booking_type = input("Choose Booking Type 1-Single booking, 2-Multiple booking\n")
    if booking_type == "1":
        single_booking(facility_type)
    elif booking_type == "2":
        multiple_booking(facility_type)


def single_booking(facility_type):
    # court = "1"
    # timing = "1"
    # facility_type = "Tennis SRC"
    # target_date = datetime.date.today() + datetime.timedelta(days=7)
    # username = "Jseow008"
    # password = "2103971q2w3e4r%T"
    # loginAndBook(court, timing, facility_type, target_date, username, password)
    # return

    today = datetime.date.today()
    selection = input("Booking at what time? 1-Midnight, 2-Now\n")
    timedelta = 8
    if selection == "2":
        timedelta = 7
    target_date = today + datetime.timedelta(days=timedelta)
    date = target_date.strftime("%d-%b-%Y")
    print("Target date: {}".format(date))
    username = input("username: ")
    password = input("password: ")

    court = input("Enter court number: ")
    print("Select a session below:")
    hash = get_timing_hash(facility_type)
    for k, v in hash.items():
        print("[{}] {}".format(k, v))
    timing = input("Enter timing: ")

    loginAndBook(court, timing, facility_type, target_date, username, password)


def multiple_booking(facility_type):
    today = datetime.date.today()
    selection = input("Booking at what time? 1-Midnight, 2-Now\n")
    timedelta = 8
    if selection == "2":
        timedelta = 7
    target_date = today + datetime.timedelta(days=timedelta)
    date = target_date.strftime("%d-%b-%Y")
    print("Target date: {}".format(date))

    accounts = {}
    timing_set = set()
    court_set = set()
    timing_hash = get_timing_hash(facility_type)
    while True:
        with open(path_to_accounts) as json_file:
            accounts = json.load(json_file)
            existing_courts = set()
            existing_timings = set()
            for key, value in accounts.items():
                existing_courts.add(key.split("_")[0])
                existing_timings.add(key.split("_")[1])
            print()
            print("###################### Settings #######################")
            if len(timing_set) == 0:
                timing_set.update(existing_timings)
            if len(court_set) == 0:
                court_set.update(existing_courts)
            print("Timings Set: {}".format(timing_set))
            print("Courts Set: {}".format(court_set))
            for key, value in accounts.items():
                print("{} Account: {}".format(key, value))
            print("########################################################\n")

        change = input(
            "1-Run Program, 2-Change Account Details, 3-Auto Assign Accounts, 4-Reset All, 5-Change Timings, 6-Change Courts, 7-Exit (1/2/3/4/5/6/7) "
        )
        print()
        if change == "1":
            # Handle parallel processing of each booking
            thread_list = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
                for court_timing, account in accounts.items():
                    # check if court_timing is assigned to an account
                    if "id" and "pw" in account:
                        print(
                            "Running Thread {}:   ID: {} PW: {}".format(
                                court_timing, account["id"], account["pw"]
                            )
                        )
                        # run threads for each account assignment
                        court = court_timing.split("_")[0]
                        time = court_timing.split("_")[1]
                        timing = [id for id, time_range in timing_hash.items() if time_range == time][0]  # get timing id
                        username = account["id"]
                        password = account["pw"]

                        thread = executor.submit(
                            loginAndBook,
                            court,
                            timing,
                            facility_type,
                            target_date,
                            username,
                            password,
                        )
                        thread_list.append(thread)

                done, not_done = concurrent.futures.wait(
                    thread_list, return_when=concurrent.futures.ALL_COMPLETED
                )
                print(
                    "\n################### RESULTS ###################\n{}".format(done)
                )
                for future in done:
                    print(future.result())
                break

        elif change == "2":
            while True:
                key = input(
                    "Enter the court_time you would like to change: (to exit enter 0) "
                )
                print(key)
                if key == "0":
                    break
                try:
                    new_id = input("Enter the new id for this court_time: ")
                    new_pw = input("Enter the new pw for this court_time: ")
                    accounts[key] = {"id": new_id, "pw": new_pw}
                    print()
                    print("new settings: #######################")
                    for key, value in accounts.items():
                        print("ID: {} PW: {}".format(key, value))
                    print()
                except Exception as e:
                    print(
                        "Invalid court_time due to {}. Please enter in court_0x00-0y00 format.".format(
                            str(e)
                        )
                    )
                    continue
        elif change == "3":
            print(
                "Enter new ids and pws. Once ready, enter 0 to start auto-allocation."
            )
            account_list = []
            while True:
                id = input("Enter id (Enter 0 to start auto-allocation): ")
                if id == "0":
                    break
                pw = input("Enter pw: ")
                account_list.append({"id": id, "pw": pw})
                print("Accounts to be allocated: {}".format(account_list))
                print()
            exit_bool = False
            account_copy = account_list
            accounts = {}
            # allocating accounts to each court and timing
            for timeslot in timing_set:
                if exit_bool:
                    break
                for court in court_set:
                    if len(account_copy) > 0:
                        sel_account = account_copy.pop()
                        temp_key = "{}_{}".format(court, timeslot)
                        accounts[temp_key] = sel_account

                        print("allocate {}: {}".format(temp_key, accounts[temp_key]))
                    else:
                        exit_bool = True
                        break
            with open(path_to_accounts, "w") as outfile:
                json.dump(accounts, outfile)
            print()
        elif change == "4":
            accounts = {}
            for timeslot in timing_set:
                for court in court_set:
                    temp_key = "{}_{}".format(court, timeslot)
                    accounts[temp_key] = ""
        elif change == "5":
            print("Current timings selection: {}".format(timing_set))
            new_range = input("Enter new timings, comma separated: ")
            timing_set.clear()
            print(new_range.split(","))
            print(timing_set)
            timing_set.update(new_range.split(","))
        elif change == "6":
            print("Current courts selection: {}".format(court_set))
            new_range = input("Enter new courts, comma separated: ")
            court_set.clear()
            court_set.update(new_range.split(","))
        elif change == "7":
            print("Exiting program")
            break


def loginAndBook(court, timing, facility_type, target_date, username, password):
    # print(f"{court} {timing} {facility_type} {target_date} {username} {password}")
    login_status = False
    booking_status = False
    timing_range = get_timing_hash(facility_type)[timing]

    try:
        print("Starting loginAndBook")
        driver = webdriver.Chrome()
        driver.implicitly_wait(30)
        date = target_date.strftime("%d-%b-%Y")
        login_status = False
        print(
            f"Waiting for target date. court: {court}, timing: {timing_range}, facility_type: {facility_type}, target_date: {date}, username: {username}, password: {password}"
        )
        # if target date is within 7 days
        if (datetime.date.today() + datetime.timedelta(days=7)) >= target_date:
            login_status = login(username, password, driver)
            print(f"{username} target date reached, starting the remaining process")
        # midnight booking
        else:
            print("Waiting for 2358:00 to log in")
            pause.until(
                datetime.datetime.combine(
                    datetime.date.today(), datetime.time(23, 58, 00)
                )
            )
            login_status = login(username, password, driver)

            print(
                "midnight booking. waiting till 0000, time now:{}. Waiting for {}".format(
                    datetime.datetime.now(),
                    datetime.datetime.combine(
                        (target_date - datetime.timedelta(days=7)),
                        datetime.time(0, 0, 0, 0),
                    ),
                )
            )
            pause.until(
                datetime.datetime.combine(
                    (target_date - datetime.timedelta(days=7)),
                    datetime.time(0, 0, 0, 0),
                )
            )
            print(f"{username} target date reached, starting the remaining process")
        if login_status:
            booking_status = doBookingRequests(
                facility_type, court, date, timing, driver, username, password
            )
            # booking_status = doBookingSelenium(
            #     facility_type, court, date, timing, driver
            # )

        return f"{username},{facility_type},C{court},{timing_range} | login:{login_status} | booking:{booking_status} | time:{datetime.datetime.now()}"
    except Exception:
        traceback.print_exc()
        return f"{username},{facility_type},C{court},{timing_range} | login:{login_status} | booking:{booking_status}"


def login(username, password, driver):
    try:
        print(f"Logging in... {username}")
        driver.get(
            "https://wis.ntu.edu.sg/webexe88/owa/srce_smain_s.SRC_GenEntry?p_closewind=N"
        )
        driver.find_element(
            By.LINK_TEXT, "Full time NTU/NIE UnderGrad Students"
        ).click()
        driver.find_element(By.ID, "userNameInput").send_keys(
            username.strip() + "@student.main.ntu.edu.sg"
        )
        driver.find_element(By.ID, "passwordInput").send_keys(password.strip())
        driver.find_element(By.ID, "submitButton").click()
    except Exception:
        print(colored("\n{} Login failed".format(username), "red"))
        traceback.print_exc()
        driver.close()
        return False
    else:
        print("{} Login successful".format(username))
        return True


def doBookingSelenium(facility_type, court, date, timing, driver):
    timing_range = get_timing_hash(facility_type)[timing]
    try:
        facility_id = facility_map[facility_type]
        driver.find_element(By.XPATH, f"//input[@value='{facility_id}']").click()
        facility_code = booking_code_map[facility_type]
        value = f"{facility_code}{court}{date}{timing}"
        print(
            "doBooking... {} {} {} C{} {} {} ".format(
                value, facility_type, facility_id, court, date, timing_range
            )
        )
        driver.find_element(By.XPATH, f"//input[@value='{value}']").click()
        driver.find_element(By.XPATH, "//input[@value='Confirm']").click()
        driver.find_element(By.XPATH, "//font[contains(text(),'Official Permit')]")
    except Exception:
        print(
            colored(
                f"\nBooking {facility_type} C{court} {timing_range} on {date} failed",
                "red",
            ),
        )
        traceback.print_exc()
        driver.close()
        return False
    else:
        print(f"Booking {facility_type} C{court} {timing_range} on {date} successful")
        driver.close()
        return True


def doBookingRequests(facility_type, court, date, timing, driver, username, password):
    cookies = driver.get_cookies()
    s = requests.Session()
    for cookie in cookies:
        if "sameSite" in cookie:
            cookie.pop("sameSite")
        if "httpOnly" in cookie:
            httpO = cookie.pop("httpOnly")
            cookie["rest"] = {"httpOnly": httpO}
        if "expiry" in cookie:
            cookie["expires"] = cookie.pop("expiry")
        s.cookies.set(**cookie)
    url = driver.current_url
    driver.close()
    matric = ""
    pattern = r"p1=([^&]+)"
    # Use re.search to find the first match in the URL
    match = re.search(pattern, url)
    # Check if a match was found
    if match:
        # Extract and return the value of p1
        matric = match.group(1)
        print(matric+" found")
    else:
        # Return None if p1 is not found in the URL
        print("no matric found")
        return
    facility_id = facility_map[facility_type]

    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36"
    }
    link = f"https://wis.ntu.edu.sg/pls/webexe88/srce_smain_s.srce$sel31_o?p1={matric}&p2=&p_info={facility_id}"

    facility_code = booking_code_map[facility_type]
    value = f"{facility_code}{court}{date}{timing}"

    try:
        resp = s.get(link, headers=headers).text
        if 'alert("Please log in' in resp:
            print()
            print(f"[!] Account {username} seems to be logged out! Logging in again!")
            # login(username, password, driver)
            print()
            return False
    except Exception as e:
        print("Failed to open link {} due to {}".format(link, str(e)))
        return False

    matching_slots = re.findall(
        r'NAME="p_rec" VALUE="(' + facility_code + court + date + timing + r')"', resp
    )
    matching_slots.extend(
        re.findall(
            r'name="p_rec" value="(' + facility_code + court + date + timing + r')"',
            resp,
        )
    )

    if len(matching_slots) == 0:
        print()
        print(
            "{}:  No available slot for {} (Court No. {}) on date {}".format(
                username, facility_code, court, date, timing
            )
        )
        print()
        return False
    else:
        matching_slots = matching_slots[-1]
        print("{} Trying to book slot {}".format(username, matching_slots))

    link = "https://wis.ntu.edu.sg/pls/webexe88/srce_sub1.srceb$sel32"
    headers = {
        "Referer": f"https://wis.ntu.edu.sg/pls/webexe88/srce_smain_s.srce$sel31_o?p1={matric}&p2=&p_info={facility_id}",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
    }
    data = {
        "p_rec": matching_slots.strip(),
        "p1": matric,
        "p2": "",
        "p_info": facility_id,
    }
    try:
        resp = s.post(link, headers=headers, data=data).text
        if 'alert("Please log in' in resp:
            print(f"[!] Account {username} seems to be logged out! Logging in again!")
            login()
            return False
    except Exception as e:
        print()
        print(
            "{username} Failed to open link {} due to {}".format(username, link, str(e))
        )
        print()
        return False
    # final confirmation

    link = "https://wis.ntu.edu.sg/pls/webexe88/srce_sub1.srceb$sel33"
    headers = {
        "Referer": "https://wis.ntu.edu.sg/pls/webexe88/srce_sub1.srceb$sel32",
        "user-agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36",
    }
    try:
        p1 = re.findall(r'NAME="p1" VALUE="(.*?)">', resp)[0]
    except:
        print()
        print(f"{username} You have an old booking! Booking failed!")
        print()
        return True
    p2 = re.findall(r'NAME="p2" VALUE="(.*?)">', resp)[0]
    fdate = re.findall(r'NAME="fdate" VALUE="(.*?)">', resp)[0]
    fcode = re.findall(r'NAME="fcode" VALUE="(.*?)">', resp)[0]
    floc = re.findall(r'NAME="floc" VALUE="(.*?)">', resp)[0]
    sno = re.findall(r'NAME="sno" VALUE="(.*?)">', resp)[0]
    stype = re.findall(r'NAME="stype" VALUE="(.*?)">', resp)[0]
    fcourt = re.findall(r'NAME="fcourt" VALUE="(.*?)">', resp)[0]
    ftype = re.findall(r'NAME="ftype" VALUE="(.*?)">', resp)[0]
    rptype = re.findall(r'NAME="rptype" VALUE="(.*?)">', resp)[0]
    P_info = re.findall(r'NAME="P_info" VALUE="(.*?)">', resp)[0]
    opmode = re.findall(r'NAME="opmode" VALUE="(.*?)">', resp)[0]
    frmk = re.findall(r'NAME="frmk" VALUE="(.*?)">', resp)[0]
    data = {
        "noaguest": "",
        "frmfrom": "selfbook",
        "p1": p1,
        "p2": p2,
        "noaguest": "0",
        "fdate": fdate,
        "fcode": fcode,
        "floc": floc,
        "sno": sno,
        "stype": stype,
        "paytype": "CC",
        "fcourt": fcourt,
        "ftype": ftype,
        "rptype": rptype,
        "P_info": P_info,
        "opmode": opmode,
        "frmk": frmk,
        "bOption": "Confirm",
    }
    try:
        resp = s.post(link, headers=headers, data=data).text
    except Exception as e:
        print()
        print("{} Failed to open link {} due to {}".format(username, link, str(e)))
        print()
        return False
    if "<font size=3>Official Permit</font>" in resp:
        print()
        print(
            f" court {court}_{timing} on {date} Booking successful! Account: {username} "
        )
        print("time completed:" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print()
        return True
    else:
        print()
        print(f" court {court}_{timing} on {date} Booking failed! Account: {username}")
        print(resp)
        print()
        return False


if __name__ == "__main__":
    main()
