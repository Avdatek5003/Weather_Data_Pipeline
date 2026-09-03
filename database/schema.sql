--
-- PostgreSQL database dump
--

\restrict KQffPz7XwIrcyKhCn0lIvHzpk7yPU2Lu5FiBVMMcRPYokM7J8OYnqeA9wCaRhbu

-- Dumped from database version 15.18 (Debian 15.18-1.pgdg13+1)
-- Dumped by pg_dump version 15.18 (Debian 15.18-1.pgdg13+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: airport_hourly_weather_data; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.airport_hourly_weather_data (
    record_id integer NOT NULL,
    airport_id integer,
    record_time timestamp without time zone NOT NULL,
    temperature_c numeric(5,2),
    dewpoint_c numeric(5,2),
    humidity_pct numeric(5,2),
    wind_speed_kmh numeric(5,2),
    wind_direction_deg integer,
    sea_level_pressure_hpa numeric(6,2),
    precipitation_mm numeric(5,2),
    wx_string character varying(50),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: airport_hourly_weather_data_record_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.airport_hourly_weather_data_record_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: airport_hourly_weather_data_record_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.airport_hourly_weather_data_record_id_seq OWNED BY public.airport_hourly_weather_data.record_id;


--
-- Name: airports; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.airports (
    airport_id integer NOT NULL,
    airport_name character varying(100) NOT NULL,
    country character varying(100),
    latitude numeric(9,2),
    longitude numeric(9,2),
    station_code character varying(10),
    wmo_id character varying(10)
);


--
-- Name: airports_airport_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.airports_airport_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: airports_airport_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.airports_airport_id_seq OWNED BY public.airports.airport_id;


--
-- Name: center_hourly_weather_data; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.center_hourly_weather_data (
    record_id integer NOT NULL,
    city_id integer,
    record_time timestamp without time zone NOT NULL,
    temperature_c numeric(5,2),
    humidity_pct numeric(5,2),
    apparent_temp_c numeric(5,2),
    precipitation_mm numeric(5,2),
    rain_mm numeric(5,2),
    snowfall_cm numeric(5,2),
    weather_code integer,
    cloud_cover_pct numeric(5,2),
    sea_level_pressure_hpa numeric(6,2),
    wind_speed_kmh numeric(5,2),
    wind_direction_deg numeric(5,2),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: center_hourly_weather_data_record_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.center_hourly_weather_data_record_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: center_hourly_weather_data_record_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.center_hourly_weather_data_record_id_seq OWNED BY public.center_hourly_weather_data.record_id;


--
-- Name: cities; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.cities (
    city_id integer NOT NULL,
    city_name character varying(75) NOT NULL,
    country character varying(75) NOT NULL,
    latitude numeric(9,2) NOT NULL,
    longitude numeric(9,2) NOT NULL,
    station_code character varying(10),
    wmo_id character varying(10)
);


--
-- Name: cities_city_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.cities_city_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: cities_city_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.cities_city_id_seq OWNED BY public.cities.city_id;


--
-- Name: daily_forecast_data; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.daily_forecast_data (
    forecast_id integer NOT NULL,
    city_id integer,
    forecast_date date NOT NULL,
    weather_code integer,
    max_temp_c numeric(5,2),
    min_temp_c numeric(5,2),
    max_wind_speed_kmh numeric(5,2),
    wind_direction_deg integer,
    precipitation_sum_mm numeric(5,2),
    rain_sum_mm numeric(5,2),
    snowfall_sum_cm numeric(5,2),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: daily_forecast_data_forecast_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.daily_forecast_data_forecast_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: daily_forecast_data_forecast_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.daily_forecast_data_forecast_id_seq OWNED BY public.daily_forecast_data.forecast_id;


--
-- Name: historical_weather; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.historical_weather (
    date timestamp without time zone,
    tavg double precision,
    tmin double precision,
    tmax double precision,
    prcp double precision,
    snow double precision,
    wdir text,
    wspd double precision,
    wpgt double precision,
    pres double precision,
    tsun double precision,
    city_name text
);


--
-- Name: airport_hourly_weather_data record_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.airport_hourly_weather_data ALTER COLUMN record_id SET DEFAULT nextval('public.airport_hourly_weather_data_record_id_seq'::regclass);


--
-- Name: airports airport_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.airports ALTER COLUMN airport_id SET DEFAULT nextval('public.airports_airport_id_seq'::regclass);


--
-- Name: center_hourly_weather_data record_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.center_hourly_weather_data ALTER COLUMN record_id SET DEFAULT nextval('public.center_hourly_weather_data_record_id_seq'::regclass);


--
-- Name: cities city_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cities ALTER COLUMN city_id SET DEFAULT nextval('public.cities_city_id_seq'::regclass);


--
-- Name: daily_forecast_data forecast_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.daily_forecast_data ALTER COLUMN forecast_id SET DEFAULT nextval('public.daily_forecast_data_forecast_id_seq'::regclass);


--
-- Name: airport_hourly_weather_data airport_hourly_weather_data_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.airport_hourly_weather_data
    ADD CONSTRAINT airport_hourly_weather_data_pkey PRIMARY KEY (record_id);


--
-- Name: airports airports_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.airports
    ADD CONSTRAINT airports_pkey PRIMARY KEY (airport_id);


--
-- Name: center_hourly_weather_data center_hourly_weather_data_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.center_hourly_weather_data
    ADD CONSTRAINT center_hourly_weather_data_pkey PRIMARY KEY (record_id);


--
-- Name: cities cities_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cities
    ADD CONSTRAINT cities_pkey PRIMARY KEY (city_id);


--
-- Name: daily_forecast_data daily_forecast_data_city_id_forecast_date_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.daily_forecast_data
    ADD CONSTRAINT daily_forecast_data_city_id_forecast_date_key UNIQUE (city_id, forecast_date);


--
-- Name: daily_forecast_data daily_forecast_data_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.daily_forecast_data
    ADD CONSTRAINT daily_forecast_data_pkey PRIMARY KEY (forecast_id);


--
-- Name: airport_hourly_weather_data unique_airport_record_time; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.airport_hourly_weather_data
    ADD CONSTRAINT unique_airport_record_time UNIQUE (airport_id, record_time);


--
-- Name: center_hourly_weather_data unique_city_record_time; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.center_hourly_weather_data
    ADD CONSTRAINT unique_city_record_time UNIQUE (city_id, record_time);


--
-- Name: airport_hourly_weather_data airport_hourly_weather_data_airport_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.airport_hourly_weather_data
    ADD CONSTRAINT airport_hourly_weather_data_airport_id_fkey FOREIGN KEY (airport_id) REFERENCES public.airports(airport_id) ON DELETE CASCADE;


--
-- Name: center_hourly_weather_data center_hourly_weather_data_city_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.center_hourly_weather_data
    ADD CONSTRAINT center_hourly_weather_data_city_id_fkey FOREIGN KEY (city_id) REFERENCES public.cities(city_id) ON DELETE CASCADE;


--
-- Name: daily_forecast_data daily_forecast_data_city_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.daily_forecast_data
    ADD CONSTRAINT daily_forecast_data_city_id_fkey FOREIGN KEY (city_id) REFERENCES public.cities(city_id);


--
-- PostgreSQL database dump complete
--

\unrestrict KQffPz7XwIrcyKhCn0lIvHzpk7yPU2Lu5FiBVMMcRPYokM7J8OYnqeA9wCaRhbu

