__author__ = "Alon Shrestha"

import boto3
from datetime import date

# Today's date
todayDate = date.today()

# IAM client session
iamSessionClient = boto3.client('iam')

# Sender and admin email IDs
senderEmailId = 'Admin <sender@example.com>'
adminEmailId = 'admin@example.com'

# Table to store IAM users without EmailID tag
tableNoEmailID = [
    # HTML table structure for email formatting
    '<html>'
    '<head><style>table {font-family: "Trebuchet MS", Arial, Helvetica, sans-serif;border-collapse: '
    'collapse; }'
    'td,th{'
    'border:1px solid #ddd;'
    'padding:8px;'
    'width:1%;'
    '}'
    '</style>''</head>',
    '<table>'
    '<tr>'
    '<td style="border:5px solid white;" colspan="8"> </td>'
    '</tr>'
    '<tr>'
    '<th style="background-color:#FFBB33" colspan="8">'"IAM Users Without EmailID Tag"'</th>'
    '</tr>'
    '<tr>'
    '<td> <strong> UserName </strong> </td>'
    '</tr>'
]   
# ... (Similar tables for Two Active Keys and Service User Age notifications)
tableUserWithTwoActiveKey = [
    # ... HTML code for IAM Users With Two Active Keys table ...
    '<html>'
    '<head><style>table {font-family: "Trebuchet MS", Arial, Helvetica, sans-serif;border-collapse: '
    'collapse; }'
    'td,th{'
    'border:1px solid #ddd;'
    'padding:8px;'
    'width:1%;'
    '}'
    '</style>''</head>',
    '<table>'
    '<tr>'
    '<td style="border:5px solid white;" colspan="8"> </td>'
    '</tr>'
    '<tr>'
    '<th style="background-color:#FFBB33" colspan="8">'"IAM Users With Two Active Keys"'</th>'
    '</tr>'
    '<tr>'
    '<td> <strong> UserName </strong> </td>'
    '</tr>'
]

tableServiceUserAgeOneYear = [
    # ... HTML code for IAM Service Users Key Age Crossed One Year table ...
    '<html>'
    '<head><style>table {font-family: "Trebuchet MS", Arial, Helvetica, sans-serif;border-collapse: '
    'collapse; }'
    'td,th{'
    'border:1px solid #ddd;'
    'padding:8px;'
    'width:1%;'
    '}'
    '</style>''</head>',
    '<table>'
    '<tr>'
    '<td style="border:5px solid white;" colspan="8"> </td>'
    '</tr>'
    '<tr>'
    '<th style="background-color:#FFBB33" colspan="8">'"IAM Service User Key Age Crossed One Year"'</th>'
    '</tr>'
    '<tr>'
    '<td> <strong> UserName </strong> </td>'
    '<td> <strong> Key Age(Days) </strong> </td>'
    '</tr>'
]


# Sending an email using Amazon SES
def sendEmail(subject, message, toEmail, bccEmail=None):
    try:
        # Constructing the destination based on whether there's BCC email or not
        if not bccEmail:
            destination = {
                'ToAddresses': toEmail,
            }
            print(f"Email '{subject}' Initiated To: {toEmail}")
        else:
            destination = {
                'ToAddresses': toEmail,
                'BccAddresses': bccEmail
            }
            print(f"Email '{subject}' Initiated To: {toEmail}, Bcc: {bccEmail}")

        ses = boto3.client('ses', region_name='us-east-1')
        response = ses.send_email(
            Source=senderEmailId,
            Destination=destination,
            Message={
                'Subject': {
                    'Data': subject
                },
                'Body': {
                    'Html': {
                        'Data': message.replace('\n', '<br>'),
                        'Charset': 'UTF-8',

                    }

                }

            }
        )
        print("Email Success!!")
    except Exception as e:
        print(f"Email Failed!! Error: {e}")


def getIAMUserEmailTag(iamClientSession, iamUserName):
    iamUserTag = iamClientSession.list_user_tags(UserName=iamUserName)
    for details in iamUserTag['Tags']:
        if details['Key'] == 'EmailID':
            emailId = str(details['Value'])
            return emailId


def generateAccessKey(userName, session, emailId):
    accessKeyId = ""
    secretKeyId = ""
    generateKey = session.create_access_key(
        UserName=userName
    )
    for key, value in generateKey["AccessKey"].items():
        if key == "AccessKeyId":
            accessKeyId = value
        if key == "SecretAccessKey":
            secretKeyId = value
    print(f"AM User: '{userName}', New AccessKey: '{accessKeyId}' Generated!")

    # Send Access Key
    subjectAccessKey = f"AWS IAM Key Rotation: AWS AccessKey: {str(todayDate)}"
    messageAccessKey = f"Hi {userName}," \
                       f"\n\nYour New AWS AccessKey is <strong>'{accessKeyId}'</strong>. " \
                       f"This key will be rotated after 60 days as part of our security policy." \
                       f"\n\n<h4> <i>Automated &#128640; </i></h4>"
    sendEmail(subjectAccessKey, messageAccessKey, [emailId], [adminEmailId])

    # Send Secret Key
    subjectSecretKey = f"AWS IAM Key Rotation: AWS SecretKey: {str(todayDate)}"
    messageSecretKey = f"Hi {userName}," \
                       f"\n\nYour New AWS SecretKey is <strong>'{secretKeyId}'</strong>. " \
                       f"This key will be rotated after 60 days as part of our security policy." \
                       f"\n\n<h4> <i>Automated &#128640; </i></h4>"
    sendEmail(subjectSecretKey, messageSecretKey, [emailId], [adminEmailId])


def deleteAccessKey(userName, accessKeyId, session):
    deleteKey = session.delete_access_key(
        UserName=userName,
        AccessKeyId=accessKeyId
    )
    print(f"IAM User: '{userName}', AccessKey: '{accessKeyId}' Deleted!")


def deactivateAccessKey(userName, accessKeyId, session):
    deactivateKey = session.update_access_key(
        UserName=userName,
        AccessKeyId=accessKeyId,
        Status='Inactive'
    )
    print(f"IAM User: '{userName}', AccessKey: '{accessKeyId}' Deactivated!")


def twoActiveKeys(accessKeys, userName):
    keyCountList = []
    keyStatusList = []
    for accessKey in accessKeys['AccessKeyMetadata']:
        keyCountList.append(accessKey['AccessKeyId'])
        keyStatusList.append(accessKey['Status'])

    # User has 2 keys and both are active
    if len(keyCountList) > 1 and keyStatusList[0] == "Active" and keyStatusList[1] == "Active":
        print(f"IAM User: '{userName}', has 2 Active Keys. Sending Notification!")
        # Add in UserWithTwoActiveKey Table
        tableUserWithTwoActiveKey.append(
            '<tr>'
            '<td>' + userName + '</td>'
                                '</tr>')
        return True
    else:
        return False


def twoInActiveKeys(userName, accessKeys, session):
    for accessKey in accessKeys:
        if accessKey['Status'] == "Inactive":
            deleteAccessKey(userName, accessKey['AccessKeyId'], session)


def oneAccessKey(userName, accessKeyId, session, emailId):
    deactivateAccessKey(userName, accessKeyId, session)
    generateAccessKey(userName, session, emailId)


def twoAccessKeys(userName, accessKeys, session, emailId):
    for accessKey in accessKeys:
        if accessKey['Status'] == "Inactive":
            deleteAccessKey(userName, accessKey['AccessKeyId'], session)
            generateAccessKey(userName, session, emailId)
        elif accessKey['Status'] == "Active":
            deactivateAccessKey(userName, accessKey['AccessKeyId'], session)


def keyAgeGreater60Days(userName, accessKeys, session, emailId):
    accessKeysCountList = []
    accessKeyStatusList = []

    for accessKey in accessKeys:
        accessKeysCountList.append(accessKey['AccessKeyId'])
        accessKeyStatusList.append(accessKey['Status'])

    # User has 2 keys and both are inactive
    if len(accessKeysCountList) > 1 and accessKeyStatusList[0] == "Inactive" and accessKeyStatusList[1] == "Inactive":
        print(f"IAM User: '{userName}', has 2 InActive Keys. Deleting Both Keys!")
        twoInActiveKeys(userName, accessKeys, session)

    # User has 2 keys and 1 active, 1 inactive
    elif len(accessKeysCountList) > 1 and (accessKeyStatusList[0] == "Active" or "Inactive") and \
            (accessKeyStatusList[1] == "Inactive" or "Active"):
        print(f"IAM User: '{userName}', has 2 Keys. 1 Active, 1 Inactive.")
        twoAccessKeys(userName, accessKeys, session, emailId)

    # User has 1 active key
    elif len(accessKeysCountList) == 1 and accessKeyStatusList[0] == "Active":
        print(f"User: '{userName}', has 1 Active Key.")
        oneAccessKey(userName, accessKeysCountList[0], session, emailId)


def keyAge59Days(userName, accessKeyId, emailId):
    print(f"Sending Pre-Rotation Notification to {emailId} ")
    subject = f"AWS IAM Key Rotation: Pre-Notification: {str(todayDate)}"
    message = f"Hi {userName}," \
              f"\n\nYour AWS AccessKey: <strong>{accessKeyId}</strong> will be rotated tomorrow." \
              f" AccessKey and SecretKey will be shared in separate email." \
              f"\n\n<h4> <i>Automated &#128640; </i></h4>"
    sendEmail(subject, message, [emailId], [adminEmailId])


def initIAMRotation(userName, session, emailId):
    accessKeys = session.list_access_keys(UserName=userName)

    if not twoActiveKeys(accessKeys, userName):
        for accessKey in accessKeys['AccessKeyMetadata']:
            # Initiate Rotate at Day 60
            if accessKey['Status'] == "Active" and ((date.today() - accessKey['CreateDate'].date()).days >= 60):  # >=60
                print(f"IAM User: '{userName}', AccessKey: '{accessKey['AccessKeyId']}' "
                      f"Age Greater than 60Days.")
                keyAgeGreater60Days(userName, accessKeys['AccessKeyMetadata'], session, emailId)

            # Initiate Pre-Notification At Day 59
            elif accessKey['Status'] == "Active" and ((date.today() - accessKey['CreateDate'].date()).days == 59):  # == 59
                print(f"IAM User: '{userName}', AccessKey: '{accessKey['AccessKeyId']}' "
                      f"Age is 59Days.")
                keyAge59Days(userName, accessKey['AccessKeyId'], emailId)
            else:
                print(f"IAM User: '{userName}', AccessKey: '{accessKey['AccessKeyId']}', "
                      f"Status: '{accessKey['Status']}' Not Aged to 60Days.")


def IAM_SERVICE_USER(userName, session, emailId):
    accessKeys = session.list_access_keys(UserName=userName)
    for accessKey in accessKeys['AccessKeyMetadata']:
        # Notify key expire rotation for service user before 2 months.
        if accessKey['Status'] == "Active" and ((date.today() - accessKey['CreateDate'].date()).days == 305):
            print(f"Sending Rotation Notification 2 Months Before to "
                  f"'{emailId}' for IAM User: '{userName}'")
            subject = f"AWS IAM Key Rotation: Service User Expires in Two Months: {str(todayDate)}"
            message = f"Hi {userName}," \
                      f"\n\nYour AWS IAM Service AccessKey: <strong>{accessKey['AccessKeyId']}</strong>" \
                      f" is due for rotation in 2 months, as part of security policy." \
                      f"\n\n<h4> <i>Automated &#128640; </i></h4>"
            sendEmail(subject, message, [emailId], [adminEmailId])

        # Notify key expire rotation for service user before 1 month.
        elif accessKey['Status'] == "Active" and ((date.today() - accessKey['CreateDate'].date()).days == 335):
            print(f"Sending Rotation Notification 1 Month Before to "
                  f"'{emailId}' for IAM User: '{userName}'")
            subject = f"AWS IAM Key Rotation: Service User Expires in One Month: {str(todayDate)}"
            message = f"Hi {userName}," \
                      f"\n\nYour AWS IAM Service AccessKey: <strong>{accessKey['AccessKeyId']}</strong>" \
                      f" is due for rotation in 1 month, as part of our security policy." \
                      f"\n\n<h4> <i>Automated &#128640; </i></h4>"
            sendEmail(subject, message, [emailId], [adminEmailId])

        # Notify key expire rotation for service user before 1 week.
        elif accessKey['Status'] == "Active" and ((date.today() - accessKey['CreateDate'].date()).days == 360):
            print(f"Sending Rotation Notification 1Week Before to "
                  f"'{emailId}' for IAM User: '{userName}'")
            subject = f"AWS IAM Key Rotation: Service User Expires in One Week: {str(todayDate)}"
            message = f"Hi {userName}," \
                      f"\n\nYour AWS IAM Service AccessKey: <strong>{accessKey['AccessKeyId']}</strong>" \
                      f" is due for rotation in 1 week, as part of our security policy." \
                      f"\n\n<h4> <i>Automated &#128640; </i></h4>"
            sendEmail(subject, message, [emailId], [adminEmailId])

        # Notify list of service users above 1 year.
        elif accessKey['Status'] == "Active" and ((date.today() - accessKey['CreateDate'].date()).days >= 365):
            print(f"Sending Notification Key Age Crossed for 1Year to "
                  f"'{emailId}' for IAM User: '{userName}'")
            tableServiceUserAgeOneYear.append(
                '<tr>'
                '<td>' + userName + '</td>'
                                    '<td>' + str((date.today() - accessKey['CreateDate'].date()).days) + '</td>''</tr>')
        else:
            print(f"IAM User: '{userName}' Key Not Aged to 305Days.")
