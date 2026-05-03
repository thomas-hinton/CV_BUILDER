PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
   id            VARCHAR(36)  NOT NULL,
   email         VARCHAR(100) NOT NULL UNIQUE,
   password_hash VARCHAR(255) NOT NULL,
   created_at    DATETIME     NOT NULL DEFAULT (datetime('now')),
   PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS cv_profiles (
   id_user_page VARCHAR(50),
   nom          VARCHAR(50)  NOT NULL,
   prenom       VARCHAR(50)  NOT NULL,
   photo_profil TEXT,
   tel          CHAR(10),
   email        VARCHAR(100),
   adresse      TEXT,
   user_id      VARCHAR(36)  NOT NULL UNIQUE,
   slug         VARCHAR(100) NOT NULL UNIQUE,
   is_public    INTEGER      NOT NULL DEFAULT 0,
   show_email   INTEGER      NOT NULL DEFAULT 0,
   show_phone   INTEGER      NOT NULL DEFAULT 0,
   PRIMARY KEY (id_user_page),
   FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE TABLE IF NOT EXISTS formations (
   id_formation          VARCHAR(50),
   nom_formation         VARCHAR(50) NOT NULL,
   date_debut            DATE        NOT NULL,
   date_fin              DATE,
   description_formation TEXT,
   organisme_formation   VARCHAR(50) NOT NULL,
   diplome_url           TEXT,
   id_user_page          VARCHAR(50) NOT NULL,
   PRIMARY KEY (id_formation),
   FOREIGN KEY (id_user_page) REFERENCES cv_profiles (id_user_page) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS experiences (
   id_experience         VARCHAR(50),
   nom_experience        VARCHAR(50) NOT NULL,
   date_debut            DATE        NOT NULL,
   date_fin              DATE,
   description_experience TEXT,
   organisme_experience  VARCHAR(50),
   lieu_experience       TEXT,
   id_user_page          VARCHAR(50) NOT NULL,
   PRIMARY KEY (id_experience),
   FOREIGN KEY (id_user_page) REFERENCES cv_profiles (id_user_page) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS skills (
   id_skill     VARCHAR(50)  NOT NULL,
   nom_skill    VARCHAR(100) NOT NULL,
   niveau       VARCHAR(50),
   categorie    VARCHAR(100),
   id_user_page VARCHAR(50)  NOT NULL,
   PRIMARY KEY (id_skill),
   FOREIGN KEY (id_user_page) REFERENCES cv_profiles (id_user_page) ON DELETE CASCADE
);
