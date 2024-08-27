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
$ADMIN_MODE = true;  // set this constant to true if you need to by-pass credit system temporarly
$GAME_ID = "4"; // Game ID

$paymentToken = null;


$BONUS_STAMP_CODE = 0;
$EXPLOSION_STAMP_CODE = -1;


function generateRandomNumbersForColumn($rows, &$alreadyFoundBonus) {
	global $BONUS_STAMP_CODE;

    $numbers = [];
    for ($j = 0; $j < $rows; $j++) {
        do {
            $stamp = draw_a_stamp();
        } while ($stamp == $BONUS_STAMP_CODE && $alreadyFoundBonus);
        
        array_push($numbers, $stamp);
		if ($stamp == $BONUS_STAMP_CODE) {
            $alreadyFoundBonus = true; // Rule : There can be only one bonus per grid generated
        }
    }
    return $numbers;
}

function generateFurtherColumns($array, $rows, $generationCounter, &$alreadyFoundBonus) {
	// goal of this function is to extend the given grid, whenever "exploding stamps" are found
	// array represents a 3-column grid with stamp codes

	global $BONUS_STAMP_CODE, $EXPLOSION_STAMP_CODE ;

    $regeneratedArrays = [];
    $alreadyFoundBonusInRegeneration = false;

    foreach ($array as $row) {
        if (in_array($EXPLOSION_STAMP_CODE , $row)) {
            $explosionLessColumn = [];
            do {
				$tempBonusHint=$alreadyFoundBonus;
                $explosionLessColumn = generateRandomNumbersForColumn($rows, $tempBonusHint);
            } while (in_array($EXPLOSION_STAMP_CODE , $explosionLessColumn));
			$alreadyFoundBonus = $alreadyFoundBonus | $tempBonusHint;

            $newRow = [$generationCounter, $row[1]];
            foreach ($explosionLessColumn as $number) {
                $newRow[] = $number;
            }
            $regeneratedArrays[] = $newRow;
        }
    }

    return array_merge($array, $regeneratedArrays);
}

function checkForBonuses($arrays) {
    global $BONUS_STAMP_CODE, $EXPLOSION_STAMP_CODE;
    
    $validBonusCount = 0;
    $columnsWithExplosion = [];

    // First pass: identify columns with explosions
    foreach ($arrays as $array) {
        $columnIndex = $array[1]; // "C0", "C1", etc.
        if (in_array($EXPLOSION_STAMP_CODE, array_slice($array, 2))) {
            $columnsWithExplosion[] = $columnIndex;
        }
    }

    // Second pass: count valid bonuses
	$already_rem = [];  // array for storing columns that have already been ignored due to an explosion, so we dont ignore the final column content!

    foreach ($arrays as $array) {
        $columnIndex = $array[1];
        // Skip columns with explosions
        if (in_array($columnIndex, $columnsWithExplosion) and !in_array($columnIndex, $already_rem)) {
			array_push($already_rem, $columnIndex);
            continue;
        }
        // Count bonuses in valid columns
        $validBonusCount += count(array_filter(array_slice($array, 2), function($stamp) use ($BONUS_STAMP_CODE) {
            return $stamp === $BONUS_STAMP_CODE;
        }));
    }

    return $validBonusCount;
}

function generateRandomArray($rows, $columns, &$generations) {
    global $BONUS_STAMP_CODE, $EXPLOSION_STAMP_CODE;
    
    $remainingGen = $generations;
    $allData = [];
    $g = 0;

    while ($remainingGen > 0) {
        $array = [];
        $alreadyFoundBonus = false;

        for ($i = 0; $i < $columns; $i++) {
            $numbers = generateRandomNumbersForColumn($rows, $alreadyFoundBonus);
            $row = [$g, "C$i"];
            $row = array_merge($row, $numbers);
            $array[] = $row;
        }

        $array = generateFurtherColumns($array, $rows, $g, $alreadyFoundBonus);
        $allData = array_merge($allData, $array);

        // Check for valid bonuses
        $validBonusCount = checkForBonuses($array);
        $remainingGen += (2 * $validBonusCount);

        $remainingGen--;
        $g++;
    }
    $generations = $g;
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