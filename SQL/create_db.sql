PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS user_(
   id_user_mail VARCHAR(50),
   password VARCHAR(50) NOT NULL,
   PRIMARY KEY(id_user_mail)
);

CREATE TABLE IF NOT EXISTS user_page(
   id_user_page VARCHAR(50),
   nom VARCHAR(50) NOT NULL,
   prénom VARCHAR(50) NOT NULL,
   photo_profils PNG,
   tel CHAR(10),
   email VARCHAR(50),
   adresse TEXT,
   id_user_mail VARCHAR(50) NOT NULL,
   PRIMARY KEY(id_user_page),
   FOREIGN KEY(id_user_mail) REFERENCES user_(id_user_mail)
);

CREATE TABLE IF NOT EXISTS formation(
   id_formation VARCHAR(50),
   nom_formation VARCHAR(50) NOT NULL,
   date_début DATE NOT NULL,
   date_fin DATE,
   description_formation VARCHAR(50),
   organisme_formation VARCHAR(50) NOT NULL,
   diplome_url url,
   id_user_page VARCHAR(50) NOT NULL,
   PRIMARY KEY(id_formation),
   FOREIGN KEY(id_user_page) REFERENCES user_page(id_user_page)
);

CREATE TABLE IF NOT EXISTS experience(
   id_experience VARCHAR(50),
   nom_experience VARCHAR(50) NOT NULL,
   date_début DATE NOT NULL,
   date_fin DATE,
   dscription_experience VARCHAR(50),
   organisme_experience VARCHAR(50),
   lieu_experience TEXT,
   id_user_page VARCHAR(50) NOT NULL,
   PRIMARY KEY(id_experience),
   FOREIGN KEY(id_user_page) REFERENCES user_page(id_user_page)
);
