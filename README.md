#  Automated Cold Email Pipeline

Automate your job outreach with Python — send **personalized cold emails**, attach resumes, and track every attempt automatically.

---

##  Overview

This project helps automate cold emailing to HRs and recruiters using **Gmail SMTP**. It reads contact data from a CSV/Excel file, personalizes each email using a template, attaches your resume, and logs results — all while skipping already sent emails.

---

##  Key Features

-  **Personalized Emails**: Customize subject & body with `{name}`, `{company}`, `{role}` placeholders  
-  **Auto Resume Attachment**: Automatically attach your resume to each email  
-  **Smart Retry & Random Delay**: Reduces spam detection and avoids Gmail blocking  
-  **Skip Already Sent Contacts**: Ensures you don’t resend emails accidentally  
-  **Detailed Logs**: Tracks sent, failed, and skipped emails in CSV  
-  **Secure Gmail Authentication**: Uses **App Password** for safe login  

---

##  Folder Structure

<img width="377" height="318" alt="Screenshot 2025-10-23 012056" src="https://github.com/user-attachments/assets/6bee85e1-8056-4b55-afdb-08c1a0e4497c" />

---

##  Usage

1. **Add Contacts**  
   - Edit `Data/recipients_list.csv` with your recipients:  
     ```csv
     name,email
     John Doe,john.doe@example.com
     Jane Smith,jane.smith@example.com
     ```

2. **Edit Email Template**  
   - Open `Templates/email_template_v1.txt` and format like:  
     ```
     Subject: Job Application for {role} at {company}

     Hi {name},

     I am reaching out to apply for the {role} position at {company}. 
     Please find my resume attached.

     Regards,
     Your Name
     ```

3. **Add Resume**  
   - Place your PDF resume inside `Assets/` folder.

4. **Run the Script**  
   ```bash
   python send_emails.py

-----------

## Check Logs

- Sent, failed, and skipped emails are updated automatically in the Data/ folder.

----------

## Security

- Use a Gmail App Password instead of your main password.
- Enable 2-Step Verification for your Gmail account.
- Learn more about App Passwords

----------------

## Requirements

- Python 3.10+
- Packages:pip install pandas openpyxl

----------------

## Notes

- Test with a dummy Gmail account before sending to real recruiters.
- Ensure the email template starts with Subject: ...
- The script avoids sending to invalid emails automatically.

------------

## Author

- Atharva Chavhan
- atharvachavhan18@gmail.com

--------------------
