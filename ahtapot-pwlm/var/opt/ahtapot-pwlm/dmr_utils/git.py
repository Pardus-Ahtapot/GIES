# -*- coding: utf-8 -*-

import gitlab
import os
from datetime import datetime
import sys
from time import sleep
import subprocess
import logger


log = logger.get_logger()


class GitCommand:

    def __init__(self, repo_path):

        self.repo = repo_path

    def change_branch(self, branch):

        subprocess.call(["cd " + self.repo + " && git checkout " + branch], shell=True)

    def get_file_from(self, branch, file_name):

        subprocess.call(["cd " + self.repo + " && git checkout " + branch + " -- " + file_name], shell=True)

    def pull_repo(self):

        subprocess.call(["cd " + self.repo + " && git pull --rebase"], shell=True)

    def add_file(self, file_name):

        subprocess.call(["cd " + self.repo + " && git add " + file_name], shell=True)

    def add_all_files(self):

        subprocess.call(["cd " + self.repo + " && git add ."], shell=True)

    def commit(self, commit_message):

        subprocess.call(["cd " + self.repo + " && git commit -m \"" + commit_message + "\""], shell=True)

    def push(self, branch):

        subprocess.call(["cd " + self.repo + " && git push origin " + branch], shell=True)

    def push_all(self, commit_message, branch):

        self.add_all_files()
        self.commit(commit_message)
        self.push(branch)

    def merge_branch(self, merge_from, merge_message):

        subprocess.call(["cd " + self.repo + " && git merge " + merge_from + " -m \"" + merge_message + "\""], \
                        shell=True)


class GitLab:

    def __init__(self, gitlab_url, user, password, project_name):

        try:
            self.git = gitlab.Gitlab(gitlab_url)
            self.git.login(user=user, password=password)
            self.projects = git.getprojects()
            for project in self.projects:
                if project["name"] == project_name:
                    self.project = project
                    self.project_id = project["id"]
        except Exception as e:
            log.send_log("error","While creating gitlab object : {} at line : {}".format(str(e),str(sys.exc_info()[2].tb_lineno)))
            raise

    def check_mergerequest(self):

        try:
            mergerequests = self.git.getmergerequests(self.project_id)
            if mergerequests != False:
                for merge in mergerequests:
                    if merge["state"] == "opened" or merge["state"] == "reopened":
                        return False
            return True
        except Exception as e:
            log.send_log("error","While checking mergerequests : {} at line : {}".format(str(e),str(sys.exc_info()[2].tb_lineno)))
            raise

    def create_mergerequest(self, title):

        try:
            return self.git.createmergerequest(self.project_id,"onay", "master", title)
        except Exception as e:
            log.send_log("error","While creating mergerequest : {} at line : {}".format(str(e),str(sys.exc_info()[2].tb_lineno)))
            raise

"""
abs_path = os.path.abspath(__file__)
path_list = abs_path.split("/")
del path_list[-1]
path_name="/".join(path_list)
full_path = path_name + "/"
logger = Syslogger("FWBUILDER-AHTAPOT",'%(name)s %(levelname)s %(message)s',"/dev/log")
filelogger = Filelogger("FWBUILDER-AHTAPOT",'%(asctime)s %(name)s %(levelname)s %(message)s',"/var/log/ahtapot/gdys-gui.log","a")

def gitlab_connect(gitlab_url,user,password):
    git = gitlab.Gitlab(gitlab_url)
    git.login(user=user,password=password)
    return git

def check_mergerequest(git,project_id):
    sleep(1)
    mergerequests = git.getmergerequests(project_id)
    if mergerequests != False:
        for merge in mergerequests:
            if merge["state"] == "opened" or merge["state"] == "reopened":
                return False
    return True

def create_mergerequest(git,project_id,source_branch,target_branch,title):
    return git.createmergerequest(project_id,source_branch,target_branch,title)

def get_mergerequest_status(git,project_id):
    if git.getmergerequests(project_id)!=False:
        if len(git.getmergerequests(project_id)) != 0:
            return git.getmergerequests(project_id)[0]["state"]
    return False

def check_merge_confirm():
    abs_path = os.path.abspath(__file__)
    path_list = abs_path.split("/")
    del path_list[-1]
    path_name = "/".join(path_list)
    full_path = path_name + "/"
    if os.path.exists(full_path + "onay.dmr"):
        return True
    return False

def get_projects(git):
    print git.getprojects()

def set_project_id(git,project_name):
    projects = git.getprojects()
    for project in projects:
        if project["name"] == project_name:
            CP.set_gitlab_config({"project_id":project["id"]})
def check_gitlab_connection(config):
    try:
        git = gitlab.Gitlab(str(config["gitlab_url"]))
        git.login(user=config["gitlab_user"],password=config["gitlab_pass"])
        return True,git
    except Exception as exc_err:
        logger.send_log("error", " Can't connect gitlab \n"+str(exc_err))
        filelogger.send_log("error", " Can't connect gitlab \n"+str(exc_err))
        return u"Gitlab bağlantı bilgileri hatalı.",False

def check_gitlab_settings(git,config):
    error_message = ""
    check_project = False
    project_id = ""
    for project in git.getprojects():
        if project["name"] == config["gitlab_project_name"]:
            check_project = True
            project_id = project["id"]
            break
    if check_project == False:
        return u" Proje Adı Hatalı "

    check_confirm_branch = False
    check_merge_branch = False
    for branch in git.getbranches(project_id):
        if branch["name"] == config["gitlab_confirm_branch"]:
            check_confirm_branch = True
        if branch["name"] == config["gitlab_master_branch"]:
            check_merge_branch = True
    if check_confirm_branch == False:
        return u" Onay Dalı Hatalı "
    if check_merge_branch == False:
        return u" Ana Dal Hatalı "

    return True

def return_date(dt):
    dt_list = dt.split(".")
    del dt_list[-1]
    dt = "".join(dt_list)
    dt = datetime.strptime(dt,"%Y-%m-%dT%H:%M:%S")

    new_date = dt.strftime("%d/%m/%Y %H:%M:%S")
    return new_date

def get_master_date(git,project_id,master_name):
    projects = git.getbranches(project_id)

    dt = ""

    for project in projects:
        if project["name"] == master_name:
            dt = project["commit"]["committed_date"]
    if dt!="":
        return return_date(dt)
    return False

def get_master_commit_id(git,project_id,master_name):
    projects = git.getbranches(project_id)
    if projects != False:
        for project in projects:
            if project["name"] == master_name:
                return str(project["commit"]["id"])
    return False

"""
