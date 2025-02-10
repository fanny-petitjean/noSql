-- Créer la base de données
CREATE DATABASE social_network;

-- Se connecter à la base
\c social_network;

-- Création des tables
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE followers (
    user_id INT REFERENCES users(id),
    follower_id INT REFERENCES users(id),
    PRIMARY KEY (user_id, follower_id)
);

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    price DECIMAL(10,2) NOT NULL
);

CREATE TABLE purchases (
    user_id INT REFERENCES users(id),
    product_id INT REFERENCES products(id),
    purchase_date TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (user_id, product_id)
);