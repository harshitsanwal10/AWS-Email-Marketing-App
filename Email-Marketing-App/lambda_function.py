import boto3
import csv

# Initialize AWS clients
s3_client = boto3.client('s3')
ses_client = boto3.client('ses')

# S3 bucket and file names
BUCKET_NAME = 'project-email-marketing10'  # Replace with your bucket name
CSV_FILE_KEY = 'contacts.csv'
EMAIL_TEMPLATE_KEY = 'email_template.html'
FROM_EMAIL = 'harshitsanwal2003@gmail.com'  # Replace with your verified SES email


def lambda_handler(event, context):
    try:
        # Retrieve the CSV file from S3
        csv_file = s3_client.get_object(Bucket=BUCKET_NAME, Key=CSV_FILE_KEY)
        lines = csv_file['Body'].read().decode('utf-8').splitlines()

        # Retrieve the HTML email template from S3
        email_template = s3_client.get_object(Bucket=BUCKET_NAME, Key=EMAIL_TEMPLATE_KEY)
        email_html = email_template['Body'].read().decode('utf-8')

        # Parse the CSV file
        contacts = csv.DictReader(lines)

        for contact in contacts:
            try:
                # Personalize the email template
                personalized_email = email_html.replace('{{FirstName}}', contact.get('FirstName', 'User'))

                # Send the email using SES
                response = ses_client.send_email(
                    Source=FROM_EMAIL,
                    Destination={'ToAddresses': [contact['Email']]},
                    Message={
                        'Subject': {'Data': 'Your Weekly Tiny Tales Mail!', 'Charset': 'UTF-8'},
                        'Body': {'Html': {'Data': personalized_email, 'Charset': 'UTF-8'}}
                    }
                )
                print(f"Email sent to {contact['Email']}: Response {response}")

            except Exception as email_error:
                print(f"Failed to send email to {contact['Email']}: {email_error}")

    except Exception as e:
        print(f"An error occurred: {e}")
