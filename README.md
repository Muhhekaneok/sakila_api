# Sakila API

The `Sakila_api` project - Restful API on FastAPI, connected to the educational database ** sakila **. 
Supports expanded search, analytical requests and interactive schedules based on Plotly.

---

## What API can do

### Films - Searching and filtration
- `GET /films` — film list (until 10 by default)
- `GET /films/{film_id}` — film by id
- `GET /films/search?keyword=` — search by name or description
- `GET /films/genre/{genre_name}` — films by genre
- `GET /films/year/{start_year}?end=` — films by year(s)

### Actors
- `GET /actors` — cast list
- `GET /actors/{actor_id}` — actor by id
- `GET /actors/search?name=` — search by first-name or last-name 

### Аналитика
- `GET /top-rented-films` — top films by rental
- `GET /top-paying-customers` — top customers by total payment
- `GET /available-films/{store_id}` — available films by store
- `GET /top-actors` — actors with the largest number of films

---

## Interactive plots (Plotly)

- `GET /stats/top-customers-chart` — top customers (bar-chart)
- `GET /stats/films-by-genre-chart` — ...
- `GET /stats/films-by-year-chart` — ...
- `GET /stats/popular-keywords-chart` — this endpoint applies to `recq`-table
- `GET /stats/search-types-chart` — ... (pie-chart)

---

## Architecture

- FastAPI + Pydantic are for structure and validation
- Connection to two DB: `sakila` (to reading) and `sak_logs` (for inserting)
- Structure of the project with two modules: `routes/`, `db/`, `models/`
- Using `.env` и `dotenv` for safe storage of configuration

---

## Setup and run

```bash
uvicorn main:app --reload
