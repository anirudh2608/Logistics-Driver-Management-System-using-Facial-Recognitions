# Logistics Management System using Face Recognition
# First Version

## Overview

The program sets up an server using Flask on which the application is hosted. The application is a one stop solution for customers and drivers of a logistics company. The customers can check the order status and change their address. The drivers can see pending orders, start their journey and deliver orders but at one cost: confirming their identity. Until the face of the driver is not matched with the database, he cannot - access his dashboard, start a new journey, see pending orders, deliver orders.
The driver while signing up for the job needs to submit their driving licence number after which the admin approves the driver. The admin can approve/reject/fire drivers, manage orders, manage trucks, check truck locations and change security.

## Important Notice
This project is tested on Ubuntu 20.04 LTS and Windows 10 home and is working as expected.

## Requirements
1. Python
2. Python virtual environment installed
3. A GPU

## How to run
1. Clone this repository and open a terminal in the project directory.
2. Create a virtual environment using the command: python3 -m venv venv/   and activate it using: source venv/bin/activate (for Linux/Mac), venv\Scripts\activate (For Windows)
3. Run this command to install all dependencies: pip3 -r install requirments.txt (For ubuntu 20.04), pip install -r newreq.txt (For Windows/Mac)
4. Now you are all loaded. Just run: python3 main.py or python main.py
5. Project running! Open the link given in the terminal on your web browser

## Important files

1. main.py
2. website/

## Important Note
This application requires a GPU to function. If you don't have a GPU, the application would not work

Versions of the software used are 
1. Python -  3.8.5
2. Tensorflow - tensorflow-gpu 2.2.0
3. CUDA - 10.2
4. CuDNN - v8.0.5 (November 9th, 2020), for CUDA 10.2 
5. GPU - Nvidia Geforce GTX 1650

## Report

The first edition is perfect when the user captures his/her image in bright light.

## Need Update

The project is the first edition. I will keep update.

