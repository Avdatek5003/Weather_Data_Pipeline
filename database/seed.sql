--
-- PostgreSQL database dump
--

\restrict Bna76HdB25qlZ57Z4UbEAUhvJ3kfbsxieetaLhM6VJKawWBn1H6F8gxG69Kz5X4

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

--
-- Data for Name: airports; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.airports (airport_id, airport_name, country, latitude, longitude, station_code, wmo_id) VALUES (1, 'Afyon Hava Meydanı', 'Türkiye', 38.73, 30.60, 'LTAF', '17190');
INSERT INTO public.airports (airport_id, airport_name, country, latitude, longitude, station_code, wmo_id) VALUES (2, 'İstanbul Havalimanı', 'Türkiye', 41.28, 28.75, 'LTFM', '17638');
INSERT INTO public.airports (airport_id, airport_name, country, latitude, longitude, station_code, wmo_id) VALUES (3, 'Esenboğa Havalimanı', 'Türkiye', 40.13, 33.00, 'LTAC', '17130');
INSERT INTO public.airports (airport_id, airport_name, country, latitude, longitude, station_code, wmo_id) VALUES (4, 'Antalya Havalimanı', 'Türkiye', 36.90, 30.80, 'LTAI', '17300');
INSERT INTO public.airports (airport_id, airport_name, country, latitude, longitude, station_code, wmo_id) VALUES (5, 'İzmir Adnan Menderes Havalimanı', 'Türkiye', 38.29, 27.16, 'LTBJ', '17220');
INSERT INTO public.airports (airport_id, airport_name, country, latitude, longitude, station_code, wmo_id) VALUES (6, 'Amsterdam Airport Schiphol', 'Hollanda', 52.31, 4.76, 'EHAM', '06240');
INSERT INTO public.airports (airport_id, airport_name, country, latitude, longitude, station_code, wmo_id) VALUES (7, 'Paris Charles de Gaulle Airport', 'Fransa', 49.01, 2.55, 'LFPG', '07156');
INSERT INTO public.airports (airport_id, airport_name, country, latitude, longitude, station_code, wmo_id) VALUES (8, 'Václav Havel Airport Prague', 'Çekya', 50.10, 14.26, 'LKPR', '11520');
INSERT INTO public.airports (airport_id, airport_name, country, latitude, longitude, station_code, wmo_id) VALUES (9, 'Budapest Ferenc Liszt International Airport', 'Macaristan', 47.44, 19.26, 'LHBP', '12843');
INSERT INTO public.airports (airport_id, airport_name, country, latitude, longitude, station_code, wmo_id) VALUES (10, 'Vienna International Airport', 'Avusturya', 48.11, 16.57, 'LOWW', '11035');
INSERT INTO public.airports (airport_id, airport_name, country, latitude, longitude, station_code, wmo_id) VALUES (11, 'John F. Kennedy International Airport', 'Amerika Birleşik Devletleri', 40.64, -73.78, 'KJFK', '72503');
INSERT INTO public.airports (airport_id, airport_name, country, latitude, longitude, station_code, wmo_id) VALUES (12, 'Haneda Airport (Tokyo International Airport)', 'Japonya', 35.55, 139.78, 'RJTT', '47662');
INSERT INTO public.airports (airport_id, airport_name, country, latitude, longitude, station_code, wmo_id) VALUES (13, 'Berlin Brandenburg Airport Willy Brandt', 'Almanya', 52.37, 13.50, 'EDDB', '10384');
INSERT INTO public.airports (airport_id, airport_name, country, latitude, longitude, station_code, wmo_id) VALUES (14, 'Oslo Airport, Gardermoen', 'Norveç', 60.19, 11.10, 'ENGM', '01415');
INSERT INTO public.airports (airport_id, airport_name, country, latitude, longitude, station_code, wmo_id) VALUES (15, 'London Heathrow Airport', 'İngiltere', 51.47, -0.46, 'EGLL', '3772');
INSERT INTO public.airports (airport_id, airport_name, country, latitude, longitude, station_code, wmo_id) VALUES (16, 'Sheremetyevo International Airport', 'Rusya', 55.97, 37.41, 'UUEE', '27612');
INSERT INTO public.airports (airport_id, airport_name, country, latitude, longitude, station_code, wmo_id) VALUES (17, 'Beijing Capital International Airport', 'Çin', 40.08, 116.58, 'ZBAA', '54511');
INSERT INTO public.airports (airport_id, airport_name, country, latitude, longitude, station_code, wmo_id) VALUES (18, 'Sydney Kingsford Smith Airport', 'Avustralya', -33.94, 151.18, 'YSSY', '94767');
INSERT INTO public.airports (airport_id, airport_name, country, latitude, longitude, station_code, wmo_id) VALUES (19, 'Indira Gandhi International Airport', 'Hindistan', 28.56, 77.10, 'VIDP', '42182');
INSERT INTO public.airports (airport_id, airport_name, country, latitude, longitude, station_code, wmo_id) VALUES (20, 'Adolfo Suárez Madrid-Barajas Airport', 'İspanya', 40.45, -3.55, 'LEMD', '08221');
INSERT INTO public.airports (airport_id, airport_name, country, latitude, longitude, station_code, wmo_id) VALUES (21, 'Brussels Airport', 'Belçika', 50.90, 4.53, 'EBBR', '06451');
INSERT INTO public.airports (airport_id, airport_name, country, latitude, longitude, station_code, wmo_id) VALUES (22, 'Rome Fiumicino Airport', 'İtalya', 41.80, 12.25, 'LIRF', '16242');
INSERT INTO public.airports (airport_id, airport_name, country, latitude, longitude, station_code, wmo_id) VALUES (23, 'Los Angeles International Airport', 'ABD', 33.94, -118.40, 'KLAX', '72295');
INSERT INTO public.airports (airport_id, airport_name, country, latitude, longitude, station_code, wmo_id) VALUES (24, 'Gimpo International Airport', 'Güney Kore', 37.56, 126.79, 'RKSS', '47110');
INSERT INTO public.airports (airport_id, airport_name, country, latitude, longitude, station_code, wmo_id) VALUES (25, 'Galeão - Antônio Carlos Jobim International Airport', 'Brezilya', -22.82, -43.25, 'SBGL', '83746');
INSERT INTO public.airports (airport_id, airport_name, country, latitude, longitude, station_code, wmo_id) VALUES (26, 'Ottawa Macdonald-Cartier International Airport', 'Kanada', 45.32, -75.67, 'CYOW', '71628');
INSERT INTO public.airports (airport_id, airport_name, country, latitude, longitude, station_code, wmo_id) VALUES (27, 'Athens International Airport', 'Yunanistan', 37.94, 23.95, 'LGAV', '16716');


--
-- Data for Name: cities; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.cities (city_id, city_name, country, latitude, longitude, station_code, wmo_id) VALUES (1, 'Afyonkarahisar', 'Türkiye', 38.76, 30.54, 'LTAF', '17190');
INSERT INTO public.cities (city_id, city_name, country, latitude, longitude, station_code, wmo_id) VALUES (2, 'İstanbul', 'Türkiye', 41.01, 28.95, 'LTFM', '17638');
INSERT INTO public.cities (city_id, city_name, country, latitude, longitude, station_code, wmo_id) VALUES (3, 'Ankara', 'Türkiye', 39.92, 32.85, 'LTAC', '17130');
INSERT INTO public.cities (city_id, city_name, country, latitude, longitude, station_code, wmo_id) VALUES (4, 'Antalya', 'Türkiye', 36.91, 30.70, 'LTAI', '17300');
INSERT INTO public.cities (city_id, city_name, country, latitude, longitude, station_code, wmo_id) VALUES (5, 'İzmir', 'Türkiye', 38.41, 27.14, 'LTBJ', '17220');
INSERT INTO public.cities (city_id, city_name, country, latitude, longitude, station_code, wmo_id) VALUES (6, 'Amsterdam', 'Hollanda', 52.37, 4.89, 'EHAM', '06240');
INSERT INTO public.cities (city_id, city_name, country, latitude, longitude, station_code, wmo_id) VALUES (7, 'Paris', 'Fransa', 48.85, 2.35, 'LFPG', '07156');
INSERT INTO public.cities (city_id, city_name, country, latitude, longitude, station_code, wmo_id) VALUES (8, 'Prag', 'Çekya', 50.09, 14.42, 'LKPR', '11520');
INSERT INTO public.cities (city_id, city_name, country, latitude, longitude, station_code, wmo_id) VALUES (9, 'Budapeşte', 'Macaristan', 47.50, 19.04, 'LHBP', '12843');
INSERT INTO public.cities (city_id, city_name, country, latitude, longitude, station_code, wmo_id) VALUES (10, 'Viyana', 'Avusturya', 48.21, 16.37, 'LOWW', '11035');
INSERT INTO public.cities (city_id, city_name, country, latitude, longitude, station_code, wmo_id) VALUES (11, 'New York', 'ABD', 40.78, -73.96, 'KJFK', '72503');
INSERT INTO public.cities (city_id, city_name, country, latitude, longitude, station_code, wmo_id) VALUES (12, 'Tokyo', 'Japonya', 35.67, 139.65, 'RJTT', '47662');
INSERT INTO public.cities (city_id, city_name, country, latitude, longitude, station_code, wmo_id) VALUES (13, 'Berlin', 'Almanya', 52.52, 13.40, 'EDDB', '10384');
INSERT INTO public.cities (city_id, city_name, country, latitude, longitude, station_code, wmo_id) VALUES (14, 'Oslo', 'Norveç', 59.91, 10.74, 'ENGM', '01415');
INSERT INTO public.cities (city_id, city_name, country, latitude, longitude, station_code, wmo_id) VALUES (15, 'Londra', 'İngiltere', 51.50, -0.12, 'EGLL', '3770');
INSERT INTO public.cities (city_id, city_name, country, latitude, longitude, station_code, wmo_id) VALUES (16, 'Moskova', 'Rusya', 55.75, 37.61, 'UUEE', '27612');
INSERT INTO public.cities (city_id, city_name, country, latitude, longitude, station_code, wmo_id) VALUES (17, 'Delhi', 'Hindistan', 28.61, 77.20, 'VIDP', '42182');
INSERT INTO public.cities (city_id, city_name, country, latitude, longitude, station_code, wmo_id) VALUES (18, 'Pekin', 'Çin', 39.90, 116.40, 'ZBAA', '54511');
INSERT INTO public.cities (city_id, city_name, country, latitude, longitude, station_code, wmo_id) VALUES (19, 'Sydney', 'Avustralya', -33.86, 151.20, 'YSSY', '94767');
INSERT INTO public.cities (city_id, city_name, country, latitude, longitude, station_code, wmo_id) VALUES (20, 'Madrid', 'İspanya', 40.47, -3.57, 'LEMD', '08221');
INSERT INTO public.cities (city_id, city_name, country, latitude, longitude, station_code, wmo_id) VALUES (21, 'Brüksel', 'Belçika', 50.90, 4.48, 'EBBR', '06451');
INSERT INTO public.cities (city_id, city_name, country, latitude, longitude, station_code, wmo_id) VALUES (22, 'Roma', 'İtalya', 41.80, 12.25, 'LIRF', '16242');
INSERT INTO public.cities (city_id, city_name, country, latitude, longitude, station_code, wmo_id) VALUES (23, 'Los Angeles', 'ABD', 33.94, -118.39, 'KLAX', '72295');
INSERT INTO public.cities (city_id, city_name, country, latitude, longitude, station_code, wmo_id) VALUES (24, 'Seul', 'Güney Kore', 37.57, 126.97, 'RKSL', '47108');
INSERT INTO public.cities (city_id, city_name, country, latitude, longitude, station_code, wmo_id) VALUES (25, 'Rio de Janeiro', 'Brezilya', -22.82, -43.25, 'SBGL', '83746');
INSERT INTO public.cities (city_id, city_name, country, latitude, longitude, station_code, wmo_id) VALUES (26, 'Ottawa', 'Kanada', 45.32, -75.67, 'CYOW', '71628');
INSERT INTO public.cities (city_id, city_name, country, latitude, longitude, station_code, wmo_id) VALUES (27, 'Atina', 'Yunanistan', 37.97, 23.72, 'ATHINAI', '16714');


--
-- Name: airports_airport_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.airports_airport_id_seq', 27, true);


--
-- Name: cities_city_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.cities_city_id_seq', 27, true);


--
-- PostgreSQL database dump complete
--

\unrestrict Bna76HdB25qlZ57Z4UbEAUhvJ3kfbsxieetaLhM6VJKawWBn1H6F8gxG69Kz5X4

