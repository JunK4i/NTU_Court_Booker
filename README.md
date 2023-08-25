# NTU_Facilities_Booker

Selenium Facilities Booking Bot for Tennis@SRC, MPF1,  MPF2. (You can find out the respective IDs by looking into the booking websites's HTML)

It automates "clicking of buttons" in order to increase the speed of the booking operation. However the bottleneck is still your network, so ensure you have good connection.

Instructions:

1. For first time run: pip3 install -r requirements.txt

2. run: python3 main.py

3. Single Booking is used for more competitive bookings

4. Multiple Booking is used to automate booking of multiple less competitive courts. It uses multithreading to make the bookings concurrently. This operation requires an accounts.json file in the same directory.

5. In order to generate the accounts.json, you need to set the timing range, court range using the functions in the terminal menu, and select "Auto Assign Accounts", and enter the account details accordingly. To speed up this process you can also copy paste a list in the following format:
   id1
   pw1
   id2
   pw3
   if the terminal says pw:, press enter and enter 0, else the terminal should instruct u you enter 0.

6. Alternatively you can type out the accounts.json yourself in the following format:
   {
   <court_choice>\*<timing_range>: {id: xxx, pw: xxx},
   Eg. 1_0800-0900: {id: xxx, pw: xxx}
   }
