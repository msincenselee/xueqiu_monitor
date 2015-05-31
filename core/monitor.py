# coding: utf-8
__author__ = 'chenguo'

import httplib2
from urllib import urlencode


class Monitor(object):
    """
    监控
    """

    url = ""
    need_auth = False

    def __init__(self):
        self.client = self.create_client()

    def create_client(self):
        return httplib2.Http()

    def run(self, task):
        task.monitor = self
        self.task = task
        self.before_task_start()
        task.server_forever()
        self.task_finish()

    def _login(self):
        raise NotImplementedError

    def task_finish(self):
        pass

    def before_task_start(self):
        self.headers = dict()
        if self.need_auth:
            self._login()


class HttpMethodMixin(object):
    """
    http 操作
    """

    def http_get(self, path, callback=None, **param):
        """
        通过get方法访问
        """
        query = urlencode(param)
        if not self.url.endswith('/') and not path.startswith('/'):
            path = '/' + path
        uri = '%s%s?%s' % (self.url, path, query)
        try:
            resp, content = self.client.request(uri, 'GET', headers=self.headers)
            if resp.status == 200:
                return callback(content)
        except Exception, e:
            print u"http get %s error: %s" % (uri, e)
            return None
        else:
            print u"http get %s status: %s" % (uri, resp.status)
            return content


    def http_post(self, path, callback=None, **param):
        """
        通过post方法访问
        """
        query = urlencode(param)
        if not self.url.endswith('/') and not path.startswith('/'):
            path = '/' + path
        uri = '%s%s' % (self.url, path)
        try:
            resp, content = self.client.request(uri, 'POST', body=query, headers=self.headers)
            if resp.status == 200:
                return resp, callback(content)
            elif resp.status == 302:
                return resp, ""
        except Exception, e:
            print u"http get %s error: %s" % (uri, e)
            return None
        else:
            print u"http get %s status: %s" % (uri, resp.status)
            return resp, content



class XueQiuMonitor(HttpMethodMixin, Monitor):

    url = "http://xueqiu.com"
    running = False
    need_auth = True

    def before_task_start(self):
        super(XueQiuMonitor, self).before_task_start()
        self.running = True

    def _login(self):
        headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36",
        }
        self.headers.update(headers)
        resp, _ = self.http_post('user/login', callback=None, **self.task.user_login_param)
        self.handler_login(resp)

    def handler_login(self, resp):
        cookie = resp.get('set-cookie', "")
        self.headers.update({'Cookie': cookie})