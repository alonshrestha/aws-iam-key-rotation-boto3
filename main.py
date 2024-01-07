__author__ = "Alon Shrestha"

import utils
from utils import initIAMRotation, IAM_SERVICE_USER, iamSessionClient


# Function to generate IAM user list and perform key rotation checks
def main():
    # Generate IAM Users of Group 'SERVICE_IAM_KEY' with a maximum count of 1000.
    IAM_SERVICE_USER_List = []
    try:
        srvGrpResponse = iamSessionClient.get_group(GroupName='IAM_SERVICE_USER', MaxItems=1000)
        for srvIAMUser in srvGrpResponse['Users']:
            IAM_SERVICE_USER_List.append(srvIAMUser['UserName'])
    except Exception as e:
        print(f"Could not get SERVICE_IAM_KEY Users. Error: {e}")

    # Generate all IAM users Max Count 1000.
    iamUserResponse = iamSessionClient.list_users(MaxItems=1000)
    for iamUser in iamUserResponse['Users']:
        # Get email of IAM user from tag 'EmailID'.
        iamUserEmail = utils.getIAMUserEmailTag(iamSessionClient, iamUser['UserName'])
        # Check if IAM user has tag 'EmailID'.
        if not iamUserEmail:
            print(f"IAM User: '{iamUser['UserName']}' EmailID Tag Not Found. No Action Made!")
            # Append IAM User with no tag 'EmailID' in NoEmailIDTagTable list
            utils.tableNoEmailID.append(
                '<tr>'
                '<td>' + iamUser['UserName'] + '</td>'
                                               '</tr>')
        else:
            # Check if IAM user exist in SERVICE_IAM_KEY Group.
            if iamUser['UserName'] in IAM_SERVICE_USER_List:
                print(f"IAM User: '{iamUser['UserName']}' is in IAM Group: SERVICE_IAM_KEY")
                IAM_SERVICE_USER(iamUser['UserName'], iamSessionClient, iamUserEmail)
            # If not initiate key rotation process.
            else:
                print(f"IAM User: '{iamUser['UserName']}' is not in IAM Group: SERVICE_IAM_KEY."
                      f" Initiating IAM Key Rotation!")
                # Initiate Credential Rotation Process
                initIAMRotation(iamUser['UserName'], iamSessionClient, iamUserEmail)

    # Initiate email notification for user with no tag 'EmailID'
    utils.tableNoEmailID.append('</table>')
    utils.tableNoEmailID.append('<h4> <i>Automated &#128640; </i></h4>')
    subjectNoEmailId = f"AWS IAM Key Rotation: Users With No EmailID Tag: {str(utils.todayDate)}"
    bodyMessageNoEmailId = (''.join(utils.tableNoEmailID))
    if len(bodyMessageNoEmailId) > 550:
        utils.sendEmail(subjectNoEmailId, bodyMessageNoEmailId, [utils.senderEmailId], None)
    else:
        print(f"User With No EmailID Table is Empty!")

    # Initiate email for users with two active keys
    utils.tableUserWithTwoActiveKey.append('</table>')
    utils.tableUserWithTwoActiveKey.append('<h4> <i>Automated &#128640; </i></h4>')
    subjectTwoActiveKey = f"AWS IAM Key Rotation: Users With Two Active Keys: {str(utils.todayDate)}"
    bodyMessageTowActiveKey = (''.join(utils.tableUserWithTwoActiveKey))
    if len(bodyMessageTowActiveKey) > 551:
        utils.sendEmail(subjectTwoActiveKey, bodyMessageTowActiveKey, [utils.senderEmailId], None)
    else:
        print(f"Two Active Keys Table is Empty!")

    # Initiate email for service user's key age crossed one year.
    utils.tableServiceUserAgeOneYear.append('</table>')
    utils.tableServiceUserAgeOneYear.append('<h4> <i>Automated &#128640; </i></h4>')
    subjectServiceUserAgeOneYear = f"AWS IAM Key Rotation: Service User Expired(1 Year+): {str(utils.todayDate)}"
    bodyServiceUserAgeOneYear = (''.join(utils.tableServiceUserAgeOneYear))
    if len(bodyServiceUserAgeOneYear) > 566:
        utils.sendEmail(subjectServiceUserAgeOneYear, bodyServiceUserAgeOneYear, [utils.senderEmailId], None)
    else:
        print(f"Service User Age One Year Table is Empty!")


if __name__ == "__main__":
    main()
