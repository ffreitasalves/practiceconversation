CREATE TABLE 	ROOMS(
   ID INTEGER PRIMARY KEY     NOT NULL,
   LANGUAGE           TEXT    NOT NULL,
   POP            INTEGER     NOT NULL,
   ts_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);