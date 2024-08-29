<?php
/* Nota Bene Tom August2024
 this file shouldnt be here as the game should not use a database
 (if its really needed for the game logic, one can use the 'homemade_db.php' tho )
 
 but right now I cannot remove it or it will crash the SpinTheWheel game logic
*/

define( "DB_DSN", "mysql:host=xxx.net;dbname=my_database_name" );
define( "DB_USERNAME", "my-username" );
define( "DB_PASSWORD", "my-password" );

function dbConnection(){
    try {
        $conn = new PDO(DB_DSN, DB_USERNAME, DB_PASSWORD);
        $conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
        return $conn;
    } catch (PDOException $e) {
        echo "Erreur de connexion à la base de données : " . $e->getMessage();
        // Gérer l'erreur de connexion à la base de données ici
    }
}