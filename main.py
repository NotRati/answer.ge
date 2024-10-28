import tempmail
import requests
import string
import random
import re
from urllib.parse import urlparse, parse_qs
import json
import time
class Account:
    def __init__(self, fileName):
        self.headerCount = None
        self.fileName = fileName
        self.email = tempmail.EMail()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }       
    def makeNewAccount(self):
        name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))
        dateOfBirth = "2005-01-11"
        mail = self.email.address
        password = 'wkalshitomara'
        files = {
            'full_name': (None, name),
            'password': (None, password),
            'email': (None, mail),
            'dob': (None, dateOfBirth),
        }
        response = requests.post('https://answers.ambebi.ge/api/user/signup/', headers=self.headers, files=files)

        if not response.ok:
            print("REGISTRATION REQUEST ERROR")
            return

        self.email.wait_for_message()
        self.inbox = self.email.get_inbox()

        for inbox in self.inbox:
            if inbox.from_addr ==  'noreply@answers.ge':
                match = re.search(r'https://answers\.ambebi\.ge/account/activate/\?token=[\w\d]+', inbox.message.html_body)
                if match:
                    self.activationLink = match.group(0)
                    continue
        token = parse_qs(urlparse(self.activationLink).query).get('token', ['none'])[0] #get token from link
        files = {
            'token': (None, token),
        }

        response1 = requests.post('https://answers.ambebi.ge/api/user/data/activate/', headers=self.headers, files=files)
        if not response1.ok:
            print("COULDNT ACTIVATE ACCOUNT")
            return
        
        # print("ACCOUNT ACTIVATED ###")
        self.details = response.text
        files = {
            'username': (None, mail),
            'password': (None, password),
        }
        response = requests.post('https://answers.ambebi.ge/api/user/signin/', headers=self.headers, files=files)

        self.token = response.json()['token']
        self.headers['Authorization'] = 'Token ' + self.token
    def saveHeaders(self):
        try:
            with open(self.fileName, 'r') as f:
                existing_headers = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            existing_headers = []

        existing_headers.append(self.headers)

        with open(self.fileName, 'w') as f:
            json.dump(existing_headers, f, indent=4)
    def getHeaders(self, index=0):
        with open(self.fileName, 'r') as f:
            temp = json.load(f)
            files = {
                'object_id': (None, '1003929'),
                'action': (None, 'bookmark'),
                'model': (None, 'question'),
            }
            response = requests.put(
                'https://answers.ambebi.ge/api/user/voting/123/',
                headers=temp[0],
                files=files,
            )
            if response.status_code == 401:
                with open(self.fileName, 'w') as f:
                    json.dump(temp[1:], f, indent=4)
                print('invalid header')
                return
        
            self.headerCount = len(temp)
            self.headers = temp[index]
    def makeAccounts(self, amount=10):
        for i in range(amount):
            self.makeNewAccount()
            self.saveHeaders()
            print("account made")
    def postComment(self, questionId, text, amount=50, useEveryHeader=False):
        start_time = time.time()
        for i in range(amount):
            if useEveryHeader:
                for j in range(self.headerCount):
                    self.getHeaders(j)
                    files = {
                        'content': (None, f'<p>{text}</p>'),
                        'question': (None, str(questionId)),
                    }

                    response = requests.post('https://answers.ambebi.ge/api/answer/',headers=self.headers, files=files)
            else:
                if i < self.headerCount:
                    self.getHeaders(i)
                else:
                    self.getHeaders(i % self.headerCount)
                files = {
                    'content': (None, f'<p>{text}</p>'),
                    'question': (None, str(questionId)),
                }

                response = requests.post('https://answers.ambebi.ge/api/answer/',headers=self.headers, files=files)
        print(f"{time.time() - start_time:.2f}")
    def notificationExplode(self, amount, userId, text, sender, image='https://ht-cdn2.adtng.com/a7/creatives/221/1559/818227/1118580/1118580_banner.png'):
        for i in range(amount):
            files = {
                'sender': (None, sender),
                'image': (None, None),
                'owner': (None, userId),
                'link': (None, 'https://grabify.link/AYI5TS'),
                'text': (None, text),
            }

            response = requests.post('https://answers.ambebi.ge/api/integration/notification/', headers=self.headers, files=files)
    def spamMainPage(self, text, amount=50):
        response = requests.get('https://answers.ambebi.ge/service/api/question/?count=50&skip=15', headers=self.headers)
        questionIds = []
        if not response.ok:
            return
        repsonseJson = response.json()
        for question in repsonseJson:
            questionIds.append(question['id'])

        for questionId in questionIds:
            print('question done')
            self.postComment(questionId, text, amount)


# class BetterAccount(Account):
#     def __init__(self, fileName):
#         super().__init__(fileName=fileName)

account = Account('header.json')
account.getHeaders()
account.postComment(1003931, 'test', 50, False)