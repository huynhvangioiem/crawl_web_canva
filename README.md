
# Web Crawler - `main.py`

## Overview

The `main.py` script is a web crawler designed to extract and process information from web pages. This tool allows users to specify a URL, and the script will traverse the web pages linked from the given URL, collecting data as specified in the implementation.

## Features

- Crawl web pages starting from a specified URL.
- Extract and process relevant information from the web pages.
- Store or display the extracted data as required.

## Prerequisites

Ensure you have the following installed:

- **Python 3.8**: The script is written in Python 3. Make sure you have Python 3 installed on your system.
- **Required Libraries**: The script may require additional Python libraries. These are typically specified in the `environment.yml` file (if provided) or within the script itself.
  - BeautifulSoup 4.12.2

# How to Run the Web Crawling Project

## Introduction
This guide will help you set up and run the web crawler using Python 3.8. Follow the steps below carefully. No prior technical knowledge is required, and all you need is a computer with internet access.

## Step 1: Install Python 3.8
1. Open a web browser and go to the link: [Python 3.8 Download](https://www.python.org/downloads/release/python-380/).
2. Download the correct version of Python 3.8 for your operating system (Windows).
3. Run the installer and make sure to check the box **"Add Python 3.8 to PATH"** during installation.
4. Click **Install Now** and wait for the installation to complete.

## Step 2: Download and Install Git
1. Open your web browser and go to: [Git Download](https://git-scm.com/downloads).
2. Download Git for your operating system.
3. Run the installer and complete the installation with default settings.

## Step 3: Clone the Project from GitHub
1. Create a new folder on your desktop where you want to keep the project files.
2. Right-click inside the folder and select **"Git Bash Here"** (this option will appear after installing Git).
3. In the Git Bash window, type the following command and press **Enter**:
   ```
   git clone <link_to_the_github_repository>
   ```
   Replace **`<link_to_the_github_repository>`** with the link to your GitHub project. This will download the project files.

## Step 4: Create a Virtual Environment and Install Required Packages
1. Open the **Command Prompt** on your computer by pressing **Windows + R**, typing **cmd**, and pressing **Enter**.
2. In the Command Prompt window, change to the folder where you downloaded the project files using the command:

   **Command:**
   ```
   cd path\to\your\project\folder
   ```
   Replace **`path\to\your\project\folder`** with the actual path to the folder.
3. Create a virtual environment by typing the following command and pressing **Enter**:

   **Command:**
   ```
   python -m venv myenv
   ```
   This will create a new folder named **myenv** containing the virtual environment.
4. Activate the virtual environment by typing the following command and pressing **Enter**:

   **Command:**
   ```
   ./myenv/Scripts/activate
   ```
5. To install all the required packages, type the following command and press **Enter**:

   **Command:**
   ```
   pip install -r instal.txt
   ```
   This command will install all the necessary libraries for the web crawler to work.

## Step 5: Run the Web Crawler
1. Still in the Command Prompt, make sure you are in the correct folder where the project is located.
2. To start the web crawler, type the following command and press **Enter**:

   **Command:**
   ```
   python main.py
   ```
   Replace **`main.py`** with the name of the Python file that runs the crawler if it has a different name.
3. Follow any on-screen instructions. The crawler will begin collecting the data you need.

## Step 6: View the Results

## Notes
- Make sure your computer is connected to the internet during the entire process.
- If you happen to have any issues, please feel free to contact me for further assistance.

## Troubleshooting Tips
- **Command not found**: Ensure that Python and Git were installed correctly, and Python was added to PATH.
- **Permission Denied**: You may need to run Command Prompt as an administrator.
