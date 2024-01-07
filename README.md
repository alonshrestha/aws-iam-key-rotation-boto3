# AWS IAM Key Rotation Automation Using Boto3

## Overview

This Python script automates the rotation of AWS IAM (Identity and Access Management) keys to enhance security practices within an AWS environment. 

The script is designed to efficiently manage key rotations for keys aged above 60 days, send notifications using AWS SES, and ensure compliance with security policies. 

The script also includes key rotation validation for specific situations, such as excluding users belonging to the 'IAM_SERVICE_USER' IAM group and those without the required 'EmailID' tag, ensuring a targeted and secure key rotation process.

## Script Workflow:

1. ### User Group Check
   - The script starts by generating a list of users from the IAM group named "IAM_SERVICE_USER."
   - Users belonging to this group are excluded from key rotation.

2. ### IAM User Tag Check
   - The script then generates a list of all IAM users and checks if they have the required tag called "EmailID."
   - Users without this tag are skipped for key rotation. 
   - This is because the script cannot send a newly generated key to the user without email address.

3. ### IAM_SERVICE_USER Group Check
   - For users with the "EmailID" tag, the script checks if they belong to the "IAM_SERVICE_USER" group.
   - If a user belongs to this group, a notification is sent, marking them as a service key. These service keys should be rotated manually, and the script skips key rotation for these users.

4. ### Key Rotation Process
   - For users not in the "IAM_SERVICE_USER" group, the key rotation process is initiated.
  
5. ### Key Checks and Actions
   - The script evaluates each user's access keys:
      - First check: If a user has two active keys, a notification is sent, and key rotation is skipped for that user.
      - Then, if a user's key age is equal to or greater than 60 days, key rotation is initiated.
        - For users with two inactive keys, both keys are deleted.
        - For users with one active and one inactive key, the inactive key is deleted, the active key is deactivated, and a new key is generated and sent to the user.
        - For users with only one active key, the key is deactivated, and a new key is generated and sent to the user.

6. ### Pre-Notification
   - If a user's key age is exactly 59 days, a pre-notification is sent to the user, informing them that their key will rotate the next day.

7. ### Final Email Notifications
   - At the end of the process, the script sends email notifications for:
      - List of users with two active keys.
      - List of service users in group "IAM_SERVICE_USER" whose key age has crossed one year.

## Script Files:

- The automation is implemented across two Python scripts:
   - `main.py`: This script contains the main process flow and orchestrates the IAM key rotation workflow.
   - `utils.py`: This script holds utility functions and dependencies used by the main script (`main.py``   ).      

## Prerequisites:

- Ensure AWS credentials are properly configured with proper access to rotate the key.

## Installation:

Install required Python packages by running:

```bash
pip install -r requirements.txt
```

## Usage

#### Running the Script

Execute the `main.py` script to run the automation.

```bash
python3 main.py
```
## Configuration

- Customize IAM group names, tag names, notification thresholds, and message templates as needed in the script.

## Dependencies

- Python 3.x
- `boto3` library

## License
- This project is licensed under the MIT License - see the [LICENSE](/LICENSE) file for details.

## Usage Disclaimer and Considerations
- This tool is a basic example and may need modifications based on specific use cases or security considerations.
- Refer to the [boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) for more information on AWS SDK for Python.
- **Important**: Do not deploy this script in a production environment without thorough testing. Always ensure that the script meets your specific requirements and does not cause any unintended consequences.
