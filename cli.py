import click
import sqlite3
from db import GenerateDatabase
from report import GenerateReport

MIN_YEAR = 2015

def main():
    initialize_db()
    max_year = get_max_year()
    year_range = get_year_range(max_year)
    generate_report(year_range[0], year_range[1])

def initialize_db():
    click.echo(click.style("Downloading data and initalizing database...", fg='cyan'))
    db = GenerateDatabase()
    db.exec()
    click.echo(click.style("Database succesfully initialized", fg='green'))

def get_max_year():
    connection = sqlite3.connect('./db/mcd_crashes.db')
    cursor = connection.cursor()
    click.echo(click.style("Determining most recently available year from crash data...", fg='cyan'))
    query = "SELECT MAX(Crash_Year) FROM mcd_crash"
    max_year = cursor.execute(query).fetchone()[0]
    click.echo(click.style(f"Most recent year: {max_year}", fg='cyan'))
    return max_year

#TODO: With more time working on this project, I would validate these inputs
def get_year_range(max_year):
    click.echo(click.style(f"Enter a year range between 2015 and {max_year}...", fg='cyan'))
    min_year_input = click.prompt(click.style("MIN YEAR", fg='magenta'))
    max_year_input = click.prompt(click.style("MAX MAX", fg='magenta'))
    return (min_year_input, max_year_input)

def generate_report(min_year, max_year):
    click.echo(click.style(f"Generating report between {min_year} and {max_year}...", fg='cyan'))
    report = GenerateReport()
    file_name = report.exec(min_year, max_year)
    click.echo(click.style(f"Report succesfully generated and outputed to generated_reports/{file_name}", fg='green'))
