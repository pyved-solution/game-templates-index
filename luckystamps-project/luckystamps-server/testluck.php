<?php
require_once('secretdraw.php');
require_once('gains.php');
require_once('low_level.php');

// REMARQUE TOM
// provoquait erreur:
// ... has been blocked by CORS policy: The 'Access-Control-Allow-Origin' header contains multiple values '*, *', but only one is allowed.
// je pense que ca venait du fait qu'on a un doublon avec le .htaccess
// du coup faut choisir: soit l'un soit l'autre !
// header('Access-Control-Allow-Origin: *');

$API_URL = "https://services-beta.kata.games/pvp";
$ADMIN_MODE = false;  // set this constant to true if you need to by-pass credit system temporarly
$GAME_ID = "4"; // Game ID

$paymentToken = null;
$BONUS_STAMP_CODE = 0;


function generateRandomNumbersForColumn($rows, &$alreadyFoundBonus) {
    $numbers = [];
    for ($j = 0; $j < $rows; $j++) {
        do {
            $stamp = draw_a_stamp();
        } while ($alreadyFoundBonus && $stamp == $BONUS_STAMP_CODE);
        
        if ($stamp == $BONUS_STAMP_CODE) {
            $alreadyFoundBonus = true; // Rule : There can be only one bonus per grid generated
        }
        $numbers[] = $stamp;
    }
    return $numbers;
}

function verifyAndRegenerate($array, $rows, $generationCounter, &$alreadyFoundBonus, &$additionalGenerationsRequired) {
    $regeneratedArrays = [];
    $alreadyFoundBonusInRegeneration = false;

    foreach ($array as $row) {
        if (in_array(-1, $row)) {
            $newNumbers = [];
            do {
                $newNumbers = generateRandomNumbersForColumn($rows, $alreadyFoundBonus);
            } while (in_array(-1, $newNumbers));

            $newRow = [$generationCounter, $row[1]];
            foreach ($newNumbers as $number) {
                $newRow[] = $number;
                if ($number === $BONUS_STAMP_CODE && !$alreadyFoundBonusInRegeneration && !$alreadyFoundBonus) {
                    $alreadyFoundBonusInRegeneration = true;
                    $alreadyFoundBonus = true;
                }
            }
            $regeneratedArrays[] = $newRow;
        }
    }

    if ($alreadyFoundBonusInRegeneration) {
        $additionalGenerationsRequired += 2;
    }

    return array_merge($array, $regeneratedArrays);
}

function generateRandomArray($rows, $columns, &$generations) {
    $allData = [];
    $g = 0;
    $additionalGenerationsRequired = 0;

    while ($g < $generations + $additionalGenerationsRequired) {
        $array = [];
        $alreadyFoundBonus = false;
        $foundNegativeOne = false;

        for ($i = 0; $i < $columns; $i++) {
            $numbers = generateRandomNumbersForColumn($rows, $alreadyFoundBonus);
            $row = [$g, "C$i"];
            
            foreach ($numbers as $number) {
                $row[] = $number;
                if ($number === $BONUS_STAMP_CODE) {
                    $alreadyFoundBonus = true;
                }
                if ($number === -1) {
                    $foundNegativeOne = true;
                }
            }
            $array[] = $row;
        }

        $array = verifyAndRegenerate($array, $rows, $g, $alreadyFoundBonus, $additionalGenerationsRequired);
        $allData = array_merge($allData, $array);
        
        if ($alreadyFoundBonus && !$foundNegativeOne) {
            $generations += 2;
        }

        $g++;
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
	global $API_URL, $GAME_ID, $paymentToken;

    $description = "Lucky Stamps winnings";
    // Prepare the URL with parameters
    $getUrl = $API_URL . '/games/getPaid';
    $getUrl .= '?user_id=' . $userId;
    $getUrl .= '&game_id=' . urlencode($GAME_ID);
    $getUrl .= '&amount=' . urlencode($totalCreditsWon);
    $getUrl .= '&token=' . urlencode($paymentToken);
    $getUrl .= '&description=' . urlencode($description);

    $responseData = std_curl_call($getUrl);

    if (isset($responseData['success']) && !$responseData['success']) {
        throw new Exception("Failed to update user credits through API.");
    }
}


function payGameFee($userId, $gameId, $gamePrice,$jwtToken) {
	global $API_URL, $paymentToken;

    $getUrl = $API_URL . '/games/payGameFee';
    $getUrl .= '?jwt=' . urlencode($jwtToken);
    $getUrl .= '&game_id=' . urlencode($gameId);
    $getUrl .= '&game_price=' . urlencode($gamePrice);

    $responseData = std_curl_call($getUrl);

    if (isset($responseData['reply_code']) && $responseData['reply_code'] == "200") {
        if (!empty($responseData['token_code'])) {
            $paymentToken = $responseData['token_code'];
        } else {
            throw new Exception("API did not return a tokenCode.");
        }
    } else {
        die('"Error in payGameFee ->'.$responseData['message'].'"');
    }
}

$userId = null;
$gamePrice = null;
$jwtValue = null;

if(!$ADMIN_MODE){
	if(!isset($_GET['user_id'])){
		throw new Exception('user_id not provided!');
	}
	if(!isset($_GET['game_price'])){
		throw new Exception('game_price not provided!');
	}
	if(!isset($_GET['jwt'])){
		throw new Exception('jwt not provided!');
	}

	$userId = $_GET['user_id'];
    $gamePrice = $_GET['game_price'];
	$jwtValue = $_GET['jwt'];
	payGameFee($userId, $GAME_ID, $gamePrice,$jwtValue);
}

$rows = 3;
$columns = 5;
$generations = 3; // Nombre initial de générations
$min = -1;
$max = 8;
$data = generateRandomArray(3, 5, $generations);  // la var. generations est mise à jour par retour de param.
$li_credit_gains = compute_credit_gains($data, 3, 5, $generations);

if(!$ADMIN_MODE){
	$totalCreditsWon = array_sum($li_credit_gains);
	if ($totalCreditsWon>0){
	  updateUserCredits($userId, $totalCreditsWon, $jwtValue);
	}
}

$response = [$data,$li_credit_gains,$ADMIN_MODE];

//ob_flush();

header('Content-Type: application/json');
echo json_encode($response);