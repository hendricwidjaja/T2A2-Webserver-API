# T2A2 API Webserver - Workout Together Planner API

Welcome to the documentation of Hendric Widjaja's - T2A2: API Webserver.

NOTE: FOR THE LATEST VERSION, PLEASE REFER TO T2A2-WEBSERVER-API-V2 (LINK HERE): [https://github.com/hendricwidjaja/T2A2-WebServer-API-v2](https://github.com/hendricwidjaja/T2A2-WebServer-API-v2)

## Quick Links

Please use the links below to quickly access key parts of this documentation.

- [Link to source control repository (GitHub)](https://github.com/hendricwidjaja/T2A2-Webserver-API)
- [R1 - Explain the problem that this app will solve and how this app addresses the problem](#r1---explain-the-problem-that-this-app-will-solve-and-how-this-app-addresses-the-problem)
- [R2 - Task allocation & Tracking](#r2---task-allocation--tracking-trello--github)
    - [Link to Trello](https://trello.com/b/2OOqzzxT/t2a2-api-webserver)
- [R3 - Third-Party Services, Packages & Dependencies](#r3---3rd-party-services-packages--dependencies)
- [R4 - Benefits & Drawbacks of Postgresql](#r4---benefits--drawbacks-of-of-postgresql)
- [R5 - Explain the features, purpose & functionalities of the object-relational mapping system (ORM) used in this app](#r5---explain-the-features-purpose-and-functionalities-of-the-orm-system-for-this-app)
- [R6 - Entity Relationship Diagram](#r6---entity-relationship-diagram)
- [R7 - Explain the implemeneted models and their relationships, including how the relationships aid database implementation](#r7-explain-the-implemented-models-and-the-relationship-including-how-the-relationshipos-aid-database-implementation)
- [R8 - API Endpoints Tutorial & Explanation](#r8---api-endpoints-tutorial--explanation)

## R1 - Explain the problem that this app will solve and how this app addresses the problem
### What is the problem?
With health being one of the most important factors of life itself, its important to exercise on a regular basis. Some of the main factors which deter and people from exercising are:

- social support
- accountability and commitment
- Cost of activities & facilities

A study in 2021 ran a specific study which measured the effect of providing social reward and support for a group of runners. The study proved that associating a positive experience with exercise leads to higher levels of energy, enjoyment and improved performance (without any additiona perceived effort) (Davis, MacCarron & Cohen 2021). They continued to strongly propose the importance and influence of social engagement and the feeling of belonging for individuals to foster deeper connections that can lead to better psychological, physical and social well being.

Accountability partners has been a term that has been thrown around in the last couple of years and for good reason. According to a study conducted in the US, an individual has a 65% success rate for achieving their goals if they share their goal with others. This success rate also goes all the way up to 95% if the individual commits completely and conducts check-ins with a accountability partner. This idea is just as successful when applied specifically to fitness and health goals (Chaudhuri, A 2023).

Other factors such as the cost of activities access to facilities also plays a significant part to the difficulty in committing to a healthy lifestyle. This can be due to the cost of gym memberships, exercise classes, personal trainers and the limitations of certain environments that individuals may experience due to their geographical location. 

### How does this app address the problem?
The 'Workout Together Planner' API is an application which promotes the health and wellbeing of individual by bringing them together. It addresses the aforementioned factors which can deter an individual from reaching their goals and sustaining a healthy lifestyle. 

The application allows users to create accounts and follows a social media platform feel. Although the API is still in its earlier stages, the current features allow users to:
- Create accounts
- Create exercises (e.g. Bench Press, Squats, Deadlifts, or even Tony's Crazy Leg Stretch Thingy Mabob?!)
- Create routines that can be viewed by other (if the user chooses to make the routine public)
- Add, remove and update exercises to their routines
    - Each exercise that is added can contain various characteristics such as sets, reps, weight, duration, etc.
- Like routines (which creates popularity and promotes routines that user's have made)
- Copy routines into their own private list which they can edit as they please

The application aims to provide further features in the future which will include more traditional social media type features such as messaging, following, posting and commenting. Not only this but it will also feature more fitness application related functions such as workout session logging and tracking.

The ultimate premise of this API is to address the detering factors of social support, accountability and commitment as well as the cost of activities and facilities. This API allows the creation of a global community where others can contact eachother to keep eachother accountable, motivate one another, share their fitness goals and successes and form stronger commitments to fitness and health. By only needing access to the internet, it drives down the problem of accessibility. Who needs a personal trainer when you have can have a community in your pocket that can help you along the way.


## R2 - Task Allocation & Tracking (Trello & GitHub)

### Trello
The creation of this API was conducted in parallel with the usage of Trello. Below are the main components ideas, and features of Trello that were utilised for task allocation and tracking purposes:
Tasks were separated into 2x main groups:

- Documentation
- Code

Each group was separated into futher categories/lists to allow the tracking of progress for the project. These lists were:
- To do
- WIP (Work in progress)
- Completed

Given the above structure, the creation of 'cards' could be implemented. Each card contained various small-medium sized tasks which needed to be completed to finalise the project as a whole. I decided to breakdown the tasks for documentation as per the requirements in the assignment (R1 - R8).  Each requirement was then broken down into smaller tasks, which made the completion of the assignment more manageable. On the category of code related cards, each card generally represented the completion of a model or a controller within the API. Each of these would then include smaller tasks such as creating a new route, completing a new feature, code refactoring, testing and reviewing. These smaller tasks were generally input as individual items in the checklist section of a requirement or code task. Dates for the completion of each card was also utilised to create a time plan for completion of each task, with the aim to be able to finalise and submit the assignment by the due date.

A link to a copy of the entire Trello Workspace can be found here: [https://trello.com/invite/b/66e1965df452f51f32ff2c94/ATTIb2433d8920ee741ceeda4fd0d9165de4C168FA8E/t2a2-api-webserver](https://trello.com/invite/b/66e1965df452f51f32ff2c94/ATTIb2433d8920ee741ceeda4fd0d9165de4C168FA8E/t2a2-api-webserver)


### GitHub / Git

GitHub and Git were also used extensively throughout the creation of this API to date. As a source control tool (Git) which can be shared on the cloud via remote repositories (GitHub), any user can easily manage and track changes, 'save' various versions and even revert back to previous versions if need be. The main useful tools which were applied for the creation of this API include:

#### To initialise the repository
```
git init
```
#### To add specific (or all) files to a staging area (this allows Git to track files you want to be tracked)
```
git add <filename> (OR) git add .
```
#### Creates a saved snapshot of the current version of the repository. This version can then be referred to at a later date or even reverted back to if need be.
```
git commit -m "<insert meaningful message>" 
```
#### To 'push' the commit to the remote repository (which can then be accessed by others)
```
git push
```
#### Creating a new branch (creates a copy of the repository where a user can make changes without affecting the "main" branch). Useful for experimentation and testing and working in collaborative environments.
```
git branch <new branch name> / git checkout <new branch name> 
```
#### Allows a user to merge their branch to the main branch (generally done on GitHub via git pull requests) which allows for better communication, collaboration and review processes before merging branches.
```
git pull / git merge 
```

Although there were other useful features which were used within Git and GitHub such as the creation of **.gitignore** files, the above git commands form the basis of the main features used for source control and tracking changes to the project.

The remote git repository which is hosted in GitHub can be found using the link here: [https://github.com/hendricwidjaja/T2A2-Webserver-API](https://github.com/hendricwidjaja/T2A2-Webserver-API)


## R3 - 3rd Party Services, Packages & Dependencies


#### PostgreSQL
PostgreSQL is an object relational database management system which is incorporated into this application for this very purpose. It allows for the storage of data in tables, rows and columns. PostgreSQL contains various features which gives it a long standing history of being ACID compliant. It ensures the atomicity, consistency, integrity and durability of the data it stores. It's robustness and ability to support complicated queries makes it a strong choice for the API. It supports these complexities via its strong feature set of creating:
- Primary Keys
- Foreign Keys
- Constraints (Unique, default, Nullable)
- Various datatypes

Other than the above, the Workout Together Planner API also utilises functions such as rollbacks which PostgreSQL supports. This allows any sessions or transactions to be cancelled in the event of errors that may cause integrity issues.

#### Flask
Flask is largely considered a micro web framework which is ultralight and easy to customise to allow various functionalities that can easily be extended through various libraries. Within this API, Flask allows for the structuring of HTTP routing to specific controllers, allowing the API to then logically fetch, create, delete and update data, before rendering the response back to the user. Flask is a crucial component of this API to handle the various routes and ensures that the right logic is applied to the data and given back to the user. Essentially, flask acts as a central control hub for the view functions and rules that are applied to URLs. Below is an example of several routes within the API that provide various functions/logic (via Blueprints).

```
from flask import Flask
```
![Flask_route_examples](/docs/R3_flask_example.png)

#### Flask-Bcrypt & bcrypt
Flask-Bcrypt is utilised to manage various verification and authentication features in APIs. It utilises various dependencies which make it possible to seamlessly integrate password hashing and password checking (bcrypt). This feature is a crucial aspect of maintaining the applications security and protection of user data. This helps prevent the sensitive password data of users of an application to be exposed. Examples of the usage of password hashing and checking can be seen under the below bcrypt dependency explanation.

```
from flask_bcrypt import Bcrypt # Importing
pw_hash = bcrypt.generate_password_hash(password) # Hashing passwords
bcrypt.check_password_hash(pw_hash, candidate) # Checking passwords
```
- An example of checking password
![bcrypt_example_1](./docs/R3_bcrypt1.png)

- An example of password hashing
![bcrypt_example_2](./docs/R3_bcrypt2.png)


#### Flask-JWT-Extended
Flask-JWT-Extended is what allows the JWT (JSON Web Token) functionality within this API. This authentication feature is another widely incorporated package which handles verfication of users and the provision of security tokens, enabling the control of access to data and database functions. 
This package can be imported via:
```
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
```
- create_access_token:
    - creates an access token for a user, usually provided to the user in the header of a HTTP response when a user logs in
- jwt_required:
    - a decorator which can wrap a function to either allow or deny access, based on if a user is logged in or not
- get_jwt_identity:
    - a function which allows an application to easily retrieve the logged in user's ID, providing a quick form of identification


#### FLask_SQLAlchemy
Flask SQLAlchemy is an object relational mapping (ORM) tool which allows for the abstraction of simplification of performing database operations. It does this by 'translating' data within the database into Python objects. The main features which are incorporated in this app are:
- Metadata
- Sessions
- Access to Columns and relationships for when defining models

An example of this implementation can be seen below for the RoutineExercise model within the API.
![SQLAlchemy_Example](/docs/R3_sqlalchemy.png)  

#### Flask-Marshmallow



#### marshmallow & marshmallow-sqlalchemy

#### python-dotenv
Python dotenv is utilised in this API to assist with configuring the necessary environment variables. This includes the 'DATABASE URI' and 'JWT' Secret Key particularly in this API. These highly important but extremely vulnerable forms of data are easily abstracted and modularised using python dotenv which allows for the separation of the APIs configuration settings and the logic's application. 

#### SQLALchemy


## R4 - Benefits & Drawbacks of of Postgresql
PostgreSQL (previously and still known as Postgres in short) is an ORDBMS (Object Relational Database Management System) which is commonly integrated in flask applications and is one of the most popular database services today due to its reach feature sets, ACID compliance and large community backing. In its most general sense, being a relational database management system infers that it stores data in the form of tables, columns and rows. Tables generally refer to entities, columns to attributes and rows to objects or instances. 


## R5 - Explain the Features, purpose and functionalities of the ORM system for this app

## R6 - Entity Relationship Diagram

## R7 Explain the implemented models and the relationship, including how the relationships aid database implementation

## R8 - API Endpoints Tutorial & Explanation

### Authentication Controller

#### 1. Register new user

- **HTTP VERB**: POST
- **ROUTE PATH**: @auth_bp.route("/register", methods=["POST"])
- **URL**: /auth/register
- **Description**: Registers a new user. If user is an admin, can register a new admin by setting "public" : "true"
- **Required Headers**: N/A
- **Required Body**: Email, Username & Password (Optional: firstname, lastname, is_admin)

**Success Example (201) vs Error Examples (401, 401, 403)**
![Register_new_user_200](./docs/R8/Authentication%20-%20Register%20new%20user%20-%20201.png)
![Register_new_user_400](<docs/R8/Authentication - Register new user - 400.png>)
![Register_new_user_401](<docs/R8/Authentication - Register new user - 401.png>)
![Register_new_user_403](<docs/R8/Authentication - Register new user - 403.png>)

#### 2. User Login

- **HTTP VERB**: POST
- **ROUTE PATH**: @auth_bp.route("/login", methods=["POST"])
- **URL**: /auth/login
- **Description**: Allows a registered user to log in. User must provide their email and password.
- **Required Headers**: N/A
- **Required Body**: Email & Password

**Success Example (201) vs Error Examples (401, 401, 403)**

#### 3. User Update Details

- **HTTP VERB**: PUT / PATCH
- **ROUTE PATH**: @auth_bp.route("/users/", methods=["PUT", "PATCH"])
- **URL**: /auth/users/
- **Description**: Allows a logged in user to update their username, firstname, lastname and/or password.
- **Required Headers**: JWT Token
- **Required Body**: (Options: Username, password, firstname, lastname)

**Success Example (201) vs Error Examples (401, 401, 403)**

#### 4.Delete user

- **HTTP VERB**: DELETE
- **ROUTE PATH**: @auth_bp.route("/users/<int:user_id>", methods=["DELETE"])
- **URL**: /auth/users/<int:user_id>
- **Description**: Allows a logged in user to delete their account. If user is an admin, they can delete ANY account. A user can insert whether they would like to leave any public routines on the database (default = delete both private & public routines)
- **Required Headers**: JWT Token
- **Required Body**: "delete_public_routines" (default=True).
  - To keep public routines on server, type in "delete_public_routines": false
  - To delete both public and private routines on server, leave body empty OR type in "delete_public_routines": true

**Success Example (201) vs Error Examples (401, 401, 403)**

### Exercises Controller

#### 5. Fetch all exercises

- **HTTP VERB**: GET
- **ROUTE PATH**: @exercises_bp.route("/", methods=["GET"])
- **URL**: /exercises
- **Description**: Fetches all exercises in the database (in alphabetical order)
- **Required Headers**: N/A
- **Required Body**: N/A

**Success Example (201) vs Error Examples (401, 401, 403)**

#### 6. Fetch all exercises (specific body_part)

- **HTTP VERB**: GET
- **ROUTE PATH**: @exercises_bp.route("/body-part/<body_part>", methods=["GET"])
- **URL**: /exercises/body-part/<body_part>
- **Description**: Fetches all exercises filtered by a specific body_part (e.g. Back). Header / Body data is not required, however this is dynamic **URL**. User will need to enter a valid "body_part" in the **URL** itself. (e.g. /exercises/body-part/Back)
- **Required Headers**:<italic>See description</italic>
- **Required Body**:*See description*

**Success Example (201) vs Error Examples (401, 401, 403)**

#### 7. Fetch exercise by ID

- **HTTP VERB**: GET
- **ROUTE PATH**: @exercises_bp.route("/id/<int:exercise_id>", methods=["GET"])
- **URL**: /exercises/id/<int:exercise_id>
- **Description**: Fetches a specific exercise based on exercise_id. Exercise ID to be input into **URL** (e.g. exercises/id/5) where exercise ID = 5
- **Required Headers**: N/A
- **Required Body**: N/A

**Success Example (201) vs Error Examples (401, 401, 403)**


#### 8. Fetch all exercises by user ID

- **HTTP VERB**: GET
- **ROUTE PATH**: @exercises_bp.route("/user/<int:user_id>/", methods=["GET"])
- **URL**: /exercises/user/<int:user_id>/
- **Description**: Fetches all exercises created by a specific user.User ID to be input into **URL** (e.g. exercises/user/9) where exercise ID = 9
- **Required Headers**: N/A
- **Required Body**: N/A

**Success Example (201) vs Error Examples (401, 401, 403)**

#### 9. Fetch exercise by user (filter by query paramater e.g. ?body_part=Chest)

- **HTTP VERB**: GET
- **ROUTE PATH**: @exercises_bp.route("/user/<int:user_id>/filter", methods=["GET"])
- **URL**: /exercises/user/<int:user_id>/filter
- **Description**: Headers and body data is not required. However user has the option to filter response data via "body_part". (e.g. /user/9/filter?body_part=Chest) where USER ID = 9
- **Required Headers**: *See body*
- **Required Body**: *See body*

**Success Example (201) vs Error Examples (401, 401, 403)**

#### 10. Create an exercise

- **HTTP VERB**: POST
- **ROUTE PATH**: @exercises_bp.route("/", methods=["POST"])
- **URL**: /exercises
- **Description**: Allows a logged in user to create an exercise. The new exercise must have a unique name and must be allocated to a specific "body_part". VALID BODY_PARTS: ("Chest", "Shoulders", "Back", "Legs", "Triceps", "Biceps", "Core", "Cardio")
- **Required Headers**: JWT Token
- **Required Body**: (Required: exercicse_name, body_part) (Optional: description)

**Success Example (201) vs Error Examples (401, 401, 403)**

#### 11. Delete an exercise

- **HTTP VERB**: DELETE
- **ROUTE PATH**: @exercises_bp.route("/<int:exercise_id>", methods=["DELETE"])
- **URL**: /exercises/<int:exercise_id>
- **Description**: Allows the creator of the exercise or an admin to delete an exercise from the database. Can only be deleted if it is not being used in any user routine.
- **Required Headers**: JWT Token
- **Required Body**: N/A

**Success Example (201) vs Error Examples (401, 401, 403)**

#### 12. Update an exercise

- **HTTP VERB**: PUT / PATCH
- **ROUTE PATH**: @exercises_bp.route("/<int:exercise_id>", methods=["PUT", "PATCH"])
- **URL**: /exercises/<int:exercise_id>
- **Description**: Allows the creator of the exercise or an admin to update an exercise from the database. Can only be updated if it is not being used in any user routine.
- **Required Headers**: JWT Token
- **Required Body**: (Optional: exercise_name, description, body_part)

**Success Example (201) vs Error Examples (401, 401, 403)**

### Routines Controller

#### 13. Fetch all routines

- **HTTP VERB**: GET
- **ROUTE PATH**: @routines_bp.route("/", methods=["GET"])
- **URL**: /routines
- **Description**: Fetch all routines (filter determined by user logged in). Routines will be ordered from most recent to oldest
  - If not logged in = public routines only
  - If logged in = public routines + user's personal/private routines
  - If admin = ALL routines
- **Required Headers**: (Optional: JWT Token)
- **Required Body**: N/A

**Success Example (201) vs Error Examples (401, 401, 403)**


#### 14. Fetch all routines (filter by target)

- **HTTP VERB**: GET
- **ROUTE PATH**: @routines_bp.route("/<target>", methods=["GET"])
- **URL**: /routines/<target>
- **Description**: Search for a public routine which targets a specific muscle group. 
  - User can also order the selected muscle group by popularity (how many likes), recent, and oldest using paramater query 
  - (e.g. ?sort=*filter* where *filter* can = popular, recent, oldest)
- **Required Headers**: (Optional: JWT Token)
- **Required Body**: N/A

**Success Example (201) vs Error Examples (401, 401, 403)**


#### 15. Fetch a routine by ID

- **HTTP VERB**: GET
- **ROUTE PATH**: @routines_bp.route("/<int:routine_id>", methods=["GET"])
- **URL**: /routines/<int:routine_id>
- **Description**: Allows a user to fetch a routine (restrictions as per below)
  - *Public Routines*:
    - If not logged in = OK
    - If logged in = OK
    - If logged in (owner of routine) = OK
    - If admin = OK

  - *Private Routines*:
    - If not logged in = ERROR
    - If logged in = ERROR
    - If logged in (owner of routine) = OK
    - If admin = OK
- **Required Headers**: (Optional: JWT Token)
- **Required Body**: N/A

**Success Example (201) vs Error Examples (401, 401, 403)**


#### 16. Fetch all routines (liked)

- **HTTP VERB**: GET
- **ROUTE PATH**: @routines_bp.route("/liked", methods=["GET"])
- **URL**: /routines/liked
- **Description**: Allows a logged in user to fetch all the routines they have liked. Ordered by most recently liked routine till oldest.
- **Required Headers**: JWT Token
- **Required Body**: N/A

**Success Example (201) vs Error Examples (401, 401, 403)**

#### 17. Create a new routine

- **HTTP VERB**: POST
- **ROUTE PATH**: @routines_bp.route("/", methods=["POST"])
- **URL**: /routines
- **Description**: Allows a logged in user to create a new routine. Routine must have a title and be allocated to a 'target'. (e.g. Upper Body)
- **Required Headers**: JWT Token
- **Required Body**: routine_title, target (optional: description, public)

**Success Example (201) vs Error Examples (401, 401, 403)**

#### 18. Update a routine

- **HTTP VERB**: PUT / PATCH
- **ROUTE PATH**: @routines_bp.route("/<int:routine_id>", methods=["PUT", "PATCH"])
- **URL**: /routines/<int:routine_id>
- **Description**: Allows an owner of a routine or an admin to update details of a specific routine.
  - NOTE: If a routine is being changed from public to 'private', all likes associated with the routine will be deleted.
  - This is to ensure that users who have liked the routine (other than the creator) will no longer be able to view the routine.
- **Required Headers**: JWT Token
- **Required Body**: (Optional: routine_title, description, target, public)

**Success Example (201) vs Error Examples (401, 401, 403)**

#### 19. Delete a routine

- **HTTP VERB**: DELETE
- **ROUTE PATH**: @routines_bp.route("/<int:routine_id>", methods=["DELETE"])
- **URL**: /routines/<int:routine_id>
- **Description**: Allows an owner of a routine or an admin to delete a specific routine.
- **Required Headers**: JWT Token
- **Required Body**: N/A

**Success Example (201) vs Error Examples (401, 401, 403)**

#### 20. Add an exercise to a routine

- **HTTP VERB**: POST
- **ROUTE PATH**: @routines_bp.route("/<int:routine_id>/exercise", methods=["POST"])
- **URL**: /routines/<int:routine_id>/exercise
- **Description**: Allows a user to add an exercise to their routine with various attributes. Routine ID required in URL
  - Attributes include ("sets", "reps", "weight", "distance_km", "distance_m", "hours", "minutes", "seconds", "note")
- **Required Headers**: JWT Token
- **Required Body**: exercise_id (At least one of: "sets", "reps", "weight", "distance_km", "distance_m", "hours", "minutes", "seconds", "note")

**Success Example (201) vs Error Examples (401, 401, 403)**

#### 21. Fetch an exercise associated to a routine

- **HTTP VERB**: GET
- **ROUTE PATH**: @routines_bp.route("/<int:routine_id>/exercise/<int:routine_exercise_id>", methods=["GET"])
- **URL**: /routines/<int:routine_id>/exercise/<int:routine_exercise_id>
- **Description**: Allows a user to fetch a specific exercise associated with a routine **(restrictions apply)**:
  - *Exercise within Public Routines*:
    - If not logged in = **OK**
    - If logged in = **OK**
    - If logged in (owner of routine) = **OK**
    - If admin = **OK**

  - *Exercise within Private Routines*:
    - If not logged in = **ERROR**
    - If logged in = **ERROR**
    - If logged in (owner of routine) = **OK**
    - If admin = **OK**
- **Required Headers**: (Optional: JWT Token)
- **Required Body**: N/A

**Success Example (201) vs Error Examples (401, 401, 403)**

#### 22. Update an exercise associated to a routine

- **HTTP VERB**: PUT / PATCH
- **ROUTE PATH**: @routines_bp.route("/<int:routine_id>/exercise/<int:routine_exercise_id>", methods=["PUT", "PATCH"])
- **URL**: /routines/<int:routine_id>/exercise/<int:routine_exercise_id>
- **Description**: Allows the creator of the routine or an admin to update an exercise within a routine. Routine and an associated routine_exercise ID is required in URL
- **Required Headers**: JWT Token
- **Required Body**: 

**Success Example (201) vs Error Examples (401, 401, 403)**

#### 23. Delete an exercise associated to a routine

- **HTTP VERB**: DELETE
- **ROUTE PATH**: @routines_bp.route("/<int:routine_id>/exercise/<int:routine_exercise_id>", methods=["DELETE"])
- **URL**: /routines/<int:routine_id>/exercise/<int:routine_exercise_id>
- **Description**: 
- **Required Headers**: 
- **Required Body**: 

**Success Example (201) vs Error Examples (401, 401, 403)**

# /routines/<int:routine_id>/<int:routine_exercise_id> - DELETE - Delete a specific routine exercise (must be owner or admin)
@routines_bp.route("/<int:routine_id>/exercise/<int:routine_exercise_id>", methods=["DELETE"])
@jwt_required()
@auth_as_admin_or_owner # Verify if logged in user is owner of the routine ID or is admin
def delete_routine_exercise(routine_id, routine_exercise_id):

#### 24. Like a routine

- **HTTP VERB**: POST
- **ROUTE PATH**: @routines_bp.route("/<int:routine_id>/like", methods=["POST"])
- **URL**: /routines/<int:routine_id>/like
- **Description**: 
- **Required Headers**: 
- **Required Body**: 

**Success Example (201) vs Error Examples (401, 401, 403)**

# /routines/<int:routine_id>/like - POST - like a routine (must be logged in)
@routines_bp.route("/<int:routine_id>/like", methods=["POST"])
@jwt_required() # User must be logged in to assign their user ID to the newly created like.
def like_routine(routine_id):

#### 25. Unlike a routine

- **HTTP VERB**: DELETE
- **ROUTE PATH**: @routines_bp.route("/<int:routine_id>/like", methods=["DELETE"])
- **URL**: /routines/<int:routine_id>/like
- **Description**: 
- **Required Headers**: 
- **Required Body**: 

**Success Example (201) vs Error Examples (401, 401, 403)**

# /routines/<int:routine_id>/like - DELETE - Delete a like from a specific routine (must be logged in)
@routines_bp.route("/<int:routine_id>/like", methods=["DELETE"])
@jwt_required() # Check if used is logged in
def unlike_routine(routine_id):

#### 26. Copy another user's routine

- **HTTP VERB**: POST
- **ROUTE PATH**: @routines_bp.route("/<int:routine_id>/copy", methods=["POST"])
- **URL**: /routines/<int:routine_id>/copy
- **Description**: 
- **Required Headers**: 
- **Required Body**: 

**Success Example (201) vs Error Examples (401, 401, 403)**

# /routines/<int:routine_id>/copy - POST - Copy another user's routine as personal private routine
@routines_bp.route("/<int:routine_id>/copy", methods=["POST"])
@jwt_required()  # User must be logged in
def copy_routine(routine_id):


## References

Chaudhuri, A. 2023. *The buddy boost: how 'accoutability partners' make you health, happy and more successful*. The Guardian, accessed 27 September 2024, Available at: [https://www.theguardian.com/lifeandstyle/2023/nov/27/the-buddy-boost-how-accountability-partners-make-you-healthy-happy-and-more-successful](https://www.theguardian.com/lifeandstyle/2023/nov/27/the-buddy-boost-how-accountability-partners-make-you-healthy-happy-and-more-successful)

Davis, A.J., MacCarron, P. and Cohen, E. 2021. *Social reward and support effects on exercise experiences and performance: Evidence from parkrun*. PLoS One, 16(9), accessed 27 September 2024, Available at: [https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8443045/](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8443045/) 

