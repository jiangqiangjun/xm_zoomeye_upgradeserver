#!/usr/bin/env python
# -*- coding: utf-8 -*-

# author: limanman
# emails: xmdevops@vip.qq.com


from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from django.db.models.signals import post_save, post_delete
from .models import Firmware, AreaControl, UuidControl, DateControl, UpgradeLog


def update_area_cache(*args, **kwargs):
    settings.AREASCTL_DICT.clear()
    settings.DEVIDCTL_DICT.clear()
    for item in AreaControl.objects.values():
        settings.DEVIDCTL_DICT.update({
            item['devid']: {}
        })
        settings.AREASCTL_DICT.update({
            item['area']: {
                'start_time': item['start_time'],
                'end_time': item['end_time'],
                'notes': item['notes']
            }
        })


def update_uuid_cache(*args, **kwargs):
    settings.UUIDSCTL_DICT.clear()
    for item in UuidControl.objects.values():
        settings.UUIDSCTL_DICT.setdefault(item['devid'], {})
        settings.UUIDSCTL_DICT[item['devid']].setdefault(item['uuid'], {})
        settings.UUIDSCTL_DICT[item['devid']][item['uuid']].update({
            'start_time': item['start_time'],
            'end_time': item['end_time'],
            'notes': item['notes']
        })


def update_date_cache(*args, **kwargs):
    settings.DATESCTL_DICT.clear()
    for item in DateControl.objects.values():
        rds_key = 'upg::datecontrol::{0}'.format(item['devid'])
        settings.REDIS_CONN.hmset(rds_key, {
            'start_time': item['start_time'],
            'end_time': item['end_time'],
            'start_date': item['start_date'],
            'end_date': item['end_date'],
            'upg_once': item['upg_once'],
            'notes': item['notes']
        })


def update_firmware_cache(*args, **kwargs):
    settings.FIRMWARES_DICT.clear()
    for item in Firmware.objects.values():
        settings.FIRMWARES_DICT.update({
            item['name']: {
                'date': item['date'],
                'is_generated': item['is_generated'],
                'is_important': item['is_important'],
                'notes': item['notes']
            }
        })


def recycle_upgradelog(*args, **kwargs):
    yesterday = timezone.now() - timedelta(days=7)
    UpgradeLog.objects.filter(upgrade_time__lt=yesterday).delete()


post_save.connect(update_area_cache, sender=AreaControl)
post_save.connect(update_uuid_cache, sender=UuidControl)
post_save.connect(update_date_cache, sender=DateControl)
post_save.connect(update_firmware_cache, sender=Firmware)
post_save.connect(recycle_upgradelog, sender=UpgradeLog)

post_delete.connect(update_area_cache, sender=AreaControl)
post_delete.connect(update_uuid_cache, sender=UuidControl)
post_delete.connect(update_date_cache, sender=DateControl)
post_delete.connect(update_firmware_cache, sender=Firmware)
