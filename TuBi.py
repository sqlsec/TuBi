import time
import json
import random
import smtplib
import requests
from bs4 import BeautifulSoup
from email.mime.text import MIMEText
from email.utils import formataddr

# t00ls 账号配置
username = '国光'  # 帐号
password = '***'  # 密码MD5 32位(小写)
question_num = 7  # 安全提问 参考下面
question_answer = '***'  # 安全提问答案

# 0 = 没有安全提问
# 1 = 母亲的名字
# 2 = 爷爷的名字
# 3 = 父亲出生的城市
# 4 = 您其中一位老师的名字
# 5 = 您个人计算机的型号
# 6 = 您最喜欢的餐馆名称
# 7 = 驾驶执照的最后四位数字

# 选择提醒方式
notice = 2  # 0 = 钉钉  1 = 邮件 2 = 我全都要

# 如果选择钉钉通知的话 请配置下方信息
webhook = 'https://oapi.dingtalk.com/robot/send?access_token=***' # 钉钉机器人的 webhook

# 如果选择邮件通知的话 请配置下方信息
sender = 'admin@sqlsec.com'  # 发件人邮箱账号
sender_pass = '***********'  # 发件人邮箱密码
receiver = 'admin@sqlsec.com'  # 收件人邮箱账号

req_headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36'
}

def t00ls_login(u_name, u_pass, q_num, q_ans):
    """
    t00ls 登录函数
    :param u_name: 用户名
    :param u_pass: 密码的 md5 值 32 位小写
    :param q_num: 安全提问类型
    :param q_ans: 安全提问答案
    :return: 签到要用的 hash 和 登录后的 Cookies
    """

    login_data = {
        'action': 'login',
        'username': u_name,
        'password': u_pass,
        'questionid': q_num,
        'answer': q_ans
    }
    response_login = requests.post('https://www.t00ls.cc/login.json', data=login_data, headers=req_headers)
    response_login_json = json.loads(response_login.text)

    if response_login_json['status'] != 'success':
        return None
    else:
        print('用户:', username, '登入成功!')
        formhash = response_login_json['formhash']
        t00ls_cookies = response_login.cookies
        return formhash, t00ls_cookies


def t00ls_sign(t00ls_hash, t00ls_cookies):
    """
    t00ls 签到函数
    :param t00ls_hash: 签到要用的 hash
    :param t00ls_cookies: 登录后的 Cookies
    :return: 签到后的 JSON 数据
    """
    sign_data = {
        'formhash': t00ls_hash,
        'signsubmit': "true"
    }
    response_sign = requests.post('https://www.t00ls.cc/ajax-sign.json', data=sign_data, cookies=t00ls_cookies,
                                  headers=req_headers)
    return json.loads(response_sign.text)


def t00ls_domain(t00ls_hash, t00ls_cookies):
    """
    t00ls 域名查询函数
    :param t00ls_hash: 签到要用的 hash
    :param t00ls_cookies: 登录后的 Cookies
    :return: 查询相关的日志信息
    """
    content = ''
    # 使用站长之家查询今天注册的域名
    start_time = time.time()

    china_url = 'https://whois.chinaz.com/suffix'
    search_data = 'ix=.com&suffix=.cn&c_suffix=&time=1&startDay=&endDay='
    req_headers['Content-Type'] = 'application/x-www-form-urlencoded'
    response_domains = requests.post(url=china_url, headers=req_headers, data=search_data, timeout=10)

    # Bs4 解析器 简单规则过滤一下放入到 domains 的列表中
    soup = BeautifulSoup(response_domains.text, 'html.parser')
    domains = []
    for i in soup.select('.listOther a'):
        if '.' in i.string and '*' not in i.string:
            domains.append(i.string)
    domain = random.sample(domains, 1)[0]  # 随机抽取一个 幸运儿

    end_time = time.time()
    print(f'站长之家随机找域名耗时: {end_time - start_time:.4f}秒')
    content += f'\n站长之家随机找域名耗时: {end_time - start_time:.4f}秒\n\n'

    start_time = time.time()

    query_url = 'https://www.t00ls.cc/domain.html'
    query_data = f'domain={domain}&formhash={t00ls_hash}&querydomainsubmit=%E6%9F%A5%E8%AF%A2'
    query_status = False
    query_count = 1  # 查询重试次数

    # 如果 t00ls 查询没有成功的话 就一直查询
    while not query_status and query_count < 4:
        domain = random.sample(domains, 1)[0]  # 随机抽取一个 幸运儿
        query_data = f'domain={domain}&formhash={t00ls_hash}&querydomainsubmit=%E6%9F%A5%E8%AF%A2'

        try:
            response_query = requests.post(url=query_url, headers=req_headers, data=query_data, cookies=t00ls_cookies)
        except Exception:
            pass

        if domain in response_query.text:
            response_tb = requests.get('https://www.t00ls.cc/members-tubilog.json', cookies=t00ls_cookies)
            if domain in response_tb.text:
                print('查询域名成功 TuBi + 1 \n')
                content += '查询域名成功 TuBi + 1\n'
                query_status = True
            else:
                print('糟糕 域名查询成功 但是 TuBi 没有增加 可能域名重复了')
                content += '糟糕 域名查询成功 但是 TuBi 没有增加 可能域名重复了\n'
                query_count += 1
                print(f'随机延时 5-10 秒，继续第 {query_count} 次查询')
                content += f'随机延时 5-10 秒，继续第 {query_count} 次查询\n\n'
                time.sleep(random.randint(5, 10))
        else:
            print(f'查询失败？失败的域名是: {domain}')
            content += f'查询失败？失败的域名是: {domain}\n'
            query_count += 1
            print(f'随机延时 5-10 秒，继续第 {query_count} 次查询')
            content += f'随机延时 5-10 秒，继续第 {query_count} 次查询\n\n'
            time.sleep(random.randint(5, 10))
        if query_count == 4:
            print('重试查询次数已达上限 终止查询')
            content += '重试查询次数已达上限 终止查询\n\n'

    end_time = time.time()
    print(f't00ls 域名查询耗时: {end_time - start_time:.4f}秒')
    content += f't00ls 域名查询耗时: {end_time - start_time:.4f}秒\n'
    return content


def dingtalk(content):
    """
    钉钉通知函数
    :param content: 要通知的内容
    :return: none
    """
    webhook_url = webhook
    dd_headers = {
        "Content-Type": "application/json",
        "Charset": "UTF-8"
    }
    dd_message = {
        "msgtype": "text",
        "text": {
            "content": f'T00ls 签到通知\n{content}'
        }
    }

    r = requests.post(url=webhook_url, headers=dd_headers, data=json.dumps(dd_message))


def mail(content):
    """
    邮件通知函数
    :param content: 要通知的内容
    :return: none
    """
    msg = MIMEText(content, 'plain', 'utf-8')
    msg['From'] = formataddr(["T00ls 签到提醒", sender])
    msg['To'] = formataddr(["", receiver])
    msg['Subject'] = "T00ls 每日签到提醒"

    server = smtplib.SMTP_SSL("smtp.qq.com", 465)
    server.login(sender, sender_pass)
    server.sendmail(sender, [receiver, ], msg.as_string())
    server.quit()


def main():
    content = ''
    response_login = t00ls_login(username, password, question_num, question_answer)
    if response_login:
        response_sign = t00ls_sign(response_login[0], response_login[1])
        if response_sign['status'] == 'success':
            print('签到成功 TuBi + 1')
            content += '\n签到成功 TuBi + 1\n'

            verbose_log = t00ls_domain(response_login[0], response_login[1])
            content += verbose_log

            if notice == 0:
                try:
                    dingtalk(content)
                except Exception:
                    print('请检查钉钉配置是否正确')
            elif notice == 1:
                try:
                    mail(content)
                except Exception:
                    print('请检查邮件配置是否正确')
            else:
                try:
                    dingtalk(content)
                except Exception:
                    print('请检查钉钉配置是否正确')
                try:
                    mail(content)
                except Exception:
                    print('请检查邮件配置是否正确')
        elif response_sign['message'] == 'alreadysign':
            print('已经签到过啦')
            content += '\n已经签到过啦\n'

            verbose_log = t00ls_domain(response_login[0], response_login[1])
            content += verbose_log

            if notice == 0:
                try:
                    dingtalk(content)
                except Exception:
                    print('请检查钉钉配置是否正确')
            elif notice == 1:
                try:
                    mail(content)
                except Exception:
                    print('请检查邮件配置是否正确')
            else:
                try:
                    dingtalk(content)
                except Exception:
                    print('请检查钉钉配置是否正确')
                try:
                    mail(content)
                except Exception:
                    print('请检查邮件配置是否正确')
        else:
            print('出现玄学问题了 签到失败')
    else:
        print('登入失败 请检查输入资料是否正确')


if __name__ == '__main__':
    main()
