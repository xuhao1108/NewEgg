from twocaptcha import TwoCaptcha
import requests
import time


def ggv2(api_key, sitekey, url):
    # config = {
    #     'apiKey':api_key,
    #     'recaptchaTimeout':120,
    # }

    # solver = TwoCaptcha(api_key)
    # result = solver.recaptcha(sitekey=sitekey,
    #                         url=url)
    # print(result)
    'http://2captcha.com/in.php?key=0adbeac6198db182b971c01e9dba84a9&invisible=1&method=userrecaptcha&googlekey=6LdsGdgZAAAAABGKg7B50R3CQSEL2hW6qLGxWztm&pageurl=https://unemployment.cmt.ohio.gov/cmtview/ojic1a.jsp'
    'http://2captcha.com/res.php?key=0adbeac6198db182b971c01e9dba84a9&action=get&id=66239951789'
    req = requests.get('http://2captcha.com/in.php?key={api_key}&method=userrecaptcha&googlekey={sitekey}&pageurl={url}&invisible=1'.format(api_key=api_key, sitekey=sitekey, url=url))
    print(req.text)
    req_status = req.text.split('|')
    if req_status[0] == 'OK':
        task_id = req_status[1]
    else:
        return False
    for i in range(0, 120, 5):
        time.sleep(5)
        req2 = requests.get('http://2captcha.com/res.php?key={api_key}&action=get&id={task_id}'.format(api_key=api_key, task_id=task_id))
        print(req2.text)
        req2_status = req2.text.split('|')
        if req2_status[0] == 'OK':
            return req2_status[1]


def hCap(api_key, sitekey, url):
    solver = TwoCaptcha(api_key)
    result = solver.hcaptcha(sitekey=sitekey,
                             url=url)
    return result


def get_recaptcha_press(siteKey, siteReferer, authorization):
    '''recaptcha.press 获取谷歌验证码 siteKey,siteReferer,authorization'''
    req = requests.get('http://api.recaptcha.press/task/create?siteKey={siteKey}&siteReferer={siteReferer}&authorization={authorization}'.format(siteKey=siteKey, siteReferer=siteReferer,
                                                                                                                                                 authorization=authorization))

    print(req.json())
    if req.json()['success'] == True:
        task_id = req.json()['data']['taskId']
    else:
        return False
    for i in range(0, 40):
        time.sleep(5)
        print(i)
        rrr = requests.get('http://api.recaptcha.press/task/status?taskId=%s' % task_id)
        print(rrr.json())
        if rrr.json()['data']['response'] != None:
            return rrr.json()['data']['response']
    return False


def run():
    api_key = '0adbeac6198db182b971c01e9dba84a9'
    authorization = '6029e45deecf93000f23f511:eedc584eba78c6400bc330f0690499a649c65c821a0f957a10bbaba370e33980'
    sitekey = '6LeNsZIUAAAAANOHTT1IaGp-RlIFHP2-YyaponYD'
    url = 'https://www.bybit.com/zh-CN/'
    code = ggv2(api_key, sitekey, url)
    print('--------')
    print(code)


if __name__ == "__main__":
    # print('获取验证码code')
    # # api_key = 'ea64258be414340729d9454e52d80a6a'
    # api_key = '0adbeac6198db182b971c01e9dba84a9'
    # authorization = '6029e45deecf93000f23f511:eedc584eba78c6400bc330f0690499a649c65c821a0f957a10bbaba370e33980'
    # siteKey = '6Le-wvkSAAAAAPBMRTvw0Q4Muexq9bi0DJwx_mJ-'
    # siteReferer = 'https://fbsbx.com/captcha/recaptcha/iframe/?referer=https%3A%2F%2Fwww.facebook.com&compact=0&__cci=FQAREhIA.ARYaJgzJZ-KIPi2YdYn9LyyBfL55Jk0rz2E9xujrIQCJSkxH'
    # code = ggv2(api_key, siteKey, siteReferer)
    # code = hCap('e2bd03e2d5e8e2053c87432d2c1034df','33f96e6a-38cd-421b-bb68-7806e1764460','https://www.getkansasbenefits.gov/BenefitsStartMenu.aspx')
    # code = get_recaptcha_press(siteKey,siteReferer,authorization)
    # print(code)
    run()