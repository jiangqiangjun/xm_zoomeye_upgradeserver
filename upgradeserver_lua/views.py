#!/usr/bin/env python
# -*- coding: utf-8 -*-

# author: limanman
# emails: xmdevops@vip.qq.com


import os
import json
from .geoip import g_ip
from django.conf import settings
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest
from .utils import (analysis_list_body, analysis_download_body, find_version, get_client_ip, area_can, uuid_can, date_can,
                    dj_logging, get_extend_id)


def list(request):
    req_body_res = analysis_list_body(request.body)
    if req_body_res[0] is None:
        dj_logging(req_body_res[1])
        return HttpResponseBadRequest(req_body_res[1])
    req_body = req_body_res[0]
    extend_id = get_extend_id(req_body['DevID'], settings.IDMAPS_DICT)
    if extend_id[0] is None:
        dj_logging(extend_id[1])
        return HttpResponseBadRequest(extend_id[1])
    devid = extend_id[0]
    clientip = get_client_ip(request)
    if clientip is None:
        level = 1 if req_body['Expect'] == 'Important' else 0
        version = find_version(settings.VERSIONS_DICT, devid, req_body['CurVersion'], level, req_body['Language'])
        if version[0] is None:
            dj_logging(version[1])
            return HttpResponse(version[1], status=204)
        return HttpResponse(json.dumps(version[0]))
    date_can_res, date_can_type = date_can(devid, req_body['CurVersion'])
    if not date_can_res:
        msg = '{0} CurVersion not allowed'.format(devid)
        dj_logging(msg)
        return HttpResponse(msg, status=204)
    uuid_can_res, uuid_can_type = uuid_can(req_body['UUID'], devid)
    if not uuid_can_res:
        msg = '{0} not allowed'.format(req_body['UUID'])
        dj_logging(msg)
        return HttpResponse(msg, status=204)
    if uuid_can_type == 0:
        area = g_ip.city(clientip)
        if area is not None:
            area_can_res, area_can_type = area_can(area)
            if not area_can_res:
                msg = '{0} not allowed'.format(clientip)
                dj_logging(msg)
                return HttpResponse(msg, status=204)
        else:
            msg = '{0} not in geoip mmdb'.format(clientip)
            dj_logging(msg)
    level = 1 if req_body['Expect'] == 'Important' else 0
    version = find_version(settings.VERSIONS_DICT, devid, req_body['CurVersion'], level, req_body['Language'])
    if version[0] is None:
        dj_logging(version[1])
        return HttpResponse(version[1], status=204)
    return HttpResponse(json.dumps(version[0]))


def download(request):
    req_body_res = analysis_download_body(request.body)
    if req_body_res[0] is None:
        dj_logging(req_body_res[1])
        return HttpResponseBadRequest(req_body_res[1])
    req_body = req_body_res[0]
    f_path = os.path.join(
        '/download_file/', req_body['DevID'],
        req_body['Date'], req_body['FileName']
    )
    response = HttpResponse()
    response['X-Accel-Redirect'] = f_path
    return response


def firmware_list(request):
    if not settings.VERSIONS_DICT:
        return HttpResponseNotFound('versions not ready')
    return HttpResponse(json.dumps({'versions': settings.VERSIONS_DICT}))


def area_list(request):
    if not settings.AREASCTL_DICT:
        return HttpResponseNotFound('areas not ready')
    return HttpResponse(json.dumps({'areas': settings.AREASCTL_DICT.keys()}))


def uuid_list(request):
    if not settings.UUIDSCTL_DICT:
        return HttpResponseNotFound('uuids not ready')
    return HttpResponse(json.dumps({'areas': settings.UUIDSCTL_DICT.keys()}))


def fdev_list(request):
    if not settings.FIRMWARES_DICT:
        return HttpResponseNotFound('firmwares not ready')
    return HttpResponse(json.dumps({'firmwares': settings.FIRMWARES_DICT.keys()}))
