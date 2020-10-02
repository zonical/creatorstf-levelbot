import json
import os
from datetime import datetime

slash = "/"

currentdir = os.path.dirname(os.path.abspath(__file__)) + f"/users/"
filecount = 0

none = 0
mercs = 0
vets = 0

startT = datetime.now()
for filename in os.listdir(currentdir):
    if filename.endswith(".json"):
        with open(currentdir + filename, 'r') as file:
            filecount += 1
            jsonObject = json.load(file)

            printFilename = filename.split(".json")
            messagecount = int(jsonObject["messagecount"])

            if messagecount < 30:
                none += 1
            elif messagecount >= 30 and messagecount < 150:
                mercs += 1
            else:
                vets += 1
            print(f"{printFilename[0]}: {messagecount}")

            file.close()

endT = datetime.now()
finaLT = endT - startT

print(f"Time taken to process {filecount} files: {str(finaLT)}")
print(f"None: {none}, Mercs: {mercs}, Veterans: {vets}")
