
DROP TABLE IF EXISTS book;

CREATE TABLE book (
       book_id serial primary key,
       title text not null,
       publisher text not null,
       book_uuid text not null,
       isbn1 text not null,
       subtitle text not null,
       page_count integer not null,
       bisac_subject_code_1 text not null,
       doi text unique not null
);
