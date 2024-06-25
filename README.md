# TheSquad

## Table of Contents
1. [Project Overview](#project-overview)
2. [Usage](#usage)
3. [Folder Structure](#folder-structure)
    - [Info](#info)
    - [Static](#static)
    - [Templates](#templates)
    - [TheSquad](#thesquad)
    - [Other Files](#other-files)
4. [Python Files Overview](#python-files-overview)
5. [Contributing](#contributing)
6. [License](#license)
7. [Contact](#contact)

## Project Overview
TheSquad is a project designed to demonstrate the functionality and organization of an API built using Flask. The project is structured to allow for easy addition of routes and subsequent route descriptions on the project
website.

## Usage
This project is not meant for installation. It serves as a showcase of the API's capabilities, as well as the structure of the codebase.

## Folder Structure

### Info
This folder contains personal notes and logs, serving as a place to document thoughts and steps taken during development.
- `setup.txt`
    - Contains a list of steps I took to intialize and begin the creation of this project
- `analysis_goals.txt`
    - Contains a written out summary of the analysis options employed 
- `app_util.txt`
    - Contains information about the Data Dragon routes for the live client asset control, as well as a basic code summary of how the encryption and decryption works for the services. This is done because Heroku requires these keys to be saved as CONFIG VARS, but certain characters within the keys are not allowed and therefore needed to be manipulated prior to be used.
- `example_live_output.txt`
    - Contains a JSON output of what the live client would respond with when pulling from the route: https://127.0.0.1:{port}/lol-champ-select/v1/session
- `instructions.txt`
    - Contains a variety of "HowTo's" to ensure I know how to manipulate the project and navigate the Heroku CLI as needed

### Static
This folder contains all web content, including CSS and HTML files.
- `content/`
  - `match-content.html` - Match data specific route showcase & usage
  - `riotID-content.html` - Player (RiotID) specific route showcase & usage
  - `squad-content.html` - Squad specific route showcase & usage
- `css/`
  - `content.css`
  - `home.css`
  - `loading.css`
  - `squad-data-demo.css`
  - `variables.css`
- `js/`
  - `loading.js` (WIP)
  - `navbar.js` - Controls the Navbar so that only the selected content will be rendered
- `images/` - Contains original project images for class, variable, and function structure and data flow

### Templates
This folder contains the HTML templates used in the project.
- `home.html`
- `squad-data-demo.html`

### TheSquad
This folder contains the core Python scripts, each with distinct functions or responsiblities. See their descriptions below.
- `analysis.py`
- `constants.py`
- `firebase.py`
- `riot_api.py`
- `squad.py`
- `test.py`

### Other Files
These files are essential for scaffolding, deploying, and running the project through Heroku. Anything not visible is purposefully witheld for security reasons
- `.env` - (Not Visible) Private keys that are stored in a local "env". Mimics the keys that are saved in Heroku as CONFIG VARS
- `.firebaserc` - (Not Visible) Firebase uses this file to ensure the project is pointing to the correct project name held by Firebase
- `.flaskenv` - (Not Visible) Has specific environment variables that establish this app as a Flask App.
- `.gitignore` - Created by https://www.toptal.com/developers/gitignore/api/firebase,python,flask. Edit at https://www.toptal.com/developers/gitignore?templates=firebase,python,flask
- `app.py` - The primary driver of this application, containing all the routes of the API.
- `app_util.py` - Contains utilities necessary for `app.py` to launch smoothly and handle GET requests.
- `firebase.json` - Contains all of the necessary authentication tokens and strings to establish a connection to the database while the project is running. Certain elements are to remain empty for viewing purposes.
- `Procfile`
- `README.md` - This file
- `requirements.txt` - List of python libraries installed in the project's virtual environment
- `runtime.txt` - Tells Heroku what version of Python I intend to use.

## Python Files Overview

### analysis.py
Contains the analysis logic for processing the squad data set and calculating scores for each player per archetype of champion. The project will eventually provide this data in real-time, either through a specific route or simply a part of the squad's primary data set.

### constants.py
Defines constants used throughout the project such as data structure templates for individual squad members, the squad data set, standardized colors, or known good variables for testing purposes.

### firebase.py
Facilitates all functions and interactions that occur between the project and Google's Firebase services, i.e., Cloud Firestore (the database of this project)

### riot_api.py
Manages API calls to the Riot Games API, handling data requests and processing the data therein. Passes this data back to a squad object.

### squad.py
This file handles everything related to a squad. It's main objective is have an object that represents a middle man between the Riot Games API and TheSquad's database. Everything from each members individual ID's, their match histories, and the eventual squad data set, are stored here as the program runs. How a squad object "looks" can be viewed in the images folder.

### test.py
Currently contains test cases to check for bad requests to Riot Games' API. Since this is mostly handled at this point, new tests will likely be made in the future to test indivdual routes and ensure both good and bad responses are handled gracefully.

## Contributing
There will be no contributing at this time. Future goals do include creating a live service/locally
installed windows application that works in tandem with the live client. Once the base app is completed, 
I'd strongly consider asking for feature additions.

## License
This project is licensed under the MIT License. See the `LICENSE` file for more details.

### Licensing and Use
Anyone is welcome to use the code, but please note that the repository isn't "functional" in the traditional sense. Much of the project's actual functionality relies on obtaining a developer key through Riot Games and creating a project in Firebase to obtain private credentials. Therefore, there's no real point in using this code other than as an example of how to manage a Flask app and apply a webpage to it.

### Endorsement
"thesquad-api" isn’t endorsed by Riot Games and doesn’t reflect the views or opinions of Riot Games or anyone officially involved in producing or managing League of Legends. League of Legends and Riot Games are trademarks or registered trademarks of Riot Games, Inc. League of Legends © Riot Games, Inc.

## Contact
For any questions or inquiries, please contact "Christopher Porter" at chris.j.porter25@gmail.com


