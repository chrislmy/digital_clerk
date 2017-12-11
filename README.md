# Digital Clerk
Digital Clerk main repository.

### Requirements
The current version of Django used for this website is version 1.10.5 and python version 3.5.2. 

### Installation
First install Django version 1.10.5
```
pip install django == 1.10.5
```
Then clone repository by using 
```
git clone https://github.com/chrislmy/digital_clerk.git
```
Change working directory into project directory
```
cd digitalclerk
```

### Database
The website is currently using postgreSQL version 9.6.5 as its database. 

### Configure Settings
In order to run the database locally, the settings.py file under digitalclerk/settings.py must be configured as follow
```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'digitalclerk',
        'USER': 'YOUR_DB_USERNAME',
        'PASSWORD': 'YOUR_DB_PASSWORD',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```
where YOUR_DB_USERNAME and YOUR_DB_PASSWORD are the username and password of your respective postgresql database.
Once settings.py is configured, make migrations to apply the changes and create the schema tables.
```
python manage.py makemigrations
python manage.py migrate
```

### Running the website locally
In order to run the website locally, change to the parent directory and run the following command
```
python manage.py runserver
```
The website should be running locally under http://127.0.0.1:8000/

### User profiles for different pages.
For development purposes, there are currently 4 manual user profiles set up. (2 student profiles and 2 staff profiles).
Below is the data format of the profiles.

Student profile 1:
```
{
  upi: 1,
  name: Christopher Lau,
  status: student
}
```
Student profile 2:
```
{
  upi: 4,
  name: LiLy Collins,
  status: student
}
```

Lecturer profile:
```
{
  upi: 2,
  name: Tony Hunter,
  status: lecturer
}
```

Assistant profile:
```
{
  upi: 3,
  name: Mike Smith,
  status: assistant
}
```

## Module detail page and office hour dashboard page
There are 3 main pages utilizing the user profiles from above.

#### Module details page
http://127.0.0.1:8000/dashboard/module_details/MODULE_CODE navigates to the dashboard page for a specific module where ```MODULE_CODE``` is the specified module.

Here the user is displayed with a calender to *create an office hour* if user is a lecturer/assistant under that module.

OR if the user is a student, they are able to see available office hours for the specific module and join them.

#### Office hour dashboard page for LECTURERS/ASSISTANTS
http://127.0.0.1:8000/office_hour_dashboard?office-hour-id=ID... navigates to the dashboard page for a specific *OFFICE HOUR*

This page is only accessible for lectueres/assistants where they can address available student requests.

#### Office hour dashboard page for STUDENTS
http://127.0.0.1:8000/office_hour_dashboard_student?office-hour-id=ID... navigates to the dashboard page for a specific *OFFICE HOUR*

This is the page where students are able to raise requests for a lecturer.

*** **The office hour dashboard page for STUDENTS and LECTURERS/ASSISTANTS can be run CONCURRENTLY on seperate tabs since the data is currently independent of each other**.

## Changing and setting user profiles for different pages.
The pages which are currently utilizing these user profiles are the ```module_detail``` page, ```office_hour_dashboard``` page, and ```office_hour_dashboard_student``` page.

To set the user profiles of the ```module_detail``` page. in settings.py change the variable 
```
MODULE_DETAIL_DASHBOARD_PROFILE = 'STUDENT_PROFILE_1'
```
The enumerable statuses for each profile is as below:

```STUDENT_PROFILE_1``` to assign data for **Student profile 1**

```STUDENT_PROFILE_2``` to assign data for **Student profile 2**

```LECTURER_PROFILE``` to assign data for **Lecturer profile**

```ASSISTANT_PROFILE ``` to assign data for **Assistant profile**

*** Note that these enumarables are used for all the 3 pages.

*** The user profiles for the module detail page and office hour dashboard page are <strong>INDEPENDENT OF EACH OTHER</strong>. Hence ensure that the profiles for each individual pages are set accordingly to your desire.

To set the user profiles of the ```office_hour_dashboard``` page. in settings.py change the variable
```
OFFICE_HOUR_DASHBOARD_STAFF_PROFILE = 'LECTURER_PROFILE'
```

And finally, to set the user profiles of the ```office_hour_dashboard_student``` page. in settings.py change the variable
```
OFFICE_HOUR_DASHBOARD_STUDENT_PROFILE = 'STUDENT_PROFIL1'
```




