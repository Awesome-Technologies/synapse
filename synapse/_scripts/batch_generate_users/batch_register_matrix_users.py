# -*- coding: utf-8 -*-
# Copyright 2015, 2016 OpenMarket Ltd
# Copyright 2018 New Vector
# Copyright 2019 Awesome Technologies Innovationslabor GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function

import argparse
import getpass
import hashlib
import hmac
import logging
import sys

from six.moves import input

import requests as _requests
import yaml

import secrets
import string
import csv
import qrcode
from fpdf import FPDF
import os
import base64

def sxor(s1,s2):    
    # convert strings to a list of character pair tuples
    # go through each tuple, converting them to ASCII code (ord)
    # perform exclusive or on the ASCII code
    # then convert the result back to ASCII (chr)
    # merge the resulting array of characters as a string
    return ''.join(chr(ord(a) ^ ord(b)) for a,b in zip(s1,s2))

def login(server_location, admin_user, admin_password, _print=print, requests=_requests, exit=sys.exit):
    if not admin_user:
        try:
            default_user = getpass.getuser()
        except Exception:
            default_user = None

        if default_user:
            admin_user = input("Admin user localpart [%s]: " % (default_user,))
            if not admin_user:
                admin_user = default_user
        else:
            admin_user = input("Admin user localpart: ")

    if not admin_user:
        print("Invalid user name")
        sys.exit(1)

    if not admin_password:
        admin_password = getpass.getpass("Password: ")

        if not admin_password:
            print("Password cannot be blank.")
            sys.exit(1)

    url = "%s/_matrix/client/r0/login" % (server_location,)
    data = {
        "type": "m.login.password",
        "user": admin_user,
        "password": admin_password,
    }

    # Get the access token
    r = requests.post(url, json=data, verify=False)

    if r.status_code != 200:
        _print("ERROR! Received %d %s" % (r.status_code, r.reason))
        if 400 <= r.status_code < 500:
            try:
                _print(r.json()["error"])
            except Exception:
                pass
        return False

    access_token = r.json()["access_token"]
    return access_token

def request_registration(
    user,
    password,
    displayname,
    server_location,
    access_token,
    admin=False,
    user_type=None,
    requests=_requests,
    _print=print,
    exit=sys.exit,
):

    url = "%s/_synapse/admin/v1/users?access_token=%s" % (server_location,access_token,)

    data = {
        "username": user,
        "password": password,
        "displayname": displayname,
        "admin": admin,
        "user_type": user_type,
    }

    _print("Sending registration request...")
    r = requests.post(url, json=data, verify=False)

    if r.status_code != 200:
        _print("ERROR! Received %d %s" % (r.status_code, r.reason))
        if 400 <= r.status_code < 500:
            try:
                _print(r.json()["error"])
            except Exception:
                pass
        return False

    return r


def generate_pdf( user_list, server_location, dry_run, _print=print,):

    counter = 0
    pdf = FPDF('P', 'mm', 'A4')

    for user in user_list:
        # generate qr string
        magicString = 'wo9k5tep252qxsa5yde7366kugy6c01w7oeeya9hrmpf0t7ii7'

        if(user[0] == ''):
            urlString = 'token=' + user[2]
        else:
            urlString = 'user=' + user[0] + '&password=' + user[2]

        while(len(urlString) > len(magicString)):
            magicString += magicString

        urlString = sxor(urlString, magicString); # xor with magic string
        urlString = base64.b64encode(urlString.encode()).decode(); # to base64
        qrString = server_location + '/#' + urlString;

        # generate qr code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )

        qr.add_data(qrString)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        img.save("qr" + str(counter) + ".png","PNG")

        # add pdf entry
        if(counter % 4 == 0):
            pdf.add_page()

        start_y = 26.5 + (counter % 4) * 61

        pdf.set_font("Helvetica", size=7)
        pdf.set_text_color(0, 0, 0)
        
        pdf.text(15, start_y + 5, 'Awesome Technologies Innovationslabor GmbH, Rückertstr. 10, 97072 Würzburg')

        pdf.set_font("Helvetica", size=22)
        pdf.text(30, start_y + 25, user[3])
        pdf.text(30, start_y + 35, user[4])

        pdf.set_font("Helvetica", size=12)
        pdf.text(140, start_y + 7, 'Ihr persönlicher Anmeldecode:')

        pdf.image('logo.png', x = 81, y = start_y + 15,
                    h = 30,
                    type = '', link = None)
        pdf.image('qr' + str(counter) + '.png', x = 143, y = start_y + 10,
                    w = 50, h = 50,
                    type = '', link = None)

        if not no_dry_run:
            pdf.set_font("Helvetica", size=24)
            pdf.set_text_color(220, 50, 50)
            pdf.text(75, start_y + 30, 'Credentials not valid !')

        counter += 1

    pdf.output("Userlist_QR.pdf")

    # delete qrs
    for i in range(0, counter):
        os.remove('qr' + str(i) + '.png')

    # second PDF with userlist
    pdf = FPDF('P', 'mm', 'A4')
    pdf.add_page()
    pdf.set_font('Helvetica','',10.0)
    # Effective page width, or just epw
    epw = pdf.w - 2*pdf.l_margin
    # Set column width to 1/4 of effective page width to distribute content 
    # evenly across table and page
    col_width = epw/3

    # Document title centered, 'B'old, 14 pt
    pdf.set_font('Helvetica','B',14.0) 
    pdf.cell(epw, 0.0, 'Users list for ' + server_location, align='C')
    pdf.set_font('Helvetica','B',10.0) 
    pdf.ln(5.5)
     
    # Text height is the same as current font size
    th = pdf.font_size

    pdf.cell(col_width, 2*th, 'Displayname', border=1)
    pdf.cell(col_width, 2*th, 'Username', border=1)
    pdf.cell(col_width, 2*th, 'Password', border=1)
    pdf.set_font('Helvetica','',10.0) 
    pdf.ln(2*th)

    for user in user_list:
        pdf.cell(col_width, 2*th, str(user[3] + ' ' + user[4]), border=1)
        pdf.cell(col_width, 2*th, str(user[0]), border=1)
        pdf.cell(col_width, 2*th, str(user[2]), border=1)
        
        pdf.ln(2*th)

    if not no_dry_run:
        pdf.set_font("Helvetica", size=24)
        pdf.set_text_color(220, 50, 50)
        pdf.text(75, 60, 'Credentials not valid !')
        pdf.text(75, 120, 'Credentials not valid !')
        pdf.text(75, 180, 'Credentials not valid !')
        pdf.text(75, 240, 'Credentials not valid !')
         
    pdf.output('Userlist.pdf','F')

    return    


def request_set_display_name( username, server_location, access_token, display_name, requests=_requests,
    _print=print):
    # TODO
    print("Setting display name for " + username + " to " + display_name)
    url = "%s/_matrix/client/r0/profile/%s/displayname?access_token=%s" % (server_location,username,access_token,)

    data = {
        "displayname": display_name,
    }

    # Get the access token
    r = requests.put(url, json=data, verify=False)

    if r.status_code != 200:
        _print("ERROR! Received %d %s" % (r.status_code, r.reason))
        if 400 <= r.status_code < 500:
            try:
                _print(r.json()["error"])
            except Exception:
                pass
        return False

    return True


def batch_register_new_users(file, server_location, admin_user, admin_password, dry_run, _print=print, exit=sys.exit,):

    # login with admin user to gain access token
    _access_token = login(server_location, admin_user, admin_password)

    if _access_token == False:
        _print("ERROR! Admin user could not be logged in.")
        exit(1)

    _print("Batch processing file %s" % (file,))

    # read file
    with open(file, newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        user_list = []
        
        # loop through users
        for row in reader:
            _print("Registering '" + row['first_name'], row['last_name'] + "'")

            # generate password
            _alphabet = string.ascii_letters + string.digits
            if row['username'] == '':
                _username = ''.join(secrets.choice(_alphabet) for i in range(8)).lower() # for a 8-character username
            else:
                _username = row['username']

            if row['password'] == '':
                _password = ''.join(secrets.choice(_alphabet) for i in range(20)) # for a 20-character password
            else:
                _password = row['password']

            _is_admin = False
            if row['admin'] == 'yes':
                _is_admin = True

            _user_type = None
            _user_id = ''
            if row['user_type'] == 'guest':
                _user_type = 'guest'
                _display_name = "Gast"
            else:
                _display_name = row['first_name'] + " " + row['last_name']
                _servername = server_location.split('/')[2]
                _user_id = '@' + _username + ':' + _servername

            res = {}
            if no_dry_run:
                res = request_registration(_username, _password, _display_name, server_location, _access_token, _is_admin, _user_type)
                if res == False:    
                    _print("ERROR while registering user '" + row['first_name'], row['last_name'] + "'")
                    continue
            # user is guest
            if('user_id' in res and 'access_token' in res):
                user_list.append(['', res.user_id, res.access_token, 'Gast', ''])
            else:
                user_list.append([_username, _user_id, _password, row['first_name'], row['last_name']])
                    


        generate_pdf(user_list, server_location, dry_run)


def main():

    logging.captureWarnings(True)

    parser = argparse.ArgumentParser(
        description="Used to register a batch of new users with a given home server."
    )
    parser.add_argument(
        "-u",
        "--user",
        default=None,
        help="Local part of the admin user. Will prompt if omitted.",
    )
    parser.add_argument(
        "-p",
        "--password",
        default=None,
        help="Password for the admin user. Will prompt if omitted.",
    )
    parser.add_argument(
        "-f",
        "--file",
        default=None,
        help="CSV file that contains users for batch adding",
    )

    parser.add_argument(
    parser.add_argument(
        "--no-dry-run",
        action="store_true",
        help="Checks if given user has admin rights, input file is readable and if pdf can be generated correctly.",
    )

    parser.add_argument(
        "server_url",
        default="https://localhost:8448",
        nargs="?",
        help="URL to use to talk to the home server. Defaults to "
        " 'https://localhost:8448'.",
    )

    args = parser.parse_args()

    if not args.no_dry_run:
        print("Performing dry run")

    if not args.server_url:
        print("No server URL given.")
        sys.exit(1)

    if not args.file:
        print("No file for batch processing given.")
        sys.exit(1)


    batch_register_new_users(args.file, args.server_url, args.user, args.password, args.dry_run)


if __name__ == "__main__":
    main()