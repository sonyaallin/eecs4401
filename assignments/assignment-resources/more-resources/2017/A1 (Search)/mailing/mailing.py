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
subject = "CSC384 Assignment 1"    #email subject
me = "joe.wu.ca@gmail.com"

template = open("template.txt")
template = template.read()

testnmails = 2

#course specific configs (configure data_map and field_map for your course)

# The rest should work.
scores = open('../A1_results_new.csv', 'rU')
c  = csv.reader(scores, delimiter=',')
print(c)
data = []
for row in c:
    data.append(row)

data = data[1:]

def generate_message(row):
    formatted_result = ''
    if row[0]:
        values = [float(x) for x in row[1:len(row)-1]]

        #init_state = sum(values[10:11+1])
        #successors = sum(values[14:19+1])
        #goal_funct = sum(values[0:3+1])
        #hash_funct = sum(values[4:7+1])
        #heur_funct = sum(values[8:9+1])
        #search     = sum(values[12:13+1])

        #total      = values[20]
        #percentage = 100 * total / 250.0

        template = open("template.txt")
        template = template.read()
        results = "../students/%s/A1/_results.txt" % row[0]
        
        #errors = writer.write_errors(results)
        formatted_result = re.sub('{:2f}',lambda match: str(values.pop(0)),template)

    return formatted_result

def mail(to):
    #s = smtplib.SMTP('mail.cs.toronto.edu')
    print("connected")
    if to == "me" or to == "test":
        nmails = testnmails - 1
    for row in data:
        stud_mes = generate_message(row)
        destination = "%s@teach.cs.toronto.edu" % row[0]

        msg = MIMEText(stud_mes, 'plain')
        #print(destination)
        

        #msg['Subject'] = subject
        #msg['From'] = me
        #msg['cc']   = me

        if to == "test":
            #print("TO: {}".format(destination))
            print("\nHello {}:\n".format(row[0]))
            print(msg.as_string())
            #print(msg)
            print("---------------")
            nmails = nmails - 1
            input("Press Enter to continue...")
        else:
            if to == "me" and nmails >= 0:
                msg['To'] = me
                #s.sendmail(me, [me], msg.as_string())
                nmails = nmails  - 1
            elif to == "students":
                msg['To'] = destination
                #s.sendmail(me, [destination], msg.as_string())
                print(msg.as_string())
            elif nmails < 0:
                continue
            else:
                print("mail({}) illegal argument".format(to))
    #s.quit()

mail("test")
