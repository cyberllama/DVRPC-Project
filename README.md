# DVRPC Project

## Scenario
The scenario that we have is that the Office of Safe Streets (OSS) has requested support in developing a
reproducible data process to consume crash data and population for a quick high-level understanding of
crashes per capita by municipality across the region.

### Setup
```
# Create venv :
python3 -m venv .venv

# Activate venv:
. .venv/bin/activate

# Sync dependencies from `requirements.txt`:
pip install -r requirements.txt

# Run application and follow prompts
python3 app.py
```

### Application
This application has 3 main components, a simple command line interface (CLI) with prompts to customize the report, a simple database to sqlize CSV data, and a report generator that queries the database and generates a csv report from the custom inputs determined in the CLI. The CLI has two prompts, MIN YEAR and MAX YEAR. These prompts determine the range of years that will be outputted into the report CSV. For example, if 2015-2020 is selected, the report will provide per capita data for every municipality between 2015 and 2020. If the user selects 2020-2020, it will only output data for 2020. Allowing for a range of years can give context on crash trends in municipalities, while looking at a single year can be a quick way to compare municipalities for the year of interest.
*note: At the moment there is no validation for entered years. With a little bit more time working on this I would add it, but for now just enter the years within the displayed range (ascending).*

### Data Source
This application draws from two different data sources that were provided in the assignment: [Crash Data](https://catalog.dvrpc.org/dataset/crash-summary-and-fatal-counts), [Population Data](https://catalog.dvrpc.org/dataset/adopted-2050-v1-0-population-employment-forecasts)
I explored other potential datasets but each had their own shortcomings. One [dataset](https://catalog.dvrpc.org/dataset/population-estimates) provided detailed population counts for each municipality by year, but it did not contain information for 2020 and beyond, which are key years for analysis and future proofing. It also did not divide philadelphia into planning districts as it is in the crash dataset.

### Database
Each time the project is exectuted, the application first downloads the Crash and Population data as CSVs then dumps them into a local sqlite3 database. Two tables are created: **mcd_crash** and **mcd_population**. This allows for simpler querying and expanded data manipulation options of crash and population data.
*note: I'm aware that the tables can be directly queried from the DVRPC api, however, this was more a demonstration of my ability to create a simple database*

### Report
To create a *high level* understanding of crashes per capita in each municipality, I chose what I believe to be the 3 most relevant fields to understanding the data at a glance. Drawing from the original crash data, I wanted to look at the Number of people Killed or Severely injured, seperated as three field types: total, pedestrians, and cyclists. Pedestrian and Cyclists are the most vulnerable road users (as are motorcyclists but that data is not provided), and the overall total provides the clearest indication of crash frequency. For these three field types, the per capita (per 100k) by year, and a per capita (per 100k) 5yr average is calculated. I chose to include a 5yr average as some munipalities have very small populations, and a small number of crashes can in these municipalities results in large outlier per capita values. 
*note: With the current set of population and crash data, 5yr averages can only be calculated for 2019 & 2020. The population data only provides estimates for 2015 and onwards, so we cannot calculate a 5yr average for 2018 and lower.*

### Population estimates
The population data only provides estimates for 2015, 2019, 2020, and 5yr increments up to 2050. To calculate accurate per capita values for each year, we need to fill in the gaps in the missing years. For the purpose of this project, I estimate the population by calculation the linear change by year between 2015-2019, and 2020-2025. While not 100% accurate as population change isn't entirely linear, it provides an estimate that will have a neglible effect on the per capita total that is calculated. With more time on this project, I would like to have created a dataset that has a combination of real an future estimated populations by municipality using census data.


### Math
For each municipality we make the following calculation from its population and the crash total for each field type, rounded to one decimal point
*Per capita*: (crash count / population) * 100,000
*Per capita 5yr average*: (sum of crash counts in 5 year range / sum of population in 5 year range) * 100,000

### Fields
| Column                  | Description                                                             |
|-------------------------|-------------------------------------------------------------------------|
| County                  | County                                                                  |
| MCD_NAME                | Municipal Civil Designation                                             |
| MCD_ID                  | 2010 Census geography GEOID                                             |
| YEAR                    | Year                                                                    |
| POPULATION ESTIMATE     | Population Estimate                                                     |
| TOTAL_KSI_RATE          | People killed or severely injured per capita (100k)                     |
| PEDESTRIAN_KSI_RATE     | Pedestrians killed or severely injured per capita (100k)                |
| BICYCLIST_KSI_RATE      | Bicyclists killed or severely injured per capita (100k)                 |
| TOTAL_KSI_RATE_5YR      | People killed or severely injured over previous 5 years per capita      |
| PEDESTRIAN_KSI_RATE_5YR | Pedestrians killed or severely injured over previous 5 years per capita |
| BICYCLIST_KSI_RATE_5YR  | Bicyclists killed or severely injured over previous 5 years per capita  |

### Future proofing
This application uses a population data source that has estimates up to 2050. Currently, the application is coded to handle data up to 2025 (current data provided only goes up to 2020) but can easily be adjusted for further years. Because this application redownloads and remakes its small database every time it's run, it will automatically include new years that are added to the crash dataset. Additionally, the CLI will adjust it's maximum allowed year depending on the highest year available in the crash dataset.

### Report Insights
Nationwide trends tell us that fatal crashes across all modes have been on the rise since roughly 2010, and have significantly increased since the onset of the pandemic. This trend is similarly visible in Philadelphia, which you can view in another application I have made [here](https://philadelphiacrashdashboardfrontenddev.azurewebsites.net/) - [github](https://github.com/cyberllama/CrashDashboardFrontend) - [backend gihub](https://github.com/cyberllama/CrashDashboardBackend). For this report, I would like to see if this national trend is roughly consistent across municipalities within this 9 county region.

There are a couple of challenges with using this report to analyze these trends. For one, you cannot average per capita values between municipalites as their populations are different. A municipality with a population of 100,000 might have a fatal crash rate of 10, whereas a municipality with a population of 1000 might have a fatal crash rate of 500. Their averaged crash rate would be 14.9, not 255. Therefore, you would need the underlying crash totals (which we reference in the data source section). 
There are a couple solutions to these problems that we can use. Rather than looking up each crash total, we can average per capita rates with some simple math. Since we provide population in the data set, this formula between two munipalities and their crash rates will give us a correct average crash rate
(crash_rate_1 * population_1 + crash_rate_2 * population_2) / (population_1 + population_2)  
To average all municipalities for a year, it will look something like this in excel 
=SUMPRODUCT(E2:E365,F2:F365) / SUM(E2:E365)
This will allow us to do some simple calculations in excel without needing to reference another dataset

| YEAR | AVG TOTAL_KSI_RATE | AVG PED_KSI_RATE | AVERAGE BIKE_KSI_RATE |
|------|--------------------|------------------|-----------------------|
| 2020 |        2506.844272 |      34.02237723 |           11.20683612 |
| 2019 |        3385.516475 |      49.33153406 |            13.2183977 |
| 2018 |        3437.825177 |      49.90189789 |           13.42778075 |
| 2017 |        3437.352007 |      50.00159346 |           15.50974737 |
| 2016 |        3463.074035 |      52.98107281 |           16.82023057 |
| 2015 |        3384.209629 |      49.54314625 |           18.03439286 |

Using the above formulas, we produce this table which shows us the average per capita rates across municipalities per year. There are a few trends visible here that I had not been suspecting. Between total ksi and pedestrian ksi rates, they stayed roughly the same between 2015 and 2019, and then drastically dropped in 2020, likely due to decreased transportation activity in the midst of the pandemic. More surprising to me is the steady rate in descreased bike ksi rate from 2015-2020, dropping by nearly 40% over 6 years. Another useful application of this table is that it allows for a simple analysis of individual municipalities compared to the baseline. Here are a few interesting outliers with populations greater than 10k (exclude extreme outliers with small sample sizes)

| COUNTY              | MCD_NAME             | MCD_ID     | YEAR | POPULATION_ESTIMATE | TOTAL_KSI_RATE | PEDESTRIAN_KSI_RATE | BICYCLIST_KSI_RATE |
|---------------------|----------------------|------------|------|---------------------|----------------|---------------------|--------------------|
| Camden County       | Bellmawr Borough     | 3400704750 | 2019 |               11359 |        21727.3 |                  44 |               35.2 |
| Gloucester County   | Deptford Township    | 3401517710 | 2018 |               30392 |        14839.4 |                36.2 |               19.7 |
| Philadelphia County | Central Philadelphia | 4210160103 | 2015 |              125180 |         2782.4 |               204.5 |               95.1 |
| Camden County       | Camden City          | 3400710000 | 2019 |               73562 |         1117.4 |               118.3 |               35.3 |

As shown here, Bellmar Borough and Depford township have exceedingly hight Total KSI Rates, 640% and 430% above the baseline respectively. Central Philadelphia and camden city both have excessively high pedestrian and bicyclist ksi rates, however, they also have a higher share of pedestrians and cyclists than other municipalities.

### Future work, conclusions
One significantly lacking data point missing from this application is Vehicle Miles Travelled (VMT). As shown for Philadelphia and Camden City, it might be misleading to compare them to a baseline average across municipalities as they have a much higher rate of pedestrians and cyclists than most municipalities. If I were to work more on this project, I would create an additional category for all 3 field types, per vehicle miles travelled. This would require having data for estimated vehicle miles travelled across all modes in every municipality, but in many cases would be a far better indicator of what municipalities have excessively dangerous roads. Additionally, I think it's important to have seperate statistics for motorists, and motorcyclists. Having a combination of motorists, motorcyclists, pedestrians, and cyclists would provide a full understanding of the rates of deaths and severe injuries across munipalities. Lastly, it would be really interesting to see the numbers from 2021 through 2023. The last year of data being a pandemic year makes it difficult to see long term trends, and in my own dashboard of Philadelphia these most recent years have shown the highest rates of fatalities and severe injuries, especially among vulnerable road users.

One other note, in the dataset provided the following fields are listed
| FIELD NAME | Description                      |
|---------------|----------------------------------------------------|
| TOTAL KILLED  | Total number of people killed                      |
| TOTAL INJURED | Total number of people injured                     |
| TOTAL PERSONS | Total number of people killed or seriously injured |

The sum of total killed and total injured has a completely different value than total persons. I used total persons for the report, which has a far higher value, as I assumed that total injured might have to do with lower severity injuries. I tested doing reports on total persons, and using the sum, and found similar trends (but vastly different rates). I just thought I would make a note of it as it seems a little misleading in the original dataset.

Thank you for reading this long report, it was a super interesting challenge and maybe I did a little more than I needed to, but I had fun doing it. I chose not to excessively comment the code, as the functions are fairly self descriptive. The exec function in db.py and report.py outlines the order in which functions are executed. There are some fairly simple class summaries and a step summary in cli.py. Please come with any specific questions about the code and my development process. Looking forward to discussing my work with you soon! 

