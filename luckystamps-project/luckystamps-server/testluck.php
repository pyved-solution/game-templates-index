<?php
include('../dbconnection.php');
require_once('secretdraw.php');
require_once('gains.php');

// REMARQUE TOM
// provoquait erreur:
// ... has been blocked by CORS policy: The 'Access-Control-Allow-Origin' header contains multiple values '*, *', but only one is allowed.

// je pense que ca venait du fait qu'on a un doublon avec le .htaccess
// du coup faut choisir: soit l'un soit l'autre !

// header('Access-Control-Allow-Origin: *');



//
header('Content-Type: application/json');


function generateRandomNumbersForColumn($rows) {
    $numbers = [];
    for ($j = 0; $j < $rows; $j++) {
        $numbers[] = draw_a_stamp();
    }
    return $numbers;
}

function verifyAndRegenerate($array, $rows, $generationCounter, &$foundZero, &$additionalGenerationsRequired) {
    $regeneratedArrays = [];
    $foundZeroInRegeneration = false;

    foreach ($array as $row) {
        if (in_array(-1, $row)) {
            $newNumbers = [];
            do {
                $newNumbers = generateRandomNumbersForColumn($rows);
            } while (in_array(-1, $newNumbers));

            $newRow = [$generationCounter, $row[1]]; // Le numéro de génération et l'identifiant de colonne restent inchangés
            foreach ($newNumbers as $number) {
                $newRow[] = $number;
                if ($number === 0) {
                    $foundZeroInRegeneration = true; // Détecter la présence d'un 0
                    $foundZero = true;
                }
            }
            $regeneratedArrays[] = $newRow;
        }
    }

    // If zeros were found during regeneration, update the additional generations required.
    if ($foundZeroInRegeneration) {
        $additionalGenerationsRequired += 2; // For simplicity, add 2 more generations for each regeneration phase that finds zeros. Adjust as needed.
    }

    return array_merge($array, $regeneratedArrays);
}


function generateRandomArray($rows, $columns, &$generations) {
    $allData = [];
    $g = 0; // Initialize the generation counter
    $additionalGenerationsRequired = 0; // Track additional generations required due to zeros found during regeneration

    while ($g < $generations + $additionalGenerationsRequired) {
        $array = [];
        $foundZero = false; // Reset for each generation
        $foundNegativeOne = false; // Flag to check for -1 in the array
        $zerosFoundInGeneration = 0; // Track zeros found in the current generation

        for ($i = 0; $i < $columns; $i++) {
            $numbers = generateRandomNumbersForColumn($rows);
            $row = [$g, "C$i"];
            $zerosInRow = 0; // Track zeros found in the current row 
            // Count all the values of the array
            $valueCounts = array_count_values($numbers);
        
            // Check if '6' is a key in the resulting array and get its count
            $countOf0 = isset($valueCounts[0]) ? $valueCounts[0] : 0;
            foreach ($numbers as $number) {
                $row[] = $number;

                if ($number === 0) {
                    $foundZero = true; // Detect the presence of a 0
                    $zerosInRow++; // Increment for each zero found in the row
                }
                if (in_array(0, $numbers) && in_array(-1, $numbers)) {
                    $foundNegativeOne = true;
                }
                
            }
            $zerosFoundInGeneration += $countOf0; // Add the count of zeros in the row to the generation's total
            $array[] = $row;
        }

        // Verify conditions and regenerate arrays if necessary
        $array = verifyAndRegenerate($array, $rows, $g, $foundZero, $additionalGenerationsRequired);
        $allData = array_merge($allData, $array);
        // Correctly adjust generations based on zeros found
        if ($foundZero && !$foundNegativeOne) {
            $generations += 2 * $zerosFoundInGeneration; // For each zero found, add two more generations
        } 

        $g++; // Increment the generation counter after each complete cycle
    }
    return $allData;
}



// function updateUserCredits($userId, $totalCreditsWon) {
//     $conn = dbConnection();
//     // Mise à jour des crédits de l'utilisateur
//     $stmt = $conn->prepare("UPDATE inventory SET credits = credits + :creditsToAdd WHERE user_id = :userId");
//     $stmt->execute(['userId' => $userId, 'creditsToAdd' => $totalCreditsWon]);
// }
function updateUserCredits($userId, $totalCreditsWon) {
    global $apiUrl, $token, $gameId;

    $description = "Lucky Stamps winnings";
    // Prepare the URL with parameters
    $getUrl = $apiUrl . '/games/getPaid';
    $getUrl .= '?user_id=' . $userId;
    $getUrl .= '&game_id=' . urlencode($gameId);
    $getUrl .= '&amount=' . urlencode($totalCreditsWon);
    $getUrl .= '&token=' . urlencode($token);
    $getUrl .= '&description=' . urlencode($description);


    // Initialize cURL session
    $ch = curl_init($getUrl);

    // Set cURL options
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_HTTPGET, true);
    curl_setopt($ch, CURLOPT_HTTPHEADER, [
        'Content-Type: application/json',
    ]);

    $response = curl_exec($ch);
    if (curl_errno($ch)) {
        throw new Exception(curl_error($ch));
    }

    curl_close($ch);

    $responseData = json_decode($response, true);
    if (isset($responseData['success']) && !$responseData['success']) {
        throw new Exception("Failed to update user credits through API.");
    }
}


function payGameFee($userId, $gameId, $gamePrice) {
    global $apiUrl, $token; // Use the global variable for API URL

    $getUrl = $apiUrl . '/games/payGameFee';
    $getUrl .= '?jwt=' . urlencode($token);
    $getUrl .= '&game_id=' . urlencode($gameId);
    $getUrl .= '&game_price=' . urlencode($gamePrice);

    $ch = curl_init($getUrl);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_HTTPGET, true);
    curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
    $response = curl_exec($ch);

    if (curl_errno($ch)) {
        curl_close($ch);
        throw new Exception(curl_error($ch));
    }
    curl_close($ch);

    $responseData = json_decode($response, true);
    if (isset($responseData['reply_code']) && $responseData['reply_code'] == "200") {
        if (!empty($responseData['token_code'])) {
            $token = $responseData['token_code'];
        } else {
            throw new Exception("API did not return a tokenCode.");
        }
    } else {
        die('"'.$responseData['message'].'"');
    }
}

$apiUrl = "https://t-api-beta.kata.games"; 
$gameId = "11"; // Game ID
$mode_admin = false;
$userId = null;
$gamePrice = null;
$token = null;
if(!isset($_GET['user_id'])){
    $mode_admin = true;
}else{
    $userId = $_GET['user_id'];
    $gamePrice = $_GET['game_price'];
    $token = $_GET['token'];
}

if(!$mode_admin){
    payGameFee($userId, $gameId, $gamePrice);
}
$rows = 3;
$columns = 5;
$generations = 3; // Nombre initial de générations
$min = -1;
$max = 8;
$data = generateRandomArray(3, 5, $generations);  // la var. generations est mise à jour par retour de param.


$li_credit_gains = compute_credit_gains($data, 3, 5, $generations);

$totalCreditsWon = array_sum($li_credit_gains);
if ($userId !== null && !$mode_admin) {
    updateUserCredits($userId, $totalCreditsWon);
}

$response = [$data,$li_credit_gains];
ob_flush();
echo json_encode($response);