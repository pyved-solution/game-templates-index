<?php
$slugName = "LuckyStamps1";
$GAME_PRICE = 5;
require_once('low_level.php');


function getUserIdByJwt($jwt) {

	$endpoint = "http://cms-beta.kata.games/content/plugins/facade/user/jwt?jwt=" . urlencode($jwt);
	$data = std_curl_call($endpoint, true);  // 2nd arg is to follow redirections & ignore https method

	if ($data['reply_code']!=200){
		echo "WARNING: was impossible to find the UserId tied to the Jwt provided: $jwt";
		return null;
	}
	return $data['user_id'];
}


if (isset($_GET['jwt'])) {

    $token = $_GET['jwt'];
    $userId = getUserIdByJwt($token);
	if ($userId==NULL){
		var_dump($userId);
		die("no valid JWT, no userId found" );
	}
    // Send parameters as part of the URL 
    $urlPourTestLuck = 'https://' . $_SERVER['HTTP_HOST'] . "/game-servers/$slugName/testluck.php";
    $params = http_build_query(['user_id' => $userId, 'game_price' => $GAME_PRICE, 'jwt' => $token]);

    // $jsonObj = json_decode(file_get_contents($url . '?' . $params), true);
    header('Content-Type: application/json');
    echo file_get_contents($urlPourTestLuck . '?' . $params);
} else {

    echo '!!! No JWT sent';
}
