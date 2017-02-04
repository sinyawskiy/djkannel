# Create your views here.
import re
import datetime
import urllib
from django.http import HttpResponse, Http404
from django.views.generic.base import View
import simplejson
import time
from gateway.models import SMSGatewayUser
from recipients.models import GroupRecipient, RecipientThrough
from settings import KANNEL_DELIVER_USER, KANNEL_DELIVER_PASSWORD
from sms_storage.models import add_remote_sms_to_queue, SMSQueue, SMSStatus
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError


class JSONResponse(HttpResponse):
    def __init__(self, data):
        super(JSONResponse, self).__init__(
                simplejson.dumps(data), mimetype='application/json')

def test_phone(phone):
    test = re.compile('^[7][0-9]{10}$')
    return test.match(phone)

class UserGateway(View):
    def get(self, request):
        status = 0
        status_description = u'SMS sent'

        if 'user' in request.GET and 'password' in request.GET:
            try:
                gateway_user = SMSGatewayUser.objects.get(name = request.GET['user'], password=request.GET['password'])
                if 'text' in request.GET and 'phone' in request.GET:
                    phone=request.GET['phone']
                    if test_phone(phone):
                        delivery_url = u''

                        if 'delivery_url' in request.GET:
                            #test url
                            val = URLValidator(verify_exists=True)
                            try:
                                val(request.GET['delivery_url'])
                                delivery_url=request.GET['delivery_url']
                            except ValidationError, e:
                                pass

                        text = request.GET['text']
                        gateway_user_max_message_len=gateway_user.max_message_len if gateway_user.max_message_len else 0
                        if gateway_user_max_message_len!=0 and len(text)>gateway_user_max_message_len:
                            text = text[:gateway_user_max_message_len]
                            status = 5
                            status_description = u'Text is longer than %d sent only %d symbols' % (gateway_user_max_message_len, gateway_user_max_message_len)

                        add_remote_sms_to_queue(phone, text, delivery_url, gateway_user)

                    else:
                        status = 4
                        status_description = u'Format 71234567890 without plus'
                else:
                    status = 3
                    status_description = u'Not exist phone or text'

            except SMSGatewayUser.DoesNotExist:
                status = 2
                status_description = u'Not found user'
        else:
            status = 1
            status_description = u'Authentication required'
        
        data={'gateway_status':status,'description':status_description}
        return JSONResponse(data)

    def post(self, request):
        status = 0
        status_description = u'SMS sent'

        if 'user' in request.POST and 'password' in request.POST:
            try:
                gateway_user = SMSGatewayUser.objects.get(name = request.POST['user'], password=request.POST['password'])
                if 'text' in request.POST and 'phone' in request.POST:
                    phone=request.POST['phone']
                    if test_phone(phone):
                        delivery_url = u''

                        if 'delivery_url' in request.POST:
                            #test url
                            val = URLValidator(verify_exists=True)
                            try:
                                val(request.POST['delivery_url'])
                                delivery_url=request.POST['delivery_url']
                            except ValidationError, e:
                                pass

                        text = request.POST['text']
                        gateway_user_max_message_len=gateway_user.max_message_len if gateway_user.max_message_len else 0
                        if gateway_user_max_message_len!=0 and len(text)>gateway_user_max_message_len:
                            text = text[:gateway_user_max_message_len]
                            status = 5
                            status_description = u'Text is longer than %d sent only %d symbols' % (gateway_user_max_message_len, gateway_user_max_message_len)

                        add_remote_sms_to_queue(phone, text, delivery_url, gateway_user)

                    else:
                        status = 4
                        status_description = u'Format 71234567890 without plus'
                else:
                    status = 3
                    status_description = u'Not exist phone or text'

            except SMSGatewayUser.DoesNotExist:
                status = 2
                status_description = u'Not found user'
        else:
            status = 1
            status_description = u'Authentication required'

        data={'gateway_status':status,'description':status_description}
        return JSONResponse(data)

class UserGatewayToGroup(View):
    def get(self, request):
        status = 0
        status_description = u'SMS sent to group'

        if 'user' in request.GET and 'password' in request.GET:
            try:
                gateway_user = SMSGatewayUser.objects.get(name = request.GET['user'], password=request.GET['password'])
                if 'text' in request.GET and 'group_id' in request.GET and 'group_password' in request.GET:
                    group_id = request.GET['group_id']
                    group_password = request.GET['group_password']
                    try:
                        group = GroupRecipient.objects.get(id=group_id)

                        if group.password and group.password == group_password:

                            delivery_url = u''
                            text = request.GET['text']

                            if group.description:
                                text = u'%s\n***\n%s'%(group.description, text)

                            gateway_user_max_message_len=gateway_user.max_message_len if gateway_user.max_message_len else 0
                            group_max_message_len=group.max_message_len if group.max_message_len else 0
                            max_message_len = gateway_user_max_message_len if gateway_user_max_message_len else (group_max_message_len if group_max_message_len else 0)
                            if max_message_len!=0 and len(text)>max_message_len:
                                text = text[:max_message_len]
                                status = 5
                                status_description = u'Text is longer than %d sent only %d symbols' % (max_message_len, max_message_len)
                            i=0
                            for item in RecipientThrough.objects.filter(group_id = group.id):
                                add_remote_sms_to_queue(item.recipient.phone, text, delivery_url, gateway_user)
                                i+=1

                            status_description = u'SMS sent to group %d recipients'%i
                        else:
                            status = 6
                            status_description = u'Invalid group password'

                    except GroupRecipient.DoesNotExist:
                        status = 4
                        status_description = u'Group with id=%s does not exist'%group_id
                else:
                    status = 3
                    status_description = u'Not exist group_id or text or group_password'

            except SMSGatewayUser.DoesNotExist:
                status = 2
                status_description = u'Not found user'
        else:
            status = 1
            status_description = u'Authentication required'

        data={'gateway_status':status,'description':status_description}
        return JSONResponse(data)

    def post(self, request):
        status = 0
        status_description = u'SMS sent to group'

        if 'user' in request.POST and 'password' in request.POST:
            try:
                gateway_user = SMSGatewayUser.objects.get(name = request.POST['user'], password=request.POST['password'])
                if 'text' in request.POST and 'group_id' in request.POST and 'group_password' in request.POST:
                    group_id = request.POST['group_id']
                    group_password = request.POST['group_password']
                    try:
                        group = GroupRecipient.objects.get(id=group_id)

                        if group.password and group.password == group_password:

                            delivery_url = u''
                            text = request.POST['text']

                            if group.description:
                                text = u'%s\n***\n%s'%(group.description, text)

                            gateway_user_max_message_len=gateway_user.max_message_len if gateway_user.max_message_len else 0
                            group_max_message_len=group.max_message_len if group.max_message_len else 0
                            max_message_len = gateway_user_max_message_len if gateway_user_max_message_len else (group_max_message_len if group_max_message_len else 0)
                            if max_message_len!=0 and len(text)>max_message_len:
                                text = text[:max_message_len]
                                status = 5
                                status_description = u'Text is longer than %d sent only %d symbols' % (max_message_len, max_message_len)
                            i=0
                            for item in RecipientThrough.objects.filter(group_id = group.id):
                                add_remote_sms_to_queue(item.recipient.phone, text, delivery_url, gateway_user)
                                i+=1

                            status_description = u'SMS sent to group %d recipients'%i
                        else:
                            status = 6
                            status_description = u'Invalid group password'

                    except GroupRecipient.DoesNotExist:
                        status = 4
                        status_description = u'Group with id=%s does not exist'%group_id
                else:
                    status = 3
                    status_description = u'Not exist group_id or text or group_password'

            except SMSGatewayUser.DoesNotExist:
                status = 2
                status_description = u'Not found user'
        else:
            status = 1
            status_description = u'Authentication required'

        data={'gateway_status':status,'description':status_description}
        return JSONResponse(data)

def get_kannel_text(sms_from, to, smsc, dlr_type, text, time, charset, coding, smssys_id):
    result = u''
    if len(sms_from):
        result += u'FROM: %s\n' % sms_from
    if len(to):
        result += u'TO: %s\n'%to
    if len(smsc):
        result += u'SMSC: %s\n'%smsc
    if len(dlr_type):
        result += u'DELIVER TYPE: %s\n'%dlr_type
    if len(text):
        result += u'TEXT: %s\n'%text
    if len(time):
        result += u'TIME: %s\n'%time
    if len(charset):
        result += u'CHARSET: %s\n'%charset
    if len(coding):
        result += u'CODING: %s\n'%coding
    if len(smssys_id):
        result += u'SMS SYS ID: %s\n'%smssys_id
    return result

def get_internal_status(remote_status):

# SMPP statuses
#    1 => "Delivery success",
#    2 => "Delivery failure",
#    4 => "Message buffirized",
#    8 => "SMSC submit",
#    16 => "SMSC reject"

    status = SMSStatus.UNKNOWN
    try:
        int_remote_status = int(remote_status)
    except ValueError:
        return status
    if int_remote_status==1:
        status = SMSStatus.DELIVERED
    elif int_remote_status==2:
        status = SMSStatus.UNDELIVERED
    elif int_remote_status==4:
        status = SMSStatus.REMOTE_QUEUED
    elif int_remote_status==8:
        status = SMSStatus.SMSC_SUBMIT
    elif int_remote_status==16:
        status = SMSStatus.SMSC_REJECT
    return status

class KannelGateway(View):
    def log_write(self, write_text):
        file_name = '/web/sms/logs/delivery_status.log'
        log = open(file_name, 'a+')
        log.write(write_text.encode('UTF8'))
        log.close()

    def get(self, request):
        #http://127.0.0.1/smsstatus/?sms_id=%s&user=%s&password=%s&
        #from=%%p&to=%%P&smsc=%%i&dlr-type=%%d&text=%%b&time=%%t&charset=%%C&coding=%%c&smssys_id=%%I
        if 'user' in request.GET and 'password' in request.GET and 'sms_id' in request.GET:
            if request.GET['user']==KANNEL_DELIVER_USER and request.GET['password']==KANNEL_DELIVER_PASSWORD:
                try:
                    sms_queue = SMSQueue.objects.get(remote_id = request.GET['sms_id'])
                    sms_queue.status_time = datetime.datetime.now()
                    sms_queue.status = get_internal_status(request.GET['dlr-type'] if 'dlr-type' in request.GET else u'')
                    sms_queue.status_text = get_kannel_text(
                        request.GET['from'] if 'from' in request.GET else u'',
                        request.GET['to'] if 'to' in request.GET else u'',
                        request.GET['smsc'] if 'smsc' in request.GET else u'',
                        request.GET['dlr-type'] if 'dlr-type' in request.GET else u'',
                        request.GET['text'] if 'text' in request.GET else u'',
                        request.GET['time'] if 'time' in request.GET else u'',
                        request.GET['charset'] if 'charset' in request.GET else u'',
                        request.GET['coding'] if 'coding' in request.GET else u'',
                        request.GET['smssys_id'] if 'smssys_id' in request.GET else u''
                    )
                    sms_queue.save()
                    self.log_write(u'Time %s\nsms_id %s\n sms status %s\n status_text %s\n'%(time.ctime(), sms_queue.remote_id, sms_queue.status, sms_queue.status_text))
                    if sms_queue.delivery_url:
                        try:
                            f = urllib.urlopen(sms_queue.delivery_url+'&status='+sms_queue.status)
                            delivery_request = f.read()
                            self.log_write(delivery_request)
                            f.close()
                        except IOError:
                            self.log_write(u'Cant go to delivery url connection refused\n'% sms_queue.delivery_url)

                except SMSQueue.DoesNotExist:
                    raise Http404
            else:
                return HttpResponse('Unauthorized', status=401)
        else:
            return HttpResponse('Unauthorized', status=401)