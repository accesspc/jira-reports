import json
import requests

from datetime import datetime

class Tools():

    def __init__(self):
        pass

    def log(self, msg, newLines=False, separator=False):
        if separator:
            print("\n================================================================================")

        if newLines:
            print()

        print(msg)

        if newLines:
            print()

    def queryGet(self, url, headers={}, params={}):
        try:
            result = requests.get(url, headers=headers, params=params)

            if result.status_code != 200:
                print(f"! HTTP response: {result.status_code}: {result.text}")
                return False
            else:

                return result

        except requests.exceptions.HTTPError as errh:
            print("! Http Error:", errh)
        except requests.exceptions.ConnectionError as errc:
            print("! Error Connecting:", errc)
        except requests.exceptions.Timeout as errt:
            print("! Timeout Error:", errt)
        except requests.exceptions.RequestException as err:
            print("! OOps: Something Else", err)

    def queryPost(self, url, headers={}, data={}):
        try:
            result = requests.post(
                url=url,
                data=json.dumps(data),
                headers=headers
            )

            if result.status_code != 200:
                print(f"! HTTP response: {result.status_code}: {result.text}")
                return False
            else:

                return result

        except requests.exceptions.HTTPError as errh:
            print("! Http Error:", errh)
        except requests.exceptions.ConnectionError as errc:
            print("! Error Connecting:", errc)
        except requests.exceptions.Timeout as errt:
            print("! Timeout Error:", errt)
        except requests.exceptions.RequestException as err:
            print("! OOps: Something Else", err)

    def queryPut(self, url, headers={}, data={}, status_code=200):
        try:
            result = requests.put(
                url=url,
                data=json.dumps(data),
                headers=headers
            )

            if result.status_code != status_code:
                print(f"! HTTP response: {result.status_code}: {result.text}")
                return False
            else:

                return result

        except requests.exceptions.HTTPError as errh:
            print("! Http Error:", errh)
        except requests.exceptions.ConnectionError as errc:
            print("! Error Connecting:", errc)
        except requests.exceptions.Timeout as errt:
            print("! Timeout Error:", errt)
        except requests.exceptions.RequestException as err:
            print("! OOps: Something Else", err)

    def validateDate(self, dt):
        try:
            parsed = datetime.strptime(dt, "%d/%b/%y %I:%M %p")
            return parsed
        except ValueError:
            pass

        try:
            parsed = datetime.strptime(dt, "%b %d, %Y %H:%M")
            return parsed
        except ValueError:
            pass

        return False
