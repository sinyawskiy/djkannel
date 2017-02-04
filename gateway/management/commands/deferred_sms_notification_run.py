# -*- coding: utf-8 -*-
import commands
import datetime
import random
import re
import urllib
from django.core.mail.message import EmailMultiAlternatives
from django.core.management.base import BaseCommand, CommandError
import time
import warnings
import sys
from django.utils.html import escape
from settings import KANNEL_DELIVER_PASSWORD, KANNEL_DELIVER_USER, SENDER, KANNEL_PASSWORD, KANNEL_USER, KANNEL_SENDSMS_PORT, KANNEL_BEARERBOX_HOST
from sms_storage.models import SMSQueue, SMSStatus
from django.utils.encoding import iri_to_uri

def is_cyrilic_exist(text):
    s=re.search(u'([а-я]\w+\s*)+',text,re.U | re.I | re.M)
    return True if s is not None else False

# Если кодировка сообщения UTF8 и есть русские символы тогда перекодируем в UCS2
# т.е. имеем русский текст
# для этого создадим временный файл
# tempFile потом мы его передадим на съедение
# утилите piconv
#def convert_sms( sms_text ):
#    tempFile = '/tmp/sms_%s.tmsg' % ( str( random.random() * 1000 ) )
#
#    try:
#        newFile = open( tempFile, 'w' )
#        newFile.write( sms_text.encode('utf8') )
#        newFile.close()
#    except IOError:
#        print 'Can not write temporary file: %s' % tempFile
#
#    sms_text = commands.getoutput( 'piconv -f utf8 -t UCS-2BE %s' % tempFile )
#    return sms_text

class Command(BaseCommand):
    help = u'Send notification sms/n'

    def send_sms(self, text, phone, sms_id):
        if is_cyrilic_exist(text):
            coding = u'&coding=2'
            #Перекодируем текст с помощью временого файла
            text = iri_to_uri(text)#urllib.quote_plus(text)# ()
        else:
            coding = u'&coding=0'
        #print text
        delivery_iri = u'http://127.0.0.1/gateway/smsstatus/?sms_id=%s&user=%s&password=%s&from=%%p&to=%%P&smsc=%%i&dlr-type=%%d&text=%%b&time=%%t&charset=%%C&coding=%%c&smssys_id=%%I'%(sms_id,KANNEL_DELIVER_USER,KANNEL_DELIVER_PASSWORD)
        delivery_uri = iri_to_uri(delivery_iri)
        #self.stdout.write(u'delivery_iri %s\n' % delivery_uri)
        delivery_url = urllib.quote_plus(delivery_uri)
        #self.stdout.write(u'delivery_url %s\n\n' % delivery_url)

        url=u'http://%s:%d/cgi-bin/sendsms?username=%s&password=%s&from=%s&to=%s&text=%s%s&charset=UTF-8&dlr-mask=31&dlr-url=%s' \
        % (KANNEL_BEARERBOX_HOST, KANNEL_SENDSMS_PORT, KANNEL_USER, KANNEL_PASSWORD, SENDER,  phone, text, coding, delivery_url) #mask = 1+2+4+8+16 = 31
        self.stdout.write(u'%s\n' % url)
        try:
            f = urllib.urlopen(url)
            print f.read()
            f.close()
        except IOError:
            self.stdout.write(u'Cant send connection refused\n')
            return False
        self.stdout.write(u'Sent\n')
        return True


    def handle(self, *args, **options):

        warnings.filterwarnings('ignore')

        start = time.time()
        limit_seconds = 20
        run_time=0
        sms_queues = SMSQueue.objects.filter(status=SMSStatus.QUEUED).order_by('queued_time')
        if sms_queues.count():
            self.stdout.write(u'Start date %s; SMS for send %d\n' % (time.ctime(),sms_queues.count()))
            num = 0
            for sms_item in sms_queues:
                #Сформировать письмо
                self.stdout.write(u'    Create message %d\n'% sms_item.id)

                if self.send_sms(sms_item.text, sms_item.phone, sms_item.remote_id):

                    #Изменить запись в базе писем
                    try:
                        sms_queue = SMSQueue.objects.get(id = sms_item.id)
                        sms_queue.sent_time = datetime.datetime.now()
                        sms_queue.status = SMSStatus.SENT
                        sms_queue.save()

                    except SMSQueue.DoesNotExist:
                        self.stdout.write(u'    Entry in database %d NOT update to SENT.\n' % sms_item.id)

                #Проверяем время если больше лимита то выходим
                num+=1
                finish = time.time()
                run_time = finish - start
                if run_time > limit_seconds:
                    self.stdout.write(u'Exit by time. SMS sent: %d\n' % num)
                    exit()

            self.stdout.write(u'Successfull. SMS sent: %d. Time %s \n' % (num, run_time, ))
        else:
            self.stdout.write(u'Start date %s;Not sms. Successful!\n' % time.ctime())