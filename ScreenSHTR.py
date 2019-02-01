import pyautogui
import time
import datetime
import os
import shutil
import ftplib
import configparser
import uuid

config = configparser.ConfigParser()
config.read('ScreenSHTR.ini')

screenSaveFolder = config['PATHS']['screenSaveFolder']
deltaScreenshot = config['TIME']['deltaScreenshot']
screenShotTimerHour = config['TIME']['screenShotTimerHour']
screenShotTimerMinutes = config['TIME']['screenShotTimerMinutes']
ftpHostName = config['FTP']['ftpHostName']
ftpUser = config['FTP']['ftpUser']
ftpPassword = config['FTP']['ftpPassword']
numberOfScreens = config['OTHER']['numberOfScreens']

today = datetime.datetime.now()
today = str(today).replace("-", "")
today = today[0:8]  # get today date in desired format (yyyymmdd)

uniqueId = str(uuid.uuid4().time)[:5]

screenFolder = str(screenSaveFolder).replace("\\", "\\\\") + "ScreenSHTR\\" + today + "_{}".format(uniqueId)


def createFolder():
    # check if ScreenSHTR folder exist. If not, create one
    if os.path.isdir(screenFolder) is True:
        pass
    else:
        os.makedirs(screenFolder, exist_ok=True)


def doScreen(index):
    # actaual part that do the screenshot and save it to defined folder
    # image name is in yyyymmdd_x format, where 'x' is a progressive number
    pyautogui.screenshot(screenFolder + "\\" + today + "_{}.png".format(index))


def createZip():
    # add all images to zip named after folder name
    shutil.make_archive(screenFolder, 'zip', screenFolder)


def sendZipToFTP():
    # here the zip is being sent to FTP server
    # no password encoding option is available in this version, so you will have to write it clear in the config
    session = ftplib.FTP(ftpHostName, ftpUser, ftpPassword)
    file = open(screenFolder + ".zip", 'rb')  # file to send
    session.storbinary('STOR {}_{}.zip'.format(today, uniqueId), file)  # send the file
    file.close()  # close file and FTP
    session.quit()


def startScreenSHTR():
    # retrieve system time
    systemTime = datetime.datetime.now()
    systemTimeVar = datetime.datetime(systemTime.year, systemTime.month, systemTime.day, systemTime.hour,
                                      systemTime.minute, systemTime.second)
    # retrieve zip time (hour and minutes) from config file when archive is created
    zipTime = datetime.datetime.now()
    zipTimeVar = datetime.datetime(zipTime.year, zipTime.month, zipTime.day,
                                   int(screenShotTimerHour),
                                   int(screenShotTimerMinutes), zipTime.second)

    # call doScreen function to take a screenshot
    doScreen(index)
    print("Screenshot {} saved\n".format(index))
    time.sleep(int(deltaScreenshot))

    # if system time is the same in config file, take all the screenshots, zip them and send to FTP
    # after, wait 60 seconds to avoid creating/uploading more files than necessary
    if systemTimeVar == zipTimeVar:
        createZip()
        sendZipToFTP()
        time.sleep(60)


while True:
    createFolder()
    for index in range(1, 100000):
        path, dirs, files = next(os.walk(screenFolder))

        # check if number of images is equal to numberOfScreens value defined in config
        # if yes, exit program
        if len(files) == int(numberOfScreens):
            exit()
        elif numberOfScreens == '-1':
            startScreenSHTR()
        else:
            startScreenSHTR()
