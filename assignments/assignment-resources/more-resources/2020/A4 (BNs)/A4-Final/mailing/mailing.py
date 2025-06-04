"""Bulk Mailing of marks/mark files"""

import csv
import fileinput
import os
import re
import sys
import smtplib
import mimetypes
from optparse import OptionParser
from email import encoders
from email.message import Message
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText

import writer

# Configure msg.txt, and the stuff below for
# a particular emailing.
#
# In msg.txt you can use the special strings like +Lname+, +A1+ etc (defined
# as in the field_map dictionary. These strings will be substituted
# for the fields of the each student record read from Marks.csv.

# We depend on "ClassList.csv" to be the marks file
# containing the partiular field names used in data_map defined
# below. Change these and the field_map to configure for your own course.
#
# mail("test") prints out "testnmails" test messages (you can reset the
#              number of test mails by resetting this variable)
# mail("me")   mails out "testnmails" to "me" (defined below)
# mail("students") mails to each student in Marks.csv

#Mailing specific configs.

subject = "CSC384 Assignment 4"    #email subject
me = "csc384ta@cs.toronto.edu" #not sure if this works this semester

template = open("template.txt")
template = template.read()

testnmails = 500

#course specific configs (configure data_map and field_map for your course)

# The rest should work.

scores = open('A4summary.csv', 'r')
c  = csv.reader(scores, delimiter=',')
data = []
for row in c:
    data.append(row)

def generate_message(row):

    results = "students/%s/A4/_results.txt" % row[0]
    if (os.path.exists(results)):
        results = open(results)
        results = results.read()
    else:
        results = ''

    formatted = template;

    for i in range(0,len(row)):
        formatted = formatted.replace("{}", str(row[i]),1)
    
    #print(results)

    #results = results.replace("Overall:", "Test Results (other than for heuristic):")
    formatted = formatted.replace("{results}", results, 1)

    return formatted


def mail(to):

    #s = smtplib.SMTP('mail.cs.toronto.edu')
    #print "connected"
    if to == "me" or to == "test":
        nmails = testnmails - 1

    for row in data:
        stud_mes = generate_message(row)
        destination = "%s@teach.cs.toronto.edu" % row[0]

        msg = MIMEText(stud_mes, 'plain')

        msg['Subject'] = subject
        msg['From'] = me
        #msg['cc']   = me

        if to == "test" and nmails >= 0:       
            print ("TO:", destination)
            print (msg.as_string())            
            #print ("---------------")
            #print(stud_mes)
            nmails = nmails - 1
            if (destination == "malikins@teach.cs.toronto.edu"):  
                input("Press Enter to continue...")
        else:
            if to == "me" and nmails >= 0:
                msg['To'] = me
                #s.sendmail(me, [me], msg.as_string())
                nmails = nmails  - 1
            elif to == "students":
                msg['To'] = destination
                #s.sendmail(me, [destination], msg.as_string())
                print (msg.as_string())
            elif nmails < 0:
                continue
            else:
                print ("mail({}) illegal argument".format(to))
    #s.quit()

mail("test")
