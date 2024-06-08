--
-- PostgreSQL database dump
--

-- Dumped from database version 16.2 (Homebrew)
-- Dumped by pg_dump version 16.2 (Homebrew)

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
-- Name: anekdotes; Type: TABLE; Schema: public; Owner: tg_bot
--

CREATE TABLE public.anekdotes (
    id integer NOT NULL,
    title character varying(50) NOT NULL,
    text text NOT NULL,
    username character varying(50) NOT NULL
);


ALTER TABLE public.anekdotes OWNER TO tg_bot;

--
-- Name: anekdotes_id_seq; Type: SEQUENCE; Schema: public; Owner: tg_bot
--

CREATE SEQUENCE public.anekdotes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.anekdotes_id_seq OWNER TO tg_bot;

--
-- Name: anekdotes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: tg_bot
--

ALTER SEQUENCE public.anekdotes_id_seq OWNED BY public.anekdotes.id;


--
-- Name: anekdotes id; Type: DEFAULT; Schema: public; Owner: tg_bot
--

ALTER TABLE ONLY public.anekdotes ALTER COLUMN id SET DEFAULT nextval('public.anekdotes_id_seq'::regclass);


--
-- Data for Name: anekdotes; Type: TABLE DATA; Schema: public; Owner: tg_bot
--

COPY public.anekdotes (id, title, text, username) FROM stdin;
1	Чопа	Пёс	Nikita
2	Лиза	Лиза хрен	Nikita
\.


--
-- Name: anekdotes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: tg_bot
--

SELECT pg_catalog.setval('public.anekdotes_id_seq', 2, true);


--
-- Name: anekdotes anekdotes_pkey; Type: CONSTRAINT; Schema: public; Owner: tg_bot
--

ALTER TABLE ONLY public.anekdotes
    ADD CONSTRAINT anekdotes_pkey PRIMARY KEY (id);


--
-- PostgreSQL database dump complete
--

