import os
import re

import selenium
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd 
import pymysql
import sys 
# init
options = webdriver.ChromeOptions()
options.headless = True 
# opt.add_extension("Block-image_v1.1.crx")
# prefs = {
#     'profile.default_content_setting_values':
#         {'notifications': 2};  # 禁止谷歌浏览器弹出通知消息,
#           "profile.managed_default_content_settings.images": 2;
# }
prefs = {"profile.managed_default_content_settings.images": 2}
options.add_experimental_option("prefs", prefs)
# ref: https://stackoverflow.com/questions/28070315/python-disable-images-in-selenium-google-chromedriver

# browser = webdriver.Edge(seleniumwire_options={'port': 10086})
browser = webdriver.Chrome(ChromeDriverManager().install(),chrome_options=options)
browser.maximize_window()  # 浏览器窗口最大化
browser.implicitly_wait(10)  # 隐形等待10秒

db = pymysql.connect(host='u6354r3es4optspf.cbetxkdyhwsb.us-east-1.rds.amazonaws.com',
                                       database='m9a0vds0zqxjfolq',
                                       user='rj8zog773jqlwyvo',
                                       password='zov05uv6u2qtla2l')
cursor = db.cursor()
def hasPrefix(str_, pre):
    return str_[:len(pre)] == pre


def login(username, passwd):
    # 设置浏览器并且登录
    global browser

    # 访问facebook网页
    try:
        browser.get('https://www.facebook.com/login.php?login_attempt=1&lwv=110/')
    # 如果打开facebook页面失败，则尝试重新加载
    except:
        browser.find_element(By.ID, 'reload-button').click()
        print('重新刷新页面~')

    # 输入账户密码
    browser.find_element(By.ID, 'email').clear()
    # browser.find_element_by_id('email').send_keys('kfengc27@gmail.com')
    browser.find_element(By.ID, 'email').send_keys(username)
    browser.find_element(By.ID, 'pass').clear()
    # browser.find_element_by_id('pass').send_keys('581039fCb!?!')
    browser.find_element(By.ID, 'pass').send_keys(passwd)

    # 模拟点击登录按钮，两种不同的点击方法
    try:
        browser.find_element(By.XPATH, '//button[@id="loginbutton"]').send_keys(Keys.ENTER)
    except:
        browser.find_element(By.XPATH, '//input[@tabindex="4"]').send_keys(Keys.ENTER)
        browser.find_element(By.XPATH, '//a[@href="https://www.facebook.com/?ref=logo"]').send_keys(Keys.ENTER)

    while browser.current_url.find('login') != -1:
        time.sleep(1)


def work(username, fb_id):
    global browser

    # browser.get('https://www.facebook.com/%s/' % username)
    browser.get(username)

    # 拉到最底部
    while True:
        try:
            browser.find_element(By.XPATH, '//div[@data-pagelet="ProfileTimeline"]/div[last() and @class]')
        except:
            break
        browser.execute_script('scrollTo(0, document.body.scrollHeight)')
        time.sleep(2)
        # 帖子全部展开
        browser.execute_script('''
                a = document.evaluate('//div[@dir="auto"]/div[@role="button"]',document.documentElement, null, XPathResult.ANY_TYPE, null);
                node = a.iterateNext();
                while(node){
                    node.click();
                    node = a.iterateNext();
                }
            ''')
        # 展开所有评论
        browser.execute_script('''
                a = document.querySelectorAll("div.oajrlxb2.g5ia77u1.mtkw9kbi.tlpljxtp.qensuy8j.ppp5ayq2.goun2846.ccm00jje.s44p3ltw.mk2mc5f4.rt8b4zig.n8ej3o3l.agehan2d.sk4xxmp2.rq0escxv.nhd2j8a9.mg4g778l.p7hjln8o.kvgmc6g5.cxmmr5t8.oygrvhab.hcukyx3x.tgvbjcpo.hpfvmrgz.jb3vyjys.qt6c0cv9.a8nywdso.l9j0dhe7.i1ao9s8h.esuyzwwr.f1sip0of.du4w35lb.n00je7tq.arfg74bv.qs9ysxi8.k77z8yql.pq6dq46d.btwxx1t3.abiwlrkh.lzcic4wl.bp9cbjyn.m9osqain.buofh1pr.g5gj957u.p8fzw8mz.gpro0wi8");
                // console.log(a);
                for (let node of a) {
                    node.click();
                }    
            ''')

    frames = browser.find_elements(By.XPATH, '//div[@data-pagelet="ProfileTimeline"]/div')
    post_id = 100000 
    for i in range(1, len(frames) + 1):
        post_id = post_id + 1
        browser.execute_script('scrollTo(0, %d)' % frames[i-1].rect['y'])
        text = browser.find_element(By.XPATH, '//div[@data-pagelet="ProfileTimeline"]/div[%d]' % i).text

        imgs = []
        for j in browser.find_elements(By.XPATH, '//div[@data-pagelet="ProfileTimeline"]/div[%d]//img' % i):
            try:
                src = j.get_attribute('src')
            except:
                continue
            if hasPrefix(src, 'http') or hasPrefix(src, 'https'):
                imgs.append(src)

        if text == '':
            continue

        try:
            [post, comment] = re.compile(r'\d+\n\d+\n').split(text)
        except:
            post = text
            comment = ''
        try:
            post = post.split('\n')
        except:
            post = ''
        try:
            state = post.pop(0)
        except:
            state = ''
        try:
            date = post.pop(0)
        except:
            date = ''
        try:
            post.pop(0)
            post = '\n'.join(post)
        except:
            post = ''
        fb_post_id = str(fb_id) + 'PS' + str(post_id)
        print(fb_id)
        print(fb_post_id)
        print(state)
        print(date)
        print(post)
        print(imgs)
        print(comment)
        cursor.execute("select * from fb_data")
        sql = "INSERT INTO fb_data(FBID, POSTID, state, date, content, images, comments) \
        VALUES ('%s', '%s', '%s', '%s', '%s','%s','%s')" % \
        (fb_id, fb_post_id, state, date, post,' , '.join(str(e) for e in imgs),str(comment))
        # ref: https://www.geeksforgeeks.org/python-mysql-insert-into-table/?ref=lbp
        try:
        # Execute the SQL command
            print("Inserting")
            cursor.execute(sql)
            print("Success")
        # Commit your changes in the database
            db.commit()
        except:
            print("Failed")
        # Rollback in case there is any error
            db.rollback()

        print(state, date, post, sep='\n')
        print(imgs)
        print(comment)



def main(argv):
    print(int(argv[0]))
    login('marketing@suyi.com.au', '581039fCb!?!') # password and account name 
    i = 1 
    while i <= int(argv[0]):
        cursor.execute("SELECT FolderId, FBURL, scrapy_status, in_progress, download_time FROM fb_user_1 where scrapy_status != 1")
        data = cursor.fetchall()
        m = 0
        row = data[m]

        while((int(row[3]) != 0)):
            m = m + 1 
            row = data[m]
        
        print("I am working on",row[0])
        updateStatement = "UPDATE fb_user_1 set in_progress = 1 where FolderId='%s'"%(str(row[0]))
        cursor.execute(updateStatement)
        db.commit()
        work(row[1], row[0])
        import datetime
        x = datetime.datetime.now()
        updateStatement = "UPDATE fb_user_1 set scrapy_status = 1 , in_progress = 2, download_time  = '%s' where FolderId='%s'"%(str(x),str(row[0]))
        cursor.execute(updateStatement)
        db.commit()
        i = i + 1 
    os.system('pause')
    browser.close()


if __name__ == '__main__':
    main(sys.argv[1:]) # we can define how many person to scrapy 
