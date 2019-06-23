# -*- coding: UTF-8 -*-
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from flask import Flask
from flask import render_template, redirect, request, flash, get_flashed_messages, send_from_directory
from gevent import pywsgi
import json, os, datetime, random
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

app = Flask(__name__)
app.secret_key='zzuisa'

def login(driver,url, username, password):
    driver.get(url)
    time.sleep(0.5)
    elem_username = driver.find_element_by_id("username")
    elem_username.clear()
    elem_username.send_keys(username)
    elem_userpas = driver.find_element_by_id("password")
    elem_userpas.clear()
    elem_userpas.send_keys(password)
    elem_submit = driver.find_element_by_css_selector("input[type='submit']")
    elem_submit.click()
    time.sleep(0.25)

def redirect_with_msg(target, msg, category):
    if msg != None:
        flash(msg, category=category)
    return redirect(target)
@app.route('/start/', methods={'post', 'get'})
def dowork():
    try:
        username = request.values.get('username').strip()
        password = request.values.get('password').strip()
        chrome_options=webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        driver=webdriver.Chrome(chrome_options=chrome_options,executable_path='/usr/chromedriver')
        url = "https://casgx.v.zzu.edu.cn/cas/login?service=https%3A%2F%2Fjw.v.zzu.edu.cn%2Feams%2Fsso%2Flogin.action%3FtargetUrl%3Dbase64aHR0cHM6Ly9qdy52Lnp6dS5lZHUuY24vZWFtcy9ob21lLmFjdGlvbg%3D%3D"
        login(driver,url, username, password)
        time.sleep(0.4)
        try:
            if str(driver.find_element_by_css_selector('.error-massage span').text) is '':
                driver.close()
                return redirect_with_msg('/evaluate/regloginpage/', u'这个学生不存在，或密码错误', 'reglogin')
        except Exception as e:
            pass
        print ("driver11111")

        # lo = driver.find_element_by_css_selector(
        #     'a[href^=\"/eams/quality/stdEvaluate.action\"]')
        # print ('lolkolo',lo)
        # lo.click()
        driver.execute_script("$('a[href^=\"/eams/quality/stdEvaluate.action\"]').click()")
        # driver.find_element_by_css_selector("").click()
        time.sleep(0.8)
        list = driver.find_elements_by_css_selector('a[href^="/eams/quality/stdEvaluate!answer.action?evaluationLesson.id"]')
        if len(list) == 0:
            driver.close()
            return redirect_with_msg('/evaluate/regloginpage/', u'你已经完成评教了，(〃＞皿＜)可恶', 'reglogin')
        while (len(list) > 0):
            list = driver.find_elements_by_css_selector(
                'a[href^="/eams/quality/stdEvaluate!answer.action?evaluationLesson.id"]')
            list[0].click()
            time.sleep(0.8)
            [item.click() for item in driver.find_elements_by_css_selector('input[value="0"]')]
            driver.find_element_by_css_selector('textarea').send_keys("祝老师身体健康，诸事顺利".decode("utf-8"))
            driver.find_element_by_css_selector("input[type='button']").click()
            dig_alert = driver.switch_to.alert
            dig_alert.accept()
            time.sleep(0.8)
        driver.execute_script("alert(u'评教全部完成，(〃＞皿＜)可恶')")
        time.sleep(1.8)
        driver.close()
        return redirect_with_msg('/evaluate/regloginpage/', u'完成咯~', 'reglogin')
    except Exception as e:
        try:
            if not driver is None:
                driver.close()
        except Exception as es:
            print str(es)
            return redirect_with_msg('/evaluate/regloginpage/', u'请不要中断程序，好吗？', 'reglogin')
        driver.close()
        return redirect_with_msg('/evaluate/regloginpage/', u'请输入正确的密码！！', 'reglogin')
@app.route('/regloginpage/')
def regloginpage():
    msg = ''
    for m in get_flashed_messages(with_categories=False, category_filter=['reglogin']):
        msg = m
    return render_template('index.html', msg=msg.decode("utf-8"), next=request.values.get('next'))
@app.route('/')
def index():
    return render_template('index.html')
if __name__ == '__main__':
    server = pywsgi.WSGIServer(('127.0.0.1', 5000), app)
    server.serve_forever()