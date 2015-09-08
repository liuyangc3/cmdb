#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import time
import re
import shutil
import subprocess
from datetime import datetime
import zerorpc


class DeployBase(object):
    date_format = '%Y-%m-%d-%H-%M-%S'

    @staticmethod
    def dir_size(dir_name):
        """ 计算一个目录的大小 """
        size = 0
        for sub in os.listdir(dir_name):
            sub_path = os.path.join(dir_name, sub)
            if os.path.isfile(sub_path):
                size += os.path.getsize(sub_path)
            elif os.path.isdir(sub_path):
                size += DeployBase.dir_size(sub_path)
        return size

    def date_to_timestamp(self, dir_name):
        dt = datetime.strptime(dir_name, self.date_format)
        return time.mktime(dt.timetuple())

    def timestamp_to_date(self, timestamp):
        time_tuple = time.localtime(timestamp)
        return time.strftime(self.date_format, time_tuple)

    @staticmethod
    def _is_valid(dir_name):
        if len(dir_name) == 19 and '-' in dir_name:
            pattern = re.compile(r'\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}')
            match = pattern.match(dir_name)
            if match:
                dir_tuple = dir_name.split('-')
                year = int(dir_tuple[0])
                month = int(dir_tuple[1])
                day = int(dir_tuple[2])
                hour = int(dir_tuple[3])
                minute = int(dir_tuple[4])
                second = int(dir_tuple[5])
                if 1970 <= year and 0 < month <= 12 and 0 < day <= 31 \
                        and 0 <= hour < 24 and 0 <= minute < 60 and 0 <= second < 60:
                    return True
        return False


class DeployDate(DeployBase):
    """
    1 目录过滤
        找出容器目录内合法的部署目录，并根据时间排序
    2 部署
        执行shell脚本
    3 回滚
        回滚到指定的目录
        回滚到当前工作目录之前的，上次部署的目录
    """

    link_name = 'current'

    def __init__(self, deploy_root):
        self._root = deploy_root  # deploy workspace

    @property
    def current_date(self):
        return os.readlink(os.path.join(self._root, self._soft_link))

    @property
    def current_date_index(self):
        """ 找出current 指向的实际目录,在sorted_dir_list中的位置 """
        return self.sorted_date_list().index(self.current_date)

    @property
    def _date_list(self):
        date_list = []
        sub_files = os.listdir(self._root)
        if not sub_files:
            raise RuntimeError('容器目录为空')
        for sub_file in sub_files:
            if os.path.isdir(os.path.join(self._root, sub_file)) and self._is_valid(sub_file):
                date_list.append(sub_file)
        if not date_list:
            raise RuntimeError('容器目录内没有合法的部署目录')
        return date_list

    @property
    def timestamp_list(self):
        ts_list = [self.date_to_timestamp(date) for date in self._date_list]
        ts_list.sort()
        return ts_list

    def sorted_date_list(self):
        return [self.timestamp_to_date(ts) for ts in self.timestamp_list]

    def do_deploy(self):
        """ 执行部署脚本
        如果软链接指向新生成的目录,返回True
        """
        subprocess.call('deploy.sh')
        current_dir_ts = self.date_to_timestamp(self.current_date)
        new_dir_ts = self.date_to_timestamp(self.current_date)
        if current_dir_ts > new_dir_ts:
            return True
        else:
            return False

    def _soft_link(self, dir_name):
        """ 删除部署目录下的 soft_link
        新建 soft_link 指向 dir """
        os.chdir(self._root)
        if os.path.exists(self.link_name):
            os.unlink(self.link_name)
        os.symlink(dir_name, self.link_name)

    def get_rollback_dir(self):
        """ 根据当前工作目录,找出上次部署目录 """
        current = self.date_to_timestamp(self.current_date)  # 当前工作部署的时间戳
        max_timestamp = 0  # 回滚目录的时间戳
        for timestamp in self.timestamp_list:
            if max_timestamp < timestamp < current:
                max_timestamp = timestamp
        if not max_timestamp:
            raise RuntimeError('只有一次部署目录，不能找到回滚目录')
        rollback_dir = self.timestamp_to_date(max_timestamp)
        return rollback_dir

    def target_rollback(self, target_dir):
        """ 回滚到指定的目录 """
        self._soft_link(target_dir)
        # 删除target日期之前的所有目录
        for ts in self.timestamp_list:
            if ts > self.date_to_timestamp(target_dir):
                shutil.rmtree(os.path.join(self._root,
                                           self.timestamp_to_date(ts)))

    def rollback(self):
        """ 回滚到上次部署的目录 """
        if len(self._date_list) == 1:
            raise RuntimeError('只有一次部署目录，无法回滚')
        self._soft_link(self.get_rollback_dir())  # 修改软链接必须在删除目录之前操作
        shutil.rmtree(os.path.join(self._root, self.current_date))  # 删除当前工作目录


s = zerorpc.Server(DeployDate('/data0/www'))
s.bind("tcp://0.0.0.0:4242")
s.run()
