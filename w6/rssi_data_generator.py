#!/usr/bin/env python3
import subprocess
import re
import time
import os

def write_data(filename, dBm):
    with open(filename, "a", encoding="utf-8") as f:
        stamp = time.strftime("%H:%M:%S")
        f.write(f"{stamp}: {dBm} dBm\n")

def main():
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    output_dir = dname + "/output"
    try:
        os.mkdir(output_dir)
    except FileExistsError:
        pass
    os.chdir(output_dir)
    filename = time.strftime("%Y%m%d-%H%M%S.txt")

    while True:
        iwconfig = subprocess.run(['iwconfig'], capture_output=True)
        iwconfig = iwconfig.stdout.decode("utf-8")
        qualityMatch = re.search('(?<=Signal level=).+(?= dBm)', iwconfig) # Look for `Signal level=XX dBm` and return the value
        if(qualityMatch):
            quality = qualityMatch.group(0)
            quality = int(quality)
            write_data(filename, quality)
            print("Printed quality")
        else:
            print(f"Unable to print at time {time.strftime('%H%M%S')}")
        time.sleep(1)
        

if __name__ == "__main__":
    main()
