# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required

from allow.models import *

from dmr_utils import config_parser
from dmr_utils import git
from dmr_utils import squid_utils
from dmr_utils.email_sender import Email
from dmr_utils import logger

import sys
from datetime import datetime

log = logger.get_logger()


def home(request):
    return render(request, "home.html")


@login_required
def show_requests(request):
    try:
        requests = RequestUrl.objects.filter(is_operated=False)

        return render(request, 'showrequests.html', {'requests': requests, 'message': ''})
    except Exception as e:
        error_message = "Error while getting config : \n {} \n:: at line {}.".format(str(e), str(
                sys.exc_info()[2].tb_lineno))
        log.send_log("error", error_message)
        return HttpResponse("<script>\
                            alert('Gösterim Sırasında Bir Hata Oluştu.');\
                            window.location.pathname = \"/\";\
                        </script>")


@login_required
def confirm_request(request):
    if request.POST:
        try:
            request_id = request.POST['requestId']
            request_obj = RequestUrl.objects.get(pk=int(request_id))

            # get config values
            config = config_parser.DmrConfigParser()
            squid_repo_path = config.get_path_configs()["squid_repo_path"]
            whitelist_file = config.get_path_configs()["whitelist_file"]
            confirm_branch = config.get_path_configs()["confirm_branch"]
            master_branch = config.get_path_configs()["master_branch"]
            # pull repo and get latest whitelist file
            git_commands = git.GitCommand(squid_repo_path)
            git_commands.change_branch(master_branch)
            git_commands.pull_repo()
            git_commands.change_branch(confirm_branch)
            git_commands.get_file_from(master_branch, whitelist_file)
            # Add url to whitelist and edit file
            whitelist = squid_utils.WhiteList(squid_repo_path + whitelist_file)
            whitelist.add_to(request_obj.url.lower())
            # commit and push new whitelist file
            git_commands.add_file(whitelist_file)
            git_commands.commit(request_obj.url.lower() + " : " + request_obj.user.lower() + "(" + \
                                request_obj.ip.lower() \
                                + ")" " tarafindan istendi.")
            git_commands.push(confirm_branch)
            # making merge
            merge_message = request_obj.url.lower() + " : " + request.user.username + " tarafindan onaylandi."
            git_commands.change_branch(master_branch)
            git_commands.merge_branch(confirm_branch, merge_message)
            git_commands.push(master_branch)

            request_obj.is_operated = True
            request_obj.last_updated = datetime.now()
            request_obj.status = "Onaylandı"
            request_obj.operated_by = request.user.username
            request_obj.save()
            requests = RequestUrl.objects.filter(is_operated=False)
            return render(request, "showrequests.html", {'requests': requests, 'message': request_obj.url + \
                                                                                          ' ONAYLANDI '})
        except Exception as e:
            error_message = "Error while getting config : \n {} \n:: at line {}.".format(str(e), str(
                sys.exc_info()[2].tb_lineno))
            log.send_log("error", error_message)
            return HttpResponse("<script>\
                            alert('Onaylama Sırasında Bir Hata Oluştu.');\
                            window.location.pathname = \"/\";\
                        </script>")

    else:
        return HttpResponse("Lütfen Geçerli İstek Gönderdiğinizden Emin Olunuz.")


@login_required
def reject_request(request, request_id):
    try:
        request_obj = RequestUrl.objects.get(pk=int(request_id))

        request_obj.is_operated = True
        request_obj.last_updated = datetime.now()
        request_obj.status = "Reddedildi"
        request_obj.operated_by = request.user.username
        request_obj.save()

        requests = RequestUrl.objects.filter(is_operated=False)
        return render(request, "showrequests.html", {'requests': requests, 'message': request_obj.url + " reddedildi."})
    except Exception as e:
        error_message = "Error while getting config : \n {} \n:: at line {}.".format(str(e), str(
                sys.exc_info()[2].tb_lineno))
        log.send_log("error", error_message)
        return HttpResponse("<script>\
                            alert('Reddetme Sırasında Bir Hata Oluştu.');\
                            window.location.pathname = \"/\";\
                        </script>")


@login_required
def show_config(request):
    try:
        config = config_parser.DmrConfigParser()
        context = {}
        context["repo_path"] = config.get_path_configs()["squid_repo_path"]
        context["whitelist_file"] = config.get_path_configs()["whitelist_file"]
        context["confirm_branch"] = config.get_path_configs()["confirm_branch"]
        context["master_branch"] = config.get_path_configs()["master_branch"]
        context["receiver_mail"] = config.get_path_configs()["receiver_mail"]
    except Exception as e:
        error_message = "Error while getting config : \n {} \n:: at line {}.".format(str(e), str(
                sys.exc_info()[2].tb_lineno))
        log.send_log("error", error_message)
        return HttpResponse("<script>\
                            alert('Yapılandırma Okunurken Bir Hata Oluştu.');\
                            window.location.pathname = \"/\";\
                        </script>")
    return render(request, "config.html", context)


@login_required
def set_config(request):
    if request.POST:
        try:
            config = config_parser.DmrConfigParser()
            new_config = {"squid_repo_path": request.POST["repoPath"],
                          "whitelist_file": request.POST["whitelistFile"],
                          "confirm_branch": request.POST["confirmBranch"],
                          "master_branch": request.POST["masterBranch"],
                          "receiver_mail": request.POST["receiverMail"]}
            config.set_path_configs(new_config)
        except Exception as e:
            error_message = "Error while setting config : \n {} \n:: at line {}.".format(str(e), str(
                sys.exc_info()[2].tb_lineno))
            log.send_log("error", error_message)
            return HttpResponse("<script>\
                            alert('Yapılandırma Kaydedilirken Bir Hata Oluştu.');\
                            window.location.pathname = \"/request/config/\";\
                        </script>")

    return HttpResponse("<script>\
                            alert('Yapılandırma Kaydedilmiştir.');\
                            window.location.pathname = \"/request/config/\";\
                        </script>")


@csrf_exempt
def create_request(request):
    if request.POST:
        error_message = ""
        try:
            # get values from form
            requested = RequestUrl()
            requested.user = request.POST["userValue"]
            requested.ip = request.POST["userIpValue"]
            requested.url = request.POST["urlValue"].split("Banned site: ")[1]
            config = config_parser.DmrConfigParser()
            squid_repo_path = config.get_path_configs()["squid_repo_path"]
            whitelist_file = config.get_path_configs()["whitelist_file"]

            whitelist = squid_utils.WhiteList(squid_repo_path + whitelist_file)
            if whitelist.check_if_exists(requested.url) is False:
                current_time = datetime.strftime(datetime.now(), "%d-%m-%Y %H:%M:%S")
                requested.message = requested.url + " adresine erisim icin " + requested.user + "(" + requested.ip + \
                                    ")" + " tarafindan " + current_time + " tarihinde izin istendi."
                requested.save()
                # send mail to notify
                config = config_parser.DmrConfigParser()
                receiver = config.get_path_configs()["receiver_mail"]
                with open("email.dmr", "w") as email:
                    email.write(requested.message)

                mail = Email(receiver)
                mail.send("Yeni İstek", "email.dmr")
            else:
                log.send_log("warning", requested.url + " zaten mevcut.")
            return render(request, "requesturl.html", {'url': requested.url, 'error_message': error_message})
        except Exception as e:
            error_message = "Error while receiving your request : \n {} \n:: at line {}.".format(str(e), str(
                sys.exc_info()[2].tb_lineno))
            log.send_log("error", error_message)
            return HttpResponse("<script>\
                            alert('Yapılandırma Kaydedilirken Bir Hata Oluştu.');\
                            window.location = \"" + requested.url + "\";\
                        </script>")
    else:
        return HttpResponse("Lütfen Geçerli İstek Gönderdiğinizden Emin Olunuz.")
