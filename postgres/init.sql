CREATE TABLE IF NOT EXISTS file_doc(
    ID SERIAL PRIMARY KEY,
    FILE_UUID varchar(250) NOT NULL,
    FILENAME varchar(250)  NOT NULL,
    UPLOAD_DATE date
);
