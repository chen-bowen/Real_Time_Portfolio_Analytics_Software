# The Real Time Portfolio Analytics Software

## Abstract

The following project was completed during 2016 as the capstone course of my Engineering Science program at the University of Toronto. The goal of this project is to provide	a	decision	support	system to	recommend	optimally	weighted	equity	portfolios	targeted	towards investors with different skill levels. The project is delivered in the form of a Flask web application format. Unfortunately, I did not have time or capacity to find an approrpriate host to put the entire application on a online server. However, the logic component of the script is fully functional and could be used anytime. I would greatly appreciate if you could acknowledge us as the contributors in case if you would like to use any part of this project. Shall time allow me to do so, I would definetely try to upload the project to an online server for you to tryout. Thank you!

## Acknowledgements

I would like to dedicate my sincere thanks to my professor Roy Kwon, for setting up this great course for us to apply the technical skills we accquired during courses to solve a complex problem with real-life datasets. I also want to thank Professor Kwon's TA, Minho Lee, for his consistent support anytime we faced technical difficulties during our quest to complete this project. Finally, I really want to attribute to my fellow teammates, Yinger Li and Jessica Leung, for their great contributions to my first ever large scale analytics project. Without their presences, the completion of this project would not be possible. 

## Technology

This project is developed with python Flask framework that consists of three main components. Currently the project is not avaliable online. If you are really interested in seeing the project in action, please follow the [installation instructions](installation_instructions.pdf	) file to recreate the envrionment. 

### Backend

We use Flask as the backend framework since my team knows python and there are many libraries readily available. Daily financial data is downloaded using python pandas data reader from Yahoo Finance and stored in the PostgreSQL database, which is hosted on the Heroku server.  The stored data is then fed to the two completed models, which calculates results to be fed 
to the frontend. The backend will download S&P 500 data and select top n assets (n = 1~5) from each sector based on 
highest EPS. The size of the portfolio will range from 10 to 50 based on the choice of the assets. The specific implementation of the backend could be found in the [app.py](./app.py) file. The return data are downloaded using the ***Return_Data_Collector.py*** file in the commons folder. The backend flow chart is shown below.
                                              
![backend.jpg](/Images/Backend.PNG)

### Logical Component

Based on the exisiting frameworks for portfolio optimization technique - Black Litterman Framework, this projects blends in two technical analysis indicators (relative strength index and stochastic oscilators) to make the algorithm more robust and versatile. The black-litterman model allows users input their personal views of the stock movements, allowing more customizations for the algorithm (For details of the Black - Litterman model, please visit the [capstone final report](CapstoneFinalReport.pdf) file in this repository). However, not many investors are skilled enough to make reasonable view inputs. The technical analysis indicators could serve as internal metrics for the algorithm to self-input the views needed for Black-Litterman model.The relative strength index and stochastic oscilators takes advantage of the stocks overbought and oversold situations and propose counter actions to gain profits.


![Capture.png](/Images/Capture.PNG)

With the utilizations of this special conjuction model, we made sure our application could be used by both professional portfolio managers and speculative investors. The specific implementation of the logic component of this app could be found in the ***Black_Litterman.py*** in the commons folder. 

### Frontend

The frontend of this application is built with the bootstrap template "SmartAdmin - Responsive WebApp". We added plenty of modifications on the page to make it pretty. Below, is the front page once we logged in.

![landing_page.jpg](/Images/Landing%20Page.PNG)
Here is the portfolio allocation presentation

![Capstone_Final_Report.jpg](/Images/Interface.PNG )


Thank you for visiting!
