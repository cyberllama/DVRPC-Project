from columns import MCDPopColumns, OutputColumns, MCDCrashColumns
from datetime import datetime
from pathlib import Path
import sqlite3
import copy
import csv

MIN_YEAR = 2015
MAX_YEAR = 2025
YEAR_RANGE = range(MIN_YEAR, MAX_YEAR)
EMPTY_YEAR_DICT = {key: None for key in YEAR_RANGE} 
REPORTS_ROOT = Path("./generated_reports")

class GenerateReport():
    """
    Generates a CSV report of crashes per capita across all municipality in 9 county region. Creates additional columns for 
    total, pedestrian, and cyclists killed and severely injured per capita, single year and 5yr average 
    """
    mcd_pop_by_year = {}
    mcd_totals_by_year = {}
    min_year_input = None
    max_year_input = None 

    def exec(self, min_year_input, max_year_input):
        self._init_folders()
        self.min_year_input = int(min_year_input)
        self.max_year_input = int(max_year_input)
        self._get_mcd_population_forecasts()
        crash_summaries = self._get_crash_summaries()
        mcd_crashes_per_capita = self._replace_totals_with_per_capita_columns(crash_summaries)
        full_rows = self._add_5yr_average_columns(mcd_crashes_per_capita)
        output = self._return_rows_within_year_range(full_rows)
        file_name = self._write_as_csv(output)
        return file_name
    
    def _init_folders(self):
        REPORTS_ROOT.mkdir(exist_ok=True)

    def _get_mcd_population_forecasts(self) -> None:
        connection = sqlite3.connect('./db/mcd_crashes.db')
        cursor = connection.cursor()
        query = "SELECT mun_dist_id, pop_2015, pop_2019, pop_2020, pop_2025 FROM mcd_population"
        rows = cursor.execute(query).fetchall()
        
        for row in rows:
            mun_dist_id = row[0]
            self.mcd_pop_by_year[mun_dist_id] = self._estimate_missing_population_years(row)
        

    def _estimate_missing_population_years(self, row):

        def convert_population_to_int(pop):
            return int(pop.replace(",", ""))
        
        def calculate_average_yearly_change(year_1, year_2):
            return (year_pop_dict[year_2] - year_pop_dict[year_1]) / (year_2 - year_1)
        
        def calculate_estimated_pop(start_pop, start_year, change, current_year):
            return round(start_pop + change * (current_year - start_year))
        
        year_pop_dict = copy.copy(EMPTY_YEAR_DICT)
        year_pop_dict[2015] = convert_population_to_int(row[MCDPopColumns.POP_2015.value])
        year_pop_dict[2019] = convert_population_to_int(row[MCDPopColumns.POP_2019.value])
        year_pop_dict[2020] = convert_population_to_int(row[MCDPopColumns.POP_2020.value])
        year_pop_dict[2025] = convert_population_to_int(row[MCDPopColumns.POP_2025.value])

        yearly_change_2015_2019 = calculate_average_yearly_change(2015, 2019)
        yearly_change_2020_2025 = calculate_average_yearly_change(2020, 2025)

        for year in range(MIN_YEAR, MAX_YEAR):
            if year_pop_dict[year] != None:
                continue
            elif year < 2019:
                year_pop_dict[year] = calculate_estimated_pop(year_pop_dict[2015], 2015, yearly_change_2015_2019, year)
            elif year > 2020:
                year_pop_dict[year] = calculate_estimated_pop(year_pop_dict[2020], 2020, yearly_change_2020_2025, year)
        
        return year_pop_dict
    
    def _get_crash_summaries(self):
        connection = sqlite3.connect('./db/mcd_crashes.db')
        cursor = connection.cursor()
        min_year_5yr_minimum = self.min_year_input - 4
        crash_query_min_year = MIN_YEAR if min_year_5yr_minimum < MIN_YEAR else min_year_5yr_minimum
        query = f"SELECT County, MCD_Name, GEOID10, Crash_Year, TOTAL_PERSONS, PEDESTRIAN_COUNT, BICYCLE_COUNT FROM mcd_crash WHERE Crash_Year >= {crash_query_min_year} AND CRASH_YEAR <= {self.max_year_input} ORDER BY Crash_Year DESC"
        rows = cursor.execute(query).fetchall()
        return rows
    
    def _calculate_per_capita(self, total: int, population: int):
        return round((total / population) * 100000, 1)


    def _replace_totals_with_per_capita_columns(self, rows):
        new_rows = []
        row_counts_start_index = MCDCrashColumns.TOTAL_KSI.value
        for row in rows:
            output_row = []
            year = row[MCDCrashColumns.YEAR.value]
            mcd_id = row[MCDCrashColumns.MCD_ID.value]

            if(mcd_id not in self.mcd_pop_by_year):
                continue

            population = self.mcd_pop_by_year[mcd_id][year]

            rates = []
            row_total_columns = row[row_counts_start_index:]
            for column in row[row_counts_start_index:]:
                rates.append(self._calculate_per_capita(column, population))

            output_row += row[0 : row_counts_start_index]
            output_row.append(population)
            output_row += rates

            if(mcd_id not in self.mcd_totals_by_year):
                self.mcd_totals_by_year[mcd_id] = copy.copy(EMPTY_YEAR_DICT)
            self.mcd_totals_by_year[mcd_id][year] = row_total_columns

            new_rows.append(output_row)
        return new_rows
    
    def _add_5yr_average_columns(self, rows):
        new_rows = []
        for row in rows:
            year = row[OutputColumns.YEAR.value]
            mcd_id = row[OutputColumns.MCD_ID.value]

            if(year - MIN_YEAR < 4):
                new_rows.append(row)
                continue

            mcd_totals_dict = self.mcd_totals_by_year[mcd_id]
            mcd_totals_as_array = [*{k: mcd_totals_dict[k] for k in range(year - 4, year + 1) if k in mcd_totals_dict}.values()]
            mcd_pop_dict = self.mcd_pop_by_year[mcd_id]
            total_5yr_population = sum([*{k: mcd_pop_dict[k] for k in range(year - 4, year + 1) if k in mcd_pop_dict}.values()])

            if(None in mcd_totals_as_array):
                new_rows.append(row)
                continue

            summed_totals = [sum(x) for x in zip(*mcd_totals_as_array)]
            averaged_5yr_rates = [self._calculate_per_capita(x, total_5yr_population) for x in summed_totals]
            row += averaged_5yr_rates
            new_rows.append(row)
        return new_rows
    
    def _return_rows_within_year_range(self, rows):
        result = [row for row in rows if row[OutputColumns.YEAR.value] >= self.min_year_input and row[OutputColumns.YEAR.value] <= self.max_year_input]
        return result

    def _write_as_csv(self, rows):
        date = datetime.today().strftime('%Y-%m-%d')
        year_range = f'{self.min_year_input}-{self.max_year_input}' if self.min_year_input != self.max_year_input else f'{self.max_year_input}'
        file_name = f'generated_reports/MCD Crash Report - {year_range} - {date}.csv'
        with open(file_name, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(list(OutputColumns.__members__))
            writer.writerows(rows)
        return file_name
